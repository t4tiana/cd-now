"""Render the two charts for the side-by-side committee memo draft."""

import json
from datetime import date, timedelta
from xml.sax.saxutils import escape

from financing_scenarios import ROOT, full_age_profile, model_scenario

OBSERVED = ROOT / "reports" / "cohort_analysis.json"
SCENARIOS = ROOT / "reports" / "future_cohort_size_scenarios.json"
ACTIVITY_CHART = ROOT / "reports" / "memo_observed_purchase_rate_v2.svg"
REPAYMENT_CHART = ROOT / "reports" / "memo_repayment_paths_v2.svg"


def svg_text(
    x: float,
    y: float,
    value: str,
    *,
    size: int = 13,
    color: str = "#334155",
    anchor: str = "start",
    weight: str = "400",
) -> str:
    """Write a text label with consistent SVG styling and escaped content."""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="Arial,sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}">{escape(value)}</text>'
    )


def render_activity() -> None:
    """Show repeat purchasing in fully observed age windows."""
    report = json.loads(OBSERVED.read_text(encoding="utf-8"))
    periods = [
        p
        for p in report["customer_age_periods"]["periods"]
        if 1 <= p["age_period"] <= 14
    ]
    assert len(periods) == 14
    assert all(p["eligible_customers"] == 23570 for p in periods)

    x0, y0, width, height = 94, 94, 850, 270
    ymax = 15
    slot = width / len(periods)
    parts = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 490" '
            'role="img" aria-labelledby="title desc">'
        ),
        '<title id="title">Observed purchasing by time since first purchase</title>',
        (
            '<desc id="desc">Share of the original 23,570 Q1 1997 first purchasers '
            "buying in each fully observed 30-day window from days 30 through 449. "
            "The share declines from 13.1 percent to 6.6 percent.</desc>"
        ),
        '<rect width="1040" height="490" fill="#ffffff"/>',
        svg_text(
            94,
            36,
            "Repeat purchasing continues, but involves fewer customers",
            size=21,
            color="#17253d",
            weight="700",
        ),
        svg_text(
            94,
            61,
            "Q1 1997 first-purchase cohort; observed through June 30, 1998",
            size=14,
            color="#475569",
        ),
    ]
    for pct in (0, 5, 10, 15):
        y = y0 + height - pct / ymax * height
        parts.append(
            f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + width}" '
            f'y2="{y:.1f}" stroke="#dbe3ed"/>'
        )
        parts.append(
            svg_text(x0 - 12, y + 5, f"{pct}%", size=12, color="#475569", anchor="end")
        )
    labels = {
        1: "30–59",
        4: "120–149",
        7: "210–239",
        10: "300–329",
        14: "420–449",
    }
    for idx, period in enumerate(periods):
        pct = period["purchasing_customers"] / period["eligible_customers"] * 100
        bar_height = pct / ymax * height
        x = x0 + idx * slot + 9
        y = y0 + height - bar_height
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{slot - 18:.1f}" '
            f'height="{bar_height:.1f}" fill="#286c93"/>'
        )
        if period["age_period"] in labels:
            parts.append(
                svg_text(
                    x + (slot - 18) / 2,
                    385,
                    labels[period["age_period"]],
                    size=11,
                    anchor="middle",
                )
            )
    parts.extend(
        [
            svg_text(
                519,
                419,
                "Days since first purchase (each bar covers 30 days)",
                anchor="middle",
            ),
            svg_text(
                94,
                456,
                "Each rate = purchasers in window / 23,570 original customers; all windows have full follow-up.",
                size=12,
                color="#475569",
            ),
            "</svg>",
        ]
    )
    ACTIVITY_CHART.write_text("\n".join(parts) + "\n", encoding="utf-8")


def quarter_end(label: str) -> date:
    """Map a YYYYQn label to its calendar quarter-end date."""
    year = int(label[:4])
    quarter = int(label[-1])
    return (
        date(year, quarter * 3 + 1, 1) - timedelta(days=1)
        if quarter < 4
        else date(year, 12, 31)
    )


def cumulative_points(payments: dict[str, float]) -> list[tuple[date, float]]:
    """Convert quarter payments into quarter-end cumulative repayments."""
    total = 0.0
    points = [(date(1998, 10, 1), 0.0)]
    for label, amount in sorted(payments.items()):
        total += amount
        points.append((quarter_end(label), total))
    return points


