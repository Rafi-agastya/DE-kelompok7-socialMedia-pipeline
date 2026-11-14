-- 1. Buat Presentation Layer (Schema Mart)
CREATE SCHEMA IF NOT EXISTS mart;

-- 2. Anonimisasi / Masking Data Sensitif (PII) pada dim_user (username & full_name)
CREATE OR REPLACE VIEW mart.dim_user_masked AS
SELECT
    user_key,
    user_id,
    -- Masking username: menyisakan 2 karakter awal dan 2 karakter akhir (contoh: ra****ya)
    CASE 
        WHEN LENGTH(username) > 4 THEN CONCAT(LEFT(username, 2), '****', RIGHT(username, 2))
        ELSE '****'
    END AS username_masked,
    -- Masking full_name: menyisakan 2 huruf awal tiap nama/string (contoh: Mu*************)
    CASE 
        WHEN LENGTH(full_name) > 3 THEN CONCAT(LEFT(full_name, 2), REPEAT('*', LEAST(LENGTH(full_name) - 2, 10)))
        ELSE '***'
    END AS full_name_masked,
    country_code,
    country_name,
    is_verified,
    joined_date,
    joined_date_key
FROM warehouse.dim_user;

-- 3. Ekspos tabel fakta & dimensi non-PII ke schema mart
CREATE OR REPLACE VIEW mart.fact_post AS SELECT * FROM warehouse.fact_post;
CREATE OR REPLACE VIEW mart.fact_interaction AS SELECT * FROM warehouse.fact_interaction;
CREATE OR REPLACE VIEW mart.fact_follow AS SELECT * FROM warehouse.fact_follow;
CREATE OR REPLACE VIEW mart.dim_date AS SELECT * FROM warehouse.dim_date;
CREATE OR REPLACE VIEW mart.dim_media_type AS SELECT * FROM warehouse.dim_media_type;
CREATE OR REPLACE VIEW mart.dim_hashtag AS SELECT * FROM warehouse.dim_hashtag;
CREATE OR REPLACE VIEW mart.bridge_post_hashtag AS SELECT * FROM warehouse.bridge_post_hashtag;

-- 4. Implementasi RBAC (Role-Based Access Control)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bi_viewer') THEN
        REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA mart FROM bi_viewer;
        REVOKE ALL PRIVILEGES ON SCHEMA mart FROM bi_viewer;
        DROP ROLE bi_viewer;
    END IF;
    IF EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'data_analyst') THEN
        REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA mart, warehouse FROM data_analyst;
        REVOKE ALL PRIVILEGES ON SCHEMA mart, warehouse FROM data_analyst;
        DROP ROLE data_analyst;
    END IF;
END
$$;

-- Role BI Viewer (Khusus Apache Superset: hanya baca schema mart yang sudah ter-masking)
CREATE ROLE bi_viewer WITH LOGIN PASSWORD 'viewer_pass_k7_2026';
GRANT USAGE ON SCHEMA mart TO bi_viewer;
GRANT SELECT ON ALL TABLES IN SCHEMA mart TO bi_viewer;
ALTER DEFAULT PRIVILEGES IN SCHEMA mart GRANT SELECT ON TABLES TO bi_viewer;
REVOKE ALL ON SCHEMA public, staging, clean, warehouse FROM bi_viewer;

-- Role Data Analyst (Baca warehouse & mart tanpa hak ubah/hapus)
CREATE ROLE data_analyst WITH LOGIN PASSWORD 'analyst_pass_k7_2026';
GRANT USAGE ON SCHEMA warehouse, mart TO data_analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA warehouse, mart TO data_analyst;
REVOKE ALL ON SCHEMA staging, clean FROM data_analyst;