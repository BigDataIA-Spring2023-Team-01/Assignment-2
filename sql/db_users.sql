

CREATE TABLE if not exists login (
    username TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    password TEXT,
    status TEXT CHECK (status IN ('active', 'inactive', 'disabled'))
);

DELETE FROM login;

INSERT INTO login VALUES('test','test@gmail.com','$2b$12$E2h35wKPuFb3Vr8uC6Du8uzukmu0f2wM44uzm.UthGjKzKHEiMZNK','active');
INSERT INTO login VALUES('damg7245','damg@gmail.com','$2b$12$yJ/iddK8UQjzx0oC3M/WteYutgmtGgub8uukDPZHj4gkk69hN97Jy','active');
INSERT INTO login VALUES('test1','test1@gmail.com','$2b$12$l7JWANZU3dr3/sQXx18FBu.oH6LMBeJy9EKuF/YcK0nFQ3N6UbZx6','inactive');
INSERT INTO login VALUES('test_disabled','test_disabled@gmail.com','$2b$12$reKZJlqbGQNOfEm8cWJpK.AkU8OxGoQcv6sJsos1A9fGiYzimXV9m','disabled');
