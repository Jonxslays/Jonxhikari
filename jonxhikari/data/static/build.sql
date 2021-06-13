CREATE TABLE IF NOT EXISTS guilds (
    GuildID integer NOT NULL PRIMARY KEY,
    Prefix text DEFAULT "$"
);

CREATE TABLE IF NOT EXISTS tags (
    TagID integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    GuildID integer, TagOwner integer,
    TagName text, TagContent text,
    Uses integer
);
