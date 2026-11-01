with likes_agg as (
    select post_id, count(*) as like_count from {{ ref('likes') }} group by post_id
),
comments_agg as (
    select post_id, count(*) as comment_count from {{ ref('comments') }} group by post_id
),
tags_agg as (
    select post_id, count(*) as hashtag_count from {{ ref('post_hashtags') }} group by post_id
)
select
    p.post_id,
    u.user_key,
    to_char(p.created_at, 'YYYYMMDD')::integer                   as date_key,
    extract(hour from p.created_at)::integer                     as posted_hour,
    m.media_type_key,
    length(p.content)                                            as content_length,
    coalesce(l.like_count, 0)::integer                           as like_count,
    coalesce(c.comment_count, 0)::integer                        as comment_count,
    coalesce(t.hashtag_count, 0)::integer                        as hashtag_count,
    (coalesce(l.like_count, 0) + coalesce(c.comment_count, 0))::integer as engagement_count
from {{ ref('posts') }} p
join {{ ref('dim_user') }} u on u.user_id = p.user_id
join {{ ref('dim_media_type') }} m on m.media_type = p.media_type
left join likes_agg l on l.post_id = p.post_id
left join comments_agg c on c.post_id = p.post_id
left join tags_agg t on t.post_id = p.post_id