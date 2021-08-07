DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS books;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE members (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status BOOLEAN DEFAULT TRUE,
  phone TEXT NOT NULL,
  email TEXT NOT NULL,
  dob DATE NOT NULL,
  gender CHARACTER(1),
  address TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE books (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  bookID INTEGER,
  title TEXT NOT NULL,
  authors TEXT NOT NULL,
  average_rating FLOAT,
  isbn TEXT,
  isbn13 TEXT,
  language_code TEXT,
  num_pages INTEGER,
  ratings_count INTEGER,
  text_reviews_count INTEGER,
  publication_date DATE,
  publisher TEXT NOT NULL,
  book_count INTEGER,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);