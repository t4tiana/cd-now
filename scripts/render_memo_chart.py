"""Render the memo's observed purchasing chart from the verified cohort JSON."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports" / "cohort_analysis.json"
TARGET = ROOT / "reports" / "memo_observed_purchase_rate.svg"


def main() -> None:
    report = json.loads(SOURCE.read_text(encoding="utf-8"))
    periods = report["customer_age_periods"]["periods"]
    values = [p for p in periods if 1 <= p["age_period"] <= 14]
    assert len(values) == 14
    assert all(p["eligible_customers"] == 23570 for p in values)

    x0, y0, width, height = 94, 87, 850, 285
    ymax = 15
    slot = width / len(values)
    elements = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 490" role="img" '
            'aria-labelledby="title desc">'
        ),
        '<title id="title">Observed purchasing by customer age</title>',
        (
            '<desc id="desc">Percentage of the original 23,570 Q1 1997 first purchasers '
            "with a transaction in each fully observed 30-day window from days 30 through 449. "
            "The rate falls from 13.1 percent to 6.6 percent.</desc>"
        ),
        '<rect width="1040" height="490" fill="#ffffff"/>',
        (
            '<text x="94" y="35" font-family="Arial,sans-serif" font-size="22" '
            'font-weight="700" fill="#17253d">Observed purchasing continues, but thins</text>'
        ),
        (
            '<text x="94" y="60" font-family="Arial,sans-serif" font-size="14" '
            'fill="#475569">Q1 1997 first-purchase cohort; transactions through June 30, 1998</text>'
        ),
    ]
    for pct in (0, 5, 10, 15):
        y = y0 + height - pct / ymax * height
        elements.extend(
            [
                (
                    f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + width}" y2="{y:.1f}" '
                    'stroke="#dbe3ed"/>'
                ),
                (
                    f'<text x="{x0 - 12}" y="{y + 5:.1f}" text-anchor="end" '
                    'font-family="Arial,sans-serif" font-size="12" fill="#475569">'
                    f"{pct}%</text>"
                ),
            ]
        )
    for idx, p in enumerate(values):
        pct = p["purchasing_customers"] / p["eligible_customers"] * 100
        bar_height = pct / ymax * height
        x = x0 + idx * slot + 9
        y = y0 + height - bar_height
        elements.extend(
            [
                (
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{slot - 18:.1f}" '
                    f'height="{bar_height:.1f}" fill="#286c93"/>'
                ),
                (
                    f'<text x="{x + (slot - 18) / 2:.1f}" y="{y0 + height + 20}" '
                    'text-anchor="middle" font-family="Arial,sans-serif" '
                    f'font-size="11" fill="#334155">{p["age_period"]}</text>'
                ),
            ]
        )
    elements.extend(
        [
            (
                '<text x="519" y="425" text-anchor="middle" font-family="Arial,sans-serif" '
                'font-size="13" fill="#334155">30-day window since first purchase '
                "(1 = days 30–59; 14 = days 420–449)</text>"
            ),
            (
                '<text x="94" y="459" font-family="Arial,sans-serif" font-size="12" '
                'fill="#475569">Each rate = purchasers in window / 23,570 original customers. '
                "All shown windows have full follow-up.</text>"
            ),
            "</svg>",
        ]
    )
    TARGET.write_text("\n".join(elements) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
