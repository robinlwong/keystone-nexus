{{ config(materialized='view') }}

WITH raw_customers AS (
    SELECT * FROM {{ source('bronze', 'customers') }}
)

SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM raw_customers
WHERE customer_id IS NOT NULL
