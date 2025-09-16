import os
import requests
import json
from dotenv import load_dotenv
from modules.chunker import chunk_text

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-nemo-instruct-2407"


def diarize_transcript(transcript: str, model: str = MODEL):
    """
    Diarize transcript in chunks and merge results into a single JSON.
    """
    if not transcript.strip():
        return [{"speaker": "Unknown", "text": ""}]

    # Use chunker from modules
    chunks = chunk_text(transcript, max_len=2500)
    all_segments = []

    for idx, chunk in enumerate(chunks, 1):
        prompt = f"""
        You are a diarization assistant.
        Split the following conversation into speaker turns.
        Assign speaker labels (Speaker 1, Speaker 2, etc.) consistently.

        Transcript (part {idx}/{len(chunks)}):
        {chunk}

        Return the result as JSON list of objects with keys: "speaker", "text".
        """

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 2000
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()

        result_text = response.json()["choices"][0]["message"]["content"].strip()

        try:
            part_json = json.loads(result_text)
            all_segments.extend(part_json)
        except Exception:
            all_segments.append({"speaker": f"Part {idx}", "text": result_text})

    return all_segments


def format_pretty_output(segments):
    """
    Format diarization results as chat-style text (for Telegram/Email).
    """
    pretty = ""
    for seg in segments:
        speaker = seg.get("speaker", "Unknown")
        text = seg.get("text", "")
        pretty += f"👤 {speaker}\n{text}\n\n"
    return pretty.strip()
