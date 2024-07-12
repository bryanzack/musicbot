CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "User" (
	"Discord_ID"	INTEGER NOT NULL UNIQUE,
	"Lastfm_Name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("Discord_ID")
)