-- ============================================================================
-- DOKUMENTASI QUERY SQL - TAB 1: EXECUTIVE OVERVIEW & USER ENGAGEMENT
-- Role / Koneksi : bi_viewer (Read-Only Access ke Schema mart)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. KPI 1: Total Users (Big Number)
-- Virtual Dataset : ds_kpi_users
-- Output Aktual   : 20.000 Users (20k)
-- ----------------------------------------------------------------------------
SELECT
    COUNT(DISTINCT user_id) AS total_users
FROM mart.dim_user_masked;


-- ----------------------------------------------------------------------------
-- 2. KPI 2: Total Posts (Big Number)
-- Virtual Dataset : ds_kpi_posts
-- Output Aktual   : 100.000 Posts (100k)
-- ----------------------------------------------------------------------------
SELECT
    COUNT(post_id) AS total_posts
FROM mart.fact_post;


-- ----------------------------------------------------------------------------
-- 3. KPI 3: Total Interactions (Big Number)
-- Virtual Dataset : ds_kpi_interactions
-- Output Aktual   : 450.000 Interactions (450k)
-- ----------------------------------------------------------------------------
SELECT
    SUM(like_count + comment_count) AS total_interactions
FROM mart.fact_post;


-- ----------------------------------------------------------------------------
-- 4. KPI 4: Engagement Rate (%) (Big Number)
-- Rumus           : ((Total Likes + Total Comments) / Total Posts) * 100
-- Virtual Dataset : ds_engagement_rate
-- Output Aktual   : 450% (Rata-rata 4,5 interaksi per unggahan)
-- ----------------------------------------------------------------------------
SELECT
    ROUND(
        (SUM(like_count + comment_count)::numeric / COUNT(post_id)) * 100,
        2
    ) AS engagement_rate_pct
FROM mart.fact_post;


-- ----------------------------------------------------------------------------
-- 5. CHART 1: Trend Aktivitas Platform (Line Chart)
-- Virtual Dataset : ds_platform_trend
-- Deskripsi       : Tren pertumbuhan jumlah post & interaksi berbasis dim_date
-- ----------------------------------------------------------------------------
SELECT
    d.full_date AS tanggal,
    COUNT(p.post_id) AS jumlah_post,
    SUM(p.like_count + p.comment_count) AS jumlah_interaksi
FROM mart.fact_post p
JOIN mart.dim_date d
    ON p.date_key = d.date_key
GROUP BY d.full_date
ORDER BY d.full_date ASC;


-- ----------------------------------------------------------------------------
-- 6. CHART 2: Distribusi Konten per Media (Bar Chart)
-- Virtual Dataset : ds_media_distribution
-- Deskripsi       : Perbandingan volume post & interaksi tiap jenis media
-- ----------------------------------------------------------------------------
SELECT
    media_type,
    COUNT(post_id) AS jumlah_post,
    SUM(like_count + comment_count) AS total_interaksi
FROM mart.fact_post
GROUP BY media_type
ORDER BY total_interaksi DESC;


-- ----------------------------------------------------------------------------
-- 7. CHART 3: Proporsi Interaksi - Like vs Comment (Donut Chart)
-- Virtual Dataset : ds_interaction_ratio
-- Output Aktual   : Like 66,67% (300k) vs Comment 33,33% (150k)
-- ----------------------------------------------------------------------------
SELECT
    'Like' AS jenis_interaksi,
    SUM(like_count) AS total_interaksi
FROM mart.fact_post
UNION ALL
SELECT
    'Comment' AS jenis_interaksi,
    SUM(comment_count) AS total_interaksi
FROM mart.fact_post;


-- ----------------------------------------------------------------------------
-- 8. CHART 4: Top 10 Kreator - Masked PII (Table + Native Filter is_verified)
-- Virtual Dataset : ds_top_creators_masked
-- Catatan         : Tanpa klausa LIMIT di SQL agar Native Filter (is_verified)
--                   tetap menghasilkan Top 10 dinamis (Row limit = 10 di Chart)
-- ----------------------------------------------------------------------------
SELECT
    u.username_masked,
    u.full_name_masked,
    u.country_name,
    u.is_verified,
    COUNT(p.post_id) AS total_post,
    SUM(p.like_count) AS total_likes,
    SUM(p.comment_count) AS total_comments,
    SUM(p.like_count + p.comment_count) AS total_interaksi
FROM mart.dim_user_masked u
JOIN mart.fact_post p
    ON u.user_id = p.user_id
GROUP BY
    u.user_id,
    u.username_masked,
    u.full_name_masked,
    u.country_name,
    u.is_verified
ORDER BY total_interaksi DESC;


-- ============================================================================
-- 9. QUERY VERIFIKASI DATA GOVERNANCE (PII MASKING & RBAC)
-- ============================================================================

-- A. Uji akses ke view mart.dim_user_masked (Sukses - PII tersamarkan)
SELECT user_id, username_masked, full_name_masked, is_verified
FROM mart.dim_user_masked
LIMIT 5;

-- B. Uji akses ilegal ke tabel mentah staging (Ditolak - permission denied)
SELECT * FROM staging.users LIMIT 5;