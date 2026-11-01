select
    f.follow_id,
    fr.user_key                                  as follower_user_key,
    fd.user_key                                  as followed_user_key,
    to_char(f.created_at, 'YYYYMMDD')::integer   as date_key
from {{ ref('follows') }} f
join {{ ref('dim_user') }} fr on fr.user_id = f.follower_id
join {{ ref('dim_user') }} fd on fd.user_id = f.followed_id