import os
import requests
import uuid
from gtts import gTTS
from dotenv import load_dotenv
from modules.chunker import chunk_text
import re

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def clean_script(raw_text: str) -> str:
    """
    Cleans the generated script by ensuring Host/Guest prefixes
    and removing unwanted formatting.
    """
    lines = raw_text.strip().splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Ensure proper prefix
        if line.lower().startswith("host:") or line.lower().startswith("guest:"):
            cleaned_lines.append(line)
        else:
            cleaned_lines.append("Host: " + line)

    return "\n".join(cleaned_lines)

def clean_script(raw_text: str) -> str:
    """
    Cleans the generated script by ensuring only one Host/Guest prefix
    and removing unwanted formatting.
    """
    lines = raw_text.strip().splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Normalize multiple Host:/Guest: occurrences
        line = re.sub(r"^(Host:|Guest:)\s*(Host:|Guest:)?", r"\1", line, flags=re.IGNORECASE)

        if line.lower().startswith("host:") or line.lower().startswith("guest:"):
            cleaned_lines.append(line)
        else:
            cleaned_lines.append("Host: " + line)

    return "\n".join(cleaned_lines)

def _call_openrouter(prompt: str, model: str, max_tokens: int = 2000) -> str:
    """Helper to call OpenRouter API safely."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    return response.json()["choices"][0]["message"]["content"]


def generate_dialogue_script(
    topic: str,
    style: str = "informative",
    duration: int = 5,
    model: str = "mistralai/mistral-7b-instruct"
):
    """
    Generate a structured podcast dialogue with Host & Guest turns.
    Handles long durations by chunking via chunker.py.
    """
    words_per_minute = 150
    target_words = duration * words_per_minute

    # Each chunk ~2500 words max
    chunk_size = 2500
    num_chunks = max(1, target_words // chunk_size)

    scripts = []
    for i in range(num_chunks):
        prompt = (
            f"Podcast script part {i+1}/{num_chunks}.\n\n"
            f"Write a {style} podcast dialogue between a Host and a Guest "
            f"on the topic: {topic}. "
            f"Ensure alternating 'Host:' and 'Guest:' turns. "
            f"Make it natural and engaging. "
            f"Approx. {chunk_size} words in this part. "
            f"Do NOT summarize previous parts; continue fresh dialogue."
        )

        raw_text = _call_openrouter(prompt, model, max_tokens=chunk_size + 200)
        scripts.append(clean_script(raw_text))

    full_script = "\n\n".join(scripts)

    # Final safeguard split if text is still huge
    final_chunks = chunk_text(full_script, max_len=2500)
    return "\n\n".join(final_chunks)


def script_to_json(script_text: str, topic: str, style: str):
    """
    Convert raw script text into structured JSON with Host/Guest speakers.
    Uses regex to properly split turns, even if they are in one big paragraph.
    """
    dialogue = []

    # Regex splits at each "Host:" or "Guest:" while keeping the speaker
    parts = re.split(r'(?=(Host:|Guest:))', script_text)

    # Rebuild into proper speaker -> text pairs
    current_speaker = None
    buffer = []
    for part in parts:
        if part in ("Host:", "Guest:"):
            # Save previous
            if current_speaker and buffer:
                dialogue.append({
                    "speaker": current_speaker,
                    "text": " ".join(buffer).strip()
                })
            # Reset for new speaker
            current_speaker = part.replace(":", "").strip()
            buffer = []
        else:
            if part.strip():
                buffer.append(part.strip())

    # Append last one
    if current_speaker and buffer:
        dialogue.append({
            "speaker": current_speaker,
            "text": " ".join(buffer).strip()
        })

    return {
        "topic": topic,
        "style": style,
        "dialogue": dialogue
    }


def format_pretty_output(script_json: dict) -> str:
    """
    Format dialogue JSON into a pretty printable string.
    """
    lines = []
    for turn in script_json.get("dialogue", []):
        lines.append(f"{turn['speaker']}: {turn['text']}")
    return "\n".join(lines)


def dialogue_to_audio(dialogue, host_lang="en", guest_lang="en"):
    """
    Convert dialogue into one MP3 audio file.
    """
    os.makedirs("temp", exist_ok=True)
    filename = f"temp/{uuid.uuid4().hex}_podcast.mp3"

    full_text = " ".join([f"{turn['speaker']}: {turn['text']}" for turn in dialogue])
    tts = gTTS(text=full_text, lang=host_lang, tld="com")
    tts.save(filename)

    return filename
