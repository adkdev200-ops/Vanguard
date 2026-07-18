# 🛡️ Vanguard

[![GitHub repo](https://img.shields.io/badge/GitHub-Vanguard-blue.svg)](https://github.com/adkdev200-ops/Vanguard.git)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)]()

**Vanguard** is a fully autonomous AI research agent that runs on a continuous background schedule. Built using **LangGraph** and the **Model Context Protocol (MCP)**, Vanguard automates deep web research, content curation, and HTML newsletter generation. 

Its standout feature is **Temporal Memory**: if Vanguard discovers that critical information (e.g., an upcoming election result, a scheduled product launch) is releasing before its next scheduled run, it dynamically schedules a targeted "Followup Run" to track that event and report back instantly, before seamlessly returning to its normal schedule.

---

## ✨ Features

- 🔄 **Persistent Autonomy**: Runs endlessly in the background. Tell it what to research and how often, and it handles the rest.
- 🧠 **Temporal Memory & Smart Followups**: Automatically parses future dates from its research. If a critical event is happening soon, it wakes up exactly when needed to grab the data rather than waiting for the normal interval.
- 🛠️ **MCP Tool Integration**: Leverages Model Context Protocol servers to provide the AI with native access to web browsing (Playwright), local file system access, and sequential thinking.
- 🧼 **Isolated Execution Contexts**: Instantiates a fresh `InMemorySaver` per run, guaranteeing zero memory leakage or context contamination between background runs.
- 📧 **Automated Dispatch**: Synthesizes findings into beautifully formatted, inline-CSS HTML emails and dispatches them directly to your mailing list.
- 📚 **Self-Learning System**: Logs failures and structural challenges to `memory/failures.txt` to adapt its approach on subsequent runs.

---

## 🏗️ Architecture Flow

1. **Scheduler (`server.py`)**: Wakes up periodically to check if a regular interval run or a critical followup run is due.
2. **Researcher Agent (`agent/main.py`)**: Uses a high-end LLM (e.g., `minimax-m3:cloud`) bound to MCP tools to search the web and synthesize information.
3. **Followup Extraction**: Analyzes the research to see if a time-sensitive event requires monitoring. If true, it saves the query and timestamp to `memory/specific_searches.json`.
4. **Delivery**: Formats the final output into a self-contained HTML file (stored in `outputs/`) and emails it via SMTP.
5. **Memory Reset**: Safely terminates the graph state and goes back to sleep.

---

## 🚀 Detailed Setup & Usage Guide

### 1. Prerequisites

Before installing Vanguard, ensure you have the following installed on your system:
- **Python 3.10+**
- **Node.js / npm**: Required to run the MCP servers via `npx`.
- **Git**

### 2. Clone the Repository

```bash
git clone https://github.com/adkdev200-ops/Vanguard.git
cd Vanguard
```

### 3. Environment Setup

Create a virtual environment and install the required dependencies:

```bash
python3 -m venv myenv
source myenv/bin/activate

# Install the necessary Python packages:
pip install langgraph langchain-ollama langchain-mcp-adapters pandas python-dotenv
```

### 4. Configuration

#### A. Environment Variables (`.env`)
Copy the provided example file to create your environment variables:
```bash
cp .env.example .env
```
Open `.env` and fill in your Gmail SMTP credentials. You must have **2-Factor Authentication** enabled on your Google Account to generate an **App Password**.
```env
SMTP_EMAIL=your_email@gmail.com
SMTP_APP_PASSWORD=your_16_character_app_password
INTERVAL_DAYS=7
```

#### B. Mailing List (`configs/emails.csv`)
Create or edit `configs/emails.csv` to specify your email recipients. It **must** include the header `email`:
```csv
email
recipient1@example.com
recipient2@example.com
```

#### C. MCP Servers (`configs/mcp_servers.json`)
Vanguard relies on external Model Context Protocol tools. You can customize them in `configs/mcp_servers.json`. 
By default, the following servers are invoked via `npx` or local commands:
- `@playwright/mcp@latest`: Allows the agent to browse and scrape the web natively.
- `@modelcontextprotocol/server-filesystem`: Allows reading/writing to specific local directories.
- `@modelcontextprotocol/server-sequential-thinking`: Enhances the AI's step-by-step reasoning logic.
- `desktop-commander`: An additional command line tool for desktop automations.

*(Note: Verify that the paths inside `mcp_servers.json` (such as the filesystem allowed directory) match your local machine's directory structure).*

### 5. Running Vanguard

To start the background scheduler, simply run the main server script from your terminal:

```bash
python server.py
```

**Initialization Prompts:**
Upon running, the script will prompt you for configuration details for the current session:
1. **Interval**: How many days between regular comprehensive research runs (e.g., `7` for weekly, `1` for daily).
2. **Topic**: What the agent should research (e.g., "Weekly global AI news" or "Stock market technical analysis").
3. **Custom Formatting**: Specific instructions for the output style (e.g., "Use bullet points and bold key names", "Write in the style of an academic paper").

**Autonomous Mode:**
Once you answer the prompts, Vanguard runs the very first research task immediately. After completion, it drops into an autonomous background loop. The script stays open, checking the clock every 60 seconds. Do not close the terminal if you want Vanguard to remain active.

---

## 💡 Example: How Temporal Memory Works

Let's say Vanguard runs on a Friday and discovers:
> *"OpenAI is scheduling a major product launch on Tuesday at 10 AM."*

Because Vanguard's standard interval might not trigger again until the *next* Friday, it will internally recognize this gap. 
1. It registers a **Followup Task** in `memory/specific_searches.json` set for Tuesday at 11 AM.
2. The agent goes to sleep.
3. On Tuesday at 11 AM, the `server.py` scheduler wakes up, reads the memory, and spins up an isolated run purely to check the *"OpenAI Product Launch"*.
4. It sends you a targeted email immediately.
5. It resumes its wait for the regular Friday run.

---

## 📁 Project Structure

- `agent/`: Contains the core LangGraph state machine, the agent logic, and the email sending utility.
- `configs/`: Stores the mailing list (`emails.csv`) and the MCP tools configuration (`mcp_servers.json`).
- `memory/`: Holds temporal data for followups (`specific_searches.json`) and learning logs (`failures.txt`).
- `outputs/`: Where Vanguard saves the generated raw HTML email files before dispatching them.
- `server.py`: The main entry point and background scheduler.

---

## 📝 License
This project is open-source and available under the MIT License.
