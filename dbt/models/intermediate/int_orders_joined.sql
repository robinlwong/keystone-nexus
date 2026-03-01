{{ config(materialized='table') }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),
payments AS (
    SELECT * FROM {{ ref('stg_order_payments') }}
),
customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),
products AS (
    SELECT * FROM {{ ref('stg_products') }}
),
sellers AS (
    SELECT * FROM {{ ref('stg_sellers') }}
)

SELECT
    o.order_id,
    o.customer_id,
    i.product_id,
    i.seller_id,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    i.price,
    i.freight_value,
    (i.price + i.freight_value) AS total_order_value,
    p.payment_type,
    p.payment_installments,
    p.payment_value,
    c.customer_state,
    c.customer_city,
    prod.product_category_name,
    s.seller_state
FROM orders o
LEFT JOIN items i ON o.order_id = i.order_id
LEFT JOIN payments p ON o.order_id = p.order_id
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN products prod ON i.product_id = prod.product_id
LEFT JOIN sellers s ON i.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
