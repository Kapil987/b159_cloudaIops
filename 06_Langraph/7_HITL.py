

import os

from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

from typing import Annotated

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def get_stock_price(symbol: str) -> float:
    '''Return the current price of a stock given the stock symbol'''
    return {"MSFT": 200.3, "AAPL": 100.4, "AMZN": 150.0, "RIL": 87.6}.get(symbol, 0.0)

@tool
def buy_stocks(symbol: str, quantity: int, total_price: float) -> str:
    '''Buy stocks given the stock symbol and quantity'''
    review = interrupt(
        {
            "prompt": f"A trade order for {quantity} shares of {symbol} totaling ${total_price:.2f} is awaiting your sign-off. Confirm as-is, cancel it, or edit the quantity/price?",
            "symbol": symbol,
            "quantity": quantity,
            "total_price": total_price,
        }
    )

    action = review.get("action")
    if action == "confirm":
        return f"You bought {quantity} shares of {symbol} for a total price of {total_price}"
    elif action == "edit":
        revised_quantity = review.get("quantity", quantity)
        revised_price = review.get("total_price", total_price)
        return f"You bought {revised_quantity} shares of {symbol} for a total price of {revised_price}"
    else:
        return "Trade order cancelled."


tools = [get_stock_price, buy_stocks]

llm = init_chat_model("groq:qwen/qwen3.8-27b")
llm_with_tools = llm.bind_tools(tools)

def chatbot_node(state: State):
    msg = llm_with_tools.invoke(state["messages"])
    return {"messages": [msg]}

memory = MemorySaver()
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")
builder.add_edge("chatbot", END)
graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "buy_thread"}}

# Step 1: user asks price
state = graph.invoke({"messages":[{"role":"user","content":"What is the current price of 10 MSFT stocks?"}]}, config=config)
print(state["messages"][-1].content)

# Step 2: user asks to buy
state = graph.invoke({"messages":[{"role":"user","content":"Buy 10 MSFT stocks at current price."}]}, config=config)
print(state.get("__interrupt__"))

choice = input("Confirm, cancel, or edit this order? (confirm/cancel/edit): ").strip().lower()
if choice == "edit":
    new_quantity = int(input("New quantity: "))
    new_total_price = float(input("New total price: "))
    resume_payload = {
        "action": "edit",
        "quantity": new_quantity,
        "total_price": new_total_price,
    }
elif choice == "confirm":
    resume_payload = {"action": "confirm"}
else:
    resume_payload = {"action": "cancel"}

state = graph.invoke(Command(resume=resume_payload), config=config)
print(state["messages"][-1].content)

# --- 🤔 Before you move on ---
# This script pauses one agent's graph for human approval, but it only runs
# locally in a single process: no real authentication, no persistent audit
# trail, and no way for a second person to review it remotely. How would you
# expose this same approve/edit/reject flow behind a real API, with proper
# auth and full observability? That's exactly what
# 07_Observability_Evaluation_Authentication builds toward next.

