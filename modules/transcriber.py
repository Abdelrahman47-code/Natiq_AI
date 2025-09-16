import whisper
import os
import tempfile
import subprocess
from pydub import AudioSegment

model = whisper.load_model("small")

def transcribe(audio_path: str, lang="auto", chunk_sec=180):
    """
    Transcribe long audio by splitting into chunks and merging results.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(audio_path)

    # Convert to wav (16kHz mono PCM)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        tmp_path = tmp_wav.name
    subprocess.run([
        "ffmpeg", "-y", "-i", audio_path,
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", tmp_path
    ], check=True)

    # Load audio
    audio = AudioSegment.from_wav(tmp_path)
    os.remove(tmp_path)

    # Split into chunks
    chunks = []
    for i in range(0, len(audio), chunk_sec * 1000):  # ms
        chunks.append(audio[i:i + chunk_sec * 1000])

    full_text = []
    options = {}
    if lang != "auto":
        options["language"] = lang

    for idx, chunk in enumerate(chunks):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as c_wav:
            c_path = c_wav.name
        chunk.export(c_path, format="wav")

        result = model.transcribe(c_path, **options, verbose=False)
        full_text.append(result["text"])
        os.remove(c_path)

    return " ".join(full_text).strip()
