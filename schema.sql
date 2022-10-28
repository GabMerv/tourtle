DROP TABLE IF EXISTS dst;
DROP TABLE IF EXISTS blog;
DROP TABLE IF EXISTS calendar;
DROP TABLE IF EXISTS follow;
DROP TABLE IF EXISTS messages;

CREATE TABLE dst (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    images TEXT NOT NULL
);

CREATE TABLE blog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    images TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    author_name TEXT NOT NULL,
    types TEXT,
    link TEXT
);

CREATE TABLE calendar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    description_ TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    creator_name TEXT NOT NULL,
    participants TEXT,
    dates DATE,
    types TEXT
);

CREATE TABLE follow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    usedFor TEXT NOT NULL
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    author_id INTEGER,
    receiver_id INTEGER,
    author_name TEXT,
    receiver_name TEXT,
    content TEXT,
    images TEXT,
    read INT
);