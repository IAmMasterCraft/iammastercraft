#!/usr/bin/env python3
"""
GitHub Profile Widgets Generator
Generates 4 unique SVG widgets for GitHub profile READMEs:
1. Code DNA - Visual fingerprint from coding patterns
2. Repo Skyline - City skyline from repo data
3. Skill Tree - RPG-style tech tree
4. Code Weather - Weather forecast from coding activity

Author: IAmMasterCraft
License: MIT
"""

import json
import math
import os
import sys
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict

# Try to import requests - needed for GitHub API
try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests --break-system-packages -q")
    import requests

# ============================================================
# CONFIGURATION
# ============================================================

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
USERNAME = os.environ.get("GITHUB_USERNAME", "IAmMasterCraft")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "widgets")

# Apple-style color palette
COLORS = {
    "bg": "#FFFFFF",
    "bg_subtle": "#F5F5F7",
    "bg_card": "#FBFBFD",
    "text_primary": "#1D1D1F",
    "text_secondary": "#86868B",
    "text_tertiary": "#AEAEB2",
    "border": "#E8E8ED",
    "border_light": "#F2F2F7",
    "accent_blue": "#007AFF",
    "accent_green": "#34C759",
    "accent_orange": "#FF9500",
    "accent_red": "#FF3B30",
    "accent_purple": "#AF52DE",
    "accent_teal": "#5AC8FA",
    "accent_indigo": "#5856D6",
    "accent_pink": "#FF2D55",
    "accent_yellow": "#FFCC00",
    "accent_mint": "#00C7BE",
    "shadow": "rgba(0,0,0,0.04)",
}

# Language color mapping (Apple-style muted tones)
LANG_COLORS = {
    "JavaScript": "#F7DF1E",
    "TypeScript": "#3178C6",
    "Python": "#3776AB",
    "HTML": "#E34F26",
    "CSS": "#1572B6",
    "Java": "#ED8B00",
    "C++": "#00599C",
    "C#": "#239120",
    "Go": "#00ADD8",
    "Rust": "#DEA584",
    "Ruby": "#CC342D",
    "PHP": "#777BB4",
    "Swift": "#F05138",
    "Kotlin": "#7F52FF",
    "Dart": "#0175C2",
    "Shell": "#89E051",
    "Vue": "#4FC08D",
    "Svelte": "#FF3E00",
    "Dockerfile": "#384D54",
    "SCSS": "#C6538C",
    "Lua": "#000080",
    "R": "#276DC3",
    "Jupyter Notebook": "#F37626",
    "C": "#555555",
    "Elixir": "#6E4A7E",
    "Haskell": "#5E5086",
    "Scala": "#DC322F",
    "Perl": "#39457E",
}

DEFAULT_LANG_COLOR = "#86868B"

# ============================================================
# GITHUB API
# ============================================================

