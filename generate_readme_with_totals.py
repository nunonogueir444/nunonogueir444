REPO_TABLE_WIDTH = "840px"  # Set your desired width here
REPO_TABLE_HEIGHT = "1600px"  # Set your desired height here

import requests
import re
import os
from collections import defaultdict

GITHUB_USERNAME = "nunonogueir444"
GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # Use environment variable for token

headers = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    headers["Authorization"] = f"token {GITHUB_TOKEN}"

def get_repos(username):
    url = f"{GITHUB_API}/users/{username}/repos?per_page=100&type=public"
    repos = []
    while url:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        repos.extend(resp.json())
        url = resp.links.get('next', {}).get('url')
    return repos

def get_languages(repo_full_name):
    url = f"{GITHUB_API}/repos/{repo_full_name}/languages"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def generate_markdown_and_collect_totals(repos):
    md = []
    lang_totals = defaultdict(int)
    for repo in repos:
        name = repo['name']
        full_name = repo['full_name']
        html_url = repo['html_url']
        languages = get_languages(full_name)
        if not languages:
            md.append(f"\n<table><tr><th colspan='2' style='text-align:center;font-size:1.1em;'><a href='{html_url}'>{name}</a></th></tr><tr><th></th><th></th></tr><tr><td colspan='2'>No code detected.</td></tr></table>\n")
            continue
        total = sum(languages.values())
        md.append(f"\n<table><tr><th colspan='2' style='text-align:center;font-size:1.1em;'><a href='{html_url}'>{name}</a></th></tr><tr><th></th><th></th></tr>")
        for lang, lines in sorted(languages.items(), key=lambda x: -x[1]):
            percent = lines / total * 100 if total else 0
            md.append(f"<tr><td>{lang}</td><td>{percent:.1f}%</td></tr>")
            lang_totals[lang] += lines
        md.append("</table>\n")
    return ''.join(md), lang_totals

def generate_totals_markdown(lang_totals):
    total = sum(lang_totals.values())
    items = []
    for lang, count in sorted(lang_totals.items(), key=lambda x: -x[1]):
        percent = count / total * 100 if total else 0
        items.append(f"<b>{lang}</b>: {percent:.1f}%")

    n = len(items)
    col_size = (n + 4) // 5  # 5 columns
    rows = [items[i*5:(i+1)*5] for i in range(col_size)]

    html = ["<table>"]
    html.append("<tr><th colspan='5' style='text-align:center;font-size:1.2em;'>Languages Statistics</th></tr>")
    for row in rows:
        html.append("<tr>")
        for cell in row:
            html.append(f"<td>{cell}</td>")
        # Fill empty cells if needed
        for _ in range(5 - len(row)):
            html.append("<td></td>")
        html.append("</tr>")
    html.append("</table>\n")
    return ''.join(html)

def main():
    repos = get_repos(GITHUB_USERNAME)
    md, lang_totals = generate_markdown_and_collect_totals(repos)
    summary = generate_totals_markdown(lang_totals)
    # Split repo tables into groups of 3 for grid layout
    repo_tables = md.split('\n<table')
    repo_tables = [('<table' + t) if i > 0 else t for i, t in enumerate(repo_tables) if t.strip()]
    grid_rows = [repo_tables[i:i+3] for i in range(0, len(repo_tables), 3)]
    grid_html = [f"<table style='margin:auto;display:block;width:{REPO_TABLE_WIDTH};height:{REPO_TABLE_HEIGHT};table-layout:fixed;'>"]
    grid_html.append("<tr><th colspan='3' style='text-align:center;font-size:1.2em;'>Repositories</th></tr><tr>")
    for row in grid_rows:
        for table in row:
            grid_html.append("<td style='width:33%;text-align:center;vertical-align:middle;padding-top:18px;padding-bottom:0;'>" + "<div style='display:inline-block;'>" + table + "</div></td>")
        # Fill empty cells if needed
        for _ in range(3 - len(row)):
            grid_html.append("<td style='width:33%;text-align:center;vertical-align:middle;padding-top:18px;padding-bottom:0;'></td>")
        grid_html.append("</tr><tr>")
    grid_html.append("</tr></table>")
    grid_html_str = ''.join(grid_html)
    with open("README.md", "w", encoding="utf-8") as f:
        # Use a very light bar or just extra space
        # Option 1: Just space
        # f.write(summary + "\n<br><br>\n" + grid_html_str)
        # Option 1: Just space
        # Center tables using margin:auto and display:block
        summary_centered = summary.replace('<table', "<table style='margin:auto;display:block;'", 1)
        # Do not override the style attribute for the repositories table
        grid_html_centered = grid_html_str
        f.write(summary_centered + "<br>" + grid_html_centered)
    print("README.md generated with totals and per-repo breakdown.")

if __name__ == "__main__":
    main()
