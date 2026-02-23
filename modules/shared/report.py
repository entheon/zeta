"""Shared HTML report generation for categorization results."""

from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Color palette for categories — visually distinct, dark-theme friendly
_CATEGORY_COLORS: dict[str, str] = {
    "Finance": "#4ecdc4",
    "Shopping": "#ff6b6b",
    "Social": "#a78bfa",
    "Entertainment": "#fbbf24",
    "Work": "#60a5fa",
    "Education": "#34d399",
    "Travel": "#f472b6",
    "Health": "#fb923c",
    "Uncategorized": "#94a3b8",
}

_DEFAULT_COLOR = "#94a3b8"


def _get_color(category: str) -> str:
    return _CATEGORY_COLORS.get(category, _DEFAULT_COLOR)


def _extract_domain(value: str) -> str:
    """Extract domain from an email address or URL.

    Handles both "user@domain.com" and "https://domain.com/path" formats.
    """
    if "@" in value:
        return value.split("@")[-1].lower()
    # Strip protocol and path for URLs
    domain = value.lower()
    for prefix in ("https://", "http://", "www."):
        domain = domain.removeprefix(prefix)
    domain = domain.split("/")[0]
    return domain or "unknown"


def _build_category_stats(
    items: list[dict[str, Any]],
    source_field: str,
    detail_field: str,
) -> dict[str, dict[str, Any]]:
    """Aggregate stats per category.

    Args:
        items: List of categorized item dicts (must have "category"
            and "confidence" keys).
        source_field: Key for the source identifier (e.g. "from",
            "login_uri").
        detail_field: Key for the detail text (e.g. "subject", "name").

    Returns:
        Dict mapping category name to stats dict.
    """
    stats: dict[str, dict[str, Any]] = {}

    for item in items:
        cat = item["category"]
        if cat not in stats:
            stats[cat] = {
                "count": 0,
                "sources": defaultdict(int),
                "details": [],
                "confidences": [],
            }

        stats[cat]["count"] += 1
        source = _extract_domain(item.get(source_field, ""))
        stats[cat]["sources"][source] += 1
        stats[cat]["confidences"].append(item.get("confidence", 0.0))

        detail = item.get(detail_field, "")
        if detail and len(stats[cat]["details"]) < 10:
            stats[cat]["details"].append(detail)

    return stats


def _render_distribution_bar(stats: dict[str, dict[str, Any]], total: int) -> str:
    """Render a horizontal stacked bar showing category distribution."""
    segments = []
    for cat, data in sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True):
        pct = (data["count"] / total) * 100 if total else 0
        if pct < 1:
            continue
        color = _get_color(cat)
        segments.append(
            f'<div class="bar-segment" style="width:{pct:.1f}%;'
            f'background:{color}" title="{cat}: {data["count"]} '
            f'({pct:.1f}%)"></div>'
        )
    return f'<div class="distribution-bar">{"".join(segments)}</div>'


def _render_category_section(
    category: str,
    data: dict[str, Any],
    total: int,
    item_noun: str,
    source_label: str,
    detail_label: str,
) -> str:
    """Render a single category card."""
    pct = (data["count"] / total) * 100 if total else 0
    color = _get_color(category)
    avg_conf = (
        sum(data["confidences"]) / len(data["confidences"])
        if data["confidences"]
        else 0.0
    )

    sorted_sources = sorted(data["sources"].items(), key=lambda x: x[1], reverse=True)
    num_sources = len(sorted_sources)

    source_items = "\n".join(
        f'<span class="domain-tag">{source} '
        f'<span class="domain-count">({count})</span></span>'
        for source, count in sorted_sources[:20]
    )
    if num_sources > 20:
        source_items += (
            f'\n<span class="domain-tag more">+{num_sources - 20} more</span>'
        )

    detail_items = "\n".join(f"<li>{_escape_html(d)}</li>" for d in data["details"])

    return f"""
    <details class="category-card" open>
      <summary class="category-header">
        <span class="category-dot" style="background:{color}"></span>
        <span class="category-name">{_escape_html(category)}</span>
        <span class="category-stats">
          {data["count"]} {item_noun} ({pct:.1f}%)
          &middot; {num_sources} {source_label}
          &middot; avg confidence {avg_conf:.0%}
        </span>
      </summary>
      <div class="category-body">
        <div class="section-label">{_escape_html(source_label)}</div>
        <div class="domain-list">{source_items}</div>
        <div class="section-label">{_escape_html(detail_label)}</div>
        <ul class="subject-list">{detail_items}</ul>
      </div>
    </details>"""


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