def github_api(endpoint, params=None):
    """Make a GitHub API request."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    url = f"https://api.github.com{endpoint}"
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"API Error {resp.status_code}: {endpoint}")
        return None


def fetch_user_data():
    """Fetch all needed data from GitHub API."""
    print(f"Fetching data for @{USERNAME}...")
    
    # User profile
    user = github_api(f"/users/{USERNAME}") or {}
    
    # Repositories (up to 100)
    repos = github_api(f"/users/{USERNAME}/repos", {"per_page": 100, "sort": "updated"}) or []
    
    # Language stats per repo
    lang_totals = defaultdict(int)
    repo_data = []
    
    for repo in repos:
        if repo.get("fork"):
            continue
        
        name = repo.get("name", "")
        lang = repo.get("language") or "Other"
        stars = repo.get("stargazers_count", 0)
        size = repo.get("size", 0)
        
        # Fetch languages for this repo
        langs = github_api(f"/repos/{USERNAME}/{name}/languages") or {}
        for l, bytes_count in langs.items():
            lang_totals[l] += bytes_count
        
        repo_data.append({
            "name": name,
            "language": lang,
            "stars": stars,
            "size": size,
            "languages": langs,
            "description": repo.get("description", ""),
            "updated_at": repo.get("updated_at", ""),
            "created_at": repo.get("created_at", ""),
        })
    
    # Events (recent activity)
    events = github_api(f"/users/{USERNAME}/events/public", {"per_page": 100}) or []
    
    # Contribution-like data from events
    daily_activity = defaultdict(int)
    hourly_activity = defaultdict(int)
    event_types = defaultdict(int)
    
    for event in events:
        created = event.get("created_at", "")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                day_key = dt.strftime("%Y-%m-%d")
                daily_activity[day_key] += 1
                hourly_activity[dt.hour] += 1
            except:
                pass
        event_types[event.get("type", "Unknown")] += 1
    
    return {
        "user": user,
        "repos": repo_data,
        "languages": dict(lang_totals),
        "daily_activity": dict(daily_activity),
        "hourly_activity": dict(hourly_activity),
        "event_types": dict(event_types),
        "total_repos": len(repo_data),
        "total_stars": sum(r["stars"] for r in repo_data),
    }


def get_mock_data():
    """Return mock data for testing/preview."""
    return {
        "user": {
            "login": USERNAME,
            "name": "Boluwaji Akinsefunmi",
            "public_repos": 28,
            "followers": 45,
            "following": 30,
        },
        "repos": [
            {"name": "awesome-project", "language": "TypeScript", "stars": 12, "size": 2400, "languages": {"TypeScript": 45000, "JavaScript": 12000, "CSS": 8000}},
            {"name": "api-gateway", "language": "Python", "stars": 8, "size": 1800, "languages": {"Python": 38000, "Shell": 2000}},
            {"name": "react-dashboard", "language": "JavaScript", "stars": 15, "size": 3200, "languages": {"JavaScript": 52000, "CSS": 15000, "HTML": 8000}},
            {"name": "ml-pipeline", "language": "Python", "stars": 6, "size": 1200, "languages": {"Python": 28000, "Jupyter Notebook": 15000}},
            {"name": "devops-toolkit", "language": "Shell", "stars": 4, "size": 800, "languages": {"Shell": 12000, "Dockerfile": 3000}},
            {"name": "portfolio-site", "language": "HTML", "stars": 3, "size": 1500, "languages": {"HTML": 18000, "CSS": 22000, "JavaScript": 8000}},
            {"name": "rust-cli", "language": "Rust", "stars": 7, "size": 900, "languages": {"Rust": 15000}},
            {"name": "go-microservice", "language": "Go", "stars": 5, "size": 700, "languages": {"Go": 12000}},
            {"name": "vue-components", "language": "Vue", "stars": 9, "size": 2100, "languages": {"Vue": 25000, "JavaScript": 10000, "CSS": 5000}},
            {"name": "data-viz", "language": "JavaScript", "stars": 4, "size": 1100, "languages": {"JavaScript": 20000, "HTML": 5000, "CSS": 7000}},
            {"name": "auth-service", "language": "TypeScript", "stars": 6, "size": 1400, "languages": {"TypeScript": 30000}},
            {"name": "mobile-app", "language": "Dart", "stars": 3, "size": 2800, "languages": {"Dart": 40000}},
            {"name": "algorithms", "language": "Python", "stars": 2, "size": 600, "languages": {"Python": 18000}},
            {"name": "css-framework", "language": "CSS", "stars": 11, "size": 1900, "languages": {"CSS": 35000, "HTML": 5000, "JavaScript": 3000}},
        ],
        "languages": {
            "JavaScript": 105000, "TypeScript": 75000, "Python": 84000,
            "CSS": 92000, "HTML": 36000, "Vue": 25000, "Shell": 14000,
            "Rust": 15000, "Go": 12000, "Dart": 40000, "Dockerfile": 3000,
            "Jupyter Notebook": 15000,
        },
        "daily_activity": {
            (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"): max(0, int(5 * math.sin(i * 0.5) + 6 + (i % 3)))
            for i in range(30)
        },
        "hourly_activity": {h: max(1, int(8 * math.sin((h - 14) * 0.3) + 8)) for h in range(24)},
        "event_types": {"PushEvent": 120, "CreateEvent": 25, "PullRequestEvent": 18, "IssuesEvent": 10, "WatchEvent": 15},
        "total_repos": 14,
        "total_stars": 95,
    }


# ============================================================
# SVG HELPERS
# ============================================================

def svg_header(width, height, title=""):
    """Generate SVG header with Apple-style base styles."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
  <title>{title}</title>
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&amp;display=swap');
      * {{ font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif; }}
      .title {{ font-size: 18px; font-weight: 600; fill: {COLORS["text_primary"]}; letter-spacing: -0.3px; }}
      .subtitle {{ font-size: 13px; font-weight: 400; fill: {COLORS["text_secondary"]}; letter-spacing: -0.1px; }}
      .label {{ font-size: 11px; font-weight: 500; fill: {COLORS["text_secondary"]}; letter-spacing: 0.3px; text-transform: uppercase; }}
      .value {{ font-size: 14px; font-weight: 600; fill: {COLORS["text_primary"]}; }}
      .small {{ font-size: 11px; font-weight: 400; fill: {COLORS["text_tertiary"]}; }}
    </style>
    <filter id="shadow" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="0" dy="1" stdDeviation="3" flood-color="#000000" flood-opacity="0.04"/>
      <feDropShadow dx="0" dy="2" stdDeviation="8" flood-color="#000000" flood-opacity="0.03"/>
    </filter>
    <filter id="softShadow" x="-2%" y="-2%" width="104%" height="104%">
      <feDropShadow dx="0" dy="1" stdDeviation="2" flood-color="#000000" flood-opacity="0.06"/>
    </filter>
    <linearGradient id="cardBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#FAFAFA"/>
    </linearGradient>
  </defs>
'''

def svg_card_bg(width, height, rx=16):
    """Draw the card background."""
    return f'''  <rect width="{width}" height="{height}" rx="{rx}" fill="url(#cardBg)" stroke="{COLORS["border"]}" stroke-width="1"/>
