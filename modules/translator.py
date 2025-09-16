import os
import requests
from dotenv import load_dotenv
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from modules.chunker import chunk_text

# Load OpenRouter key
load_dotenv()
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")

# MODELS CONFIG
EN_AR_MODEL = "Helsinki-NLP/opus-mt-en-ar"
AR_EN_MODEL = "Helsinki-NLP/opus-mt-ar-en"

# Lazy init
_en_ar = None
_ar_en = None

# Custom cache dir
MODEL_DIR = os.path.join(os.getcwd(), "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def load_classic_models():
    """Lazy load Opus MT models."""
    global _en_ar, _ar_en
    if _en_ar is None:
        _en_ar = pipeline(
            "translation",
            model=AutoModelForSeq2SeqLM.from_pretrained(EN_AR_MODEL, cache_dir=MODEL_DIR),
            tokenizer=AutoTokenizer.from_pretrained(EN_AR_MODEL, cache_dir=MODEL_DIR)
        )
    if _ar_en is None:
        _ar_en = pipeline(
            "translation",
            model=AutoModelForSeq2SeqLM.from_pretrained(AR_EN_MODEL, cache_dir=MODEL_DIR),
            tokenizer=AutoTokenizer.from_pretrained(AR_EN_MODEL, cache_dir=MODEL_DIR)
        )


def translate_classic(text: str, target_lang="en") -> str:
    """Classic translation using HuggingFace + chunking."""
    if not text.strip():
        return ""

    load_classic_models()
    chunks = chunk_text(text, max_len=200)
    outputs = []

    for ch in chunks:
        if target_lang == "ar":
            res = _en_ar(ch)
        elif target_lang == "en":
            res = _ar_en(ch)
        else:
            res = [{"translation_text": ch}]
        outputs.append(res[0]["translation_text"])

    return "\n".join(outputs)


def translate_llm(text: str, target_lang="en", model="mistralai/mistral-7b-instruct") -> str:
    """LLM translation using OpenRouter + chunking."""
    if not text.strip():
        return ""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    chunks = chunk_text(text, max_len=300)
    outputs = []

    for ch in chunks:
        messages = [
            {"role": "system", "content": f"You are a professional translator. Translate to {target_lang.upper()} with good formatting."},
            {"role": "user", "content": ch}
        ]
        payload = {"model": model, "messages": messages, "max_tokens": 800}
        resp = requests.post(API_URL, headers=headers, json=payload)
        if resp.status_code != 200:
            raise Exception(f"API Error {resp.status_code}: {resp.text}")
        outputs.append(resp.json()["choices"][0]["message"]["content"].strip())

    return "\n".join(outputs)


def translate_text(text: str, target_lang="en", mode="classic") -> str:
    """Wrapper for translation."""
    if mode == "llm":
        return translate_llm(text, target_lang=target_lang)
    return translate_classic(text, target_lang=target_lang)
