with ranked as (
    select *, row_number() over (partition by user_id order by batch_id desc) as rn
    from {{ source('staging', 'users') }}
)
select
    user_id::integer                                         as user_id,
    lower(trim(username))::varchar(50)                       as username,
    lower(trim(email))::varchar(120)                         as email,
    trim(full_name)::varchar(100)                            as full_name,
    coalesce(nullif(trim(bio), ''), 'Tidak ada bio')         as bio,
    coalesce(nullif(upper(trim(country)), ''), 'XX')         as country_code,
    coalesce(is_verified, false)                             as is_verified,
    created_at::timestamp                                    as created_at,
    batch_id                                                 as source_batch_id
from ranked
where rn = 1
  and user_id is not null and username is not null and email is not null