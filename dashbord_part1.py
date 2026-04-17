import os
import re
import html
from openpyxl import load_workbook

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
TRACKER_PATH = os.path.join(BASE_DIR, 'tracker.xlsx')
DASHBOARD_PATH = os.path.join(BASE_DIR, 'dashboard.html')


def normalize_text(value):
    return str(value).strip() if value is not None else ''


def split_tags(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [normalize_text(item) for item in value if normalize_text(item)]
    text = normalize_text(value)
    if not text:
        return []
    return [normalize_text(part) for part in re.split(r'[\n,;]+', text) if normalize_text(part)]


def parse_markdown_report(path):
    report = {
        'company': '',
        'position': '',
        'fit_score': None,
        'decision': '',
        'matches': [],
        'gaps': [],
        'snippet': '',
        'path': path,
    }
    with open(path, 'r', encoding='utf-8') as file:
        lines = [line.rstrip() for line in file]

    section = None
    reasoning = []
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            if '—' in title:
                company, position = [part.strip() for part in title.split('—', 1)]
                report['company'] = company
                report['position'] = position
            elif '-' in title:
                parts = [part.strip() for part in title.split('-', 1)]
                if len(parts) == 2:
                    report['company'], report['position'] = parts
        elif line.startswith('**Fit Score:**'):
            value = line.split('**Fit Score:**', 1)[1].strip()
            if '/' in value:
                value = value.split('/', 1)[0].strip()
            try:
                report['fit_score'] = int(value)
            except Exception:
                pass
        elif line.startswith('**Decision:**'):
            report['decision'] = line.split('**Decision:**', 1)[1].strip()
        elif line.startswith('## '):
            section = line[3:].strip().lower()
        elif section == 'matches' and line.startswith('- '):
            report['matches'].append(line[2:].strip())
        elif section == 'gaps' and line.startswith('- '):
            report['gaps'].append(line[2:].strip())
        elif section == 'reasoning' and line:
            reasoning.append(line.strip())

    if not report['snippet'] and reasoning:
        report['snippet'] = ' '.join(reasoning[:3])

    if not report['company'] or not report['position']:
        filename = os.path.splitext(os.path.basename(path))[0]
        if not report['company']:
            report['company'] = filename
        if not report['position']:
            report['position'] = filename

    return report
