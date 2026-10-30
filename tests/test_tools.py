import json
import pytest
from app.agent.tools.meeting_retriever import search_meeting_recordings
from app.agent.tools.transcript_loader import load_class_transcript
from app.agent.tools.syllabus_auditor import audit_curriculum_alignment
from app.agent.tools.action_tracker import extract_commitments_and_homework
from app.agent.tools.material_generator import generate_next_class_package

def test_search_meeting_recordings():
    output = search_meeting_recordings.invoke({"course_keyword": "Ciencia de Datos"})
    data = json.loads(output)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "recording_id" in data[0]

def test_load_class_transcript():
    output = load_class_transcript.invoke({"recording_id": "rec-2026-09-04-clase-08"})
    data = json.loads(output)
    assert data["recording_id"] == "rec-2026-09-04-clase-08"
    assert "summary" in data

def test_audit_curriculum_alignment():
    output = audit_curriculum_alignment.invoke({
        "course_id": "python-ds-2026",
        "recording_id": "rec-2026-09-04-clase-08"
    })
    data = json.loads(output)
    assert "pacing_diagnosis" in data
    assert data["pacing_diagnosis"]["pacing_status"] == "Behind Schedule"
    assert len(data["topics_covered"]) > 0

def test_extract_commitments_and_homework():
    output = extract_commitments_and_homework.invoke({"recording_id": "rec-2026-09-04-clase-08"})
    data = json.loads(output)
    assert isinstance(data, list)
    assert len(data) >= 3
    assert any(item["assignee"] == "Students" for item in data)
    assert any(item["assignee"] == "Professor" for item in data)

def test_generate_next_class_package():
    output = generate_next_class_package.invoke({
        "course_name": "Ciencia de Datos",
        "target_class_num": 9
    })
    data = json.loads(output)
    assert data["target_class_number"] == 9
    assert "demonstration_code" in data
    assert "import pandas as pd" in data["demonstration_code"]
