
def fraud_risk_score(customer_claim: str):
    risk = 0.0
    text = customer_claim.lower()
    
    # Price discrepancy specific fraud indicators
    if "price was less" in text and "receipt" not in text:
        risk += 0.3
    if "charged more" in text and "proof" not in text:
        risk += 0.2
    if "wrong price" in text and "evidence" not in text:
        risk += 0.2
    
    # Strong fraud indicators
    if "not delivered" in text and "tracking" not in text:
        risk += 0.3
    if "urgent refund" in text:
        risk += 0.3
    if "multiple times" in text:
        risk += 0.4
    if "guarantee" in text or "promise" in text:
        risk += 0.2
    
    # Additional fraud indicators
    if "never received" in text and "tracking" not in text:
        risk += 0.2
    if "immediately" in text and "refund" in text:
        risk += 0.2
    if "threat" in text or "legal action" in text:
        risk += 0.3
    if "friend said" in text or "someone told me" in text:
        risk += 0.2
    
    # Reduce risk if legitimate concerns are mentioned
    if "damaged" in text or "wrong item" in text:
        risk -= 0.2
    if "saw price tag" in text or "displayed price" in text:
        risk -= 0.1
    if "employee told me" in text:
        risk -= 0.1
    
    # Price dispute specific patterns
    if "$" in text and "different" in text:
        risk += 0.1
    if "receipt shows" in text and "wrong" in text:
        risk += 0.1
    
    return min(max(risk, 0.0), 1.0)
