# GenAI Dispute Resolution System

An AI-powered dispute resolution system for handling payment disputes between customers, merchants, and issuers. The system uses LangGraph for agentic AI reasoning and provides human-in-the-loop override capabilities.

## Features

- 🤖 **AI-Powered Analysis**: Uses locally hosted LLM (Ollama/Llama3.1) for intelligent dispute resolution
- 📊 **Scoring System**: Rule-based and fraud risk scoring for evidence assessment
- 🔄 **Human-in-the-Loop**: Analyst override functionality for final decisions
- 📄 **Receipt Processing**: OCR support for PDF receipt uploads
- 🎨 **Modern UI**: Clean, responsive web interface with real-time analysis

## Use Case Scenario

The system handles disputes where:
- **Customer Claims**: "I was charged more than the displayed price"
- **Merchant Evidence**: Provides official receipt showing correct pricing
- **AI Resolution**: Analyzes evidence, applies rules, and recommends decision
- **Human Override**: Analyst can accept or reject AI recommendation

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Customer      │    │   AI Agent       │    │   Human Analyst │
│                 │    │   (LangGraph)    │    │                 │
│ Price Dispute   │───▶│  - Scoring       │───▶│  Final Review   │
│ Receipt Upload  │    │  - Analysis      │    │  Override       │
│                 │    │  - Decision      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install and start Ollama:
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama3.1 model
ollama pull llama3.1

# Start Ollama server
ollama serve
```

3. Start the FastAPI server:
```bash
python main.py
```

4. Open browser to `http://localhost:8002`

## Usage

### Web Interface
1. Enter Case ID, Customer Claim, and Merchant Evidence
2. Upload supporting documents (receipt PDFs)
3. Click "Submit for Analysis"
4. Review AI recommendation and confidence score
5. Apply human override if needed

### Programmatic Testing
```bash
python test_dispute.py
```

## System Components

### AI Agent (LangGraph)
- **Scoring Agent**: Calculates rule compliance and fraud risk scores
- **Decision Agent**: Uses LLM to analyze evidence and make recommendations

### Scoring Logic
- **Rule-Based Score**: Evaluates receipt completeness, pricing evidence, transaction details
- **Fraud Risk Score**: Identifies suspicious claim patterns and fraud indicators

### Human Override
- Analyst can accept or reject AI recommendations
- Final decision is logged with audit trail

## Sample Test Cases

### Case 1: Price Dispute with Receipt
- **Customer**: Charged $564.99, expected $449.99
- **Merchant**: Receipt shows $499.99 + $65.00 tax = $564.99
- **Expected**: REJECT (merchant evidence is strong)

### Case 2: Price Dispute Without Receipt  
- **Customer**: Overcharged by ~$165
- **Merchant**: No receipt provided, only system records
- **Expected**: ACCEPT (insufficient merchant evidence)

## File Structure

```
genai_dispute_resolution_read_receipt/
├── main.py              # FastAPI server
├── agent.py             # LangGraph AI agents
├── scoring.py           # Rule-based scoring logic
├── fraud.py             # Fraud risk assessment
├── ocr.py               # PDF text extraction
├── test_dispute.py      # Test script
├── static/
│   ├── index.html       # Web interface
│   ├── script.js        # Frontend logic
│   └── styles.css       # UI styling
├── receipts/            # Sample receipt data
│   └── Best_Electronics_POS_Receipt.txt
└── uploads/             # File upload directory
```

## Configuration

- **Port**: 8002 (configurable in main.py)
- **LLM Model**: llama3.1 (change in agent.py)
- **Upload Directory**: uploads/ (change in main.py)

## API Endpoints

- `POST /submit` - Submit dispute for analysis
- `GET /` - Web interface
- `GET /static/*` - Static files

## Future Enhancements

- [ ] Multi-language receipt processing
- [ ] Integration with payment processors
- [ ] Advanced fraud detection patterns
- [ ] Case management and tracking
- [ ] Reporting and analytics dashboard 
