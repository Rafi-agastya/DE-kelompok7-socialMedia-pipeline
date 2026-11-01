with ranked as (
    select *, row_number() over (partition by hashtag_id order by batch_id desc) as rn
    from {{ source('staging', 'hashtags') }}
)
select
    hashtag_id::integer           as hashtag_id,
    lower(trim(tag))::varchar(60) as tag,
    batch_id                      as source_batch_id
from ranked
where rn = 1 and hashtag_id is not null and tag is not null 