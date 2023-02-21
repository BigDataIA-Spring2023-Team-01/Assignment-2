

CREATE TABLE if not exists login (
    username TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    password TEXT,
    status TEXT CHECK (status IN ('active', 'inactive', 'disabled'))
);

DELETE FROM login;

INSERT INTO login VALUES('test','test@gmail.com','9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08','active');
INSERT INTO login VALUES('test1','test1@gmail.com','1b4f0e9851971998e732078544c96b36c3d01cedf7caa332359d6f1d83567014','inactive');
INSERT INTO login VALUES('test2','test2@gmail.com','test2','disabled');
INSERT INTO login VALUES('test3','test3@gmail.com','test3','disabled');
