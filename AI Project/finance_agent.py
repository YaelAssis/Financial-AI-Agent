import os
from typing_extensions import TypedDict
from typing import Literal
from langgraph.graph import StateGraph, START, END

# יבוא המודל של OpenAI
from langchain_openai import ChatOpenAI

# =====================================================================
# 1. SETUP OPENAI AUTHENTICATION (הגדרת החיבור ל-OpenAI)
# =====================================================================
os.environ["OPENAI_API_KEY"] = "sYOUR_OPENAI_API_KEY_HERE"

# אתחול המודל החכם של OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# =====================================================================
# 2. DEFINITION OF THE AGENT STATE
# =====================================================================
class AgentState(TypedDict):
    customer_message: str    
    predicted_category: str  
    selected_policy: str     
    final_response: str      

# =====================================================================
# 3. TOOLS & GRAPH NODES (הפונקציות של הגרף באמצעות OpenAI)
# =====================================================================
def lookup_policy(category: str) -> str:
    """כלי 1: שליפת מדיניות החברה לפי קטגוריה"""
    policies = {
        "Banking Services": "Banking Policy: For fee refunds, verify account status. Standard processing takes 2-3 business days.",
        "Credit Services": "Credit Policy: Unauthorized charges must be frozen immediately. Dispute forms sent to the credit bureau.",
        "Loans": "Loans Policy: Payment extensions can be granted up to 30 days upon review of interest terms.",
        "Mortgage": "Mortgage Policy: Escrow updates require formal documentation. Hardship relief programs available.",
        "Debt Collection": "Debt Collection Policy: Cease and desist letters must be acknowledged. Validate debt within 5 days.",
        "Other": "General Policy: Forward inquiry to senior human representative for manual review within 24 hours."
    }
    return policies.get(category, policies["Other"])


def classify_inquiry_node(state: AgentState):
    """צומת 1: OpenAI מסווג את הודעת הלקוח לקטגוריה הנכונה"""
    print("\n--- [Node 1] Asking OpenAI GPT to Classify Inquiry ---")
    message = state["customer_message"]
    
    system_prompt = (
        "You are an expert AI classifier for a bank. Classify the user's message into exactly ONE of these categories:\n"
        "['Banking Services', 'Credit Services', 'Debt Collection', 'Loans', 'Mortgage', 'Other'].\n"
        "Respond ONLY with the exact category name, nothing else."
    )
    
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ])
    
    predicted = response.content.strip()
    print(f"    > OpenAI GPT Result: '{predicted}'")
    return {"predicted_category": predicted}

# החזרת ה-print-ים החסרים כדי שתראו את התחנות בלייב!
def policy_node_banking(state: AgentState):
    print("--- [Node 2] Fetching Banking Policy Rules ---")
    return {"selected_policy": lookup_policy("Banking Services")}

def policy_node_credit(state: AgentState):
    print("--- [Node 2] Fetching Credit Policy Rules ---")
    return {"selected_policy": lookup_policy("Credit Services")}

def policy_node_loans(state: AgentState):
    print("--- [Node 2] Fetching Loans Policy Rules ---")
    return {"selected_policy": lookup_policy("Loans")}

def policy_node_mortgage(state: AgentState):
    print("--- [Node 2] Fetching Mortgage Policy Rules ---")
    return {"selected_policy": lookup_policy("Mortgage")}

def policy_node_debt(state: AgentState):
    print("--- [Node 2] Fetching Debt Collection Rules ---")
    return {"selected_policy": lookup_policy("Debt Collection")}

def policy_node_other(state: AgentState):
    print("--- [Node 2] Fetching General Policy Rules ---")
    return {"selected_policy": lookup_policy("Other")}


def generate_response_node(state: AgentState):
    """צומת 3: OpenAI מנסח מייל מקצועי וייחודי המבוסס על הפוליסה"""
    print("--- [Node 3] OpenAI GPT is Drafting a Custom Email Response ---")
    
    system_prompt = (
        "You are an empathetic customer support agent for a financial institution.\n"
        "Write a professional email response to the customer based on their message and the company policy provided.\n"
        "Be polite, clear, and follow the policy strictly."
    )
    
    user_content = f"Customer Message: {state['customer_message']}\nCompany Policy: {state['selected_policy']}"
    
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ])
    
    return {"final_response": response.content}


# =====================================================================
# 4. CONDITIONAL ROUTER (המוח המנתב)
# =====================================================================
def route_inquiry(state: AgentState) -> Literal["banking", "credit", "loans", "mortgage", "debt_collection", "other"]:
    category = state["predicted_category"]
    if category == "Banking Services": return "banking"
    elif category == "Credit Services": return "credit"
    elif category == "Loans": return "loans"
    elif category == "Mortgage": return "mortgage"
    elif category == "Debt Collection": return "debt_collection"
    else: return "other"


# =====================================================================
# 5. BUILDING & COMPILING THE STATE GRAPH
# =====================================================================
workflow = StateGraph(AgentState)

workflow.add_node("classify_inquiry", classify_inquiry_node)
workflow.add_node("policy_banking", policy_node_banking)
workflow.add_node("policy_credit", policy_node_credit)
workflow.add_node("policy_loans", policy_node_loans)
workflow.add_node("policy_mortgage", policy_node_mortgage)
workflow.add_node("policy_debt", policy_node_debt)
workflow.add_node("policy_other", policy_node_other)
workflow.add_node("generate_response", generate_response_node)

workflow.add_edge(START, "classify_inquiry")

workflow.add_conditional_edges(
    "classify_inquiry",
    route_inquiry,
    {
        "banking": "policy_banking",
        "credit": "policy_credit",
        "loans": "policy_loans",
        "mortgage": "policy_mortgage",
        "debt_collection": "policy_debt",
        "other": "policy_other"
    }
)

workflow.add_edge("policy_banking", "generate_response")
workflow.add_edge("policy_credit", "generate_response")
workflow.add_edge("policy_loans", "generate_response")
workflow.add_edge("policy_mortgage", "generate_response")
workflow.add_edge("policy_debt", "generate_response")
workflow.add_edge("policy_other", "generate_response")

workflow.add_edge("generate_response", END)

app = workflow.compile()


# =====================================================================
# 6. RUNNING THE LLM AGENT
# =====================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("   OPENAI POWERED AI AGENT INITIALIZED    ")
    print("=" * 50)
    
    user_query = "I am writing to dispute an unauthorized transaction on my credit card. Please apply the credit services protocol."
    
    inputs = {"customer_message": user_query}
    result = app.invoke(inputs)
    
    print("\n" + "="*40)
    print("REAL OPENAI GENERATED EMAIL RESPONSE:")
    print("="*40)
    print(result["final_response"])