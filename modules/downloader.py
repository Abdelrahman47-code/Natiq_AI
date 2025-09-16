import os
import yt_dlp
from pydub import AudioSegment

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def save_file(uploaded_file):
    """Save an uploaded file locally in the temp directory."""
    path = os.path.join(TEMP_DIR, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def download_youtube(url):
    """Download audio from YouTube and convert it to WAV using yt-dlp + pydub."""
    output_path = os.path.join(TEMP_DIR, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_file = ydl.prepare_filename(info)

    # Set WAV file name
    base, _ = os.path.splitext(downloaded_file)
    wav_path = f"{base}.wav"

    # Convert audio using pydub
    audio = AudioSegment.from_file(downloaded_file)
    audio.export(wav_path, format="wav")

    return wav_path
