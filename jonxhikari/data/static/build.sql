CREATE TABLE IF NOT EXISTS guilds (
    GuildID integer NOT NULL PRIMARY KEY,
    Prefix text DEFAULT "$"
);

CREATE TABLE IF NOT EXISTS tags (
    GuildID integer, TagOwner integer,
    TagName text, TagContent text,
    Uses integer DEFAULT 0,
    PRIMARY KEY (GuildID, TagName)
);
