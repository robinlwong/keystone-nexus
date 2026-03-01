{{ config(materialized='view') }}

WITH raw_payments AS (
    SELECT * FROM {{ source('bronze', 'order_payments') }}
)

SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    CAST(payment_value AS DOUBLE) as payment_value
FROM raw_payments
WHERE order_id IS NOT NULL
