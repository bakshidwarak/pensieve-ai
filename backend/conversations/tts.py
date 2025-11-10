"""Text-to-speech utilities for conversation roleplay."""

import os
from pathlib import Path
from openai import OpenAI
import uuid

# Initialize OpenAI client
client = OpenAI()

# Ensure uploads directory exists
UPLOADS_DIR = Path(__file__).parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def generate_speech(text: str, gender: str = "male") -> str:
    """Generate speech from text using OpenAI TTS.

    Args:
        text: The text to convert to speech
        gender: 'male' or 'female' for voice selection

    Returns:
        Relative path to the generated audio file (e.g., "/uploads/filename.mp3")
    """

    # Select voice based on gender
    # OpenAI TTS voices: alloy, echo, fable, onyx, nova, shimmer
    # Male voices: alloy, echo, fable, onyx
    # Female voices: nova, shimmer
    voice = "onyx" if gender == "male" else "nova"

    # Generate unique filename
    filename = f"tts_{uuid.uuid4()}.mp3"
    file_path = UPLOADS_DIR / filename

    # Generate speech
    response = client.audio.speech.create(
        model="tts-1",  # or "tts-1-hd" for higher quality
        voice=voice,
        input=text
    )

    # Save to file
    response.stream_to_file(str(file_path))

    # Return relative URL path
    return f"/uploads/{filename}"
