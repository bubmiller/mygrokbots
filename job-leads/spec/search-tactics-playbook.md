# Job search tactics playbook (added 2026-09-23 from Megan Torres tips; LinkedIn window updated 2026-09-24; **search opened up 2026-10-03**; **Cincinnati Metro careers-page pass 2026-10-05**; **single daily routine, careers pass Tue/Thu, Indeed/ZipRecruiter dropped 2026-10-14**)

> **CHANGE 2026-10-14 (Steve, via Captian):**
> - The 5 PM digest routine is retired. The **Weekday morning job scan is the only daily job routine**; Emily's forwards cover urgent mail.
> - The top-100 Cincinnati Metro careers-page pass (§7) runs **only on Tuesdays and Thursdays** (ET weekday checked at runtime); skipped Mon/Wed/Fri.
> - **Indeed and ZipRecruiter are dropped as sources.** Evidence 2026-10-14: Indeed `/jobs?...&fromage=7` → HTTP 401 "Authenticating..." JS challenge; Indeed `/rss` and `rss.indeed.com` → HTTP 403 (WebFetch 404); ZipRecruiter `/jobs-search?...&days=7` and `/candidate/search` → HTTP 403 Cloudflare "Just a moment..." challenge; ZipRecruiter MCP failed every run 10-12→10-14 (HTTP 429 / WouldBlock / Connection closed). No credential-free public feed works; do not scrape around the blocks.
> - New skip rule: skip roles that **require Spanish** (bilingual required; Aspect 2182 precedent).

> **CHANGE 2026-10-03 (Steve):** "Open the search up. Make the time limit 7 days and be less picky about matches."
> - Freshness window is now **past 7 days** on every source (LinkedIn `f_TPR=r604800` replaces `r86400`; Dice / Indeed / Google careers / other boards use last-7-days).
> - Match bar loosened: surface **Strong AND Medium** fits, plus **Stretch** roles where Steve meets most core requirements. Label each Strong / Medium / Stretch with a one-line why + gaps.
> - Because 7-day windows overlap day to day, **dedupe against every prior `digest-*.md` and `morning-scan-*.md`** — never re-pitch a role already shown.
> - Unchanged: geo, scam/ghost filter, never auto-apply, keep-off list, no invented answers.

> **CHANGE 2026-10-05 (Steve):** "Let’s be sure to search the career pages for companies with a large Cincinnati Metro area presence."
> - ~~Every morning scan and 5pm digest~~ (superseded 2026-10-14: Tue/Thu morning scan only) runs a **Cincinnati Metro employer careers-page pass** (§7): curated **top ~100** large local employers (expanded 2026-10-05 from ~35), Google `site:` + direct ATS crawl, past 7 days, same match bar / geo / dedupe / never auto-apply.
> - **CHANGE 2026-10-05 follow-up (Steve):** "Let’s try the top 100 employers in the Cincinnati area." Seed list expanded to 100 HQ / major-presence employers across Cincy / Mason / Blue Ash / NKY / Butler–Warren–Clermont.

Steve asked Julie to apply these on every scan / dig / apply package.

## 1. Keyword matching & ATS scoring
- Mirror JD phrases word-for-word where honest.
- Before submit: score tailored resume at https://fitmyroleresume.com against that JD; note score + gaps in package NOTES; one honest revise+rescore if weak.
- Check the application's screening / knockout questions **before** building a package (lesson from OLIPOP 2026-09-30).

