import os
import requests
from dotenv import load_dotenv
from modules.chunker import chunk_text

# Load env
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_MODEL = "mistralai/mistral-nemo-instruct-2407"


def answer_question(question: str, context: str, model: str = DEFAULT_MODEL):
    """
    Ask the selected model (via OpenRouter) to answer the question based on context.
    Handles long context via chunking.
    """
    if not question.strip() or not context.strip():
        return "⚠️ No question or context provided."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    chunks = chunk_text(context, max_len=2500)
    answers = []

    for idx, chunk in enumerate(chunks, 1):
        prompt = f"""
        You are a Question Answering assistant. 
        Answer the question strictly based on the given context. 
        If the answer is not in the context, reply with: "Answer not found in context."

        Context (part {idx}/{len(chunks)}):
        {chunk}

        Question:
        {question}
        """

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 500
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()

        answers.append(response.json()["choices"][0]["message"]["content"].strip())

    # Merge answers, remove duplicates
    merged = "\n\n".join([a for a in answers if "Answer not found" not in a])

    return merged if merged else "❌ Answer not found in transcript."


def format_pretty_history(history):
    """
    Format full Q&A history for Telegram/Email.
    """
    output = "📚 Q&A Session Log:\n\n"
    for i, qa_pair in enumerate(history, 1):
        q, a = qa_pair["q"], qa_pair["a"]
        output += f"❓ Question{i}: {q}\n✅ Answer{i}: {a}\n\n"
    return output.strip()

