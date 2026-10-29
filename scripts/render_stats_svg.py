#!/usr/bin/env python3
"""
Render a GitHub stats card SVG from the GitHub GraphQL API, replacing the
third-party github-readme-stats service (its public instance is paused).

Needs GITHUB_TOKEN in the environment. Run by
.github/workflows/update-profile-art.yml.
"""
import json
import os
import urllib.request

HERE = os.path.dirname(__file__)
OUT_PATH = os.path.join(HERE, "..", "stats-card.svg")
LOGIN = "mahakaal2005"

BG = "#0d1117"
MUTED = "#7d8590"
TEXT = "#e6edf3"
ACCENT = "#10b981"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection { totalCommitContributions restrictedContributionsCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, REPOSITORY]) { totalCount }
    repositories(ownerAffiliations: OWNER, first: 100, isFork: false) {
      totalCount
      nodes { stargazerCount }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def stats(u):
    c = u["contributionsCollection"]
    return [
        ("Commits (last year)", c["totalCommitContributions"] + c["restrictedContributionsCount"]),
        ("Pull requests", u["pullRequests"]["totalCount"]),
        ("Issues", u["issues"]["totalCount"]),
        ("Repositories", u["repositories"]["totalCount"]),
        ("Stars earned", sum(n["stargazerCount"] for n in u["repositories"]["nodes"])),
        ("Contributed to", u["repositoriesContributedTo"]["totalCount"]),
    ]


def render(rows):
    w, h, top, step = 495, 195, 62, 22
    lines = []
    for i, (label, value) in enumerate(rows):
        y = top + i * step
        lines.append(
            f'<circle cx="32" cy="{y - 4}" r="3.5" fill="{ACCENT}"/>'
            f'<text x="46" y="{y}" class="l">{label}:</text>'
            f'<text x="300" y="{y}" class="v">{value:,}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>
.t {{ font: 600 18px 'Segoe UI', Ubuntu, sans-serif; fill: {ACCENT}; }}
.l {{ font: 600 14px 'Segoe UI', Ubuntu, sans-serif; fill: {TEXT}; }}
.v {{ font: 700 14px 'Segoe UI', Ubuntu, sans-serif; fill: {TEXT}; }}
.s {{ font: 400 11px 'Segoe UI', Ubuntu, sans-serif; fill: {MUTED}; }}
</style>
<rect width="{w}" height="{h}" rx="6" fill="{BG}"/>
<text x="25" y="34" class="t">Atul's GitHub Stats</text>
{''.join(lines)}
</svg>
"""


def main():
    svg = render(stats(fetch()))
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
