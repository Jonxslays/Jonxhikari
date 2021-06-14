CREATE TABLE IF NOT EXISTS guilds (
    GuildID integer NOT NULL PRIMARY KEY,
    Prefix text DEFAULT "$",
    StarChannel integer DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tags (
    GuildID integer, TagOwner integer,
    TagName text, TagContent text,
    Uses integer DEFAULT 0,
    PRIMARY KEY (GuildID, TagName)
);

CREATE TABLE IF NOT EXISTS starboard (
    BaseMessageID integer,
    GuildID integer,
    StartMessageID integer,
    Stars integer DEFAULT 1,
    PRIMARY KEY (BaseMessageID, GuildID)
);
