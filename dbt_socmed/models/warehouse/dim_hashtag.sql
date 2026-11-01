select
    row_number() over (order by hashtag_id)::integer as hashtag_key,
    hashtag_id,
    tag
from {{ ref('hashtags') }}