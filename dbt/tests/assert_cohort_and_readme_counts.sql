-- Match the readme's stated cohort size and recorded first-purchase window.
with
    first_dates as (
        select customer_id, min(transaction_date) as first_date
        from {{ ref('stg_cdnow_transactions') }}
        group by 1
    ),
    summary as (
        select
            (select count(*) from {{ ref('stg_cdnow_transactions') }}) as transactions,
            (select count(*) from first_dates) as customers,
            (
                select count(*)
                from first_dates
                where
                    first_date not between date '1997-01-01'
                    and date '1997-03-31'
                    or first_date is null
            ) as outside_cohort
    )
select *
from summary
where transactions <> 69659 or customers <> 23570 or outside_cohort <> 0