'''

def svg_footer():
    return "</svg>\n"

def get_lang_color(lang):
    return LANG_COLORS.get(lang, DEFAULT_LANG_COLOR)


# ============================================================
# WIDGET 1: CODE DNA
# ============================================================

def generate_code_dna(data):
    """Generate a unique DNA helix fingerprint from coding patterns."""
    print("  Generating Code DNA...")
    
    width, height = 800, 280
    svg = svg_header(width, height, f"@{USERNAME}'s Code DNA")
    svg += svg_card_bg(width, height)
    
    # Title area
    svg += f'  <text x="32" y="38" class="title">Code DNA</text>\n'
    svg += f'  <text x="32" y="58" class="subtitle">Your unique developer fingerprint</text>\n'
    
    # Build DNA sequence from user data
    languages = data.get("languages", {})
    total_bytes = sum(languages.values()) or 1
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:8]
    
    # Generate DNA helix
    helix_start_x = 32
    helix_end_x = width - 32
    helix_width = helix_end_x - helix_start_x
    center_y = 155
    amplitude = 40
    num_points = 60
    
    # Create a hash from user data for unique pattern
    data_hash = hashlib.md5(json.dumps(sorted(languages.items())).encode()).hexdigest()
    phase_offset = int(data_hash[:4], 16) / 65535 * math.pi * 2
    freq_mod = 0.8 + (int(data_hash[4:8], 16) / 65535) * 0.6
    
    # Draw connecting rungs first (behind strands)
    for i in range(num_points):
        t = i / num_points
        x = helix_start_x + t * helix_width
        angle = t * math.pi * 4 * freq_mod + phase_offset
        
        y1 = center_y + math.sin(angle) * amplitude
        y2 = center_y - math.sin(angle) * amplitude
        
        # Only draw rungs at intervals
        if i % 3 == 0:
            # Pick language color based on position
            lang_idx = i % len(sorted_langs) if sorted_langs else 0
            lang_name = sorted_langs[lang_idx][0] if sorted_langs else "Other"
            color = get_lang_color(lang_name)
            
            opacity = 0.15 + 0.1 * abs(math.sin(angle))
            svg += f'  <line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.5" opacity="{opacity:.2f}"/>\n'
    
    # Draw strand 1 (front)
    points_1 = []
    points_2 = []
    
    for i in range(num_points + 1):
        t = i / num_points
        x = helix_start_x + t * helix_width
        angle = t * math.pi * 4 * freq_mod + phase_offset
        
        y1 = center_y + math.sin(angle) * amplitude
        y2 = center_y - math.sin(angle) * amplitude
        
        points_1.append((x, y1))
        points_2.append((x, y2))
    
    # Smooth path for strand 1
    path1 = f"M {points_1[0][0]:.1f} {points_1[0][1]:.1f}"
    for i in range(1, len(points_1)):
        px, py = points_1[i]
        path1 += f" L {px:.1f} {py:.1f}"
    
    path2 = f"M {points_2[0][0]:.1f} {points_2[0][1]:.1f}"
    for i in range(1, len(points_2)):
        px, py = points_2[i]
        path2 += f" L {px:.1f} {py:.1f}"
    
    # Gradient for strands
    svg += f'''  <defs>
    <linearGradient id="strand1" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{COLORS["accent_blue"]}"/>
      <stop offset="50%" stop-color="{COLORS["accent_purple"]}"/>
      <stop offset="100%" stop-color="{COLORS["accent_teal"]}"/>
    </linearGradient>
    <linearGradient id="strand2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{COLORS["accent_indigo"]}"/>
      <stop offset="50%" stop-color="{COLORS["accent_pink"]}"/>
      <stop offset="100%" stop-color="{COLORS["accent_orange"]}"/>
    </linearGradient>
  </defs>