## 2. Freshness window — past 7 days (all sources)
- LinkedIn sweep URLs use `f_TPR=r604800` (past 7 days). `r86400` (24h) is retired as the default as of 2026-10-03. Do **not** use last-hour (`r3600`).
- Example: `https://www.linkedin.com/jobs/search/?keywords=IT%20Manager&location=Cincinnati%2C%20Ohio&f_TPR=r604800`
- Dice: posted-date filter = last 7 days (Composio `DICE_MCP_SEARCH_JOBS` posted-date option / Dice UI "Last 7 Days").
- ~~Indeed / ZipRecruiter~~ — **dropped 2026-10-14** (Indeed 401/403 bot wall incl. RSS; ZipRecruiter Cloudflare 403 + MCP 429/connection closed). Do not attempt; don't log them as blockers.
- Google careers / web searches: restrict to past week (`tbs=qdr:w` or "past week") and confirm `datePosted` on the employer ATS is within 7 days (or the role is otherwise clearly new to us).
- Gmail job-alert sweeps (LinkedIn / TealHQ alerts): `newer_than:7d`, still deduped.

## 3. Match bar — Strong / Medium / Stretch
- Surface roughly **55+/100 (~5/10+)** fits. Label each:
  - **Strong** (~75+): title + core duties + geo + pay all line up.
  - **Medium** (~60–74): good lane, a few gaps or unknown pay.
  - **Stretch** (~55–59): Steve meets most core requirements; named gaps (e.g. a specific tool) but not a lane change.
- Every pitched role: label, fit score, one-line **why**, one-line **gaps** (and any likely knockout screening question).
- Adjacent titles now OK when duties fit: IT Operations Manager, Service Delivery Manager, EUC / Desktop Support Manager, IT Support Manager, Infrastructure/Endpoint Manager, IT Site Lead, Technical Support Manager (internal IT), Help Desk Manager/Supervisor, sysadmin-leaning manager.
- Still skip: wrong lane (audit, app dev, product/customer support, sales/BDM, pure IC tech roles), K-12 solo IT, roles requiring an active clearance, roles requiring Spanish (bilingual required; added 2026-10-14).
- Steve's recent passes (V2X, OLIPOP) skewed against heavy security/AI-tool stacks he hasn't used — show those as Stretch with the gap stated plainly; don't oversell.

## 4. Dedupe (required with the 7-day window)
- Before pitching, grep company + title / job ID across all prior `/workspace/job-search/digest-*.md` and `morning-scan-*.md` (shortlists, reviewed/dropped tables) plus `applications-tracker.md/json`.
- Already pitched, passed, applied, quarantined, or dropped → do not re-pitch. Only resurface if something material changed (e.g. pay newly posted, quarantined role now verified on employer ATS) and say so explicitly.

## 5. Google hidden jobs (company careers)
- `site:company.com/careers "job title"`
- `site:company.com/jobs ("hiring" OR "job title") (remote OR hybrid OR Cincinnati OR Mason)`
- Prefer employer ATS over aggregators; quarantine TealHQ-only / stale mirrors.
- **Required on Tuesday and Thursday runs:** the curated Cincinnati Metro employer list in §7 (not ad-hoc only). Ad-hoc `site:` searches for shortlist companies are fine any day.

## 6. Recent hires reverse-engineering
- Company LinkedIn → People → joined past 1–3 months on the same team.
- Mirror honest overlapping titles/skills language into tailored materials for Strong/Medium fits Steve chooses to pursue.

## 7. Cincinnati Metro employer careers-page pass (added 2026-10-05; expanded to top 100 later same day)

