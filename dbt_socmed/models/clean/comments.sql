with ranked as (
    select *, row_number() over (partition by comment_id order by batch_id desc) as rn
    from {{ source('staging', 'comments') }}
)
select
    comment_id::integer     as comment_id,
    post_id::integer        as post_id,
    user_id::integer        as user_id,
    trim(content)           as content,
    created_at::timestamp   as created_at,
    batch_id                as source_batch_id
from ranked
where rn = 1
  and comment_id is not null and content is not null
  and post_id in (select post_id from {{ ref('posts') }})
  and user_id in (select user_id from {{ ref('users') }})