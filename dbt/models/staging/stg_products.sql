{{ config(materialized='view') }}

WITH raw_products AS (
    SELECT * FROM {{ source('bronze', 'products') }}
)

SELECT
    product_id,
    product_category_name,
    CAST(product_name_lenght AS INT) as product_name_lenght,
    CAST(product_description_lenght AS INT) as product_description_lenght,
    CAST(product_photos_qty AS INT) as product_photos_qty,
    CAST(product_weight_g AS INT) as product_weight_g,
    CAST(product_length_cm AS INT) as product_length_cm,
    CAST(product_height_cm AS INT) as product_height_cm,
    CAST(product_width_cm AS INT) as product_width_cm
FROM raw_products
WHERE product_id IS NOT NULL
