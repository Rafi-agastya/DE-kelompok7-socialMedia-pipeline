select
    row_number() over (order by user_id)::integer as user_key,
    user_id,
    username,
    full_name,
    country_code,
    case country_code
        when 'ID' then 'Indonesia'
        when 'MY' then 'Malaysia'
        when 'SG' then 'Singapura'
        when 'US' then 'Amerika Serikat'
        when 'JP' then 'Jepang'
        when 'AU' then 'Australia'
        else 'Tidak diketahui'
    end                                           as country_name,
    is_verified,
    created_at::date                              as joined_date,
    to_char(created_at, 'YYYYMMDD')::integer      as joined_date_key
from {{ ref('users') }}