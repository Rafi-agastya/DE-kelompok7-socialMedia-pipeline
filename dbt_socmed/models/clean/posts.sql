with ranked as (
    select *, row_number() over (partition by post_id order by batch_id desc) as rn
    from {{ source('staging', 'posts') }}
)
select
    post_id::integer              as post_id,
    user_id::integer              as user_id,
    trim(content)                 as content,
    lower(trim(media_type))       as media_type,
    created_at::timestamp         as created_at,
    batch_id                      as source_batch_id
from ranked
where rn = 1
  and post_id is not null and content is not null
  and lower(trim(media_type)) in ('text', 'image', 'video')
  and user_id in (select user_id from {{ ref('users') }})