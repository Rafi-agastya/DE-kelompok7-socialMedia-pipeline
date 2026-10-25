CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.users (
    user_id INTEGER, username VARCHAR(50), email VARCHAR(120), full_name VARCHAR(100),
    bio TEXT, country VARCHAR(2), is_verified BOOLEAN, created_at TIMESTAMP,
    source_table VARCHAR(50), batch_id VARCHAR(20), ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.posts (
    post_id INTEGER, user_id INTEGER, content TEXT, media_type VARCHAR(10), created_at TIMESTAMP,
    source_table VARCHAR(50), batch_id VARCHAR(20), ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.comments (
    comment_id INTEGER, post_id INTEGER, user_id INTEGER, content TEXT, created_at TIMESTAMP,
    source_table VARCHAR(50), batch_id VARCHAR(20), ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.likes (
    like_id INTEGER, post_id INTEGER, user_id INTEGER, created_at TIMESTAMP,
    source_table VARCHAR(50), batch_id VARCHAR(20), ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.follows (
    follow_id INTEGER, follower_id INTEGER, followed_id INTEGER, created_at TIMESTAMP,
    source_table VARCHAR(50), batch_id VARCHAR(20), ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.hashtags (
    hashtag_id INTEGER, tag VARCHAR(60),
    source_table VARCHAR(50), batch_id VARCHAR(20), ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.post_hashtags (
    post_id INTEGER, hashtag_id INTEGER,
    source_table VARCHAR(50), batch_id VARCHAR(20), ingested_at TIMESTAMP
);
