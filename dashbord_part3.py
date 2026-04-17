import html
import os
from dashbord_part1 import OUTPUTS_DIR, TRACKER_PATH, DASHBOARD_PATH
from dashbord_part2 import load_reports, load_tracker, match_jobs, score_color


def build_html(jobs):
    total = len(jobs)
    apply_count = sum(1 for job in jobs if job['decision'].strip().lower() == 'apply')
    skip_count = sum(1 for job in jobs if job['decision'].strip().lower() == 'skip')

    html_lines = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '  <title>Job Fit Dashboard</title>',
        '  <style>',
        '    :root { --bg: #f8fafc; --hero: #111827; --hero-soft: #1f2937; --surface: #ffffff; --surface-soft: #f1f5f9; --text: #0f172a; --muted: #64748b; --border: #cbd5e1; --accent: #6366f1; --success: #16a34a; --danger: #dc2626; --warning: #f59e0b; --card-shadow: 0 28px 80px rgba(15, 23, 42, 0.12); }',
        '    * { box-sizing: border-box; }',
        '    body { margin: 0; min-height: 100vh; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: radial-gradient(circle at top left, rgba(99, 102, 241, 0.12), transparent 28%), linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%); color: var(--text); }',
        '    .page { max-width: 1240px; margin: 0 auto; padding: 32px 24px 48px; }',
        '    .hero { background: linear-gradient(135deg, var(--hero), #1e293b); border-radius: 32px; padding: 36px 32px; color: #f8fafc; box-shadow: var(--card-shadow); overflow: hidden; }',
        '    .hero-top { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 24px; align-items: flex-start; }',
        '    .hero-top h1 { margin: 0; font-size: clamp(2.4rem, 3vw, 3.4rem); line-height: 1.02; }',
        '    .hero-top p { margin: 0; max-width: 760px; color: #cbd5e1; font-size: 1rem; line-height: 1.75; }',
        '    .hero-stats { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); margin-top: 28px; }',
        '    .hero-card { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); border-radius: 22px; padding: 22px 24px; }',
        '    .hero-card strong { display: block; font-size: 2rem; margin-bottom: 8px; color: #ffffff; }',
        '    .hero-card span { color: #cbd5e1; }',
        '    .filter-bar { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 32px; }',
        '    .filter-btn { border: 1px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.08); color: #f8fafc; padding: 12px 18px; border-radius: 999px; cursor: pointer; transition: background 0.2s ease, transform 0.2s ease; }',
        '    .filter-btn:hover { background: rgba(255,255,255,0.16); transform: translateY(-1px); }',
        '    .filter-btn.active { background: #ffffff; color: var(--hero); border-color: transparent; }',
        '    .grid { display: grid; gap: 26px; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); margin-top: 32px; }',
        '    .card { background: var(--surface); border: 1px solid rgba(148, 163, 184, 0.16); border-radius: 32px; padding: 28px; box-shadow: var(--card-shadow); transition: transform 0.25s ease, box-shadow 0.25s ease; }',
        '    .card:hover { transform: translateY(-4px); box-shadow: 0 32px 100px rgba(15, 23, 42, 0.16); }',
        '    .card-header { display: flex; justify-content: space-between; gap: 18px; align-items: flex-start; margin-bottom: 18px; }',
        '    .card-header h2 { margin: 0; font-size: 1.3rem; }',
        '    .position { margin: 6px 0 0; color: var(--muted); }',
        '    .badge { min-width: 110px; text-align: right; color: #fff; padding: 12px 16px; border-radius: 999px; font-weight: 600; }',
        '    .badge.apply { background: var(--success); }',
        '    .badge.skip { background: var(--danger); }',
        '    .card-body { display: grid; gap: 16px; }',
        '    .snippet { margin: 0; color: var(--text); line-height: 1.75; }',
        '    .progress-row { display: grid; gap: 10px; }',
        '    .progress-label { display: flex; justify-content: space-between; gap: 16px; font-size: 0.95rem; color: var(--muted); }',
        '    .progress-track { background: var(--surface-soft); border-radius: 999px; overflow: hidden; height: 14px; }',
        '    .progress-fill { height: 100%; border-radius: 999px; transition: width 0.3s ease; }',
        '    .progress-fill.apply { background: var(--success); }',
        '    .progress-fill.skip { background: var(--danger); }',
        '    .tags-row { display: flex; flex-wrap: wrap; gap: 10px; }',
        '    .tag { display: inline-flex; align-items: center; gap: 6px; padding: 8px 12px; border-radius: 999px; background: #eff6ff; color: #1d4ed8; font-size: 0.92rem; }',
        '    .tag.gap { background: #fee2e2; color: #b91c1c; }',
        '    .tag.empty { background: #f3f4f6; color: #64748b; }',
        '    @media (max-width: 840px) { .hero-top { flex-direction: column; } .card-header { flex-direction: column; align-items: stretch; } }',
        '    @media (max-width: 640px) { .page { padding: 24px 16px 36px; } .filter-bar { justify-content: stretch; } .filter-btn { flex: 1 1 auto; } }',
        '  </style>',
        '</head>',
        '<body>',
        '  <div class="page">',
        '    <div class="hero">',
        '      <div class="hero-top">',
        '        <div>',
        '          <p style="text-transform: uppercase; letter-spacing: 0.24em; font-size: 0.78rem; margin:0; opacity: 0.8;">Job Fit Dashboard</p>',
        '          <h1>Job analysis and application tracking</h1>',
        '          <p>See your fit score, decision signal, matches, and gaps for each role in one clean dashboard.</p>',
        '        </div>',
        '        <div class="filter-bar">',
        '          <button class="filter-btn active" data-filter="all">All</button>',
        '          <button class="filter-btn" data-filter="apply">Apply</button>',
        '          <button class="filter-btn" data-filter="skip">Skip</button>',
        '        </div>',
        '      </div>',
        '      <div class="hero-stats">',
        f'        <div class="hero-card"><strong>{total}</strong><span>Total jobs analyzed</span></div>',
        f'        <div class="hero-card"><strong>{apply_count}</strong><span>Jobs to apply</span></div>',
        f'        <div class="hero-card"><strong>{skip_count}</strong><span>Jobs skipped</span></div>',
        '      </div>',
        '    </div>',
    ]
    for job in jobs:
        decision_key = job['decision'].strip().lower()
        color = score_color(job['fit_score'], job['decision'])
        score = job['fit_score'] if isinstance(job['fit_score'], int) else 0
        score_text = f"{score}/100" if isinstance(job['fit_score'], int) else 'N/A'
        score_percent = max(0, min(100, score)) if isinstance(job['fit_score'], int) else 0
        badge_class = 'apply' if decision_key == 'apply' else 'skip' if decision_key == 'skip' else ''
        matches_html = ''.join(f'<span class="tag match">{html.escape(tag)}</span>' for tag in job['matches']) or '<span class="tag empty">No matches listed</span>'
        gaps_html = ''.join(f'<span class="tag gap">{html.escape(tag)}</span>' for tag in job['gaps']) or '<span class="tag empty gap">No gaps listed</span>'
        snippet_html = html.escape(job['snippet']).replace('\n', '<br>')
        html_lines.extend([
            f'    <article class="card card-{decision_key if decision_key else "all"}">',
            '      <div class="card-header">',
            '        <div>',
            f'          <h2>{html.escape(job["company"])}</h2>',
            f'          <p class="position">{html.escape(job["position"])}</p>',
            '        </div>',
            f'        <div class="badge {badge_class}">',
            f'          <strong>{score_text}</strong>',
            f'          <span>{html.escape(job["decision"].title())}</span>',
            '        </div>',
            '      </div>',
            '      <div class="card-body">',
            '        <div class="progress-row">',
            '          <div class="progress-label"><span>Fit score</span><span>' + score_text + '</span></div>',
            '          <div class="progress-track">',
            f'            <div class="progress-fill {badge_class}" style="width: {score_percent}%;"></div>',
            '          </div>',
            '        </div>',
            f'        <p class="snippet">{snippet_html}</p>' if snippet_html else '',
            '        <div class="tags-row">',
            f'          {matches_html}',
            '        </div>',
            '        <div class="tags-row">',
            f'          {gaps_html}',
            '        </div>',
            '      </div>',
            '    </article>',
        ])
    html_lines.extend([
        '  </div>',
        '  <script>',
        '    const buttons = document.querySelectorAll(".filter-btn");',
        '    const cards = document.querySelectorAll(".card");',
        '    buttons.forEach(button => {',
        '      button.addEventListener("click", () => {',
        '        buttons.forEach(btn => btn.classList.remove("active"));',
        '        button.classList.add("active");',
        '        const filter = button.getAttribute("data-filter");',
        '        cards.forEach(card => {',
        '          if (filter === "all") {',
        '            card.style.display = "block";',
        '          } else {',
        '            card.style.display = card.classList.contains(`card-${filter}`) ? "block" : "none";',
        '          }',
        '        });',
        '      });',
        '    });',
        '  </script>',
        '</body>',
        '</html>',
    ])
    return '\n'.join(line for line in html_lines if line is not None)


def save_dashboard(content, path):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)


def main():
    tracker_data = load_tracker(TRACKER_PATH)
    reports = load_reports()
    jobs = match_jobs(reports, tracker_data)
    html = build_html(jobs)
    save_dashboard(html, DASHBOARD_PATH)
    print(f'Created {DASHBOARD_PATH}')


if __name__ == '__main__':
    main()
