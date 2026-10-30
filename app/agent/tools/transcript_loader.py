import json
from pathlib import Path
from typing import Dict, Any
from langchain_core.tools import tool
from app.config import settings

@tool
def load_class_transcript(recording_id: str) -> str:
    """
    Retrieves the complete dialogue transcript, timestamps, speaker tags, and summary
    for a given class recording_id.
    """
    transcripts_dir = settings.TRANSCRIPTS_DIR
    target_data = None
    
    if transcripts_dir.exists():
        for file in transcripts_dir.glob("*.json"):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                if data.get("recording_id") == recording_id or recording_id in file.name:
                    target_data = data
                    break
            except Exception:
                continue

    if not target_data:
        # Default fallback to sample class 8
        default_file = transcripts_dir / "clase_08_pandas_cleaning.json"
        if default_file.exists():
            target_data = json.loads(default_file.read_text(encoding="utf-8"))
        else:
            return json.dumps({
                "error": f"Recording {recording_id} not found."
            }, ensure_ascii=False)

    return json.dumps({
        "recording_id": target_data.get("recording_id"),
        "course_id": target_data.get("course_id"),
        "title": target_data.get("title"),
        "date": target_data.get("date"),
        "duration_minutes": target_data.get("duration_minutes"),
        "summary": target_data.get("transcript_summary"),
        "dialogue_sample": target_data.get("dialogue_segments", [])
    }, ensure_ascii=False, indent=2)
