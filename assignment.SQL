CREATE TABLE PUser(
	uid INTEGER,
	fname CHAR(20),
	lname CHAR(20),
	email CHAR(26),
	dob DATE,
	htown CHAR(20),
	gender CHAR(20),
	pw CHAR(26),
	PRIMARY KEY (uid)
);

CREATE TABLE Friends{
	uid INTEGER,
	fid INTEGER 
	CONSTRAINT nonself (uid != fid),
	PRIMARY KEY (uid, fid)
	FOREIGN KEY (uid) REFERENCES Users (uid),
);

CREATE TABLE Cmnt(
	cid INTEGER,
	uid INTEGER,
	cmt CHAR(100),
	docmt DATE,
	PRIMARY KEY (cid),
	FOREIGN KEY (uid) REFERENCES Puser (uid),
	FOREIGN KEY (pid) REFERENCES Photo (pid)
);

CREATE TABLE Commented(
	pid INTEGER,
	cid INTEGER,
	PRIMARY KEY(pid, cid),
	FOREIGN KEY (pid) REFERENCES Photo (pid),
	FOREIGN KEY (cid) REFERENCES Cmnt (cid)
);

CREATE TABLE Tag(
	word CHAR(10),
	PRIMARY KEY (word)
);

CREATE TABLE Adds(
	pid INTEGER,
	word CHAR(10),
	PRIMARY KEY(pid, word),
	FOREIGN KEY (pid) REFERENCES Photo (pid),
	FOREIGN KEY (word) REFERENCES Tag (word)
);

CREATE TABLE Photo(
	pid INTEGER,
	caption CHAR(100),
	loc CHAR(100),
	PRIMARY KEY (pid)
);

CREATE TABLE Holds(
	aid INTEGER,
	pid INTEGER,
	PRIMARY KEY(aid, pid),
	FOREIGN KEY (aid) REFERENCES Album (aid),
	FOREIGN KEY (pid) REFERENCES Photo (pid)
);

CREATE TABLE Album(
	aid INTEGER,
	name CHAR(20),
	uid INTEGER,
	doc DATE,
	PRIMARY KEY (aid),
	FOREIGN KEY (uid) REFERENCES PUser (uid)
);

CREATE TABLE Owns(
	uid INTEGER,
	aid INTEGER,
	PRIMARY KEY(uid, aid),
	FOREIGN KEY (uid) REFERENCES PUser (uid),
	FOREIGN KEY (aid) REFERENCES Album (aid)
);