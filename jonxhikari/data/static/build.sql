CREATE TABLE IF NOT EXISTS guilds (
    GuildID bigint NOT NULL PRIMARY KEY,
    Prefix text DEFAULT '$',
    StarChannel bigint DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tags (
    GuildID bigint,
    TagOwner bigint,
    TagName text,
    TagContent text,
    Uses bigint DEFAULT 0,
    PRIMARY KEY (GuildID, TagName)
);

CREATE TABLE IF NOT EXISTS starboard (
    BaseMessageID bigint,
    GuildID bigint,
    StarMessageID bigint,
    Stars bigint DEFAULT 1,
	FOREIGN KEY (GuildID) REFERENCES guilds(GuildID),
    PRIMARY KEY (BaseMessageID, GuildID)
);
