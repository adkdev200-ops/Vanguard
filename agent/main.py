from pathlib import Path
from typing import TypedDict, List
from datetime import datetime
import json

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from send_email import send_html_email
import pandas as pd
from agent import generate_workflow

_BASE_DIR = Path(__file__).resolve().parent.parent


class FollowUp(BaseModel):

    needs_followup: bool = Field(
        description="Check if we need actual followup is the information coming is very much critical like election results, if it is a general information tell false, if it is very life changing information then true"
    )
    query: str = Field(
        description="The specific information that was being searched."
    )

    research_time: datetime = Field(
        description="Timestamp when the research was performed."
    )

    status: str = Field(
        description="Reason the requested information was unavailable."
    )

    attempts: List[str] = Field(
        default_factory=list,
        description="Concise list of search attempts made.",
    )

    next_check: datetime = Field(
        description="Recommended time to retry the search."
    )

    reason: str = Field(
        description="Why this retry time was chosen."
    )


class SuperState(TypedDict):
    topic: str
    messages: list[BaseMessage]
    needs_followup: bool
    followup: list[FollowUp]
    is_followup: bool


model = ChatOllama(model="minimax-m3:cloud")
followup_model = model.with_structured_output(FollowUp)

try:
    with open(_BASE_DIR / "memory" / "failures.txt", "r") as f:
        previous_failures = f.read()
except FileNotFoundError:
    previous_failures = ""

with open(_BASE_DIR / "prompts" / "post_learning.md", "r") as f:
    post_learner_prompts = f.read()

with open(_BASE_DIR / "prompts" / "followups.md", "r") as f:
    followup_checker = f.read()


async def generateworkflow(checkpointer):
    graph = StateGraph(SuperState)

    async def post_learn(state: SuperState):
        response = await model.ainvoke(
            [
                SystemMessage(content=post_learner_prompts),
                *state["messages"],
            ]
        )

        with open(_BASE_DIR / "memory" / "failures.txt", "a") as f:
            f.write(response.content + "\n")

        return {}

    async def followup_checker_node(state: SuperState):
        try:
            response = await followup_model.ainvoke(
                [
                    SystemMessage(content=followup_checker),
                    *state["messages"],
                ]
            )
            return {"followup": [response]}
        except Exception as e:
            print(f"Failed to parse structured output from followup model: {e}")
            from datetime import datetime, timezone
            fallback = FollowUp(
                needs_followup=False,
                query="Fallback due to parsing error",
                research_time=datetime.now(timezone.utc),
                status="error",
                attempts=["Parsing error"],
                next_check=datetime.now(timezone.utc),
                reason="Parsing error"
            )
            return {"followup": [fallback]}

    async def researcher(state: SuperState):
        workflow, config = await generate_workflow()
        
        topic = state["topic"]
        if state.get("is_followup"):
            topic = f"URGENT FOLLOWUP: {topic}\nThis is a critical time-sensitive search. Focus entirely on finding this specific information and write an HTML report about it."

        response = await workflow.ainvoke(
            {"messages": [HumanMessage(content=topic)]},
            config=config,
        )

        return {"messages": response["messages"]}

    async def save_followups_to_json(state: SuperState):
        followups = state.get("followup", [])
        new_entries = []
        for f in followups:
            if f.needs_followup:
                new_entries.append({
                    "query": f.query,
                    "next_check": f.next_check.isoformat(),
                    "status": "pending"
                })
                
        if new_entries:
            searches_path = _BASE_DIR / "memory" / "specific_searches.json"
            try:
                with open(searches_path, "r") as f_obj:
                    data = json.load(f_obj)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []
            
            data.extend(new_entries)
            with open(searches_path, "w") as f_obj:
                json.dump(data, f_obj, indent=4)
                
        return {}

    async def route_after_research(state: SuperState):
        if state.get("is_followup"):
            return "post_learn"
        return "followup_checker_node"

    async def send_email(state: SuperState):
        output_dir = _BASE_DIR / "outputs"

        try:
            with open(output_dir / "output.html", "r") as f:
                html_content = f.read()

            with open(output_dir / "subject.txt", "r") as f:
                subject = f.read().strip()
        except FileNotFoundError as e:
            print(f"Error: Could not find output files for email: {e}")
            return {}

        try:
            emails_df = pd.read_csv(_BASE_DIR / "configs" / "emails.csv")
            email_list = emails_df["email"].dropna().tolist()
        except Exception as e:
            print(f"Error reading emails.csv: {e}")
            return {}

        if email_list:
            send_html_email(to=email_list, subject=subject, html=html_content)

        return {}

    graph.add_node("researcher", researcher)
    graph.add_node("post_learn", post_learn)
    graph.add_node("followup_checker_node", followup_checker_node)
    graph.add_node("save_followups_to_json", save_followups_to_json)
    graph.add_node("send_email", send_email)

    graph.add_edge(START, "researcher")
    
    graph.add_conditional_edges(
        "researcher",
        route_after_research,
        {
            "post_learn": "post_learn",
            "followup_checker_node": "followup_checker_node",
        },
    )

    graph.add_edge("followup_checker_node", "save_followups_to_json")
    graph.add_edge("save_followups_to_json", "post_learn")
    graph.add_edge("post_learn", "send_email")
    graph.add_edge("send_email", END)
    
    workflow = graph.compile(checkpointer=checkpointer)

    return workflow
