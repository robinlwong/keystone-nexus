{{ config(materialized='view') }}

WITH raw_orders AS (
    SELECT * FROM {{ source('bronze', 'orders') }}
)

SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date
FROM raw_orders
WHERE order_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_purchase_timestamp DESC) = 1
