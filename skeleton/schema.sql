CREATE DATABASE IF NOT EXISTS photoshare;
CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  loc CHAR(100),
  album_id int4,
  INDEX upid_idx (user_id),
  PRIMARY KEY (picture_id),
  FOREIGN KEY (album_id) REFERENCES Albums (album_id) ON DELETE CASCADE
);

CREATE TABLE Albums (
    album_id INT4 AUTO_INCREMENT,
    album_name CHAR(20),
    user_id INT4,
    doc DATE,
    PRIMARY KEY (album_id),
    FOREIGN KEY (user_id) REFERENCES Users (user_id)
        ON DELETE CASCADE
);

CREATE TABLE Tag(
  word CHAR(10),
  picture_id int4,
  PRIMARY KEY (word),
  FOREIGN KEY (picture_id) REFERENCES Pictures (picture_id)
 );

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
SELECT picture_id, caption FROM Pictures;
SELECT * FROM Tag T;
SELECT P.picture_id, P.user_id, P.imgdata, P.caption, P.loc, P.album_id FROM Pictures P, Tag T WHERE T.word = 'jo' AND T.picture_id = P.picture_id;
INSERT INTO Tag(word, picture_id) VALUES ('jo', 3);
SELECT P.picture_id, P.user_id, P.imgdata, P.caption, P.loc, P.album_id FROM Pictures P, Tag T WHERE T.word = 'jo' AND T.picture_id
