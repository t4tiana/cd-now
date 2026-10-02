-- These conditions are established for this supplied source file; zero dollars are
-- allowed.
select source_line_number
from {{ ref('stg_cdnow_transactions') }}
where
    conversion_issue is not null
    or not regexp_full_match(customer_id, '[0-9]{5}')
    or transaction_date not between date '1997-01-01'
    and date '1998-06-30'
    or cd_count is null
    or cd_count <= 0
    or transaction_dollars is null
    or transaction_dollars < 0
