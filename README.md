# 📰 CyberPulse

**CyberPulse** is a web-based tool for tracking and aggregating high-signal cybersecurity news and alerts from over 40 of the most trusted public sources. Whether you're a researcher, analyst, or just staying informed, CyberPulse helps you quickly discover the latest cyber threats, breaches, vulnerabilities, and more—all in one place.

## 🔍 Features

- **Keyword Search**: Enter search terms (e.g. `ransomware`, `APT`, `malware finance`) to filter news articles by relevance.
- **Toggle All Sources**: Easily enable or disable news feeds across all categories with a single click.
- **Categorized Sources**: Sources are grouped for easier navigation:
  - Mainstream News
  - Cybersecurity Blogs
  - Vendor & Research Feeds
  - Government & Law Enforcement
  - Community & Aggregators
- **High Coverage**: Over 90–95% coverage of public, high-signal cybersecurity sources.
- **Lightweight Interface**: Clean UI optimized for fast access and reading.
- **No Ads / No Tracking**: 100% user-focused.

## 🌐 Categories and Example Sources

- **Mainstream News**:  
  _BBC, CNN, Wired, Ars Technica_  
  Coverage of global-scale cyber events, nation-state incidents, and policy reactions.

- **Cybersecurity Blogs**:  
  _KrebsOnSecurity, The Hacker News, Google Project Zero, PortSwigger, NCC Group, TrustedSec_  
  Deep-dive reporting, vulnerability breakdowns, and security research.

- **Vendors & Feeds**:  
  _CrowdStrike, Microsoft, Cisco Talos, Palo Alto Networks, ExploitDB_  
  Technical advisories, threat intelligence, and exploit telemetry.

- **Government & Law Enforcement**:  
  _CISA (CERT-US), NCSC UK, FBI, Europol_  
  Public alerts, takedown operations, and cyber defense recommendations.

- **Community & Aggregators**:  
  _Risky Biz (Substack), Darknet Diaries_  
  Curated security news, expert commentary, and real-world incident retrospectives.

## 📎 How to Use

1. Go to the CyberPulse web app: **(https://cyberpulse-cybersecurity-news-and-threat.onrender.com/)**

`Note: Running on Render’s free plan means slow startup times and limited resources cause slow performance.`

2. Enter keywords (e.g. `zero-day`, `crypto hack`, `phishing`, `APT`).
3. Select the sources you want to include—or click "Toggle All Sources."
4. Click **Search** to view real-time summaries from trusted news feeds.

> Tip: Enter `*` as the keyword to fetch **all recent articles** without filtering.

## 🔐 No API Keys or Logins Required

CyberPulse uses only publicly available RSS feeds. It does **not** rely on APIs that require authentication, rate limits, or tokens.

## 🚫 Limitations

- Twitter, Reddit, and Discord sources are **not included** due to lack of RSS or free API support.
- Some sources may go temporarily offline or restrict feed length.

---

**Built With:**  
- Python + Flask  
- HTML/CSS/JS (Vanilla)  
- `feedparser`, `BeautifulSoup`

---

