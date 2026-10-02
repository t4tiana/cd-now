{{ config(materialized='table') }}

with
    raw as (select * from {{ source('cdnow_raw', 'source_lines') }}),

    typed as (
        select
            'CDNOW_master.txt:'
            || cast(source_line_number as varchar) as source_record_id,
            source_line_number,
            original_line,
            field_count,
            parse_status,
            parse_reason,
            customer_id_raw,
            transaction_date_raw,
            cd_count_raw,
            dollar_value_raw,
            customer_id_raw as customer_id,
            case
                when regexp_full_match(transaction_date_raw, '[0-9]{8}')
                then try_strptime(transaction_date_raw, '%Y%m%d')::date
            end as transaction_date,
            case
                when regexp_full_match(cd_count_raw, '[+-]?[0-9]+')
                then try_cast(cd_count_raw as integer)
            end as cd_count,
            case
                when regexp_full_match(dollar_value_raw, '[+-]?[0-9]+(\.[0-9]{1,2})?')
                then try_cast(dollar_value_raw as decimal(18, 2))
            end as transaction_dollars
        from raw
    ),

    checked as (
        select
            *,
            case
                when parse_status <> 'four_fields' then parse_reason
            end as structure_issue,
            case
                when
                    parse_status = 'four_fields'
                    and (customer_id is null or customer_id = '')
                then 'missing customer ID'
            end as customer_id_issue,
            case
                when parse_status = 'four_fields' and transaction_date is null
                then 'invalid transaction date'
            end as transaction_date_issue,
            case
                when parse_status = 'four_fields' and cd_count is null
                then 'invalid CD count'
            end as cd_count_issue,
            case
                when parse_status = 'four_fields' and transaction_dollars is null
                then 'invalid transaction dollars or non-cent precision'
            end as transaction_dollars_issue
        from typed
    )

select
    *,
    nullif(
        concat_ws(
            '; ',
            structure_issue,
            customer_id_issue,
            transaction_date_issue,
            cd_count_issue,
            transaction_dollars_issue
        ),
        ''
    ) as conversion_issue
from checked
