{{ config(materialized='table') }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
order_items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
)

SELECT 
    o.order_id,
    oi.order_item_id,
    o.customer_id,
    oi.product_id,
    oi.seller_id,
    CAST(FORMAT(CAST(o.order_purchase_timestamp AS DATE), 'yyyyMMdd') AS INT) AS date_key,
    oi.price,
    oi.freight_value,
    (oi.price + oi.freight_value) AS total_order_value,
    DATE_DIFF('day', CAST(o.order_purchase_timestamp AS DATE), CAST(o.order_delivered_customer_date AS DATE)) AS delivery_lag_days
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
  -- ATHENA PARTITIONING: Filter by year/month/day to minimize scan costs
  AND o.year = {{ var('target_year', format_date(current_timestamp(), '%Y')) }}
  AND o.month = {{ var('target_month', format_date(current_timestamp(), '%m')) }}
  AND o.day = {{ var('target_day', format_date(current_timestamp(), '%d')) }}
