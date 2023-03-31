CREATE TABLE IF NOT EXISTS Diaries (
    diary_id TEXT PRIMARY KEY,
    title TEXT,
    content TEXT,
    color TEXT,
    inserted_time DATETIME,
    updated_time DATETIME
);

CREATE TABLE IF NOT EXISTS Tags (
    tag_id TEXT PRIMARY KEY,
    tag_name TEXT,
    diary_id TEXT,
    source TEXT,
    inserted_time DATETIME,
    updated_time DATETIME,
    FOREIGN KEY(diary_id) REFERENCES Diaries(diary_id)
);