> **CHANGE 2026-10-05 (Steve):** "Let’s be sure to search the career pages for companies with a large Cincinnati Metro area presence."
> **FOLLOW-UP 2026-10-05 (Steve):** "Let’s try the top 100 employers in the Cincinnati area."
> - **CHANGE 2026-10-14:** the weekday morning scan (now the only daily routine; 5pm digest retired) runs this pass **only on Tuesdays and Thursdays** (ET weekday at runtime) — required on those days (not optional / not "if time"), skipped Mon/Wed/Fri.
> - Method: for each employer, (1) Google `site:<domain>/careers|jobs` with title keywords + past week (`tbs=qdr:w`), and (2) open the preferred ATS careers URL when reachable and filter IT Manager / Service Desk / Help Desk Manager / EUC / Infrastructure Manager (and adjacent titles from §3).
> - Freshness: past **7 days** when `datePosted` / "posted" is detectable; otherwise treat as new-to-us only if not already in prior digests/scans.
> - Geo still applies: Mason ≤30 min, Cincinnati metro hybrid/onsite, or remote US.
> - **Dedupe** against keep-offs + all prior `digest-*.md` / `morning-scan-*.md` / `applications-tracker`. Never auto-apply.
> - Re-pitch only on a material change (new req ID, pay newly posted, previously quarantined now verified on employer ATS) — say what changed.
> - Keep-off notes on the list mean: skip that specific role; other IT-manager-lane openings at the same employer are still in scope after dedupe.
> - **List sources (not an official ranked Book of Lists dump):** Cincinnati Business Courier / Chamber largest-employer & manufacturer rankings, Kirkland Co. 2026 metro major-employers summary, Warren/Butler/NKY county employer PDFs, Fortune 500 Cincy HQs, and well-known Greater Cincinnati / Mason / Blue Ash / NKY presence. Prefer HQ or major local footprint. Exact headcount ranks shift year to year — treat this as a practical top-100-style careers crawl list.

### Title keywords for careers-page queries
`("IT Manager" OR "IT Operations Manager" OR "Service Desk Manager" OR "Help Desk Manager" OR "Help Desk Supervisor" OR "Service Delivery Manager" OR "EUC" OR "Desktop Support Manager" OR "Infrastructure Manager" OR "Endpoint Manager" OR "IT Support Manager" OR "IT Site Lead")`

### Curated seed list (100 employers — HQ or major Cincy Metro / Mason / Blue Ash / NKY / Butler–Warren–Clermont presence)

