import requests
import os
from dotenv import load_dotenv
from transformers import pipeline
from modules.chunker import chunk_text

# Load API Key for OpenRouter
load_dotenv()
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")

# MODELS CONFIG
EN_MODEL = "facebook/bart-large-cnn"
AR_MODEL = "csebuetnlp/mT5_multilingual_XLSum"

# Lazy init
_en_summarizer = None
_ar_summarizer = None


def load_classic_summarizers():
    """Lazy load BART (EN) and mT5 (AR)."""
    global _en_summarizer, _ar_summarizer
    if _en_summarizer is None:
        _en_summarizer = pipeline("summarization", model=EN_MODEL, tokenizer=EN_MODEL, device=0)
    if _ar_summarizer is None:
        _ar_summarizer = pipeline("summarization", model=AR_MODEL, tokenizer=AR_MODEL, device=0)


def summarize_classic(text: str, lang="en") -> str:
    """Summarize using BART (EN) or mT5 (AR) with chunking."""
    load_classic_summarizers()
    chunks = chunk_text(text, max_len=800)

    summaries = []
    for ch in chunks:
        if lang == "ar":
            out = _ar_summarizer(ch, max_length=200, min_length=50, do_sample=False)
        else:
            out = _en_summarizer(ch, max_length=150, min_length=40, do_sample=False)
        summaries.append(out[0]["summary_text"])

    return "\n".join([f"- {s}" for s in summaries])


def summarize_llm(text: str, lang="en", model: str = "mistralai/mistral-7b-instruct", max_length: int = 500) -> str:
    """Summarize using OpenRouter LLM with chunking."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    chunks = chunk_text(text, max_len=800)
    summaries = []

    for ch in chunks:
        messages = [
            {"role": "system", "content": f"You are a helpful assistant that summarizes {lang.upper()} text into clear bullet points."},
            {"role": "user", "content": f"Summarize this:\n\n{ch}"}
        ]
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_length
        }
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")

        summaries.append(response.json()["choices"][0]["message"]["content"].strip())

    return "\n".join([f"- {s}" for s in summaries])



def summarize_text(text: str, lang="en", mode="classic") -> str:
    """
    Wrapper for summarization.
    """
    if mode == "llm":
        return summarize_llm(text, lang=lang)
    return summarize_classic(text, lang=lang)
