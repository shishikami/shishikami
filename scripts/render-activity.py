"""Wrap the generated contribution snake in a matching, accessible activity card."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET


def contribution_count():
    query = 'query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar { totalContributions } } } }'
    payload = json.dumps({'query': query, 'variables': {'login': os.environ['PROFILE_OWNER']}}).encode()
    request = urllib.request.Request(
        'https://api.github.com/graphql', data=payload,
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                 'Content-Type': 'application/json', 'User-Agent': 'profile-assets'},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError('GitHub did not return the contribution calendar')
    return int(result['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions'])


def render(snake_path, total, updated, output):
    snake = ET.parse(snake_path).getroot()
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    snake.set('x', '32')
    snake.set('y', '87')
    snake.set('width', '1136')
    snake.set('height', '205')
    nested = ET.tostring(snake, encoding='unicode')
    image = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="330" viewBox="0 0 1200 330" role="img" aria-labelledby="activity-title">
<title id="activity-title">{total:,} GitHub contributions in the last 12 months. Updated {updated}. Animated contribution snake.</title>
<defs><linearGradient id="activity-bg" x2="1" y2="1"><stop stop-color="#101e34"/><stop offset="1" stop-color="#090f1c"/></linearGradient></defs>
<rect x="1" y="1" width="1198" height="328" rx="22" fill="url(#activity-bg)" stroke="#26374f"/>
<g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif">
  <text x="36" y="44" fill="#f0f6fc" font-size="25" font-weight="600">A little progress, every time.</text>
  <text x="1164" y="44" fill="#5eead4" font-size="23" text-anchor="end">{total:,}<tspan fill="#8ba4bf" font-size="17"> contributions</tspan></text>
  <text x="36" y="74" fill="#829cb7" font-size="15">The last 12 months, one square at a time.</text>
  <text x="36" y="307" fill="#7f99b3" font-size="13" letter-spacing="1.5">GITHUB / CONTRIBUTION LOG</text>
  <text x="1164" y="307" fill="#7f99b3" font-size="13" text-anchor="end">UPDATED {updated} UTC</text>
</g>
{nested}
</svg>
'''
    ET.fromstring(image)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(image)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--snake', type=Path, default=Path('work/snake.svg'))
    parser.add_argument('--output', type=Path, default=Path('assets/activity.svg'))
    parser.add_argument('--snapshot-count', type=int)
    parser.add_argument('--date', default=datetime.now(timezone.utc).strftime('%Y-%m-%d'))
    args = parser.parse_args()
    total = args.snapshot_count if args.snapshot_count is not None else contribution_count()
    render(args.snake, total, args.date, args.output)
