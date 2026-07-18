import json
from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

_BASE_DIR = Path(__file__).resolve().parent.parent

with open(_BASE_DIR / "prompts" / "systemprompt.md") as f:
    SYSTEM_PROMPT = f.read()

with open(_BASE_DIR / "configs" / "mcp_servers.json") as f:
    MCP_SERVERS = json.load(f)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


async def generate_workflow(thread_id: str = "thread_1"):
    model = ChatOllama(
        model="minimax-m3:cloud",
        reasoning=False,
    )

    client = MultiServerMCPClient(MCP_SERVERS)
    tools = await client.get_tools()

    model = model.bind_tools(tools)
    checkpointer = InMemorySaver()

    async def chat_node(state: ChatState):
        response = await model.ainvoke(state["messages"])
        return {"messages": [response]}

    graph = StateGraph(ChatState)

    graph.add_node("chat", chat_node)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "chat")
    graph.add_conditional_edges("chat", tools_condition)
    graph.add_edge("tools", "chat")

    workflow = graph.compile(checkpointer=checkpointer)

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    workflow.update_state(
        config,
        {
            "messages": [
                SystemMessage(content=SYSTEM_PROMPT)
            ]
        },
    )

    return workflow, config