'''
    
    svg += f'  <path d="{path1}" stroke="url(#strand1)" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.8"/>\n'
    svg += f'  <path d="{path2}" stroke="url(#strand2)" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.8"/>\n'
    
    # Draw nucleotide dots at key points
    for i in range(0, num_points + 1, 3):
        t = i / num_points
        x = helix_start_x + t * helix_width
        angle = t * math.pi * 4 * freq_mod + phase_offset
        
        y1 = center_y + math.sin(angle) * amplitude
        y2 = center_y - math.sin(angle) * amplitude
        
        lang_idx = (i // 3) % len(sorted_langs) if sorted_langs else 0
        lang_name = sorted_langs[lang_idx][0] if sorted_langs else "Other"
        color = get_lang_color(lang_name)
        
        # Front/back effect based on sine
        sin_val = math.sin(angle)
        r1 = 3.5 if sin_val > 0 else 2.5
        r2 = 2.5 if sin_val > 0 else 3.5
        o1 = 0.9 if sin_val > 0 else 0.5
        o2 = 0.5 if sin_val > 0 else 0.9
        
        svg += f'  <circle cx="{x:.1f}" cy="{y1:.1f}" r="{r1}" fill="{color}" opacity="{o1:.1f}"/>\n'
        svg += f'  <circle cx="{x:.1f}" cy="{y2:.1f}" r="{r2}" fill="{color}" opacity="{o2:.1f}"/>\n'
    
    # Language legend at bottom
    legend_y = 235
    legend_x = 32
    for i, (lang, bytes_count) in enumerate(sorted_langs[:6]):
        pct = bytes_count / total_bytes * 100
        color = get_lang_color(lang)
        col = i % 6
        x = legend_x + col * 125
        
        svg += f'  <circle cx="{x}" cy="{legend_y}" r="4" fill="{color}"/>\n'
        svg += f'  <text x="{x + 10}" y="{legend_y + 4}" class="small" fill="{COLORS["text_secondary"]}">{lang}</text>\n'
        svg += f'  <text x="{x + 10 + len(lang) * 6.2}" y="{legend_y + 4}" class="small" fill="{COLORS["text_tertiary"]}"> {pct:.1f}%</text>\n'
    
    # Unique hash ID
    short_hash = data_hash[:8].upper()
    svg += f'  <text x="{width - 32}" y="{legend_y + 18}" class="small" text-anchor="end" fill="{COLORS["text_tertiary"]}">DNA #{short_hash}</text>\n'
    
    svg += svg_footer()
    return svg


# ============================================================
# WIDGET 2: REPO SKYLINE
# ============================================================

def generate_repo_skyline(data):
    """Generate a city skyline where buildings represent repos."""
    print("  Generating Repo Skyline...")
    
    width, height = 800, 320
    svg = svg_header(width, height, f"@{USERNAME}'s Repo Skyline")
    svg += svg_card_bg(width, height)
    
    # Title
    svg += f'  <text x="32" y="38" class="title">Repo Skyline</text>\n'
    svg += f'  <text x="32" y="58" class="subtitle">{data["total_repos"]} repositories · {data["total_stars"]} stars</text>\n'
    
    repos = sorted(data.get("repos", []), key=lambda r: r.get("size", 0), reverse=True)[:18]
    if not repos:
        repos = [{"name": "no-repos", "language": "Other", "size": 100, "stars": 0}]
    
    max_size = max(r.get("size", 1) for r in repos) or 1
    
    ground_y = 250
    building_area_start = 40
    building_area_width = width - 80
    
    num_buildings = len(repos)
    gap = 6
    building_width = min(36, (building_area_width - gap * (num_buildings - 1)) / num_buildings)
    total_buildings_width = num_buildings * building_width + (num_buildings - 1) * gap
    start_x = (width - total_buildings_width) / 2
    
    # Sky gradient
    svg += f'''  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#F0F4FF" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{COLORS["bg_subtle"]}"/>
      <stop offset="100%" stop-color="{COLORS["bg"]}"/>
    </linearGradient>
  </defs>
