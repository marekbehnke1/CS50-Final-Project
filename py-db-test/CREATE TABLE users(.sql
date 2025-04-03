CREATE TABLE users(
    userid integer PRIMARY KEY,
    username text unique not null,
    fname text not null,
    lname text not null,
    email text not null,
    balance integer not NULL
);