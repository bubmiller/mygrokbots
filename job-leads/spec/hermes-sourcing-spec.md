# Hermes raw-sourcing script — spec (draft 2026-10-14)

**Goal:** move raw lead fetching off Julie's box onto Hermes (Steve's machine). Hermes fetches and pushes raw leads; Julie scores, dedupes, and packages. Nothing on Hermes applies, messages, or logs in anywhere as Steve. (Spec only. Julie has not touched Hermes.)

## 1. What it fetches (7-day window everywhere)
- **LinkedIn public guest API**, no login: `https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=<kw>&<geo>&f_TPR=r604800&start=<0|25|50>`
  - Cincy geo `location=Cincinnati%2C%20Ohio&distance=25`, pages 0/25/50: IT Manager, IT Operations Manager, Service Desk Manager, Help Desk Manager, Help Desk Supervisor, End User Computing Manager, Desktop Support Manager, Infrastructure Manager, IT Support Manager, IT Site Lead, Service Delivery Manager.
  - Cincy geo, pages 0/25 only: Service Desk Team Lead, IT Director, Technical Support Manager, IT Infrastructure Manager, ITSM Manager, Information Technology Manager.
  - Remote US `location=United%20States&f_WT=2`, pages 0/25/50: Service Desk Manager, IT Operations Manager, End User Services Manager, Help Desk Manager, IT Support Manager, Service Delivery Manager IT.
  - Never `r3600`. Wait ≥1–2 s between requests and back off on 429 (retry at most 2 slow passes). Optional: fetch `jobs-guest/jobs/api/jobPosting/<id>` for new IDs only.
- **Google `site:` careers searches** (past week, `tbs=qdr:w`) using the playbook §5 patterns and §7 title-keyword string. Use a search API with its own key (e.g. Google Programmable Search or SerpAPI). Do not scrape google.com.
- **Top-100 Cincy Metro careers crawl, Tue/Thu only (ET):** for each playbook §7 employer, hit the preferred ATS (Workday CXS JSON, Phenom, Oracle HCM, iCIMS, Greenhouse/Lever JSON where available) and filter by the §7 title keywords. Read the list from a checked-in `job-leads/employers.csv` exported from §7 so the script and playbook stay in sync.
- **Dice:** optional, only if Steve has a legit API/feed. Otherwise Julie keeps doing Dice via Composio.
- **Not included:** Indeed and ZipRecruiter (dropped 2026-10-14: bot walls 401/403/Cloudflare), Gmail (Emily forwards job mail), and anything Crocs.

## 2. Output
- **File:** `job-leads/YYYY-MM-DD.jsonl` (ET date) in the GitHub repo `bubmiller/mygrokbots`, one commit per run (`leads: YYYY-MM-DD (n rows, sources…)`). Add `job-leads/YYYY-MM-DD.status.json` with per-source counts, HTTP codes, errors, and the run start and end times.
- **JSONL row:** `id, source (linkedin|google|careers:<employer>|dice), source_job_id, title, company, location, workplace (onsite|hybrid|remote|unknown), url (prefer the employer ATS URL), posted_date (ISO or null), salary (raw string or null), query (keywords+geo), fetched_at (ISO UTC), raw_snippet (≤500 chars)`.
- **`id`/dedupe key:** `<source>:<source_job_id>` when there is a native ID (LinkedIn job ID, ATS req ID). Otherwise use `sha1(lower(company)|lower(title)|normalized location)`. Dedupe within the run and against the previous 7 days of files, but keep a `seen_before` boolean instead of dropping rows.
- No raw HTML in the repo. Keep it local on Hermes for 7 days for debugging.

## 3. Schedule
- Weekdays ~**8:30 AM ET** so the push lands before Julie's 9:00 AM scan. The careers crawl runs only when the ET weekday is Tue or Thu. It may start ~8:00 AM on those days because it is slower.
- If a run fails, still push the status file so Julie can see it.

## 4. What Steve sets up on Hermes
- **Runtime:** Python 3.11+ (`requests`, `beautifulsoup4`) in a venv, with the script checked into the repo under `job-leads/scripts/`.
- **Scheduler:** cron, launchd, or Task Scheduler, with the TZ set to America/New_York (or converted correctly).
- **GitHub:** a fine-grained PAT (or deploy key) scoped to `bubmiller/mygrokbots` only, with Contents read/write. Store it in the OS keychain or an env file outside the repo, never committed.
- **Search API key** for Google `site:` queries, if used.
- **LinkedIn:** guest endpoints only. No logged-in session, cookies, or Steve's account (risk of account restriction). Expect 429s and accept partial coverage.
- **Logging:** a rotating local log (`~/job-leads/logs/`) plus the pushed status.json. Optional: send an email/Telegram alert to Steve if 0 rows come back from all sources.

## 5. What Julie does after (9 AM scan)
Read today's JSONL and status.json from the repo, then:
1. Dedupe against all prior scans/digests, the Google Sheet (source of truth), and the keep-offs.
2. Verify promising leads on the employer ATS.
3. Score them Strong/Medium/Stretch and apply the filters: scam/ghost, geo, pay, Crocs, Spanish-required.
4. Write the morning-scan artifact and package for Steve.

Julie never applies. If the file is missing or stale, she falls back to her own LinkedIn guest + WebSearch sourcing and notes it as a blocker.
