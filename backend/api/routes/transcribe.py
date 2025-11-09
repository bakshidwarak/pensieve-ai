"""Voice transcription endpoints using OpenAI Whisper."""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from openai import OpenAI
from backend.core.config import settings
from backend.core.schemas import TranscribeResponse

router = APIRouter()

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


@router.post("/", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form(default="en")
):
    """
    Transcribe audio file using OpenAI Whisper API.

    Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm

    - **file**: Audio file to transcribe
    - **language**: Language code (default: 'en' for English)
    """
    # Validate file type
    allowed_extensions = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    try:
        # Read file content
        content = await file.read()

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Transcribe using Whisper
            with open(temp_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"  # Get detailed response
                )

            # Extract information
            text = transcript.text
            duration = getattr(transcript, 'duration', None)
            detected_language = getattr(transcript, 'language', language)

            return TranscribeResponse(
                text=text,
                duration=duration,
                language=detected_language
            )

        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/from-recording", response_model=TranscribeResponse)
async def transcribe_recording(
    audio_data: UploadFile = File(...),
    language: str = Form(default="en")
):
    """
    Transcribe audio from browser recording (typically webm format).

    This endpoint is optimized for browser-based audio recordings.

    - **audio_data**: Audio blob from browser MediaRecorder
    - **language**: Language code
    """
    return await transcribe_audio(file=audio_data, language=language)
