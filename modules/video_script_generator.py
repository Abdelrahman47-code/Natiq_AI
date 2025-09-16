import requests
from gtts import gTTS
import uuid
import os
import math
from dotenv import load_dotenv
from modules.chunker import chunk_text

# Load API Key
load_dotenv()
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")


def _call_openrouter(prompt: str, model: str, max_tokens: int = 600):
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

    return response.json()["choices"][0]["message"]["content"].strip()


def generate_structured_video_script(topic: str, style: str = "educational",
                                     duration: int = 5,
                                     model: str = "mistralai/mistral-7b-instruct"):
    """
    Generate a structured video script with Intro, Body (sequence), Conclusion.
    Duration in minutes determines total length.
    """

    words_per_minute = 150
    target_words = duration * words_per_minute
    body_word_count = int(target_words * 0.7)
    intro_word_count = int(target_words * 0.15)
    conclusion_word_count = target_words - (body_word_count + intro_word_count)

    # Intro
    intro_prompt = f"Write an engaging introduction for a {style} video script about {topic}. Limit to {intro_word_count} words."
    intro = _call_openrouter(intro_prompt, model, max_tokens=intro_word_count + 100)

    # Body (sequence chunks)
    body_chunks = []
    chunk_size = 400
    num_chunks = math.ceil(body_word_count / chunk_size)

    for i in range(num_chunks):
        body_prompt = (
            f"Write part {i+1} of a {style} video script about {topic}. "
            f"This should be a sequential narrative continuing the topic. "
            f"Limit to {chunk_size} words."
        )
        body_chunks.append(_call_openrouter(body_prompt, model, max_tokens=chunk_size + 100))

    body = " ".join(body_chunks)

    # Conclusion
    conclusion_prompt = f"Write a clear conclusion for a {style} video script about {topic}. Limit to {conclusion_word_count} words."
    conclusion = _call_openrouter(conclusion_prompt, model, max_tokens=conclusion_word_count + 100)

    # Final script
    script_text = f"{intro}\n\n{body}\n\n{conclusion}"

    # Apply chunking
    script_chunks = chunk_text(script_text, max_len=500)

    # JSON structure
    script_json = {
        "title": topic,
        "style": style,
        "duration_minutes": duration,
        "sections": {
            "intro": intro,
            "body": body,
            "conclusion": conclusion
        },
        "narration": script_text,
        "chunks": script_chunks
    }

    return script_text, script_json


def video_to_audio(script_text: str, lang="en"):
    """Convert video script narration into one MP3 file."""
    os.makedirs("temp", exist_ok=True)
    filename = f"temp/{uuid.uuid4().hex}_video_script.mp3"
    tts = gTTS(text=script_text, lang=lang, tld="com")
    tts.save(filename)
    return filename
