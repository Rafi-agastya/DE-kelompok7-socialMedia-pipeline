with interactions as (
    select 'like'::varchar(10) as interaction_type, like_id as source_id, post_id, user_id, created_at
    from {{ ref('likes') }}
    union all
    select 'comment', comment_id, post_id, user_id, created_at
    from {{ ref('comments') }}
)
select
    row_number() over (order by i.interaction_type, i.source_id)::integer as interaction_key,
    i.interaction_type,
    i.source_id,
    i.post_id,
    actor.user_key                                   as actor_user_key,
    author.user_key                                  as post_author_user_key,
    to_char(i.created_at, 'YYYYMMDD')::integer       as date_key,
    extract(hour from i.created_at)::integer         as interaction_hour
from interactions i
join {{ ref('dim_user') }} actor on actor.user_id = i.user_id
join {{ ref('posts') }} p on p.post_id = i.post_id
join {{ ref('dim_user') }} author on author.user_id = p.user_id