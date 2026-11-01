with ranked as (
    select *, row_number() over (partition by post_id, hashtag_id order by batch_id desc) as rn
    from {{ source('staging', 'post_hashtags') }}
)
select
    post_id::integer      as post_id,
    hashtag_id::integer   as hashtag_id,
    batch_id              as source_batch_id
from ranked
where rn = 1
  and post_id in (select post_id from {{ ref('posts') }})
  and hashtag_id in (select hashtag_id from {{ ref('hashtags') }})