def render_repayments() -> None:
    """Compare modeled capped payments with the combined downside."""
    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    profile = full_age_profile()
    selected = next(
        row
        for row in scenarios["proposed_ceiling_rows"]
        if row["first_purchasers"] == 40000
        and row["behavior_case"] == "top_25_spend_20pct"
    )
    joint = scenarios["joint_downside"]
    factor = joint["age_90_and_later_dollars_factor_from_top_25_stress"]
    advance = joint["advance"]
    favorable_model = model_scenario(
        profile, factor, 0.8, cohort_customers=40000, advances=(advance,)
    )["illustrative_advances"][0]
    stress_model = model_scenario(
        profile,
        factor,
        joint["eligible_collected_fraction_assumed"],
        cohort_customers=joint["first_purchasers"],
        advances=(advance,),
        initial_factor=joint["first_90_day_dollars_factor_assumed"],
    )["illustrative_advances"][0]
    assert (
        favorable_model["capped_repayments_through_2000"]
        == selected["repayments_through_2000"]
    )
    assert favorable_model["cap_date"] == selected["cap_date_if_reached"]
    assert (
        stress_model["capped_repayments_through_2000"]
        == joint["repayments_through_2000"]
    )

    start, end = date(1998, 10, 1), date(2000, 12, 31)
    x0, x1, y0, y1 = 100, 850, 88, 392
    max_dollars = 1_600_000

    def x(day: date) -> float:
        return x0 + (day - start).days / (end - start).days * (x1 - x0)

    def y(dollars: float) -> float:
        return y1 - dollars / max_dollars * (y1 - y0)

    def path(points: list[tuple[date, float]]) -> str:
        return " ".join(
            f"{'M' if idx == 0 else 'L'}{x(day):.1f},{y(amount):.1f}"
            for idx, (day, amount) in enumerate(points)
        )

    parts = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 520" '
            'role="img" aria-labelledby="title desc">'
        ),
        '<title id="title">Modeled investor repayments on a 1.2 million dollar advance</title>',
        (
            '<desc id="desc">Quarter-end cumulative repayments for two hypothetical Q4 1998 '
            "cohorts. The 40,000-buyer case reaches the 1.44 million dollar cap by December "
            "1999. The combined downside reaches 1.041 million dollars by December 2000, "
            "below 1.2 million dollar principal. Both assume immediate collection and remittance.</desc>"
        ),
        '<rect width="1040" height="520" fill="#ffffff"/>',
        svg_text(
            100,
            34,
            "Repayment depends on more than repeat sales",
            size=21,
            color="#17253d",
            weight="700",
        ),
        svg_text(
            100,
            60,
            "Illustrative $1.2m advance for Q4 1998 first purchasers; quarterly cumulative payments",
            size=14,
            color="#475569",
        ),
    ]
    for dollars in (0, 400_000, 800_000, 1_200_000, 1_440_000):
        yy = y(dollars)
        stroke = "#b1bccb" if dollars >= 1_200_000 else "#e0e7ef"
        dash = "5 4" if dollars >= 1_200_000 else "none"
        parts.append(
            f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" '
            f'stroke="{stroke}" stroke-dasharray="{dash}"/>'
        )
        parts.append(
            svg_text(
                x0 - 12,
                yy + 5,
                f"${dollars / 1_000_000:.2f}m",
                size=12,
                color="#475569",
                anchor="end",
            )
        )
    for day, label in (
        (date(1998, 12, 31), "Dec 1998"),
        (date(1999, 6, 30), "Jun 1999"),
        (date(1999, 12, 31), "Dec 1999"),
        (date(2000, 6, 30), "Jun 2000"),
        (date(2000, 12, 31), "Dec 2000"),
    ):
        parts.append(svg_text(x(day), 417, label, size=12, anchor="middle"))
    favorable = cumulative_points(favorable_model["repayment_by_quarter"])
    stress = cumulative_points(stress_model["repayment_by_quarter"])
    parts.extend(
        [
            f'<path d="{path(favorable)}" fill="none" stroke="#147d78" stroke-width="4"/>',
            f'<path d="{path(stress)}" fill="none" stroke="#c96b24" stroke-width="4"/>',
            svg_text(
                865,
                y(1_440_000) + 4,
                "Cap $1.44m",
                size=12,
                color="#147d78",
                weight="700",
            ),
            svg_text(
                865, y(1_200_000) + 4, "Principal $1.20m", size=12, color="#475569"
            ),
            svg_text(
                865,
                y(joint["repayments_through_2000"]) + 4,
                "Stress $1.04m",
                size=12,
                color="#c96b24",
                weight="700",
            ),
            '<line x1="100" y1="449" x2="132" y2="449" stroke="#147d78" stroke-width="4"/>',
            svg_text(
                141,
                454,
                "40,000 buyers; 80% eligible and collected; later-spend downside",
                size=12,
            ),
            '<line x1="100" y1="473" x2="132" y2="473" stroke="#c96b24" stroke-width="4"/>',
            svg_text(
                141,
                478,
                "Combined downside: 30,000 buyers; lower early/later spend; 60% eligible",
                size=12,
            ),
            svg_text(
                100,
                505,
                "Forecast scenarios, not observed cash. Payments = 50% of assumed eligible collections, capped at 1.2× advance.",
                size=11,
                color="#475569",
            ),
            "</svg>",
        ]
    )
    REPAYMENT_CHART.write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    render_activity()
    render_repayments()
