{{ config(materialized='view') }}

WITH raw_order_items AS (
    SELECT * FROM {{ source('bronze', 'order_items') }}
)

SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    CAST(shipping_limit_date AS TIMESTAMP) as shipping_limit_timestamp,
    CAST(price AS DOUBLE) as price,
    CAST(freight_value AS DOUBLE) as freight_value
FROM raw_order_items
WHERE order_id IS NOT NULL