| # | Employer | Presence | Preferred careers / ATS | Google site: domain hint | Notes |
|---|---|---|---|---|---|
| 1 | Procter & Gamble | HQ Cincinnati / Mason R&D | https://pg.wd5.myworkdayjobs.com/ | `site:pg.wd5.myworkdayjobs.com` / `site:pgcareers.com` | Strong local HQ; Fortune 500 |
| 2 | The Kroger Co. | HQ Cincinnati | https://jobs.kroger.com/ | `site:jobs.kroger.com` | Largest local employer; CPG/retail HQ |
| 3 | Fifth Third Bank | HQ Cincinnati | https://jobs.53.com/ | `site:jobs.53.com` | Finance HQ; Fortune 500 |
| 4 | Cincinnati Children's Hospital Medical Center | HQ Cincinnati | https://www.cincinnatichildrens.org/careers | `site:cincinnatichildrens.org/careers` | Region's largest health employer |
| 5 | UC Health | Cincinnati / West Chester | https://careers.uchealth.com/ | `site:careers.uchealth.com` | Distinct from UC university jobs |
| 6 | University of Cincinnati | Cincinnati | https://career8.successfactors.com/ (UC) | `site:career8.successfactors.com` + UC | **Keep-off:** Help Desk Supervisor REQ 104051 (applied); other titles OK after dedupe |
| 7 | TriHealth | Cincinnati | https://www.trihealth.com/careers | `site:trihealth.com/careers` | Health system |
| 8 | Mercy Health / Bon Secours Mercy Health | Cincinnati / SW OH | https://careers.mercy.com/ | `site:careers.mercy.com` | Health system |
| 9 | The Christ Hospital Health Network | Cincinnati | https://www.thechristhospital.com/careers | `site:thechristhospital.com/careers` | Health system |
| 10 | St. Elizabeth Healthcare | Northern KY | https://www.stelizabeth.com/careers | `site:stelizabeth.com/careers` | NKY major health system |
| 11 | GE Aerospace (GE Aviation) | Evendale / Cincy / West Chester | https://careers.geaerospace.com/ | `site:careers.geaerospace.com` | Major engineering HQ presence; Fortune 500 |
| 12 | Cintas | HQ Mason / Cincy | https://www.cintas.jobs/ | `site:cintas.jobs` / `site:cintas.com/careers` | **Keep-off:** IT Manager–OT Mason (filled); other IT mgr roles OK after dedupe |
| 13 | EssilorLuxottica / Luxottica | Mason OH (NA hub) | https://careers.essilorluxottica.com/ | `site:careers.essilorluxottica.com` | Strong Mason presence |
| 14 | Ethicon / Johnson & Johnson | Blue Ash / Cincinnati area | https://jobs.jnj.com/ | `site:jobs.jnj.com` | Med device; filter Cincinnati/Blue Ash |
| 15 | Western & Southern Financial Group | HQ Cincinnati | https://www.westernsouthern.com/careers | `site:westernsouthern.com/careers` | Insurance/finance HQ; Fortune 500 |
| 16 | Cincinnati Financial / Cincinnati Insurance | Fairfield / Cincy | https://www.cinfin.com/careers | `site:cinfin.com/careers` | Insurance HQ; Fortune 500 |
| 17 | American Financial Group / Great American Insurance | HQ Cincinnati | https://www.greatamericaninsurancegroup.com/careers | `site:greatamericaninsurancegroup.com/careers` | Insurance HQ; Fortune 500 |
| 18 | altafiber (Cincinnati Bell) | Cincinnati | https://www.altafiber.com/careers | `site:altafiber.com/careers` | Telecom |
| 19 | E.W. Scripps | HQ Cincinnati | https://scripps.com/careers/ | `site:scripps.com/careers` | Media HQ |
| 20 | Fidelity Investments | Covington KY (NKY) | https://jobs.fidelity.com/ | `site:jobs.fidelity.com` | Large NKY campus; filter Covington/Cincinnati |
| 21 | First Financial Bank | Cincinnati / SW OH | https://www.bankatfirst.com/careers | `site:bankatfirst.com/careers` | Regional bank |
| 22 | U.S. Bank | Large Cincy presence | https://www.usbank.jobs/ | `site:usbank.jobs` | Filter Cincinnati |
| 23 | Huntington Bank | Cincy presence | https://huntington.wd5.myworkdayjobs.com/ | `site:huntington.wd5.myworkdayjobs.com` | Filter Cincinnati |
| 24 | PNC | Cincy presence | https://careers.pnc.com/ | `site:careers.pnc.com` | Filter Cincinnati |
| 25 | Total Quality Logistics (TQL) | HQ Cincinnati | https://www.tql.com/careers | `site:tql.com/careers` | Logistics HQ; large private employer |
| 26 | 84.51° | HQ Cincinnati | https://www.8451.com/careers/ | `site:8451.com/careers` / `site:job-boards.greenhouse.io/8451` | Kroger analytics; often data-heavy — only pitch IT/service-desk lane |
| 27 | Medpace | HQ Cincinnati | https://careers.medpace.com/ | `site:careers.medpace.com` | **Keep-off:** Manager Infrastructure Endpoint 12273 (applied); other reqs OK after dedupe |
| 28 | Lahlouh | Blue Ash | https://lahlouh.applytojob.com/ | `site:lahlouh.applytojob.com` | **Keep-off:** IT Manager (applied); other titles only |
| 29 | Macy's | Historic Cincy HQ / Deerfield Twp credit ops | https://www.macysjobs.com/ | `site:macysjobs.com` | Filter Cincinnati / Mason area |
| 30 | Emerson | Local / regional presence | https://www.emerson.com/en-us/careers | `site:emerson.com/careers` | Filter Cincinnati / Dayton if ≤ stretch |
| 31 | Siemens / Siemens Energy | Local presence | https://jobs.siemens.com/ | `site:jobs.siemens.com` | Filter Cincinnati |
| 32 | Cleveland-Cliffs (AK Steel) | Middletown / West Chester | https://www.clevelandcliffs.com/careers | `site:clevelandcliffs.com/careers` | Nearby heavy industry |
| 33 | Castellini Group | Cincinnati | https://www.castellini.com/careers | `site:castellini.com/careers` | Produce logistics |
| 34 | Ascension | Regional health IT footprint | https://ascension.org/careers | `site:ascension.org/careers` | Steve's prior employer; filter OH / Cincinnati |
| 35 | Amazon (non-OTS only) | Springdale OH / Hebron KY / Monroe DCs | https://www.amazon.jobs/ | `site:amazon.jobs` Cincinnati OR Mason OR Hebron OR Monroe | **Keep-off:** IT Manager OTS Job 10432129 (passed); other IT Manager / EUC roles only after dedupe |
| 36 | CVG Airport (Kenton County Airport Board) | Hebron KY (NKY) | https://www.cvgairport.com/careers/ | `site:cvgairport.com/careers` | Among region's largest employers (airport authority + tenants) |
| 37 | DHL Express | CVG hub / Erlanger KY | https://careers.dhl.com/ | `site:careers.dhl.com` CVG OR Erlanger OR Cincinnati | Major NKY cargo hub (~5k) |
| 38 | Elevance Health (Anthem) | Deerfield Twp / Mason / Cincinnati | https://careers.elevancehealth.com/ | `site:careers.elevancehealth.com` | Large Warren County / Mason-area presence |
| 39 | Miami University | Oxford / Hamilton / Middletown (Butler) | https://jobs.miamioh.edu/ | `site:jobs.miamioh.edu` | Large Butler County employer; filter IT/manager titles |
| 40 | Paycor (Paychex) | HQ Cincinnati | https://www.paycor.com/company/careers/ | `site:paycor.com/careers` / `site:careers.paychex.com` | HCM software HQ; may route via Paychex ATS post-acquisition |
| 41 | United Dairy Farmers (UDF) | HQ Cincinnati | https://www.udfinc.com/careers | `site:udfinc.com/careers` | Regional convenience/dairy HQ |
| 42 | American Modern Insurance Group | Amelia (Clermont) | https://www.amig.com/careers | `site:amig.com/careers` | Specialty P&C; Munich Re subsidiary |
| 43 | AtriCure | HQ Mason | https://job-boards.greenhouse.io/atricure | `site:job-boards.greenhouse.io/atricure` / `site:atricure.com/careers` | Med device HQ Mason |
| 44 | Prasco Laboratories | Mason | https://www.prasco.com/careers | `site:prasco.com/careers` | Authorized generics; Mason |
| 45 | Honeywell Intelligrated | Mason | https://careers.honeywell.com/ | `site:careers.honeywell.com` Mason OR Intelligrated | Automation / warehouse systems; Mason campus |
| 46 | L3Harris Technologies | Mason | https://careers.l3harris.com/ | `site:careers.l3harris.com` Mason OR Cincinnati | Electronics / defense presence Mason |
| 47 | Makino | Mason | https://www.makino.com/about/careers | `site:makino.com/careers` | Machine tools; Mason HQ USA |
| 48 | Mitsubishi Electric Automotive America | Mason | https://www.mitsubishielectric.com/en/careers/ | `site:mitsubishielectric.com/careers` Mason OR Cincinnati | Automotive electronics Mason |
| 49 | ADVICS Manufacturing | Lebanon (Warren) | https://www.advics-na.com/careers | `site:advics-na.com/careers` | Automotive brakes; Warren County |
| 50 | Belcan (Cognizant) | HQ Cincinnati | https://www.belcan.com/careers/ | `site:belcan.com/careers` | Engineering services; Cognizant-owned — pitch IT/ops mgr only if Cincy/hybrid verified |
| 51 | The Gorilla Glue Company | Sharonville | https://www.gorillatough.com/careers | `site:gorillatough.com/careers` | Consumer adhesives HQ |
| 52 | totes Isotoner | West Chester | https://www.totes-isotoner.com/careers | `site:totes-isotoner.com/careers` | Consumer accessories; West Chester |
| 53 | Milacron | Batavia (Clermont) | https://www.milacron.com/careers | `site:milacron.com/careers` | Plastics machinery |
| 54 | ProAmpac | Springdale / Cincy area | https://www.proampac.com/careers/ | `site:proampac.com/careers` | Flexible packaging; large private employer |
| 55 | Givaudan | Cincinnati / area plants | https://www.givaudan.com/careers | `site:givaudan.com/careers` | Flavors/fragrances; filter Cincinnati |
| 56 | MANE Inc. | Lebanon (Warren) | https://www.mane.com/careers | `site:mane.com/careers` | Flavors; Warren County |
| 57 | Empire Packing | Mason | https://www.empirepacking.com/careers | `site:empirepacking.com/careers` | Food processing Mason — ATS may be thin |
| 58 | VEGA Americas | Mason | https://www.vega.com/en-us/company/career | `site:vega.com/career` Mason OR Cincinnati | Level/process instrumentation Mason |
| 59 | Forvia / Faurecia | Franklin / Warren area | https://www.forvia.com/en/careers | `site:forvia.com/careers` / `site:faurecia.com/careers` | Auto parts; filter Cincinnati/Franklin |
| 60 | Duke Energy | Cincinnati / SW OH presence | https://dukeenergy.wd1.myworkdayjobs.com/ | `site:dukeenergy.wd1.myworkdayjobs.com` | Utility; filter Cincinnati / Ohio |
| 61 | City of Cincinnati | Cincinnati | https://www.governmentjobs.com/careers/cincinnati | `site:governmentjobs.com/careers/cincinnati` | Municipal (~6k); NeoGov |
| 62 | Hamilton County | Cincinnati | https://www.hamiltoncountyohio.gov/jobs | `site:hamiltoncountyohio.gov/jobs` | County government |
| 63 | Xavier University | Cincinnati | https://www.xavier.edu/hr/careers | `site:xavier.edu` careers OR jobs | Private university |
| 64 | Northern Kentucky University (NKU) | Highland Heights KY | https://jobs.nku.edu/ | `site:jobs.nku.edu` | NKY public university |
| 65 | Cincinnati State Technical and Community College | Cincinnati | https://www.cincinnatistate.edu/about/employment/ | `site:cincinnatistate.edu` employment OR careers | Community college |
| 66 | Meijer | Multiple Cincy / Middletown stores + ops | https://jobs.meijer.com/ | `site:jobs.meijer.com` | Filter Cincinnati / Northern Kentucky |
| 67 | Walmart | Regional stores / DCs | https://careers.walmart.com/ | `site:careers.walmart.com` Cincinnati OR Mason OR Hebron | Filter metro; skip pure store IC |
| 68 | The Home Depot | Regional stores / Monroe presence | https://careers.homedepot.com/ | `site:careers.homedepot.com` Cincinnati OR Monroe | Filter metro; skip pure store IC |
| 69 | Delta Air Lines | CVG focus city | https://delta.avature.net/ | `site:delta.avature.net` / `site:delta.com/careers` CVG OR Cincinnati | Airport ops / IT if posted locally or remote |
| 70 | XPO Logistics | Cincinnati LTL hub | https://jobs.xpo.com/ | `site:jobs.xpo.com` | Filter Cincinnati |
| 71 | Meridian Bioscience | HQ Cincinnati area | https://careers-meridianbioscience.icims.com/ | `site:careers-meridianbioscience.icims.com` | Diagnostics / life sciences |
| 72 | Roto-Rooter | HQ Cincinnati | https://www.rotorooter.com/careers/ | `site:rotorooter.com/careers` | Plumbing services HQ |
| 73 | Rumpke Waste & Recycling | HQ Cincinnati area | https://www.rumpke.com/careers | `site:rumpke.com/careers` | Waste / recycling regional HQ |
| 74 | Messer Construction | HQ Cincinnati | https://www.messer.com/careers/ | `site:messer.com/careers` | Construction HQ |
| 75 | Drees Homes | HQ Fort Mitchell KY (NKY) | https://www.dreeshomes.com/careers/ | `site:dreeshomes.com/careers` | Homebuilder HQ NKY |
| 76 | Philips Edison & Company | HQ Cincinnati | https://www.philipsedison.com/careers | `site:philipsedison.com/careers` | Retail REIT HQ |
| 77 | Cornerstone Brands / HSN | West Chester | https://www.hsn.com/careers | `site:hsn.com/careers` / Cornerstone Brands | Consumer brands campus West Chester |
| 78 | Koch Foods | Fairfield (Butler) | https://www.kochfoodsinc.com/careers | `site:kochfoodsinc.com/careers` | Poultry processing; Butler County |
| 79 | Tyson Foods | West Chester / regional | https://www.tysonfoods.com/careers | `site:tysonfoods.com/careers` | Filter Cincinnati / West Chester |
| 80 | Kettering Health | Hamilton / Butler presence | https://www.ketteringhealth.org/careers/ | `site:ketteringhealth.org/careers` | Health system; Hamilton campus |
| 81 | Premier Health / Atrium Medical Center | Middletown | https://www.premierhealth.com/careers | `site:premierhealth.com/careers` | Middletown hospital campus |
| 82 | Otterbein SeniorLife | Warren / regional | https://www.otterbein.org/careers | `site:otterbein.org/careers` | Senior living; filter IT/manager |
| 83 | Atos | Deerfield Twp presence | https://atos.net/en/careers | `site:atos.net/careers` Cincinnati OR Mason | IT services; only if Cincy/hybrid IT-manager posting verified |
| 84 | Skyline Chili | HQ Cincinnati | https://www.skylinechili.com/careers | `site:skylinechili.com/careers` | Regional restaurant HQ — corp IT only |
| 85 | Graeter's Ice Cream | HQ Cincinnati | https://www.graeters.com/careers | `site:graeters.com/careers` | Regional dairy/retail HQ — corp IT only |
| 86 | Standard Textile | HQ Cincinnati | https://www.standardtextile.com/careers | `site:standardtextile.com/careers` | Textile / hospitality products HQ |
| 87 | Fischer Homes | HQ Erlanger KY (NKY) | https://www.fischerhomes.com/careers | `site:fischerhomes.com/careers` | Homebuilder NKY |
| 88 | Jeff Wyler Automotive Family | Milford / regional | https://www.jeffwyler.com/careers | `site:jeffwyler.com/careers` | Auto dealer group — corp IT only |
| 89 | Heidelberg Distributing | HQ Cincinnati area | https://www.heidelbergdistributing.com/careers | `site:heidelbergdistributing.com/careers` | Beverage distribution |
| 90 | Sysco | Cincinnati / regional DC | https://careers.sysco.com/ | `site:careers.sysco.com` Cincinnati | Foodservice distribution; filter metro |
| 91 | US Foods | Cincinnati / regional | https://www.usfoods.com/careers.html | `site:usfoods.com/careers` Cincinnati | Foodservice distribution; filter metro |
| 92 | PepsiCo / Pepsi Beverages | Regional ops | https://www.pepsicojobs.com/ | `site:pepsicojobs.com` Cincinnati | Filter Cincinnati; skip pure warehouse IC |
| 93 | Coca-Cola Consolidated | Regional presence | https://cokeconsolidated.wd1.myworkdayjobs.com/ | `site:cokeconsolidated.wd1.myworkdayjobs.com` | Filter Cincinnati / NKY |
| 94 | Cincom Systems | HQ Cincinnati | https://www.cincom.com/careers/ | `site:cincom.com/careers` | Enterprise software HQ |
| 95 | Q Laboratories | Cincinnati | https://www.qlaboratories.com/careers | `site:qlaboratories.com/careers` | Testing lab; smaller IT footprint |
| 96 | LCA-Vision / LasikPlus | HQ Cincinnati | https://www.lasikplus.com/careers | `site:lasikplus.com/careers` | Vision correction HQ |
| 97 | AssureCare | Cincinnati | https://www.assurecare.com/careers | `site:assurecare.com/careers` | Healthcare software |
| 98 | Michelman | HQ Cincinnati | https://www.michelman.com/careers/ | `site:michelman.com/careers` | Specialty chemicals HQ |
| 99 | Hillenbrand / Milacron-related brands | Batesville IN stretch / Cincy ties | https://www.hillenbrand.com/careers | `site:hillenbrand.com/careers` | Only if Cincy/remote US posting; Batesville is stretch geo |
| 100 | Cedar Fair / Kings Island | Mason (seasonal + corp ops) | https://www.cedarfair.com/careers | `site:cedarfair.com/careers` / `site:experiencekingsisland.com` | Pitch year-round corp/IT only; skip seasonal park IC |

