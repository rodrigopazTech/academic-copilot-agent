import pytest
from app.agent.core import AcademicCopilotAgent

def test_agent_run_audit_simulation():
    agent = AcademicCopilotAgent(mock_mode=True)
    result = agent.run_audit(course_keyword="Ciencia de Datos", recording_id="rec-2026-09-04-clase-08")

    assert result.success is True
    assert result.audit_report is not None
    assert result.audit_report.pacing_diagnosis.pacing_status == "Behind Schedule"
    assert len(result.execution_trace) == 5
    assert result.next_class_package is not None
    assert result.next_class_package.target_class_number == 9

def test_agent_chat_query():
    agent = AcademicCopilotAgent(mock_mode=True)
    resp = agent.chat("¿Cuáles son los compromisos y tareas pendientes?")
    assert "reply" in resp
    assert "Compromisos" in resp["reply"] or "Tarea" in resp["reply"]
