#!/usr/bin/env python3
"""
Self-research module — lets the agent research a topic and feed its own
knowledge base, growing its knowledge automatically.

Design:
    research(topic, urls, source):
        - fetch each URL, extract clean text
        - write a sourced Markdown doc to knowledge/auto/<topic>.md
        - mark memory so the agent knows the topic exists
        - ingest the new doc into the KB index

Auto-job:
    The agent can run `research` on-demand (you ask it to). If you also want it
    to actively go learn new things every so often, call the auto-job on a
    schedule (e.g. cron) — see run_auto().

URL-fetch only: it does NOT have a search-engine API key, so it can only learn
from URLs you (or your cron seeds) provide. Point it at the canonical docs /
homepages you care about.

Note: this only fetches URLs the user authorizes. It won't scrape the open web
on its own — that way it can't wander off and pull whatever it wants.
"""
import html
import re
import sys
import urllib.parse
import urllib.robotparser
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

from knowledge import kb_ingest, kb_search

load_dotenv()

AUTO_DIR = Path("knowledge/auto")
FETCH_TIMEOUT = 15      # seconds per URL
MAX_FETCH_CHARS = 40000  # max characters to keep from one page
DEFAULT_MAX_URLS = 5

# We never follow URLs that point somewhere we're not allowed to learn from.
_BLOCKED_HOSTS = {
    "localhost", "127.0.0.1", "::1", "10.", "192.168.", "172.16.", "0.0.0.0",
}
_USER_AGENT = "self-research-local/1.0"


# ---------------------------------------------------------------------------
# URL allow / fetch
# ---------------------------------------------------------------------------

def _is_allowed(url: str) -> tuple[bool, str]:
    """Allow only http(s) public URLs (local content blocked / SSRF-safe)."""
    try:
        parts = urllib.parse.urlsplit(url)
    except Exception:
        return False, "not a valid URL"
    if parts.scheme not in ("http", "https"):
        return False, "only http/https URLs are allowed"
    host = (parts.hostname or "").lower()
    if not host:
        return False, "missing host"
    if host in _BLOCKED_HOSTS or any(host.startswith(p) for p in _BLOCKED_HOSTS):
        return False, "local/private hosts are blocked"
    return True, ""


def _robots_allows(url: str) -> bool:
    """Respect robots.txt when possible (best-effort). Fetches robots.txt with
    our own requests client (urllib's read() can mis-request on some hosts) and
    checks the '*'' wildcard rule the standard expects."""
    try:
        parts = urllib.parse.urlsplit(url)
        robots_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))
        resp = requests.get(robots_url, headers={"User-Agent": _USER_AGENT}, timeout=FETCH_TIMEOUT)
        if resp.status_code == 404:
            return True  # no robots.txt -> nothing disallowed
        if resp.status_code >= 400:
            return True
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(resp.text.splitlines())
        return rp.can_fetch("*", url)
    except Exception:
        return True  # if we can't read robots, be permissive (static content)


def _fetch_text(url: str) -> str:
    """Fetch a URL and return clean text. Raises on hard failure."""
    ok, why = _is_allowed(url)
    if not ok:
        raise ValueError(f"URL blocked: {why} ({url})")
    if not _robots_allows(url):
        raise ValueError(f"robots.txt disallows {url}")
    resp = requests.get(url, headers={"User-Agent": _USER_AGENT}, timeout=FETCH_TIMEOUT)
    resp.raise_for_status()
    ctype = resp.headers.get("Content-Type", "")
    if "html" in ctype:
        return _html_to_text(resp.text)
    return resp.text


def _html_to_text(raw: str) -> str:
    """Very small HTML→markdown-ish text extractor. No deps, good enough for
    docs and summaries. Keeps headings, links text, paragraphs."""
    # strip scripts/styles
    raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    # headings
    raw = re.sub(r"(?i)<h([1-6])[^>]*>(.*?)</h\1>", lambda m: "\n\n## " + _clean(m.group(2)) + "\n", raw)
    # links -> text (so we keep the readable label, not the URL)
    raw = re.sub(r"(?is)<a[^>]*>(.*?)</a>", lambda m: _clean(m.group(1)), raw)
    # paragraphs / list items / br -> newlines
    raw = re.sub(r"(?is)<(p|div|li|br|tr)[^>]*>", "\n", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)          # drop remaining tags
    text = html.unescape(raw)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def _clean(s: str) -> str:
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------------------
# Document writing
# ---------------------------------------------------------------------------

