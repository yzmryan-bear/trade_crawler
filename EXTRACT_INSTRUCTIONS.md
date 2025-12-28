# PDF to JSON Extraction Instructions

## Prerequisites

1. **Install PDF library:**
   ```bash
   pip install pdfplumber
   # OR
   pip install PyPDF2
   ```

2. **Install OpenAI library (for translation):**
   ```bash
   pip install openai
   ```

3. **Set OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   Or create a `.env` file in the project root with:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Running the Extraction

```bash
python3 extract_pdf_to_json.py
```

The script will:
1. Extract text from `2024:10-2025:08_yuanzidan_dc_track.pdf`
2. Parse messages (sender, time, content)
3. Translate Chinese messages to English
4. Save to `dc_tracker.json`

## Output Format

The JSON file will contain an array of messages, each with:
```json
{
  "sender": "Sender Name",
  "send_time": "2024-10-15 14:30",
  "message": "Translated English message",
  "original_message": "Original Chinese message (if translated)"
}
```

## Troubleshooting

If messages aren't parsed correctly:
1. Check `pdf_extracted_text_sample.txt` to see the raw extracted text
2. The parsing function may need adjustment based on your PDF format
3. Common Discord export formats are supported, but custom formats may need custom parsing

