import os
import dotenv
dotenv.load_dotenv(dotenv_path='../.env')

import operator 
from typing import Annotated, Sequence 
from typing_extensions import TypedDict 
from langchain_core.messages import BaseMessage, ToolMessage

from langchain_openai import ChatOpenAI

# state for an agent
class AgentState(TypedDict): 
  messages: Annotated[Sequence[BaseMessage], operator.add]
  sender: str

import functools 

from langchain_core.messages import AIMessage

# node for an agent
def agent_node(state, agent, name): 
  result = agent.invoke(state)
  if isinstance(result, ToolMessage): 
    pass
  else: 
    result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
  return { 
    "messages": [result], 
    # track the sender so we know who to pass to next.
    "sender": name
  }

llm = ChatOpenAI(model="gpt-4o")

from agent import create_agent

triage_agent = create_agent(
  llm, 
  [], 
  system_message="You should find the homework assignments and assign it to the appropriate team member."
)
triage_node = functools.partial(agent_node, agent=triage_agent, name="Triage")

from langgraph.prebuilt import ToolNode 
from tool import get_current_time, get_weather

tools = [get_weather, get_current_time]
tool_node = ToolNode(tools)

from typing import Literal 
from langgraph.graph import END, StateGraph, START

def router(state): 
  messages = state["messages"]
  last_message = messages[-1]
  if last_message.tool_calls: 
    return "call_tool"
  if "FINAL ANSWER" in last_message.content: 
    return END
  return "continue"

workflow = StateGraph(AgentState)

workflow.add_node("triage", triage_node)

workflow