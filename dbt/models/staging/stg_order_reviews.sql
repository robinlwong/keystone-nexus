{{ config(materialized='view') }}

WITH raw_reviews AS (
    SELECT * FROM {{ source('bronze', 'order_reviews') }}
)

SELECT
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    CAST(review_creation_date AS TIMESTAMP) as review_creation_timestamp,
    CAST(review_answer_timestamp AS TIMESTAMP) as review_answer_timestamp
FROM raw_reviews
WHERE review_id IS NOT NULL
