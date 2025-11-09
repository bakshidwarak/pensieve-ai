import openai
import os
import tempfile
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")

def transcribe_audio_bytes_blocking(audio_bytes: bytes, filename_hint: str = "audio_chunk.webm") -> str:
    fd, tmp_path = tempfile.mkstemp(suffix=os.path.splitext(filename_hint)[1] or ".webm")
    os.close(fd)
    with open(tmp_path, "wb") as f:
        f.write(audio_bytes)

    try:
        with open(tmp_path, "rb") as audio_file:
            resp = openai.Audio.transcribe("whisper-1", audio_file)
            text = resp.get("text") if isinstance(resp, dict) else str(resp)
    except Exception as e:
        print("transcription error", e)
        text = ""
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass
    return text
