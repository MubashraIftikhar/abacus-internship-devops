const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());
const PORT = 5000;

let db;

function connectWithRetry() {
  db = mysql.createConnection({          // NEW connection object every retry
    host: 'database',
    user: 'root',
    password: 'examplepass',
    database: 'studentdb'
  });

  db.connect((err) => {
    if (err) {
      console.log('DB not ready yet, retrying in 3s...', err.message);
      setTimeout(connectWithRetry, 3000);
    } else {
      console.log('Connected to MySQL database!');
      db.query(`
        CREATE TABLE IF NOT EXISTS students (
          id INT AUTO_INCREMENT PRIMARY KEY,
          name VARCHAR(100),
          roll_no VARCHAR(50)
        )
      `);
    }
  });
}

connectWithRetry();

app.post('/submit', (req, res) => {
  const { name, roll_no } = req.body;
  db.query('INSERT INTO students (name, roll_no) VALUES (?, ?)', [name, roll_no], (err) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: 'Saved successfully' });
  });
});

app.get('/students', (req, res) => {
  db.query('SELECT * FROM students', (err, results) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(results);
  });
});

app.listen(PORT, () => console.log(`Backend running on port ${PORT}`));
