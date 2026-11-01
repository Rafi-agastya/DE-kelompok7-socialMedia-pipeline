select
    ph.post_id,
    h.hashtag_key
from {{ ref('post_hashtags') }} ph
join {{ ref('dim_hashtag') }} h on h.hashtag_id = ph.hashtag_id