'''
    
    # Ground
    svg += f'  <rect x="0" y="{ground_y}" width="{width}" height="{height - ground_y}" fill="url(#ground)" rx="0"/>\n'
    svg += f'  <line x1="32" y1="{ground_y}" x2="{width - 32}" y2="{ground_y}" stroke="{COLORS["border"]}" stroke-width="1"/>\n'
    
    # Buildings
    for i, repo in enumerate(repos):
        x = start_x + i * (building_width + gap)
        size = repo.get("size", 1)
        lang = repo.get("language", "Other")
        stars = repo.get("stars", 0)
        name = repo.get("name", "repo")
        
        # Height proportional to size (min 25, max 170)
        bh = 25 + (size / max_size) * 145
        by = ground_y - bh
        
        color = get_lang_color(lang)
        
        # Building shadow
        svg += f'  <rect x="{x + 2:.1f}" y="{by + 2:.1f}" width="{building_width:.1f}" height="{bh:.1f}" rx="3" fill="#000" opacity="0.03"/>\n'
        
        # Building body
        svg += f'  <rect x="{x:.1f}" y="{by:.1f}" width="{building_width:.1f}" height="{bh:.1f}" rx="3" fill="{color}" opacity="0.15"/>\n'
        svg += f'  <rect x="{x:.1f}" y="{by:.1f}" width="{building_width:.1f}" height="{bh:.1f}" rx="3" fill="none" stroke="{color}" stroke-width="1" opacity="0.3"/>\n'
        
        # Windows (small dots)
        window_rows = int(bh / 16)
        window_cols = max(1, int(building_width / 12))
        for wy in range(window_rows):
            for wx in range(window_cols):
                win_x = x + 6 + wx * 10
                win_y = by + 10 + wy * 14
                if win_x < x + building_width - 4 and win_y < ground_y - 6:
                    lit = (hash(f"{name}{wx}{wy}") % 3) != 0
                    opacity = 0.4 if lit else 0.1
                    svg += f'  <rect x="{win_x:.1f}" y="{win_y:.1f}" width="4" height="6" rx="1" fill="{color}" opacity="{opacity}"/>\n'
        
        # Antenna on tall buildings
        if bh > 100:
            antenna_h = 12
            ax = x + building_width / 2
            svg += f'  <line x1="{ax:.1f}" y1="{by:.1f}" x2="{ax:.1f}" y2="{by - antenna_h:.1f}" stroke="{color}" stroke-width="1" opacity="0.4"/>\n'
            svg += f'  <circle cx="{ax:.1f}" cy="{by - antenna_h:.1f}" r="2" fill="{color}" opacity="0.5"/>\n'
        
        # Star indicator
        if stars > 0:
            svg += f'  <text x="{x + building_width / 2:.1f}" y="{by - 6:.1f}" text-anchor="middle" font-size="9" fill="{COLORS["text_tertiary"]}">★ {stars}</text>\n'
        
        # Reflection (subtle)
        ref_h = min(bh * 0.3, 20)
        svg += f'  <rect x="{x:.1f}" y="{ground_y + 1:.1f}" width="{building_width:.1f}" height="{ref_h:.1f}" rx="2" fill="{color}" opacity="0.04"/>\n'
    
    # Repo names along the bottom
    svg += f'  <text x="{width / 2}" y="{ground_y + 40}" text-anchor="middle" class="small" fill="{COLORS["text_tertiary"]}">Each building represents a repository · Height = codebase size · Color = primary language</text>\n'
    
    # Top language legend
    top_langs = sorted(data.get("languages", {}).items(), key=lambda x: x[1], reverse=True)[:5]
    legend_x = width - 32
    for i, (lang, _) in enumerate(top_langs):
        lx = legend_x - (len(top_langs) - 1 - i) * 90
        color = get_lang_color(lang)
        svg += f'  <circle cx="{lx - 8}" cy="48" r="4" fill="{color}" opacity="0.7"/>\n'
        svg += f'  <text x="{lx}" y="52" class="small" fill="{COLORS["text_secondary"]}">{lang}</text>\n'
    
    # Stats row at bottom
    stats_y = height - 22
    svg += f'  <text x="32" y="{stats_y}" class="small" fill="{COLORS["text_tertiary"]}">'
    svg += f'{data["total_repos"]} repos · {len(data.get("languages", {}))} languages · {data["total_stars"]} ★</text>\n'
    
    svg += svg_footer()
    return svg


# ============================================================
# WIDGET 3: SKILL TREE
# ============================================================

def generate_skill_tree(data):
    """Generate an RPG-style skill tree from language data."""
    print("  Generating Skill Tree...")
    
    width, height = 800, 400
    svg = svg_header(width, height, f"@{USERNAME}'s Skill Tree")
    svg += svg_card_bg(width, height)
    
    # Title
    svg += f'  <text x="32" y="38" class="title">Skill Tree</text>\n'
    svg += f'  <text x="32" y="58" class="subtitle">Languages &amp; frameworks mastery</text>\n'
    
    # Calculate XP for each language
    languages = data.get("languages", {})
    total_bytes = sum(languages.values()) or 1
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    
    # Categorize languages
    categories = {
        "Frontend": ["JavaScript", "TypeScript", "HTML", "CSS", "SCSS", "Vue", "Svelte", "Dart"],
        "Backend": ["Python", "Java", "Go", "Rust", "Ruby", "PHP", "C#", "Kotlin", "Scala", "Elixir", "Perl", "C", "C++", "Haskell"],
        "Data & ML": ["Jupyter Notebook", "R", "Lua"],
        "DevOps": ["Shell", "Dockerfile"],
    }
    
    categorized = {}
    for cat, cat_langs in categories.items():
        items = [(lang, bytes_count) for lang, bytes_count in sorted_langs if lang in cat_langs]
        if items:
            categorized[cat] = items
    
    # Also add uncategorized
    all_categorized = set()
    for cat_langs in categories.values():
        all_categorized.update(cat_langs)
    uncategorized = [(lang, b) for lang, b in sorted_langs if lang not in all_categorized]
    if uncategorized:
        categorized["Other"] = uncategorized
    
    # Layout
    cat_names = list(categorized.keys())
    num_cats = len(cat_names)
    
    col_width = (width - 64) / max(num_cats, 1)
    start_y = 85
    
    # Category icons/colors
    cat_colors = {
        "Frontend": COLORS["accent_blue"],
        "Backend": COLORS["accent_green"],
        "Data & ML": COLORS["accent_orange"],
        "DevOps": COLORS["accent_purple"],
        "Other": COLORS["text_tertiary"],
    }
    
    max_bytes = max(languages.values()) if languages else 1
    
    for ci, cat in enumerate(cat_names):
        cx = 32 + ci * col_width + col_width / 2
        cat_color = cat_colors.get(cat, COLORS["text_tertiary"])
        
        # Category header
        svg += f'  <rect x="{cx - col_width / 2 + 8}" y="{start_y - 4}" width="{col_width - 16}" height="28" rx="8" fill="{cat_color}" opacity="0.08"/>\n'
        svg += f'  <text x="{cx}" y="{start_y + 14}" text-anchor="middle" class="label" fill="{cat_color}">{cat.upper()}</text>\n'
        
        # Vertical connector line
        items = categorized[cat]
        if items:
            line_top = start_y + 32
            line_bottom = start_y + 32 + len(items) * 44
            svg += f'  <line x1="{cx}" y1="{line_top}" x2="{cx}" y2="{line_bottom}" stroke="{COLORS["border_light"]}" stroke-width="2"/>\n'
        
        # Skills
        for si, (lang, bytes_count) in enumerate(items[:6]):
            sy = start_y + 44 + si * 44
            pct = bytes_count / max_bytes
            xp_width = max(12, pct * (col_width - 80))
            
            # Determine level
            if pct > 0.7:
                level = "Master"
                level_color = COLORS["accent_yellow"]
            elif pct > 0.4:
                level = "Expert"
                level_color = COLORS["accent_purple"]
            elif pct > 0.2:
                level = "Adept"
                level_color = COLORS["accent_blue"]
            elif pct > 0.08:
                level = "Skilled"
                level_color = COLORS["accent_green"]
            else:
                level = "Novice"
                level_color = COLORS["text_tertiary"]
            
            lang_color = get_lang_color(lang)
            node_x = cx
            
            # Connection dot
            svg += f'  <circle cx="{node_x}" cy="{sy + 8}" r="5" fill="{COLORS["bg"]}" stroke="{lang_color}" stroke-width="2"/>\n'
            svg += f'  <circle cx="{node_x}" cy="{sy + 8}" r="2.5" fill="{lang_color}"/>\n'
            
            # Skill name and XP bar
            bar_x = node_x + 14
            bar_y = sy + 2
            bar_h = 6
            
            # Truncate lang name if too long
            display_name = lang[:12] + ".." if len(lang) > 14 else lang
            svg += f'  <text x="{bar_x}" y="{sy}" font-size="12" font-weight="500" fill="{COLORS["text_primary"]}">{display_name}</text>\n'
            
            # XP bar background
            full_bar_width = col_width - 80
            svg += f'  <rect x="{bar_x}" y="{bar_y + 8}" width="{full_bar_width}" height="{bar_h}" rx="3" fill="{COLORS["bg_subtle"]}"/>\n'
            
            # XP bar fill
            svg += f'  <rect x="{bar_x}" y="{bar_y + 8}" width="{xp_width:.1f}" height="{bar_h}" rx="3" fill="{lang_color}" opacity="0.6"/>\n'
            
            # Level badge
            svg += f'  <text x="{bar_x + full_bar_width + 4}" y="{sy + 1}" font-size="8" font-weight="600" fill="{level_color}" letter-spacing="0.5">{level.upper()}</text>\n'
    
    # Footer stats
    total_langs = len(sorted_langs)
    master_count = sum(1 for _, b in sorted_langs if b / max_bytes > 0.7)
    svg += f'  <text x="32" y="{height - 22}" class="small" fill="{COLORS["text_tertiary"]}">{total_langs} skills unlocked · {master_count} mastered</text>\n'
    
    svg += svg_footer()
    return svg


# ============================================================
# WIDGET 4: CODE WEATHER
# ============================================================

def generate_code_weather(data):
    """Generate a weather forecast card from coding activity."""
    print("  Generating Code Weather...")
    
    width, height = 800, 300
    svg = svg_header(width, height, f"@{USERNAME}'s Code Weather")
    svg += svg_card_bg(width, height)
    
    daily = data.get("daily_activity", {})
    
    # Calculate activity metrics
    today = datetime.now()
    last_7 = []
    last_30 = []
    
    for i in range(30):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        count = daily.get(day, 0)
        last_30.append(count)
        if i < 7:
            last_7.append(count)
    
    avg_7 = sum(last_7) / max(len(last_7), 1)
    avg_30 = sum(last_30) / max(len(last_30), 1)
    today_count = last_30[0] if last_30 else 0
    max_30 = max(last_30) if last_30 else 1
    
    # Determine "weather"
    if today_count == 0:
        weather = "Cloudy"
        weather_icon = "☁️"
        weather_desc = "No commits detected today"
        temp = 0
    elif today_count <= 2:
        weather = "Partly Cloudy"
        weather_icon = "⛅"
        weather_desc = "Light coding activity"
        temp = today_count * 12
    elif today_count <= 5:
        weather = "Sunny"
        weather_icon = "☀️"
        weather_desc = "Good coding flow"
        temp = today_count * 10
    elif today_count <= 10:
        weather = "Hot"
        weather_icon = "🔥"
        weather_desc = "On fire! High activity"
        temp = today_count * 8
    else:
        weather = "Thunderstorm"
        weather_icon = "⚡"
        weather_desc = "Massive commit storm!"
        temp = min(99, today_count * 6)
    
    # Trend
    if avg_7 > avg_30 * 1.2:
        trend = "↑ Trending up"
        trend_color = COLORS["accent_green"]
    elif avg_7 < avg_30 * 0.8:
        trend = "↓ Cooling down"
        trend_color = COLORS["accent_orange"]
    else:
        trend = "→ Steady"
        trend_color = COLORS["accent_blue"]
    
    # Title
    svg += f'  <text x="32" y="38" class="title">Code Weather</text>\n'
    svg += f'  <text x="32" y="58" class="subtitle">Developer activity forecast</text>\n'
    
    # Current weather card (left side)
    card_x, card_y = 32, 78
    card_w, card_h = 240, 140
    
    svg += f'  <rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="12" fill="{COLORS["bg_subtle"]}"/>\n'
    
    # Weather icon (text emoji)
    svg += f'  <text x="{card_x + 24}" y="{card_y + 52}" font-size="36">{weather_icon}</text>\n'
    
    # Temperature
    svg += f'  <text x="{card_x + 80}" y="{card_y + 48}" font-size="42" font-weight="300" fill="{COLORS["text_primary"]}">{temp}°</text>\n'
    
    # Weather name
    svg += f'  <text x="{card_x + 24}" y="{card_y + 80}" font-size="15" font-weight="600" fill="{COLORS["text_primary"]}">{weather}</text>\n'
    svg += f'  <text x="{card_x + 24}" y="{card_y + 98}" font-size="11" fill="{COLORS["text_secondary"]}">{weather_desc}</text>\n'
    
    # Trend
    svg += f'  <text x="{card_x + 24}" y="{card_y + 122}" font-size="12" font-weight="500" fill="{trend_color}">{trend}</text>\n'
    
    # 7-day forecast (right side)
    forecast_x = 300
    forecast_y = 78
    day_width = (width - forecast_x - 40) / 7
    
    svg += f'  <text x="{forecast_x}" y="{forecast_y - 4}" class="label">7-DAY FORECAST</text>\n'
    
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    
    for i in range(7):
        day_idx = 6 - i  # Reverse so most recent is on right
        day = today - timedelta(days=day_idx)
        day_name = day_names[day.weekday()] if day.weekday() < 7 else "?"
        count = last_7[day_idx] if day_idx < len(last_7) else 0
        
        dx = forecast_x + i * day_width + day_width / 2
        dy = forecast_y + 16
        
        # Day name
        is_today = day_idx == 0
        font_weight = "600" if is_today else "400"
        text_fill = COLORS["text_primary"] if is_today else COLORS["text_secondary"]
        svg += f'  <text x="{dx}" y="{dy}" text-anchor="middle" font-size="11" font-weight="{font_weight}" fill="{text_fill}">{day_name}</text>\n'
        
        # Mini weather icon based on count
        if count == 0:
            mini_icon = "☁️"
        elif count <= 2:
            mini_icon = "⛅"
        elif count <= 5:
            mini_icon = "☀️"
        elif count <= 10:
            mini_icon = "🔥"
        else:
            mini_icon = "⚡"
        
        svg += f'  <text x="{dx}" y="{dy + 28}" text-anchor="middle" font-size="18">{mini_icon}</text>\n'
        
        # Commit count
        svg += f'  <text x="{dx}" y="{dy + 46}" text-anchor="middle" font-size="13" font-weight="600" fill="{COLORS["text_primary"]}">{count}</text>\n'
        svg += f'  <text x="{dx}" y="{dy + 60}" text-anchor="middle" font-size="9" fill="{COLORS["text_tertiary"]}">commits</text>\n'
    
    # 30-day activity chart (bottom)
    chart_x = 300
    chart_y = 200
    chart_w = width - chart_x - 40
    chart_h = 60
    
    svg += f'  <text x="{chart_x}" y="{chart_y - 6}" class="label">30-DAY ACTIVITY</text>\n'
    
    # Bar chart
    bar_w = chart_w / 30 - 1
    max_val = max(last_30) if last_30 and max(last_30) > 0 else 1
    
    for i in range(min(30, len(last_30))):
        bx = chart_x + (29 - i) * (bar_w + 1)
        val = last_30[i]
        bh = max(2, (val / max_val) * chart_h)
        by = chart_y + chart_h - bh + 8
        
        # Color intensity based on value
        if val == 0:
            color = COLORS["border_light"]
        elif val <= 2:
            opacity = 0.3
            color = COLORS["accent_blue"]
        elif val <= 5:
            opacity = 0.5
            color = COLORS["accent_blue"]
        else:
            opacity = 0.7
            color = COLORS["accent_blue"]
        
        if val == 0:
            svg += f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" rx="1.5" fill="{color}"/>\n'
        else:
            svg += f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" rx="1.5" fill="{color}" opacity="{opacity}"/>\n'
    
    # Stats footer
    stats_y = height - 22
    svg += f'  <text x="32" y="{stats_y}" class="small" fill="{COLORS["text_tertiary"]}">'
    svg += f'Today: {today_count} commits · 7-day avg: {avg_7:.1f} · 30-day avg: {avg_30:.1f}</text>\n'
    
    svg += svg_footer()
    return svg


# ============================================================
# README GENERATOR
# ============================================================

def generate_readme(data):
    """Generate an updated README.md."""
    print("  Generating README.md...")
    
    user = data.get("user", {})
    name = user.get("name", USERNAME)
    
    # Top languages for badges
    languages = data.get("languages", {})
    total = sum(languages.values()) or 1
    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]
    
    readme = f'''<div align="center">

