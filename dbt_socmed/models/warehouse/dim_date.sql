with bounds as (
    select min(d) as min_d, max(d) as max_d
    from (
        select created_at::date as d from {{ ref('users') }}
        union all select created_at::date from {{ ref('posts') }}
        union all select created_at::date from {{ ref('comments') }}
        union all select created_at::date from {{ ref('likes') }}
        union all select created_at::date from {{ ref('follows') }}
    ) t
),
spine as (
    select generate_series(min_d::timestamp, max_d::timestamp, interval '1 day')::date as full_date
    from bounds
)
select
    to_char(full_date, 'YYYYMMDD')::integer                    as date_key,
    full_date,
    extract(day from full_date)::integer                       as day_of_month,
    extract(isodow from full_date)::integer                    as day_of_week,
    (array['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu'])[extract(isodow from full_date)::integer] as day_name,
    extract(week from full_date)::integer                      as week_of_year,
    extract(month from full_date)::integer                     as month_number,
    (array['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'])[extract(month from full_date)::integer] as month_name,
    extract(quarter from full_date)::integer                   as quarter,
    extract(year from full_date)::integer                      as year,
    extract(isodow from full_date) in (6, 7)                   as is_weekend
from spine