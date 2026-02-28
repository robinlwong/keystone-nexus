{{ config(materialized='table') }}

WITH reviews AS (
    SELECT * FROM {{ ref('stg_order_reviews') }}
),
orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
)

SELECT 
    r.review_id,
    r.order_id,
    o.customer_id,
    r.review_score,
    r.review_comment_title,
    r.review_comment_message,
    CAST(FORMAT(CAST(r.review_creation_timestamp AS DATE), 'yyyyMMdd') AS INT) AS date_key,
    r.review_creation_timestamp,
    r.review_answer_timestamp
FROM reviews r
LEFT JOIN orders o ON r.id = o.id
-- ATHENA PARTITIONING: Filter by year/month/day to minimize scan costs
WHERE r.year = {{ var('target_year', format_date(current_timestamp(), '%Y')) }}
  AND r.month = {{ var('target_month', format_date(current_timestamp(), '%m')) }}
  AND r.day = {{ var('target_day', format_date(current_timestamp(), '%d')) }}
