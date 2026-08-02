# ELK Stack Setup — Elasticsearch, Kibana & Filebeat on Ubuntu (systemd)

A hands-on project setting up a self-hosted log monitoring pipeline using the Elastic Stack (Elasticsearch, Kibana, Filebeat), running as native systemd services on a single Ubuntu VM — including the real debugging process, not just the happy path.

---

## 🎯 Goal

Set up a working log monitoring pipeline where:
1. **Elasticsearch** stores and indexes log data
2. **Kibana** provides a UI to search and visualize that data
3. **Filebeat** tails log files on the server and ships them to Elasticsearch automatically

All three run as **systemd services** (not Docker), managed the same way as any other Linux service (`daemon-reload`, `enable`, `start`, `status`) — the goal being to understand the stack at the OS/service level rather than abstracting it away behind containers.

**Why this matters:** centralized log shipping is standard practice the moment you have more than one server — "SSH in and grep the log file" doesn't scale. This project was built to understand each moving part (config files, REST APIs, service lifecycle) well enough to reason about it in a real production environment, not just get it running once.

---

## 🧱 Architecture

```
Log files on disk (/var/log/*.log, syslog, custom app logs)
          │
          ▼
      Filebeat  ──ships (HTTPS, Bulk API)──▶  Elasticsearch  ◀──queries (Search API)──  Kibana
   (reads/tails)                              (stores/indexes)                         (visualizes)
```

- Elasticsearch: `https://localhost:9200`
- Kibana: `http://localhost:5601`
- Filebeat: no listening port — outbound shipper only

---

## 🛠️ What Was Done

### 1. Prior state — cleaned up a conflicting Docker setup
The Elastic Stack had previously been run via Docker containers for testing. Before installing the systemd-based services, leftover containers, images, and networks were removed to avoid port conflicts (9200/5601) and reclaim disk space:
```bash
docker ps -a
sudo docker system prune -a --volumes
```

### 2. Installed Elasticsearch, Kibana, and Filebeat via APT
Added Elastic's official package repository and GPG key, then installed all three components:
```bash
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elastic-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/elastic-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt-get update
sudo apt-get install elasticsearch kibana filebeat
```

### 3. Enabled and started all three as systemd services
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now elasticsearch
sudo systemctl enable --now kibana
sudo systemctl enable --now filebeat
```

### 4. Diagnosed and fixed a RED cluster / authentication failure
`curl localhost:9200` initially returned an empty reply, later a `401`. Root cause tracing (via `journalctl -u elasticsearch`) revealed the disk was above the **90% high watermark**, which blocked Elasticsearch from allocating the internal `.security-7` index — meaning the `elastic` user's credentials couldn't be read *or* reset. This wasn't a password problem; it was a disk-space problem masquerading as one.

**Fix:** freed disk space (the earlier Docker cleanup), restarted Elasticsearch, then reset the password successfully:
```bash
sudo /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic -f
```

### 5. Enrolled Kibana with Elasticsearch
Generated a one-time enrollment token and used it in Kibana's browser setup screen to establish trust between the two services:
```bash
sudo /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
```

### 6. Configured Filebeat to ship logs to Elasticsearch
Edited `/etc/filebeat/filebeat.yml`:
```yaml
filebeat.inputs:
  - type: filestream
    id: my-filestream-id
    enabled: true
    paths:
      - /var/log/*.log
      - /var/log/syslog

output.elasticsearch:
  hosts: ["https://localhost:9200"]
  username: "elastic"
  password: "<redacted>"
  ssl.verification_mode: none
```

Along the way, fixed two config bugs:
- **YAML indentation error** — a misaligned `ssl.verification_mode` line broke the entire file's structure (`did not find expected key`)
- **Path typo** — `/var/logs/*.log` (extra "s") silently matched zero files; corrected to `/var/log/*.log`

### 7. Verified the pipeline end-to-end
```bash
sudo filebeat test config
sudo filebeat test output
sudo filebeat setup -e          # loads index template + Kibana dashboards
for i in {1..20}; do logger "filebeat test line $i - $(date)"; done
curl -k -u "elastic:<password>" "https://localhost:9200/filebeat-*/_count?pretty"
```
Confirmed a non-zero document count, then viewed the entries live in **Kibana → Discover** under the `filebeat-*` data view.

### 8. Documented safe shutdown/restart procedure
Since an unclean shutdown risks Elasticsearch data corruption (in-memory data not flushed to disk), established the correct stop order:
```bash
sudo systemctl stop filebeat
sudo systemctl stop kibana
sudo systemctl stop elasticsearch
```
(reverse order on restart — all three are `enabled`, so they also auto-start on boot).

---

## 🐛 Key Issues Hit & Root Causes

| Issue | Symptom | Root Cause | Fix |
|---|---|---|---|
| Empty curl reply | `curl: (52) Empty reply from server` | ES 8.x defaults to HTTPS; was querying plain HTTP | Use `https://` + `-k` (self-signed cert) |
| Password reset failing (exit 69/75) | `Cluster health is currently RED` | Disk usage >90%, blocking `.security-7` index allocation | Freed disk space (removed old Docker images/volumes) |
| Filebeat config parse error | `yaml: line 169: did not find expected key` | `ssl.verification_mode` line had zero indentation | Corrected YAML indentation |
| Zero documents indexed | `harvester: {open_files: 0}`, count stayed 0 | Typo in path: `/var/logs/*.log` instead of `/var/log/*.log` | Fixed path, restarted Filebeat |
| `filebeat.yml` appeared empty in `nano` | Blank buffer on open | File was `-rw-------` root-only; opened without `sudo` | Reopened with `sudo nano` |

---

## 📂 Key File Locations

| Component | Config | Data | Logs |
|---|---|---|---|
| Elasticsearch | `/etc/elasticsearch/elasticsearch.yml` | `/var/lib/elasticsearch/` | `/var/log/elasticsearch/` |
| Kibana | `/etc/kibana/kibana.yml` | `/var/lib/kibana/` | `/var/log/kibana/` |
| Filebeat | `/etc/filebeat/filebeat.yml` | `/var/lib/filebeat/registry/` | `/var/log/filebeat/` |

---

## ✅ Current Status

- [x] Elasticsearch, Kibana, Filebeat installed and running as systemd services
- [x] Elasticsearch authenticated (`elastic` user, password securely stored outside version control)
- [x] Kibana enrolled and connected to Elasticsearch
- [x] Filebeat actively shipping log data, confirmed via document count and Kibana Discover
- [x] Safe shutdown/restart procedure documented and tested

## 🔜 Possible Next Steps

- Set up **Index Lifecycle Management (ILM)** to auto-delete old indices and prevent repeat disk-space incidents
- Point Filebeat at real application logs instead of test data
- Build custom Kibana dashboards for specific monitoring needs
- Explore multi-node Elasticsearch for high availability (not needed at current scale)

---

## ⚠️ Note on Secrets

The `elastic` user password and any enrollment tokens used in this project are **not included** in this repository. If documenting your own setup, store credentials in a local, git-ignored file (e.g. `/etc/elastic-credentials/`) — never commit them.
