# GreeksDB : ⚡ NSE Options Chain Automated Scraper
Webscrape the Greeks values of NSE FNO allowed scripts once in every 15 minutes

A lightweight, serverless, production-grade data pipeline that automatically scrapes, processes, and archives near real-time options chain data for over 200+ NSE liquid scripts.

Powered entirely by **GitHub Actions** and the **Fyers API v3**, the pipeline runs tracking routines during Indian market hours, archiving granular time-series datasets as flat JSON files without requiring a paid database server.

---

## 🚀 Key Features

* **Zero-Infrastructure Automation:** Uses GitHub Actions crons to execute data runs entirely free, eliminating the need for a 24/7 dedicated VPS.
* **Market-Hours Alignment:** Automatically triggers every 15 minutes between **9:15 AM IST and 3:30 PM IST**, Monday through Friday.
* **Smart Rate-Limiting:** Built-in sleep throttles guarantee conformance with the Fyers API single-second request thresholds.
* **Failover & Retry Architecture:** Implements a 5-attempt fallback loop per symbol to survive random network drops or API gateway timeouts.
* **Dynamic Token Management:** Pulls valid OAuth access tokens on-the-fly from a centralized remote endpoint (`PythonAnywhere`), avoiding authentication stagnation.
* **Incremental Delta Storage:** Merges new market snapshots directly into existing localized JSON structures sequentially.

---

## 🏗️ System Architecture & Data Flow

```text
[ GitHub Actions Cron ] 
         │
         ▼
 1. Fetches Token ────────► [ PythonAnywhere Secure Vault ]
         │
         ▼
 2. Loops Watchlist ──────► [ Fyers API v3 Gateways ] (Enforces 1s rate-limit window)
         │
         ▼
 3. Merges Snapshots ─────► [ Append-only Local JSONs ] (data/SYMBOL.json)
         │
         ▼
 4. Git Push Commit ──────► [ Your GitHub Repository ]

```

---

## 📁 Repository Structure

```text
├── .github/workflows/
│   └── options-scraper.yml   # GitHub Actions Cron Configuration
├── data/
│   ├── TCS.json              # Historical compiled JSON tracking for TCS
│   ├── RELIANCE.json         # Historical compiled JSON tracking for Reliance
│   └── ...                   # (Auto-generated per symbol)
├── requirements.txt          # Python dependency manifests
└── scraper.py                # Main ETL pipeline core execution logic

```

---

## 📊 Data Schema Output

Data is sequentially appended inside individual files under the `data/` folder. The structure utilizes a highly nested timestamp layout to preserve clean temporal tracking:

```json
{
  "17-05-2026-09-15-00": {
    "2026-05-21": { "expiry0_raw_fyers_option_chain_data" },
    "2026-05-28": { "expiry1_raw_fyers_option_chain_data" },
    "2026-06-25": { "expiry2_raw_fyers_option_chain_data" }
  },
  "17-05-2026-09-30-00": {
    "2026-05-21": { "expiry0_raw_fyers_option_chain_data" },
    "2026-05-28": { "expiry1_raw_fyers_option_chain_data" },
    "2026-06-25": { "expiry2_raw_fyers_option_chain_data" }
  }
}

```

---

## 🛠️ Local Development & Setup

To run a diagnostic cycle or manage testing execution routines on your local workstation:

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/nse-options-scraper.git
cd nse-options-scraper

```

### 2. Configure Virtual Environment & Dependencies

```bash
python -m venv venv
source venv/bin/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt

```

### 3. Run a Manual Scrape Test

```bash
python scraper.py

```

---

## ⚙️ Automated Deployment (GitHub Actions Setup)

To seamlessly operationalize the background data pipeline pipelines, verify the following configuration switches are checked:

### ⚠️ Crucial Step: Workflow Write Access

By default, GitHub Workflow Bots cannot push newly extracted files back up to your codebase without explicit authorization.

1. Navigate to your repository's **Settings** tab.
2. Select **Actions** $\rightarrow$ **General** from the sidebar.
3. Scroll downwards to find **Workflow permissions**.
4. Change the toggle selection from *Read repository contents permission* to **Read and write permissions**.
5. Hit **Save**.

### Manual Activation Trigger

If you want to force an instantaneous execution run outside of the standard Indian market hours timeline:
Go to your repository's **Actions** tab $\rightarrow$ select **NSE Options Chain Scraper** $\rightarrow$ click the **Run workflow** drop-down menu.

---

## ⚖️ Disclaimer

*This project is built purely for educational and personal analytical purposes. Data feeds are sourced directly using Fyers standard user APIs. The developer holds zero liability regarding usage quotas, API restrictions, or financial trading losses resulting from automated script operations.*
