import io
import os
import csv
import random
from datetime import datetime, timedelta

import psycopg2
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
random.seed(42)
Faker.seed(42)
fake_id = Faker("id_ID")   # untuk nama
fake_en = Faker("en_US")   # untuk teks

N_USERS, N_POSTS, N_COMMENTS = 20_000, 100_000, 150_000
N_LIKES, N_FOLLOWS = 300_000, 100_000
N_HASHTAGS, N_POST_HASHTAGS = 2_000, 200_000

NOW = datetime.now().replace(microsecond=0)
START = NOW - timedelta(days=3 * 365)
COUNTRIES = ["ID"] * 8 + ["MY", "SG", "US", "JP", "AU"]


def rand_dt(start, end=NOW):
    span = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, max(span, 1)))


def copy(cur, table, cols, rows):
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    buf.seek(0)
    cur.copy_expert(f"COPY {table} ({cols}) FROM STDIN WITH CSV", buf)
    print(f"[OK] {table}: {len(rows):,} baris")


def main():
    conn = psycopg2.connect(
        host="localhost", port=os.getenv("OLTP_PORT"), dbname=os.getenv("OLTP_DB"),
        user=os.getenv("OLTP_USER"), password=os.getenv("OLTP_PASSWORD"),
    )
    cur = conn.cursor()
    cur.execute("TRUNCATE users, posts, comments, likes, follows, hashtags, post_hashtags CASCADE")

    # users
    user_created, rows = {}, []
    for i in range(1, N_USERS + 1):
        created = rand_dt(START)
        user_created[i] = created
        uname = f"{fake_en.user_name()}_{i}"
        rows.append([i, uname, f"{uname}@{fake_en.free_email_domain()}", fake_id.name(),
                     fake_en.sentence(), random.choice(COUNTRIES),
                     random.random() < 0.02, created])
    copy(cur, "users", "user_id,username,email,full_name,bio,country,is_verified,created_at", rows)

    # posts
    post_created, rows = {}, []
    for i in range(1, N_POSTS + 1):
        uid = random.randint(1, N_USERS)
        created = rand_dt(user_created[uid])
        post_created[i] = created
        rows.append([i, uid, fake_en.text(max_nb_chars=200),
                     random.choices(["text", "image", "video"], [5, 4, 1])[0], created])
    copy(cur, "posts", "post_id,user_id,content,media_type,created_at", rows)

    # comments
    rows = []
    for i in range(1, N_COMMENTS + 1):
        pid = random.randint(1, N_POSTS)
        rows.append([i, pid, random.randint(1, N_USERS), fake_en.sentence(),
                     rand_dt(post_created[pid])])
    copy(cur, "comments", "comment_id,post_id,user_id,content,created_at", rows)

    # likes (unik per post + user)
    pairs = set()
    while len(pairs) < N_LIKES:
        pairs.add((random.randint(1, N_POSTS), random.randint(1, N_USERS)))
    rows = [[i, p, u, rand_dt(post_created[p])] for i, (p, u) in enumerate(pairs, 1)]
    copy(cur, "likes", "like_id,post_id,user_id,created_at", rows)

    # follows (unik, tanpa follow diri sendiri)
    pairs = set()
    while len(pairs) < N_FOLLOWS:
        a, b = random.randint(1, N_USERS), random.randint(1, N_USERS)
        if a != b:
            pairs.add((a, b))
    rows = [[i, a, b, rand_dt(max(user_created[a], user_created[b]))]
            for i, (a, b) in enumerate(pairs, 1)]
    copy(cur, "follows", "follow_id,follower_id,followed_id,created_at", rows)

    # hashtags
    rows = [[i, f"{fake_en.word()}{i}"] for i in range(1, N_HASHTAGS + 1)]
    copy(cur, "hashtags", "hashtag_id,tag", rows)

    # post_hashtags
    pairs = set()
    while len(pairs) < N_POST_HASHTAGS:
        pairs.add((random.randint(1, N_POSTS), random.randint(1, N_HASHTAGS)))
    copy(cur, "post_hashtags", "post_id,hashtag_id", [list(p) for p in pairs])

    conn.commit()
    cur.close()
    conn.close()
    print("Selesai.")


if __name__ == "__main__":
    main()