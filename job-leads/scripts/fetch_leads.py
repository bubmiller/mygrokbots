#!/usr/bin/env python3
"""Fetch raw job leads for Julie. Spec: job-leads/spec/hermes-sourcing-spec.md.

Hermes fetches and pushes. Julie scores. This script never applies, messages,
or logs in as Steve. LinkedIn is the public guest API only.

GitHub writes use HERMES_HOME/github_token (Steve authorized the broad token).
The token is never printed or committed.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

TZ = ZoneInfo("America/New_York")
REPO = "bubmiller/mygrokbots"
BRANCH = "main"
HERMES_HOME = Path(os.environ.get("HERMES_HOME") or Path.home() / "AppData/Local/hermes")
TOKEN_PATH = HERMES_HOME / "github_token"
LOCAL_ROOT = Path.home() / "job-leads"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
LINKEDIN_GAP = 1.5
SLOW_GAP = 6.0
CAREERS_GAP = 0.8
REQUEST_TIMEOUT = 20
CAREERS_BUDGET_S = 35 * 60
FRESH_DAYS = 7

# Spec section 1. Pages are LinkedIn start offsets, not page numbers.
CINCY = "location=Cincinnati%2C%20Ohio&distance=25"
REMOTE = "location=United%20States&f_WT=2"
CINCY_FULL = [
    "IT Manager",
    "IT Operations Manager",
    "Service Desk Manager",
    "Help Desk Manager",
    "Help Desk Supervisor",
    "End User Computing Manager",
    "Desktop Support Manager",
    "Infrastructure Manager",
    "IT Support Manager",
    "IT Site Lead",
    "Service Delivery Manager",
]
CINCY_SHORT = [
    "Service Desk Team Lead",
    "IT Director",
    "Technical Support Manager",
    "IT Infrastructure Manager",
    "ITSM Manager",
    "Information Technology Manager",
]
REMOTE_FULL = [
    "Service Desk Manager",
    "IT Operations Manager",
    "End User Services Manager",
    "Help Desk Manager",
    "IT Support Manager",
    "Service Delivery Manager IT",
]
TITLE_PHRASES = [
    "it manager",
    "it operations manager",
    "service desk manager",
    "help desk manager",
    "help desk supervisor",
    "service delivery manager",
    "end user computing",
    "desktop support manager",
    "infrastructure manager",
    "endpoint manager",
    "it support manager",
    "it site lead",
    "service desk team lead",
    "it director",
    "technical support manager",
    "it infrastructure manager",
    "itsm manager",
    "information technology manager",
    "end user services manager",
    "euc manager",
]
# Hosts whose Workday site id is not in the public URL. Others are probed.
WORKDAY_SITES = {
    "pg.wd5.myworkdayjobs.com": "1000",
    "dukeenergy.wd1.myworkdayjobs.com": "Search",
}
WORKDAY_GUESSES = ["External", "Search", "1000", "Careers", "Jobs"]

log = logging.getLogger("fetch_leads")


def now_et() -> datetime:
    return datetime.now(TZ)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(dt: datetime | None = None) -> str:
    dt = dt or now_utc()
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def redact(text: str) -> str:
    text = str(text).replace("\n", " ")
    text = re.sub(r"(api_key|key|access_token)=[^&\s]+", r"\1=[redacted]", text, flags=re.I)
    text = re.sub(r"(ghp_|github_pat_|gho_|sk-)[A-Za-z0-9._\-]+", "[redacted]", text)
    return text[:500]


def setup_logging() -> None:
    LOCAL_ROOT.joinpath("logs").mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        LOCAL_ROOT / "logs" / "fetch_leads.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.setLevel(logging.INFO)
    log.addHandler(handler)
    log.propagate = False


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_token() -> str:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        val = (os.environ.get(key) or "").strip()
        if val:
            return val
    if TOKEN_PATH.exists():
        return TOKEN_PATH.read_text(encoding="utf-8").strip()
    return ""


def title_matches(title: str) -> bool:
    text = re.sub(r"\s+", " ", (title or "").lower()).strip()
    if not text:
        return False
    if re.search(r"\beuc\b", text):
        return True
    for phrase in TITLE_PHRASES:
        if phrase in text:
            return True
    return False


def is_crocs(company: str, title: str = "", url: str = "") -> bool:
    blob = f"{company} {title} {url}".lower()
    return "crocs" in blob or "careers.crocs.com" in blob


def workplace_of(*parts: str, remote_query: bool = False) -> str:
    blob = " ".join(p or "" for p in parts).lower()
    if remote_query or re.search(r"\bremote\b", blob):
        return "remote"
    if "hybrid" in blob:
        return "hybrid"
    if any(parts):
        return "onsite"
    return "unknown"


def normalize_location(location: str) -> str:
    text = (location or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def make_id(source: str, source_job_id: str | None, company: str, title: str, location: str) -> str:
    if source_job_id:
        return f"{source}:{source_job_id}"
    digest = hashlib.sha1(
        f"{company.lower()}|{title.lower()}|{normalize_location(location)}".encode("utf-8")
    ).hexdigest()
    return digest


def snippet(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text[:500]


def parse_relative_date(text: str, today) -> str | None:
    raw = (text or "").strip().lower()
    if not raw:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        return raw
    if "today" in raw or "just posted" in raw or "hour" in raw:
        return today.isoformat()
    if "yesterday" in raw:
        return (today - timedelta(days=1)).isoformat()
    match = re.search(r"(\d+)\s+day", raw)
    if match:
        return (today - timedelta(days=int(match.group(1)))).isoformat()
    match = re.search(r"(\d+)\s+week", raw)
    if match:
        return (today - timedelta(days=7 * int(match.group(1)))).isoformat()
    return None


def within_window(posted: str | None, today) -> bool:
    if not posted:
        return True
    try:
        day = datetime.strptime(posted[:10], "%Y-%m-%d").date()
    except ValueError:
        return True
    return (today - day).days <= FRESH_DAYS


class HttpStats:
    def __init__(self) -> None:
        self.codes: dict[str, int] = {}
        self.errors: list[str] = []
        self.requests = 0

    def note(self, code, detail: str = "") -> None:
        key = str(code)
        self.codes[key] = self.codes.get(key, 0) + 1
        self.requests += 1
        if detail and (not str(code).isdigit() or int(code) >= 400):
            if len(self.errors) < 40:
                self.errors.append(redact(detail)[:240])

    def as_dict(self) -> dict:
        return {"requests": self.requests, "http_codes": self.codes, "errors": self.errors}


def save_raw(day: str, name: str, body: str) -> None:
    folder = LOCAL_ROOT / "raw" / day
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.html"
    path.write_text(body[:400_000], encoding="utf-8", errors="replace")


def prune_raw(today) -> None:
    root = LOCAL_ROOT / "raw"
    if not root.exists():
        return
    cutoff = today - timedelta(days=FRESH_DAYS)
    for child in root.iterdir():
        if not child.is_dir():
            continue
        try:
            day = datetime.strptime(child.name, "%Y-%m-%d").date()
        except ValueError:
            continue
        if day < cutoff:
            for item in child.iterdir():
                item.unlink(missing_ok=True)
            child.rmdir()


class Client:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        self._next = 0.0

    def _wait(self, gap: float) -> None:
        delay = self._next - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        self._next = time.monotonic() + gap

    def request(self, method: str, url: str, *, gap: float, stats: HttpStats, **kwargs):
        self._wait(gap)
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.RequestException as exc:
            stats.note(type(exc).__name__, f"{method} {urlparse(url).netloc} {exc}")
            return None
        stats.note(response.status_code, f"{method} {urlparse(url).netloc} {response.status_code}")
        return response


def linkedin_queries(limit: int | None) -> list[tuple[str, str, str, int, bool]]:
    planned: list[tuple[str, str, str, int, bool]] = []
    for keyword in CINCY_FULL:
        for start in (0, 25, 50):
            planned.append((keyword, CINCY, "Cincinnati, Ohio", start, False))
    for keyword in CINCY_SHORT:
        for start in (0, 25):
            planned.append((keyword, CINCY, "Cincinnati, Ohio", start, False))
    for keyword in REMOTE_FULL:
        for start in (0, 25, 50):
            planned.append((keyword, REMOTE, "United States remote", start, True))
    if limit is not None:
        return planned[:limit]
    return planned


def parse_linkedin_html(html: str, query: str, remote_query: bool, today) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.select("div.base-search-card"):
        urn = card.get("data-entity-urn") or ""
        match = re.search(r"jobPosting:(\d+)", urn)
        job_id = match.group(1) if match else ""
        title_el = card.select_one("h3")
        company_el = card.select_one("h4")
        loc_el = card.select_one("span.job-search-card__location")
        time_el = card.select_one("time")
        link = card.select_one("a.base-card__full-link")
        title = title_el.get_text(" ", strip=True) if title_el else ""
        company = company_el.get_text(" ", strip=True) if company_el else ""
        location = loc_el.get_text(" ", strip=True) if loc_el else ""
        if not title or is_crocs(company, title):
            continue
        posted = None
        if time_el is not None:
            posted = (time_el.get("datetime") or "")[:10] or parse_relative_date(
                time_el.get_text(" ", strip=True), today
            )
        href = ""
        if link and link.get("href"):
            href = link["href"].split("?")[0]
        if job_id and not href:
            href = f"https://www.linkedin.com/jobs/view/{job_id}"
        source = "linkedin"
        rows.append(
            {
                "source": source,
                "source_job_id": job_id or None,
                "title": title,
                "company": company,
                "location": location,
                "workplace": workplace_of(location, remote_query=remote_query),
                "url": href,
                "posted_date": posted,
                "salary": None,
                "query": query,
                "raw_snippet": snippet(card.get_text(" ", strip=True)),
            }
        )
    return rows


def fetch_linkedin(client: Client, today, day: str, limit: int | None) -> tuple[list[dict], dict]:
    stats = HttpStats()
    rows: list[dict] = []
    failed: list[tuple] = []
    queries = linkedin_queries(limit)

    def one(item, gap: float) -> None:
        keyword, geo, label, start, remote_query = item
        url = (
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={quote(keyword)}&{geo}&f_TPR=r604800&start={start}"
        )
        response = client.request("GET", url, gap=gap, stats=stats, headers={"Accept": "text/html"})
        if response is None:
            failed.append(item)
            return
        if response.status_code == 429:
            failed.append(item)
            return
        if response.status_code != 200:
            return
        save_raw(day, f"linkedin-{keyword}-{start}".replace(" ", "_"), response.text)
        query = f"{keyword} | {label}"
        rows.extend(parse_linkedin_html(response.text, query, remote_query, today))

    for item in queries:
        one(item, LINKEDIN_GAP)
    for _pass in range(2):
        if not failed:
            break
        pending, failed = failed, []
        log.info("LinkedIn slow pass %s for %s urls", _pass + 1, len(pending))
        time.sleep(20)
        for item in pending:
            one(item, SLOW_GAP)
    summary = stats.as_dict()
    summary["rows"] = len(rows)
    summary["queries"] = len(queries)
    summary["unresolved_429"] = len(failed)
    return rows, summary


def search_credentials() -> tuple[str, str, str] | None:
    serp = (os.environ.get("SERPAPI_KEY") or os.environ.get("SERPAPI_API_KEY") or "").strip()
    if not serp and (HERMES_HOME / "serpapi_key").exists():
        serp = (HERMES_HOME / "serpapi_key").read_text(encoding="utf-8").strip()
    if serp:
        return ("serpapi", serp, "")
    key = (os.environ.get("GOOGLE_CSE_KEY") or "").strip()
    cx = (os.environ.get("GOOGLE_CSE_ID") or os.environ.get("GOOGLE_CSE_CX") or "").strip()
    key_file = HERMES_HOME / "google_cse_key"
    cx_file = HERMES_HOME / "google_cse_cx"
    if not key and key_file.exists():
        key = key_file.read_text(encoding="utf-8").strip()
    if not cx and cx_file.exists():
        cx = cx_file.read_text(encoding="utf-8").strip()
    if key and cx:
        return ("cse", key, cx)
    return None


def first_site(hint: str) -> str:
    match = re.search(r"site:([^\s/]+)", hint or "")
    return match.group(1) if match else ""


def fetch_google(client: Client, employers: list[dict], today) -> tuple[list[dict], dict]:
    creds = search_credentials()
    if not creds:
        return [], {"rows": 0, "skipped": "no_search_api_key"}
    kind, key, cx = creds
    stats = HttpStats()
    rows = []
    keyword = (
        '("IT Manager" OR "Service Desk Manager" OR "Help Desk Manager" '
        'OR "Infrastructure Manager" OR "IT Support Manager")'
    )
    for employer in employers:
        domain = first_site(employer["site_hint"]) or urlparse(employer["careers_url"]).netloc
        if not domain:
            continue
        q = f"site:{domain}/careers OR site:{domain}/jobs {keyword}"
        if kind == "serpapi":
            response = client.request(
                "GET",
                "https://serpapi.com/search.json",
                gap=1.0,
                stats=stats,
                params={"engine": "google", "q": q, "tbs": "qdr:w", "api_key": key},
            )
            organic = (response.json().get("organic_results") or []) if response and response.ok else []
        else:
            response = client.request(
                "GET",
                "https://www.googleapis.com/customsearch/v1",
                gap=1.0,
                stats=stats,
                params={"key": key, "cx": cx, "q": q, "dateRestrict": "w1"},
            )
            organic = (response.json().get("items") or []) if response and response.ok else []
        for item in organic:
            title = item.get("title") or ""
            url = item.get("link") or ""
            if not title_matches(title) or is_crocs(employer["employer"], title, url):
                continue
            rows.append(
                {
                    "source": "google",
                    "source_job_id": None,
                    "title": title,
                    "company": employer["employer"],
                    "location": "",
                    "workplace": workplace_of(title, item.get("snippet") or ""),
                    "url": url,
                    "posted_date": None,
                    "salary": None,
                    "query": f"site:{domain} | past week",
                    "raw_snippet": snippet(item.get("snippet") or title),
                }
            )
    summary = stats.as_dict()
    summary["rows"] = len(rows)
    summary["provider"] = kind
    summary["date"] = today.isoformat()
    return rows, summary


def load_employers() -> list[dict]:
    path = repo_root() / "job-leads" / "employers.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def blocked(text: str) -> bool:
    low = text.lower()
    return "just a moment" in low or "cf-browser-verification" in low or "authenticating..." in low


def workday_jobs(client: Client, employer: dict, stats: HttpStats, today) -> list[dict]:
    host = urlparse(employer["careers_url"]).netloc
    tenant = host.split(".")[0]
    site = WORKDAY_SITES.get(host)
    if not site:
        for guess in WORKDAY_GUESSES:
            url = f"https://{host}/wday/cxs/{tenant}/{guess}/jobs"
            response = client.request(
                "POST",
                url,
                gap=CAREERS_GAP,
                stats=stats,
                json={"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": "IT Manager"},
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
            if response is not None and response.status_code == 200 and "jobPostings" in response.text:
                site = guess
                WORKDAY_SITES[host] = guess
                break
    if not site:
        stats.errors.append(f"{employer['employer']}: workday site id not found")
        return []
    found = []
    seen = set()
    for term in ("IT Manager", "Service Desk", "Help Desk"):
        response = client.request(
            "POST",
            f"https://{host}/wday/cxs/{tenant}/{site}/jobs",
            gap=CAREERS_GAP,
            stats=stats,
            json={"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": term},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        if response is None or response.status_code != 200:
            continue
        for job in response.json().get("jobPostings") or []:
            title = job.get("title") or ""
            req = ""
            bullets = job.get("bulletFields") or []
            if bullets:
                req = str(bullets[0])
            key = req or job.get("externalPath") or title
            if key in seen or not title_matches(title):
                continue
            posted = parse_relative_date(job.get("postedOn") or "", today)
            if not within_window(posted, today):
                continue
            seen.add(key)
            path = job.get("externalPath") or ""
            url = f"https://{host}/en-US/{site}{path}" if path else employer["careers_url"]
            location = job.get("locationsText") or ""
            found.append(
                {
                    "source": f"careers:{employer['employer']}",
                    "source_job_id": req or None,
                    "title": title,
                    "company": employer["employer"],
                    "location": location,
                    "workplace": workplace_of(location),
                    "url": url,
                    "posted_date": posted,
                    "salary": None,
                    "query": f"workday:{term}",
                    "raw_snippet": snippet(f"{title} {location} {job.get('postedOn') or ''}"),
                }
            )
    return found


def greenhouse_board(employer: dict) -> str:
    for text in (employer["careers_url"], employer["site_hint"]):
        match = re.search(r"greenhouse\.io/([A-Za-z0-9_\-]+)", text or "")
        if match:
            return match.group(1)
    return ""


def greenhouse_jobs(client: Client, employer: dict, stats: HttpStats, today) -> list[dict]:
    board = greenhouse_board(employer)
    if not board:
        return []
    response = client.request(
        "GET",
        f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs",
        gap=CAREERS_GAP,
        stats=stats,
        headers={"Accept": "application/json"},
    )
    if response is None or response.status_code != 200:
        return []
    found = []
    for job in response.json().get("jobs") or []:
        title = job.get("title") or ""
        if not title_matches(title) or is_crocs(employer["employer"], title):
            continue
        updated = (job.get("updated_at") or "")[:10]
        if updated and not within_window(updated, today):
            continue
        location = ((job.get("location") or {}).get("name")) or ""
        req = job.get("requisition_id")
        if req in (None, "", "--"):
            req = str(job.get("id") or "") or None
        found.append(
            {
                "source": f"careers:{employer['employer']}",
                "source_job_id": str(req) if req else None,
                "title": title,
                "company": employer["employer"],
                "location": location,
                "workplace": workplace_of(location),
                "url": job.get("absolute_url") or employer["careers_url"],
                "posted_date": updated or None,
                "salary": None,
                "query": f"greenhouse:{board}",
                "raw_snippet": snippet(f"{title} {location}"),
            }
        )
    return found


def html_jobs(client: Client, employer: dict, stats: HttpStats, day: str) -> list[dict]:
    url = employer["careers_url"]
    response = client.request("GET", url, gap=CAREERS_GAP, stats=stats, headers={"Accept": "text/html"})
    if response is None:
        return []
    if response.status_code in (401, 403) or blocked(response.text):
        stats.errors.append(f"{employer['employer']}: blocked {response.status_code}")
        return []
    if response.status_code != 200:
        return []
    save_raw(day, f"careers-{employer['n']}", response.text)
    soup = BeautifulSoup(response.text, "html.parser")
    found = []
    seen = set()
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or "")
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict) or item.get("@type") != "JobPosting":
                continue
            title = item.get("title") or ""
            if not title_matches(title):
                continue
            job_url = item.get("url") or url
            if job_url in seen:
                continue
            seen.add(job_url)
            location = ""
            loc = item.get("jobLocation")
            if isinstance(loc, dict):
                address = loc.get("address") or {}
                if isinstance(address, dict):
                    location = address.get("addressLocality") or ""
            found.append(_html_row(employer, title, job_url, location, item.get("datePosted")))
    for link in soup.select("a[href]"):
        title = link.get_text(" ", strip=True)
        if not title_matches(title):
            continue
        job_url = urljoin(response.url, link["href"])
        if job_url in seen:
            continue
        seen.add(job_url)
        found.append(_html_row(employer, title, job_url, "", None))
    return found


def _html_row(employer: dict, title: str, url: str, location: str, posted) -> dict:
    posted_s = str(posted)[:10] if posted else None
    return {
        "source": f"careers:{employer['employer']}",
        "source_job_id": None,
        "title": title,
        "company": employer["employer"],
        "location": location,
        "workplace": workplace_of(location, title),
        "url": url,
        "posted_date": posted_s,
        "salary": None,
        "query": "careers-page",
        "raw_snippet": snippet(f"{title} {location}"),
    }


def fetch_careers(client: Client, employers: list[dict], today, day: str) -> tuple[list[dict], dict]:
    stats = HttpStats()
    rows = []
    deferred = []
    deadline = time.monotonic() + CAREERS_BUDGET_S
    checked = 0
    for employer in employers:
        if is_crocs(employer["employer"], url=employer["careers_url"]):
            continue
        if time.monotonic() > deadline:
            deferred.append(employer["employer"])
            continue
        checked += 1
        host = urlparse(employer["careers_url"]).netloc
        try:
            if "myworkdayjobs.com" in host:
                rows.extend(workday_jobs(client, employer, stats, today))
            elif greenhouse_board(employer):
                rows.extend(greenhouse_jobs(client, employer, stats, today))
            else:
                rows.extend(html_jobs(client, employer, stats, day))
        except Exception as exc:
            stats.errors.append(redact(f"{employer['employer']}: {exc}"))
            log.exception("careers %s", employer["employer"])
    summary = stats.as_dict()
    summary["rows"] = len(rows)
    summary["employers_checked"] = checked
    summary["employers_deferred"] = deferred
    return rows, summary


def github_headers(token: str, raw: bool = False) -> dict:
    accept = "application/vnd.github.raw" if raw else "application/vnd.github+json"
    return {
        "Authorization": f"Bearer {token}",
        "Accept": accept,
        "User-Agent": "hermes-job-leads",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def github_json(method: str, path: str, token: str, payload: dict | None = None):
    response = requests.request(
        method,
        f"https://api.github.com{path}",
        headers={**github_headers(token), "Content-Type": "application/json"},
        data=None if payload is None else json.dumps(payload),
        timeout=40,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"GitHub {method} {path} {response.status_code} {redact(response.text)}")
    if not response.text:
        return {}
    return response.json()


def prior_ids(token: str, today) -> set[str]:
    ids: set[str] = set()
    if not token:
        return ids
    try:
        listing = github_json("GET", f"/repos/{REPO}/contents/job-leads?ref={BRANCH}", token)
    except Exception as exc:
        log.warning("prior list failed: %s", redact(exc))
        return ids
    if not isinstance(listing, list):
        return ids
    cutoff = today - timedelta(days=FRESH_DAYS)
    for item in listing:
        name = item.get("name") or ""
        match = re.fullmatch(r"(\d{4}-\d{2}-\d{2})\.jsonl", name)
        if not match:
            continue
        day = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        if day < cutoff or day > today:
            continue
        try:
            response = requests.get(
                item.get("download_url") or item["url"],
                headers=github_headers(token),
                timeout=40,
            )
            response.raise_for_status()
        except Exception as exc:
            log.warning("prior file %s failed: %s", name, redact(exc))
            continue
        for line in response.text.splitlines():
            if not line.strip():
                continue
            try:
                ids.add(json.loads(line)["id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return ids


def stamp_rows(rows: list[dict], seen: set[str]) -> list[dict]:
    stamped = []
    fetched = iso_utc()
    for row in rows:
        row = dict(row)
        row_id = make_id(
            row["source"], row.get("source_job_id"), row.get("company") or "", row.get("title") or "", row.get("location") or ""
        )
        row["id"] = row_id
        row["seen_before"] = row_id in seen
        row["fetched_at"] = fetched
        seen.add(row_id)
        stamped.append(row)
    return stamped


def github_commit(token: str, files: dict[str, str], message: str) -> str:
    last_error = ""
    for _attempt in range(3):
        ref = github_json("GET", f"/repos/{REPO}/git/ref/heads/{BRANCH}", token)
        parent = ref["object"]["sha"]
        commit = github_json("GET", f"/repos/{REPO}/git/commits/{parent}", token)
        tree_items = []
        for path, content in files.items():
            blob = github_json(
                "POST",
                f"/repos/{REPO}/git/blobs",
                token,
                {"content": base64.b64encode(content.encode("utf-8")).decode("ascii"), "encoding": "base64"},
            )
            tree_items.append({"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        tree = github_json(
            "POST",
            f"/repos/{REPO}/git/trees",
            token,
            {"base_tree": commit["tree"]["sha"], "tree": tree_items},
        )
        new = github_json(
            "POST",
            f"/repos/{REPO}/git/commits",
            token,
            {"message": message, "tree": tree["sha"], "parents": [parent]},
        )
        try:
            github_json(
                "PATCH",
                f"/repos/{REPO}/git/refs/heads/{BRANCH}",
                token,
                {"sha": new["sha"]},
            )
            return new["sha"]
        except Exception as exc:
            last_error = redact(exc)
            log.warning("ref update raced: %s", last_error)
            time.sleep(2)
    raise RuntimeError(last_error or "GitHub ref update failed")


def source_names(rows: list[dict]) -> str:
    names = []
    for row in rows:
        source = row["source"]
        label = "careers" if source.startswith("careers:") else source
        if label not in names:
            names.append(label)
    return ", ".join(names) if names else "none"


def write_local(day: str, jsonl: str, status: str) -> None:
    folder = LOCAL_ROOT / "out"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{day}.jsonl").write_text(jsonl, encoding="utf-8")
    (folder / f"{day}.status.json").write_text(status, encoding="utf-8")


def self_test() -> int:
    html = """
    <div class="base-search-card" data-entity-urn="urn:li:jobPosting:4477492958">
      <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/staff-site-it-manager-at-ge-aerospace-4477492958?position=1"></a>
      <h3 class="base-search-card__title">Staff Site IT Manager</h3>
      <h4>GE Aerospace</h4>
      <span class="job-search-card__location">Cincinnati, OH</span>
      <time datetime="2026-10-09">6 days ago</time>
    </div>
    """
    rows = parse_linkedin_html(html, "IT Manager | Cincinnati, Ohio", False, datetime(2026, 10, 14).date())
    assert len(rows) == 1, rows
    assert rows[0]["source_job_id"] == "4477492958"
    assert rows[0]["title"] == "Staff Site IT Manager"
    assert rows[0]["posted_date"] == "2026-10-09"
    assert title_matches("Service Desk Manager")
    assert not title_matches("Accounting Co-op")
    assert is_crocs("Crocs")
    employers = load_employers()
    assert len(employers) == 100, len(employers)
    print("self-test ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch raw job leads and push JSONL to GitHub.")
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--max-linkedin", type=int, default=None)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--careers", action="store_true", help="Force the careers pass")
    parser.add_argument("--no-careers", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()

    setup_logging()
    prune_raw(now_et().date())
    started = now_et()
    day = started.date()
    day_s = day.isoformat()
    careers_day = started.weekday() in (1, 3)
    if args.careers:
        careers_day = True
    if args.no_careers:
        careers_day = False
    log.info("start %s careers=%s", day_s, careers_day)

    status: dict = {
        "date": day_s,
        "timezone": "America/New_York",
        "weekday": started.strftime("%A"),
        "started_at": started.isoformat(),
        "careers_pass": careers_day,
        "sources": {},
    }
    rows: list[dict] = []
    client = Client()
    try:
        linkedin_rows, linkedin_status = fetch_linkedin(client, day, day_s, args.max_linkedin)
        status["sources"]["linkedin"] = linkedin_status
        rows.extend(linkedin_rows)
        if careers_day:
            employers = load_employers()
            google_rows, google_status = fetch_google(client, employers, day)
            careers_rows, careers_status = fetch_careers(client, employers, day, day_s)
        else:
            google_rows, google_status = [], {"rows": 0, "skipped": "not_tue_thu"}
            careers_rows, careers_status = [], {"rows": 0, "skipped": "not_tue_thu", "employers_checked": 0}
        status["sources"]["google"] = google_status
        status["sources"]["careers"] = careers_status
        status["sources"]["dice"] = {"rows": 0, "skipped": "no_api"}
        rows.extend(google_rows)
        rows.extend(careers_rows)
    except Exception as exc:
        status["fatal"] = redact(exc)
        log.exception("fetch failed")

    token = load_token()
    seen = prior_ids(token, day)
    stamped = stamp_rows(rows, seen)
    jsonl = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in stamped)
    ended = now_et()
    status["ended_at"] = ended.isoformat()
    status["rows"] = len(stamped)
    status_text = json.dumps(status, indent=2)
    write_local(day_s, jsonl, status_text)

    attempted = []
    for name, info in status["sources"].items():
        if info.get("skipped"):
            continue
        attempted.append(info.get("rows") or 0)
    all_empty = bool(attempted) and all(count == 0 for count in attempted) and not status.get("fatal")
    if all_empty:
        print(
            f"Job leads {day_s}: every source came back empty. "
            f"Status is job-leads/{day_s}.status.json in bubmiller/mygrokbots."
        )

    if args.no_push:
        log.info("no-push rows=%s", len(stamped))
        return 0
    if not token:
        log.error("GitHub token missing at %s", TOKEN_PATH.name)
        print("Job leads push failed: GitHub token file is missing.")
        return 1

    message = f"leads: {day_s} ({len(stamped)} rows, {source_names(stamped)})"
    files = {
        f"job-leads/{day_s}.jsonl": jsonl,
        f"job-leads/{day_s}.status.json": status_text + "\n",
    }
    try:
        sha = github_commit(token, files, message)
        log.info("pushed %s", sha)
        return 0
    except Exception as exc:
        log.error("push failed: %s", redact(exc))
        status["push_error"] = redact(exc)
        try:
            github_commit(
                token,
                {f"job-leads/{day_s}.status.json": json.dumps(status, indent=2) + "\n"},
                f"leads: {day_s} (status only, push failed)",
            )
        except Exception as inner:
            log.error("status push failed: %s", redact(inner))
        print(f"Job leads {day_s}: GitHub push failed. Local copy is in ~/job-leads/out.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
