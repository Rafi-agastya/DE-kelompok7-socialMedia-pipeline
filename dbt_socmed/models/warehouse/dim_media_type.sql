select
    row_number() over (order by media_type)::integer as media_type_key,
    media_type,
    case media_type
        when 'text'  then 'Unggahan teks'
        when 'image' then 'Unggahan gambar'
        when 'video' then 'Unggahan video'
    end as media_type_label
from (select distinct media_type from {{ ref('posts') }}) t