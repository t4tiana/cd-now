-- Fail if a source line is missing, repeated, or changed during staging.
with
    raw as (
        select source_line_number, original_line
        from {{ source('cdnow_raw', 'source_lines') }}
    ),
    staged as (
        select source_line_number, original_line
        from {{ ref('stg_cdnow_transactions') }}
    ),
    problems as (
        select source_line_number
        from raw
        group by 1
        having count(*) <> 1
        union all
        select source_line_number
        from staged
        group by 1
        having count(*) <> 1
        union all
        select coalesce(r.source_line_number, s.source_line_number)
        from raw r
        full outer join staged s using (source_line_number)
        where
            r.source_line_number is null
            or s.source_line_number is null
            or r.original_line is distinct from s.original_line
    )
select *
from problems
