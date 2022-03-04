CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

CREATE TABLE Users(
	user_id INTEGER AUTO_INCREMENT,
	first_name VARCHAR(100),
	last_name VARCHAR(100),
	email VARCHAR(100) UNIQUE,
	birth_date DATE,
	hometown VARCHAR(100),
	gender VARCHAR(100),
	password VARCHAR(100) NOT NULL,
	PRIMARY KEY (user_id)
);
 
CREATE TABLE Friends(
	user_id1 INTEGER,
	user_id2 INTEGER,
	PRIMARY KEY (user_id1, user_id2),
	FOREIGN KEY (user_id1) REFERENCES Users(user_id),
	FOREIGN KEY (user_id2) REFERENCES Users(user_id)
);

CREATE TABLE Albums (
    album_id INTEGER AUTO_INCREMENT,
    album_name VARCHAR(100),
	doc DATE,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (album_id),
    FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
);

CREATE TABLE Pictures(
	picture_id INTEGER AUTO_INCREMENT,
	caption VARCHAR(255),
	imgdata LONGBLOB,
	loc CHAR(100),
	album_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	PRIMARY KEY (picture_id),
	FOREIGN KEY (album_id) REFERENCES Albums (album_id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES Users (user_id)
);

CREATE TABLE Tag(
  word VARCHAR(100),
  picture_id INTEGER,
  PRIMARY KEY (word, picture_id),
  FOREIGN KEY (picture_id) REFERENCES Pictures (picture_id)
  ON DELETE CASCADE
 );

CREATE TABLE Comments(
 cmmt_id INTEGER,
 user_id INTEGER NOT NULL,
 picture_id INTEGER NOT NULL,
 cmmt VARCHAR (100),
 doc DATE,
 PRIMARY KEY (cmmt_id),
 FOREIGN KEY (user_id) REFERENCES Users (user_id),
 FOREIGN KEY (picture_id) REFERENCES Pictures (picture_id)
 ON DELETE CASCADE
);

CREATE TABLE Likes(
	picture_id INTEGER,
	user_id INTEGER,
	PRIMARY KEY (picture_id, user_id),
	FOREIGN KEY (picture_id) REFERENCES Pictures (picture_id), 
	FOREIGN KEY (user_id) REFERENCES Users (user_id)
);

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
