
import requests
import re
import os
from collections import defaultdict

GITHUB_USERNAME = "nunonogueir444"
GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

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
        total = sum(languages.values())
        md.append(f"\n### [{name}]({html_url})\n")
        if total == 0:
            md.append("No code detected.\n")
            continue
        md.append("| Language | Lines | Percent |\n|---|---:|---:|\n")
        for lang, lines in sorted(languages.items(), key=lambda x: -x[1]):
            percent = lines / total * 100
            md.append(f"| {lang} | {lines} | {percent:.1f}% |\n")
            lang_totals[lang] += lines
    return ''.join(md), lang_totals

def generate_totals_markdown(lang_totals):
    total_lines = sum(lang_totals.values())
    summary = ["| Language | Total Lines | Percent |\n|---|---:|---:|\n"]
    for lang, count in sorted(lang_totals.items(), key=lambda x: -x[1]):
        percent = count / total_lines * 100 if total_lines else 0
        summary.append(f"| {lang} | {count} | {percent:.1f}% |\n")
    return ''.join(summary)

def main():
    repos = get_repos(GITHUB_USERNAME)
    md, lang_totals = generate_markdown_and_collect_totals(repos)
    summary = generate_totals_markdown(lang_totals)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(summary + "\n" + md)
    print("README.md generated with totals and per-repo breakdown.")

if __name__ == "__main__":
    main()
