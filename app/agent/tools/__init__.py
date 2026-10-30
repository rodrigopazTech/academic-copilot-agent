from .meeting_retriever import search_meeting_recordings
from .transcript_loader import load_class_transcript
from .syllabus_auditor import audit_curriculum_alignment
from .action_tracker import extract_commitments_and_homework
from .material_generator import generate_next_class_package

ALL_TOOLS = [
    search_meeting_recordings,
    load_class_transcript,
    audit_curriculum_alignment,
    extract_commitments_and_homework,
    generate_next_class_package,
]
