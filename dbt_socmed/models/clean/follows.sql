with ranked as (
    select *, row_number() over (partition by follow_id order by batch_id desc) as rn
    from {{ source('staging', 'follows') }}
)
select
    follow_id::integer      as follow_id,
    follower_id::integer    as follower_id,
    followed_id::integer    as followed_id,
    created_at::timestamp   as created_at,
    batch_id                as source_batch_id
from ranked
where rn = 1
  and follow_id is not null
  and follower_id <> followed_id
  and follower_id in (select user_id from {{ ref('users') }})
  and followed_id in (select user_id from {{ ref('users') }})