### Explicitly out of this seed (do not expand here without a new Steve ask)
- **Pass keep-offs (do not re-pitch):** Kao, V2X, OLIPOP, Vernovis/Rhinestahl Mason IT Ops, IronOrbit, Amazon OTS Job 10432129.
- Columbus-only (e.g. L Brands / Bath & Body Works HQ, NetJets, Nationwide) unless a posting is Cincy/remote US.
- Pure warehouse/fulfillment IC roles, zoo/museum/nonprofit micro-IT, Cognizant/Belcan/Atos **unless** a Cincy onsite/hybrid IT-manager posting is verified.
- Toyota Georgetown KY — stretch geography; only if remote US or Steve later widens radius.
- Pure K-12 school districts (solo IT / district tech) — wrong lane unless a clear multi-site IT Manager posting appears and Steve asks to widen.

### How to log the pass in artifacts
In each Tue/Thu `morning-scan-*.md`, include a short **Cincy careers-page pass** line: employers checked (count), hits found, hits dropped to keep-off/dedupe, blockers (ATS login wall / SPA). Do not list every empty employer. With 100 employers, sampling/batching Google `site:` queries is OK as long as the pass covers the list each Tue/Thu run (or notes which batch was deferred). On Mon/Wed/Fri log one line: `Cincy careers-page pass: skipped (Tue/Thu only)`.