_CSS = """\
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
               Roboto, sans-serif;
  background: #0f172a;
  color: #e2e8f0;
  line-height: 1.6;
  padding: 2rem;
  max-width: 960px;
  margin: 0 auto;
}
h1 {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}
.subtitle {
  color: #94a3b8;
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}
.distribution-bar {
  display: flex;
  height: 28px;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 0.5rem;
  gap: 2px;
}
.bar-segment {
  transition: opacity 0.2s;
  cursor: default;
}
.bar-segment:hover { opacity: 0.8; }
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 2rem;
  font-size: 0.8rem;
  color: #94a3b8;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}
.category-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  margin-bottom: 0.75rem;
  overflow: hidden;
}
.category-header {
  padding: 1rem 1.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  list-style: none;
  user-select: none;
}
.category-header::-webkit-details-marker { display: none; }
.category-header::before {
  content: '▸';
  font-size: 0.75rem;
  color: #64748b;
  transition: transform 0.2s;
}
details[open] > .category-header::before {
  transform: rotate(90deg);
}
.category-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}
.category-name {
  font-weight: 600;
  font-size: 1.05rem;
}
.category-stats {
  color: #94a3b8;
  font-size: 0.85rem;
  margin-left: auto;
}
.category-body {
  padding: 0 1.25rem 1.25rem;
  border-top: 1px solid #334155;
}
.section-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin: 1rem 0 0.5rem;
}
.domain-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.domain-tag {
  background: #334155;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-family: 'SF Mono', 'Fira Code', monospace;
}
.domain-count { color: #94a3b8; }
.domain-tag.more {
  background: transparent;
  color: #64748b;
  font-style: italic;
}
.subject-list {
  list-style: none;
  font-size: 0.85rem;
  color: #cbd5e1;
}
.subject-list li {
  padding: 0.2rem 0;
  border-bottom: 1px solid #1e293b;
}
.subject-list li:last-child { border-bottom: none; }
footer {
  text-align: center;
  color: #475569;
  font-size: 0.75rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #1e293b;
}
"""


def generate_html_report(
    items: list[dict[str, Any]],
    output_path: Path,
    *,
    title: str = "Categorization Report",
    item_noun: str = "items",
    source_field: str = "from",
    source_label: str = "Domains",
    detail_field: str = "subject",
    detail_label: str = "Examples",
) -> None:
    """Generate a self-contained HTML report from categorized items.

    Args:
        items: List of dicts, each must have "category" and "confidence"
            keys plus whatever source_field and detail_field point to.
        output_path: Where to write the HTML file.
        title: Report heading.
        item_noun: Noun for items (e.g. "emails", "passwords").
        source_field: Key in item dicts for the source (domain/URL).
        source_label: Display label for the source section.
        detail_field: Key in item dicts for detail text.
        detail_label: Display label for the detail section.
    """
    total = len(items)
    stats = _build_category_stats(items, source_field, detail_field)

    sorted_cats = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)

    bar_html = _render_distribution_bar(stats, total)

    legend_items = "".join(
        f'<span class="legend-item">'
        f'<span class="legend-dot" style="background:'
        f'{_get_color(cat)}"></span>'
        f"{_escape_html(cat)} ({data['count']})"
        f"</span>"
        for cat, data in sorted_cats
    )

    cards_html = "".join(
        _render_category_section(
            cat, data, total, item_noun, source_label, detail_label
        )
        for cat, data in sorted_cats
    )

    num_categories = len(stats)
    timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")

    _font_url = (
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"
    )

    escaped_title = _escape_html(title)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="{_font_url}" rel="stylesheet">
  <style>{_CSS}</style>
</head>
<body>
  <h1>{escaped_title}</h1>
  <p class="subtitle">
    {total:,} {item_noun} across {num_categories} categories
  </p>

  {bar_html}
  <div class="legend">{legend_items}</div>

  {cards_html}

  <footer>Generated {timestamp} by Zeta</footer>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
