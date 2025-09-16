import os
import requests
import json
from dotenv import load_dotenv
from modules.chunker import chunk_text

# Load API Key for OpenRouter
load_dotenv()
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Default model for sentiment
DEFAULT_MODEL = "mistralai/mistral-7b-instruct"


def analyze_sentiment(text: str, model: str = DEFAULT_MODEL, max_len: int = 2000):
    """
    Analyze sentiment using OpenRouter LLM.
    Handles long text by chunking automatically.
    Returns structured dict with aggregated label, score, and explanation.
    """
    if not text.strip():
        return {"label": "NEUTRAL", "score": 0.0, "explanation": "No input text provided."}

    # Split text into manageable chunks
    chunks = chunk_text(text, max_len=max_len)
    results = []

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for idx, chunk in enumerate(chunks, 1):
        prompt = f"""
        Analyze the sentiment of the following text (English or Arabic).
        Respond in JSON with keys: label (POSITIVE, NEGATIVE, NEUTRAL), score (0-1), and explanation.

        Text (part {idx}/{len(chunks)}):
        {chunk}
        """

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 300
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"OpenRouter API Error {response.status_code}: {response.text}")

        raw_output = response.json()["choices"][0]["message"]["content"].strip()

        try:
            result = json.loads(raw_output)
        except Exception:
            # fallback: wrap raw text
            result = {"label": "NEUTRAL", "score": 0.0, "explanation": raw_output}

        results.append(result)

    # Aggregate results across chunks
    if len(results) == 1:
        return results[0]

    from collections import Counter
    avg_score = sum(r.get("score", 0.0) for r in results) / len(results)
    labels = [r.get("label", "NEUTRAL").upper() for r in results]
    explanation = "\n\n".join(r.get("explanation", "") for r in results)
    majority_label = Counter(labels).most_common(1)[0][0]

    return {"label": majority_label, "score": avg_score, "explanation": explanation}
