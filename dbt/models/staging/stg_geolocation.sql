{{ config(materialized='view') }}

WITH raw_geolocation AS (
    SELECT * FROM {{ source('bronze', 'geolocation') }}
)

SELECT
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state
FROM raw_geolocation
WHERE geolocation_zip_code_prefix IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY geolocation_zip_code_prefix 
    ORDER BY geolocation_lat, geolocation_lng
) = 1
