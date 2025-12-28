# Trading Action Extraction Agent

An agentic application that extracts trading actions (buy/sell, stock symbols, prices) from expert messages in Discord/Telegram channels, with initial testing support via JSON message file (dc_tracker.json).

## Project Structure

```
follow_trader/
├── src/
│   ├── platforms/      # Platform adapters (JSON, Discord, Telegram)
│   ├── extractors/     # Trading action extraction logic
│   ├── models/         # Data models (Message, TradingAction)
│   ├── storage/        # Database layer
│   ├── services/       # Business logic services
│   └── ui/             # User interface (Streamlit dashboard)
├── config/             # Configuration files
├── scripts/            # Utility scripts (PDF extraction, etc.)
├── data/               # Data files (database, etc.)
├── tests/              # Unit tests
├── dc_tracker.json     # Pre-extracted messages (619 messages)
├── requirements.txt    # Python dependencies
└── main.py            # Application entry point (to be created)
```

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy `.env.example` to `.env` (or create manually)
   - Add your LLM API key (OpenAI or Anthropic)

3. **Configure the application:**
   - Copy `config/config.yaml.example` to `config/config.yaml`
   - Update JSON file path (dc_tracker.json) and other settings as needed

## Development Status

✅ **Phase 1 Complete**: Message Extraction Agent
- ✅ Project structure setup
- ✅ Data models (Message, TradingAction)
- ✅ Platform interface and JSON adapter
- ✅ Database schema and storage
- ✅ LLM-based extraction agent
- ✅ Action validator
- ✅ Message processor service
- ✅ Streamlit monitoring dashboard
- ✅ Configuration system

## Usage

### 1. Test the Pipeline (without LLM)

```bash
python3 test_pipeline.py
```

This tests all components without making API calls.

### 2. Run Full Extraction (requires API key)

```bash
# Set your API key
export OPENAI_API_KEY="your-key-here"

# Run extraction
python3 main.py
```

This will:
- Load messages from `dc_tracker.json`
- Extract trading actions using LLM
- Store results in database
- Display statistics

### 3. View Dashboard

```bash
streamlit run streamlit_app.py
```

Opens a web dashboard to:
- View extracted trading actions
- Filter by confidence, action type, symbol
- See statistics and recent messages

## Data

The `dc_tracker.json` file contains 619 messages extracted from Discord channel exports, with the following structure:
- `sender`: Message sender name
- `send_time`: Timestamp (e.g., "10/5/2024 12:25 PM")
- `message`: Message content (currently in Chinese, can be translated using OpenAI API)

