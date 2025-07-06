# LLM Guardrails Server

A FastAPI-based moderation server that detects personally identifiable information (PII) in text, optimized for  context and compatible with OpenAI's moderation API format.

## Features

- ** PII Detection**: Detects various types of personally identifiable information specific to y:
  -  phone numbers (landline and mobile)
  - Email addresses
  - Credit card numbers (Visa, MasterCard, AmEx)
  -  date formats (DD.MM.YYYY)
  - IP addresses (IPv4 and IPv6)
  - IBAN and BIC codes
  - Medical information with  terms

- **Dual Detection Engine**:
  - **Regex-based**: Fast pattern matching for structured  PII data
  - **BERT-based**: ML-powered detection for contextual content (optional)

- **OpenAI API Compatibility**: Drop-in replacement for OpenAI's moderation API

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd llm-guardrails-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) For BERT-based detection, ensure PyTorch and transformers are properly installed:
```bash
pip install torch transformers
```

## Quick Start

1. Start the server:
```bash
python main.py
```

2. Test with curl (OpenAI-compatible format):
```bash
curl http://localhost:8000/v1/moderations \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model": "moderation-latest",
    "input": "My phone is 01542345678 and E-Mail max@example.de"
  }'
```

3. Or use the test client:
```bash
python test_client.py
```

## API Endpoints

### POST /v1/moderations
Analyze text for  PII content. Compatible with OpenAI's moderation API.

**Request:**
```json
{
  "model": "moderation-latest",
  "input": "Text to analyze for  PII"
}
```

**Response:**
```json
{
  "id": "modr-xxxxx",
  "model": "moderation-latest",
  "results": [
    {
      "flagged": true,
      "categories": {
        "pii/phone": true,
        "pii/email": false,
        // ... other categories
      },
      "category_scores": {
        "pii/phone": 0.9,
        "pii/email": 0.0,
        // ... other scores
      },
      "category_applied_input_types": {
        "pii/phone": ["text"],
        // ... other applied types
      }
    }
  ]
}
```

### GET /health
Health check endpoint.

### GET /v1/models
List available models (for compatibility).

## Configuration

Environment variables:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `USE_BERT`: Enable BERT-based detection (default: true)
- `FLAGGING_THRESHOLD`: Threshold for flagging content (default: 0.5)
- `BERT_MODEL_NAME`: BERT model to use (default: unitary/toxic-bert)

##  PII Categories Detected

| Category | Description | Examples |
|----------|-------------|----------|
| `pii/phone` |  phone numbers | 030-12345678, +49 30 12345678, 0172-9876543 |
| `pii/email` | Email addresses | user@domain.de |
| `pii/credit_card` | Credit card numbers | 4532-1234-5678-9012 |
| `pii/ip_address` | IP addresses | 192.168.1.1 |
| `pii/iban` | IBAN code | DE89 3704 0044 0532 0130 00 |

## Development

The project structure:
```
├── main.py                 # FastAPI application
├── models.py              # Pydantic models
├── service.py             # Moderation service logic
├── checkers/              # Detection modules
│   ├── __init__.py
│   ├── regex_checker.py   # Regex-based  PII detection
│   └── bert_checker.py    # BERT-based detection
├── test_client.py         # Test client with  examples
└── requirements.txt       # Dependencies
```