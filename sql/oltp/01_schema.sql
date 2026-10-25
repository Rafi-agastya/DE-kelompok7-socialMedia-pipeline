CREATE TABLE users (
    user_id     INTEGER PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    email       VARCHAR(120) UNIQUE NOT NULL,
    full_name   VARCHAR(100) NOT NULL,
    bio         TEXT,
    country     VARCHAR(2),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP NOT NULL
);

CREATE TABLE posts (
    post_id    INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(user_id),
    content    TEXT NOT NULL,
    media_type VARCHAR(10) NOT NULL,   -- text / image / video
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE comments (
    comment_id INTEGER PRIMARY KEY,
    post_id    INTEGER NOT NULL REFERENCES posts(post_id),
    user_id    INTEGER NOT NULL REFERENCES users(user_id),
    content    TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE likes (
    like_id    INTEGER PRIMARY KEY,
    post_id    INTEGER NOT NULL REFERENCES posts(post_id),
    user_id    INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP NOT NULL,
    UNIQUE (post_id, user_id)
);

CREATE TABLE follows (
    follow_id   INTEGER PRIMARY KEY,
    follower_id INTEGER NOT NULL REFERENCES users(user_id),
    followed_id INTEGER NOT NULL REFERENCES users(user_id),
    created_at  TIMESTAMP NOT NULL,
    UNIQUE (follower_id, followed_id),
    CHECK (follower_id <> followed_id)
);

CREATE TABLE hashtags (
    hashtag_id INTEGER PRIMARY KEY,
    tag        VARCHAR(60) UNIQUE NOT NULL
);

CREATE TABLE post_hashtags (
    post_id    INTEGER NOT NULL REFERENCES posts(post_id),
    hashtag_id INTEGER NOT NULL REFERENCES hashtags(hashtag_id),
    PRIMARY KEY (post_id, hashtag_id)
);
