CREATE DATABASE IF NOT EXISTS rst_library CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE rst_library;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  fullName VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  studentId VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  memberSince DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(100) NOT NULL,
  category ENUM('Computer Science','AI & ML','Physics','Web Development') NOT NULL,
  description TEXT,
  coverImage VARCHAR(255) DEFAULT 'https://via.placeholder.com/150x200?text=No+Cover',
  addedDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  date DATE NOT NULL,
  time VARCHAR(50) NOT NULL,
  location VARCHAR(100) NOT NULL,
  description TEXT
);

CREATE TABLE IF NOT EXISTS complaints (
  id INT AUTO_INCREMENT PRIMARY KEY,
  issueType ENUM('Technical Issue','Another issue type') NOT NULL,
  message TEXT NOT NULL,
  userId INT,
  createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (userId) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS user_events (
  user_id INT NOT NULL,
  event_id INT NOT NULL,
  PRIMARY KEY (user_id, event_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_favorites (
  user_id INT NOT NULL,
  book_id INT NOT NULL,
  PRIMARY KEY (user_id, book_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

INSERT INTO books (title, author, category) VALUES
('Data Structures and Algorithms','Robert Lafore','Computer Science'),
('Introduction to Machine Learning','Ethem Alpaydin','AI & ML'),
('Quantum Physics for Beginners','Michael Brooks','Physics'),
('Modern Web Development','Kyle Simpson','Web Development'),
('Clean Code','Robert C. Martin','Computer Science'),
('Deep Learning Illustrated','Jon Krohn','AI & ML'),
('Astrophysics for People in a Hurry','Neil deGrasse Tyson','Physics'),
('Eloquent JavaScript','Marijn Haverbeke','Web Development'),
('Computer Networking: A Top-Down Approach','James Kurose','Computer Science'),
('Pattern Recognition and Machine Learning','Christopher Bishop','AI & ML'),
('The Feynman Lectures on Physics','Richard Feynman','Physics'),
('HTML and CSS: Design and Build Websites','Jon Duckett','Web Development'),
('Operating System Concepts','Abraham Silberschatz','Computer Science'),
('Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow','Aurélien Géron','AI & ML'),
('Seven Brief Lessons on Physics','Carlo Rovelli','Physics');

INSERT INTO events (title, date, time, location, description) VALUES
('Research Paper Writing Workshop','2026-04-15','14:00 - 16:00','Main Library, Room B12','Learn effective strategies for writing academic research papers.'),
('Digital Resources Orientation','2026-04-20','10:00 - 11:30','Library Computer Lab','Tour of our digital databases, e-books, and research tools.'),
('Book Club: Classic Literature','2026-05-01','16:00 - 17:30','Library Reading Room','Monthly discussion on selected classic novels. All are welcome!'),
('Citation Management Tools','2026-05-10','13:00 - 14:30','Online (Zoom)','Workshop on Zotero, Mendeley, and other reference managers.'),
('Poetry Reading Night','2026-04-25','18:00 - 20:00','Library Auditorium','Open mic night for poetry lovers. Share your work or listen!'),
('Library Tour for New Students','2026-04-10','11:00 - 12:00','Library Main Entrance','Guided tour of the library facilities and services.');