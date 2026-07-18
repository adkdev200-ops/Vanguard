# 🛡️ Vanguard

[![GitHub repo](https://img.shields.io/badge/GitHub-Vanguard-blue.svg)](https://github.com/adkdev200-ops/Vanguard.git)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)]()

**Vanguard** is a fully autonomous AI research agent that runs on a continuous background schedule. Built using **LangGraph** and the **Model Context Protocol (MCP)**, Vanguard automates deep web research, content curation, and HTML newsletter generation. 

Its standout feature is **Temporal Memory**: if Vanguard discovers that critical information (e.g., an upcoming election result, a scheduled product launch) is releasing before its next scheduled run, it dynamically schedules a targeted "Followup Run" to track that event and report back instantly, before seamlessly returning to its normal schedule.

---

## ✨ Features

- 🔄 **Persistent Autonomy**: Runs endlessly in the background. Tell it what to research and how often, and it handles the rest.
- 🧠 **Temporal Memory & Smart Followups**: Automatically parses future dates from its research. If a critical event is happening soon, it wakes up exactly when needed to grab the data rather than waiting for the normal interval.
- 🛠️ **MCP Tool Integration**: Uses Model Context Protocol servers (like Playwright and local Filesystem) to browse the web, bypass blocks, and manage outputs natively.
- 🧼 **Isolated Execution Contexts**: Instantiates a fresh `InMemorySaver` per run, guaranteeing zero memory leakage or context contamination between weeks.
- 📧 **Automated Dispatch**: Synthesizes its findings into a beautifully formatted, inline-CSS HTML email and dispatches it directly to your mailing list.
- 📚 **Self-Learning System**: Logs failures and structural challenges to `memory/failures.txt` to adapt its approach on subsequent runs.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/adkdev200-ops/Vanguard.git
cd Vanguard
```

### 2. Environment Setup
Create a virtual environment and install dependencies:
```bash
python3 -m venv myenv
source myenv/bin/activate
# Make sure to install required packages like langgraph, langchain-ollama, langchain-mcp-adapters, pandas, etc.
```

### 3. Configuration
Copy the `.env.example` file to create your own configuration:
```bash
cp .env.example .env
```
Open `.env` and fill in your Gmail SMTP credentials:
```env
SMTP_EMAIL=your_email@gmail.com
SMTP_APP_PASSWORD=your_16_character_app_password
INTERVAL_DAYS=7
```
*(Note: To get an app password for Gmail, you must have 2-Factor Authentication enabled on your Google Account).*

You will also need a `configs/emails.csv` file formatted with an `email` header to specify your mailing list recipients.

### 4. Run Vanguard
Start the agent initializer:
```bash
python server.py
```
You will be prompted to enter:
1. **The Interval** (e.g., `7` for weekly, `1` for daily).
2. **The Topic** (e.g., "Weekly dose of AI" or "Global Economic News").
3. **Custom Formatting** (e.g., "Write it in the style of a pirate" or leave blank).

Once initialized, Vanguard enters its background scheduling loop and operates autonomously.

---

## 🏗️ Architecture Flow

1. **Scheduler (`server.py`)**: Wakes up every 60 seconds to check if a regular interval run or a critical followup run is due.
2. **Researcher Agent (`agent/main.py`)**: Uses the `minimax-m3:cloud` model bound to MCP tools to search the web and synthesize information.
3. **Followup Extraction**: Analyzes the research to see if a time-sensitive event requires monitoring. If true, it saves the query and timestamp to `memory/specific_searches.json`.
4. **Delivery**: Formats the final output into a self-contained HTML file and emails it via SMTP.
5. **Memory Reset**: Safely terminates the graph state and goes back to sleep.

---

## 📝 License
This project is open-source and available under the MIT License.
