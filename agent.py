
import json
from typing import TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from scoring import rule_based_score
from fraud import fraud_risk_score

llm = ChatOllama(model="llama3.1")

class DisputeState(TypedDict):
    case_id: str
    customer_claim: str
    merchant_evidence: str
    rule_score: float
    fraud_score: float
    final_decision: dict

def scoring_agent(state: DisputeState):
    state["rule_score"] = rule_based_score(state["merchant_evidence"])
    state["fraud_score"] = fraud_risk_score(state["customer_claim"])
    return state

def decision_agent(state: DisputeState):
    prompt = f"""
    You are an expert dispute resolution analyst for a payment processing company. 
    Analyze the following dispute case between a customer and merchant:

    CUSTOMER CLAIM: {state['customer_claim']}
    
    MERCHANT EVIDENCE: {state['merchant_evidence']}
    
    ANALYSIS SCORES:
    - Rule Compliance Score: {state['rule_score']} (higher = stronger merchant case)
    - Fraud Risk Score: {state['fraud_score']} (higher = more suspicious customer claim)

    DISPUTE RESOLUTION RULES:
    1. If merchant provides valid receipt with correct pricing, REJECT customer claim
    2. If customer claims price discrepancy but receipt shows correct amount, REJECT claim
    3. If merchant evidence is unclear or incomplete, ACCEPT claim for further review
    4. High fraud score (>0.7) strongly suggests REJECT the customer claim
    5. High rule score (>0.6) strongly suggests REJECT the customer claim

    Return ONLY JSON in this exact format, no other text:
    {{"decision": "REJECT or ACCEPT", "confidence": 0-1, "reasoning": "detailed explanation based on evidence and scores"}}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Try to extract JSON from the response
    content = response.content.strip()
    
    # Look for JSON in markdown code blocks
    if "```json" in content:
        start = content.find("```json") + 7
        end = content.find("```", start)
        if end != -1:
            content = content[start:end].strip()
    elif "```" in content:
        start = content.find("```") + 3
        end = content.find("```", start)
        if end != -1:
            content = content[start:end].strip()
    
    # Try to find JSON object boundaries
    if content.startswith('{') and content.endswith('}'):
        try:
            result = json.loads(content)
        except:
            result = {"decision": "REVIEW", "confidence": 0.5, "reasoning": "JSON parsing failed"}
    else:
        # Try to extract JSON from anywhere in the text
        import re
        json_match = re.search(r'\{[^}]*"decision"[^}]*\}', content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
            except:
                result = {"decision": "REVIEW", "confidence": 0.5, "reasoning": "JSON extraction failed"}
        else:
            result = {"decision": "REVIEW", "confidence": 0.5, "reasoning": "No JSON found in response"}

    # More logical decision making based on scores
    # Strong merchant evidence (high rule score) should lead to REJECT
    # High fraud risk should also lead to REJECT
    base_conf = result.get("confidence", 0.5)
    
    if state["rule_score"] >= 0.8:
        # Very strong merchant evidence - override to REJECT
        result["decision"] = "REJECT"
        result["reasoning"] = "Merchant provided complete receipt with clear pricing evidence. Customer claim of price discrepancy is not supported by documentation."
        final_conf = max(0.8, base_conf)
    elif state["rule_score"] >= 0.6 and state["fraud_score"] < 0.3:
        # Good merchant evidence but not overwhelming - consider LLM decision
        # If LLM says ACCEPT, keep it (weak merchant case)
        if result["decision"] == "ACCEPT":
            result["reasoning"] = "Merchant evidence is incomplete or weak. Customer claim may have merit. Further investigation recommended."
        else:
            result["decision"] = "REJECT"
            result["reasoning"] = "Merchant evidence is sufficient to dispute customer claim."
        final_conf = max(0.6, base_conf)
    elif state["fraud_score"] >= 0.7:
        # High fraud risk - REJECT the claim
        result["decision"] = "REJECT"
        result["reasoning"] = "High fraud risk detected in customer claim. Pattern suggests potential dispute abuse."
        final_conf = max(0.8, base_conf)
    else:
        # Use LLM decision with confidence adjustment
        final_conf = base_conf
    
    # Apply score-based confidence adjustment
    score_adjustment = (state["rule_score"] * 0.6) - (state["fraud_score"] * 0.4)
    final_conf = min(1.0, max(0.0, final_conf + score_adjustment))
    
    result["confidence"] = round(final_conf, 2)
    state["final_decision"] = result
    return state

def build_graph():
    workflow = StateGraph(DisputeState)
    workflow.add_node("scoring", scoring_agent)
    workflow.add_node("decision", decision_agent)
    workflow.set_entry_point("scoring")
    workflow.add_edge("scoring", "decision")
    workflow.add_edge("decision", END)
    return workflow.compile()

graph = build_graph()
