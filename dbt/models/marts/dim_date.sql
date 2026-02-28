{{ config(materialized='table') }}

-- Generating a date dimension from the order timestamps
WITH dates AS (
    SELECT DISTINCT 
        CAST(order_purchase_timestamp AS DATE) as date_day
    FROM {{ ref('stg_orders') }}
)

SELECT
    CAST(FORMAT(date_day, 'yyyyMMdd') AS INT) as date_key,
    date_day,
    YEAR(date_day) as year,
    MONTH(date_day) as month,
    DAY(date_day) as day,
    QUARTER(date_day) as quarter,
    FORMAT(date_day, 'MMMM') as month_name,
    FORMAT(date_day, 'EEEE') as day_name
FROM dates
WHERE date_day IS NOT NULL