def _slug(topic: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return s or "topic"


def _write_doc(topic: str, fetched: list[tuple[str, str, str]]) -> Path:
    AUTO_DIR.mkdir(parents=True, exist_ok=True)
    path = AUTO_DIR / f"{_slug(topic)}.md"
    lines = [
        f"# Research: {topic}",
        "",
        f"> Auto-researched on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "> Fetched from source URLs below. Content is unedited extracts.",
        "",
    ]
    for url, source, text in fetched:
        lines.append(f"## Source: {url}")
        if source:
            lines.append(f"**Title/tag:** {source}")
        lines.append("")
        lines.append(text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def research(topic: str, urls: list[str] | None = None, source: str = "") -> dict:
    """Fetch the given URLs, save them as a knowledge doc, and ingest it.
    Returns a summary of what was added."""
    urls = (urls or [])[:DEFAULT_MAX_URLS]
    if not urls:
        return {"error": "No URLs provided. Pass the list of URLs to research."}

    fetched: list[tuple[str, str, str]] = []
    errors: list[dict] = []
    for u in urls:
        try:
            text = _fetch_text(u)[:MAX_FETCH_CHARS]
            fetched.append((u, source, text))
        except Exception as e:
            errors.append({"url": u, "error": str(e)})

    if not fetched:
        return {"error": "No source pages could be fetched", "errors": errors}

    path = _write_doc(topic, fetched)
    ingest = kb_ingest(str(path))

    # Also record the topic in memory so the agent recalls it long-term.
    try:
        from memory import remember_fact
        remember_fact("topic:" + _slug(topic), datetime.now().strftime("%Y-%m-%d") + " | " + ", ".join(u for u, _, _ in fetched))
    except Exception:
        pass

    return {
        "status": "researched",
        "topic": topic,
        "doc": str(path),
        "sources": [u for u, _, _ in fetched],
        "ingest": ingest,
        "errors": errors,
        "note": "Saved to knowledge and added to your KB. Ask me about this topic anytime.",
    }


def run_auto(topics: list[str], urls_by_topic: dict[str, list[str] | None] | None = None) -> dict:
    """Scheduled auto-research: for each topic, if we have seed URLs, fetch and
    ingest. If only the topic is given (no seed URLs), it skips (URL-fetch only
    can't discover URLs by itself) UNLESS a seed URL is provided.
    Returns a per-topic report."""
    urls_by_topic = urls_by_topic or {}
    results = {}
    for topic in topics:
        urls = urls_by_topic.get(topic)
        if not urls:
            results[topic] = {
                "skipped": True,
                "reason": "no seed URLs for this topic (URL-fetch research needs at least one URL)",
            }
            continue
        results[topic] = research(topic, urls)
    return {"auto_run": True, "topics": results}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_seeds() -> dict:
    seeds_path = Path("knowledge/research_seeds.json")
    if not seeds_path.exists():
        return {"topics": []}
    import json as _json
    data = _json.loads(seeds_path.read_text(encoding="utf-8"))
    topics = [t["topic"] for t in data.get("topics", [])]
    urls = {t["topic"]: t.get("urls") for t in data.get("topics", [])}
    return {"topics": topics, "urls_by_topic": urls}


def _cli() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "research":
        topic = sys.argv[2] if len(sys.argv) > 2 else "topic"
        urls = sys.argv[3:] or None
        import json as _json
        print(_json.dumps(research(topic, urls), indent=2, default=str))
    elif cmd == "auto":
        # Re-run every seeded topic. For cron/systemd auto-learning.
        import json as _json
        seeds = _load_seeds()
        report = run_auto(seeds["topics"], seeds["urls_by_topic"])
        print(_json.dumps(report, indent=2, default=str))
    elif cmd == "fetch":
        # one-off: just return clean text of a URL (sanity check)
        url = sys.argv[2]
        print(_fetch_text(url)[:2000])
    else:
        print("usage:")
        print("  research.py research '<topic>' <url1> [url2 ...]   -> learn a topic now")
        print("  research.py auto                                   -> re-run seeded topics")
        print("  research.py fetch <url>")


if __name__ == "__main__":
    _cli()