# Hey, I'm {name} 👋

**`@{USERNAME}`** · Full-Stack Developer · Building things that matter

<br>

[![Follow on X](https://img.shields.io/twitter/follow/bomoakin?logo=x&label=Follow%20%40IAmMasterCraft&style=flat-square&color=1D1D1F)](https://x.com/bomoakin)
[![GitHub followers](https://img.shields.io/github/followers/IAmMasterCraft?style=flat-square&color=1D1D1F&label=Follow)](https://github.com/IAmMasterCraft)
[![Email](https://img.shields.io/badge/Email-bolu.akinsefunmi%40gmail.com-1D1D1F?style=flat-square)](mailto:bolu.akinsefunmi@gmail.com)

<br>

<a href="https://codepen.io/online_digital_skills"><img src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/codepen.svg" height="22" width="22" /></a>&nbsp;&nbsp;&nbsp;
<a href="https://x.com/bomoakin"><img src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/twitter.svg" height="22" width="22" /></a>&nbsp;&nbsp;&nbsp;
<a href="https://linkedin.com/in/boluwaji-akinsefunmi-68a65615a"><img src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/linkedin.svg" height="22" width="22" /></a>&nbsp;&nbsp;&nbsp;
<a href="https://fb.com/akinsefunmi.boluwaji"><img src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/facebook.svg" height="22" width="22" /></a>&nbsp;&nbsp;&nbsp;
<a href="https://instagram.com/iammastercraft"><img src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/instagram.svg" height="22" width="22" /></a>

</div>

<br>

---

<br>

<!-- CODE DNA -->
<div align="center">
  <img src="./widgets/code-dna.svg" alt="Code DNA" width="100%" />
</div>

<br>

<!-- REPO SKYLINE -->
<div align="center">
  <img src="./widgets/repo-skyline.svg" alt="Repo Skyline" width="100%" />
</div>

<br>

<!-- SKILL TREE -->
<div align="center">
  <img src="./widgets/skill-tree.svg" alt="Skill Tree" width="100%" />
</div>

<br>

<!-- CODE WEATHER -->
<div align="center">
  <img src="./widgets/code-weather.svg" alt="Code Weather" width="100%" />
</div>

<br>

---

<br>

<div align="center">

<img src="http://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=IAmMasterCraft&theme=github" width="100%" alt="Profile Details" />

<br><br>

<img src="http://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=IAmMasterCraft&theme=github" width="49%" alt="Repos per Language" />
<img src="http://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username=IAmMasterCraft&theme=github" width="49%" alt="Most Commit Language" />

<br>

<img src="http://github-profile-summary-cards.vercel.app/api/cards/stats?username=IAmMasterCraft&theme=github" width="49%" alt="Stats" />
<img src="http://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=IAmMasterCraft&theme=github&utcOffset=1" width="49%" alt="Productive Time" />

<br><br>

<img src="https://github-readme-streak-stats.herokuapp.com/?user=IAmMasterCraft" width="100%" alt="GitHub Streaks" />

</div>

<br>

---

<div align="center">
  <sub>Widgets auto-generated with ❤️ by <a href="https://github.com/IAmMasterCraft">@IAmMasterCraft</a> · Updated daily via GitHub Actions</sub>
</div>
'''
    return readme


# ============================================================
# GITHUB ACTION WORKFLOW
# ============================================================

WORKFLOW_YAML = '''name: Update Profile Widgets

on:
  schedule:
    # Runs daily at 6:00 AM UTC
    - cron: '0 6 * * *'
  workflow_dispatch: # Allow manual trigger
  push:
    branches: [main]
    paths:
      - 'scripts/generate_widgets.py'

permissions:
  contents: write

jobs:
  update-widgets:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Generate widgets
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_USERNAME: ${{ github.repository_owner }}
          OUTPUT_DIR: widgets
        run: python scripts/generate_widgets.py

      - name: Commit and push changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add widgets/ README.md
          git diff --quiet && git diff --staged --quiet || (
            git commit -m "🎨 Update profile widgets [skip ci]"
            git push
          )
'''


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 50)
    print("  GitHub Profile Widgets Generator")
    print("=" * 50)
    
    # Fetch data (use real API if token available, else mock)
    if GITHUB_TOKEN:
        print("Using GitHub API with token...")
        data = fetch_user_data()
    else:
        print("No GITHUB_TOKEN found, using mock data for preview...")
        data = get_mock_data()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate all widgets
    print("\nGenerating widgets...")
    
    widgets = {
        "code-dna.svg": generate_code_dna(data),
        "repo-skyline.svg": generate_repo_skyline(data),
        "skill-tree.svg": generate_skill_tree(data),
        "code-weather.svg": generate_code_weather(data),
    }
    
    for filename, svg_content in widgets.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            f.write(svg_content)
        print(f"  ✓ {filepath}")
    
    # Generate README
    readme = generate_readme(data)
    with open("README.md", "w") as f:
        f.write(readme)
    print("  ✓ README.md")
    
    print("\n✅ All widgets generated successfully!")
    print(f"   Output directory: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
