{{ config(materialized='view') }}

select *
from {{ ref('stg_cdnow_transactions') }}
where conversion_issue is not null
