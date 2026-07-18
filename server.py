import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent / "agent"))

from main import generateworkflow
from langgraph.checkpoint.memory import InMemorySaver

_BASE_DIR = Path(__file__).resolve().parent
SEARCHES_PATH = _BASE_DIR / "memory" / "specific_searches.json"
INTERVAL_DAYS = int(os.environ.get("INTERVAL_DAYS", "7"))

async def run_agent(topic: str, is_followup: bool):
    print(f"\n--- Starting Agent Run ---")
    print(f"Topic: {topic}")
    print(f"Is Followup: {is_followup}")
    
    checkpointer = InMemorySaver()
    workflow = await generateworkflow(checkpointer)

    result = await workflow.ainvoke(
        {
            "topic": topic,
            "messages": [],
            "needs_followup": False,
            "followup": [],
            "is_followup": is_followup
        },
        config={"configurable": {"thread_id": "main_1"}},
    )

    print("--- Run Complete! Check outputs/ for generated files. ---\n")

def get_due_followups():
    try:
        with open(SEARCHES_PATH, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [], []
        
    now = datetime.now()
    due = []
    pending = []
    
    for item in data:
        try:
            next_check = datetime.fromisoformat(item["next_check"])
            if now >= next_check:
                due.append(item)
            else:
                pending.append(item)
        except (ValueError, KeyError):
            pass 
            
    return due, pending

def save_pending_followups(pending):
    with open(SEARCHES_PATH, "w") as f:
        json.dump(pending, f, indent=4)

async def main():
    print("==================================================")
    print("       Vanguard Autonomous Agent Initializer      ")
    print("==================================================\n")
    
    interval_input = input("How many days should the agent wait between regular runs? (default 7): ").strip()
    try:
        interval_days = float(interval_input)
    except ValueError:
        interval_days = 7.0

    topic_input = input("What should the agent research and write about? (e.g. 'Weekly dose of AI'): ").strip()
    base_topic = topic_input if topic_input else "Weekly dose of AI"

    format_req = input("Any specific format or instructions for the email? (leave blank for default): ").strip()

    topic = base_topic
    if format_req:
        topic += f"\n\nAdditional formatting/content instructions: {format_req}"

    last_main_run = datetime.min # Start immediately on first boot

    print("\n==================================================")
    print(f"Vanguard Scheduler Started.")
    print(f"Topic: {base_topic}")
    print(f"Interval: {interval_days} days.")
    if format_req:
        print(f"Custom Format: Yes")
    print("Agent is now running autonomously in the background.")
    print("Press Ctrl+C to stop.")
    print("==================================================\n")
    
    while True:
        now = datetime.now()
        
        due, pending = get_due_followups()
        
        if due:
            item = due[0]
            print(f"[{now.isoformat()}] Critical Followup Due: {item['query']}")
            
            try:
                await run_agent(topic=item["query"], is_followup=True)
            except Exception as e:
                print(f"Error during followup run: {e}")
                
            save_pending_followups(pending + due[1:])
            continue
            
        if now - last_main_run >= timedelta(days=interval_days):
            print(f"[{now.isoformat()}] Regular Interval Run Due.")
            try:
                await run_agent(topic=topic, is_followup=False)
            except Exception as e:
                print(f"Error during main run: {e}")
            
            last_main_run = datetime.now()
            continue
            
        await asyncio.sleep(60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Vanguard Scheduler.")