## Standing rules (unchanged)
- Geo: Mason OH ≤30 min, Cincinnati metro hybrid/onsite, or remote US.
- No auto-apply; Steve decides. No invented form answers. Scam/ghost filter before pitching. Tracker: Google Sheet is SoT (2026-10-11); md/json are backups.
- Keep-off: UC Help Desk Supervisor 104051, Medpace 12273, Lahlouh IT Manager (applied); Pass: V2X, OLIPOP, Kao, Vernovis/Rhinestahl Mason IT Ops, Amazon OTS, IronOrbit; Cintas IT Manager–OT Mason (filled); plus the longer keep-off list carried in recent digests.

Skill: [job-search-tactics](sand-workflow:job-search-tactics)


## Résumé claims rule (2026-10-06)
- Compliance/audit claims stay off the master and all tailored résumés unless Steve confirms them. Removed the "Protected compliance posture by auditing systems…" bullet from the master.

## Keep-off employer: Crocs (2026-10-10)
Steve is trying to leave Crocs, his current employer. Never surface Crocs roles, internal or external, and ignore Crocs Talent Community / careers.crocs.com alerts.

## Tracker (2026-10-11)
- The Google Sheet is the source of truth for application tracking (Steve, 2026-10-11): https://docs.google.com/spreadsheets/d/1JR7lZQsWFl56WfcXTHvNWQobXPy3jLSPClJxk5HZkWs/edit
- Tabs: **Applications** (one row per submitted application, newest first), **Passed / Skipped**, **Keep-off rules**. Column order is in `sheets-mirror.json`.
- Read and write application status in the Sheet first via Composio Google Sheets (`GOOGLESHEETS_BATCH_GET` / `GOOGLESHEETS_UPDATE_VALUES_BATCH`), then mirror the change to `applications-tracker.md` / `.json` (local backups).
- Never put passwords, tokens, or login secrets in the Sheet; "Portal account" = account type + email only.
