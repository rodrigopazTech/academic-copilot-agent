from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.agent.core import AcademicCopilotAgent
from app.agent.schemas import AgentRunResult
from app.agent.tools import ALL_TOOLS
from app.config import settings

router = APIRouter(prefix="/api", tags=["Agent"])
agent = AcademicCopilotAgent()

class AuditRequest(BaseModel):
    course_keyword: str = Field(default="Ciencia de Datos", description="Course name or search filter")
    recording_id: Optional[str] = Field(default=None, description="Specific recording ID to audit")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt or question to the Academic Copilot")
    history: Optional[List[Dict[str, str]]] = Field(default=None, description="Conversation history")

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mock_mode": settings.MOCK_MODE,
        "default_llm": settings.DEFAULT_LLM_PROVIDER
    }

@router.post("/agent/run", response_model=AgentRunResult)
def run_agent_workflow(req: AuditRequest):
    """
    Triggers the autonomous LangChain Agent to audit the class session,
    measure syllabus alignment, extract action items, and synthesize upcoming materials.
    """
    try:
        result = agent.run_audit(
            course_keyword=req.course_keyword,
            recording_id=req.recording_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")

@router.post("/agent/chat")
def chat_with_agent(req: ChatRequest):
    """
    Interactive conversation with the Academic Copilot Agent.
    """
    try:
        response = agent.chat(message=req.message, history=req.history)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/agent/tools")
def get_registered_tools():
    """
    Returns metadata and JSON schemas of all LangChain tools available to the Agent.
    """
    tools_info = []
    for t in ALL_TOOLS:
        tools_info.append({
            "name": t.name,
            "description": t.description,
            "args_schema": getattr(t, "args", {})
        })
    return {"registered_tools": tools_info}

@router.get("/agent/reports")
def list_saved_reports():
    """
    Lists historical audit reports persisted on disk.
    """
    reports = []
    if settings.REPORTS_DIR.exists():
        for file in settings.REPORTS_DIR.glob("audit_*.json"):
            import json
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                audit_rep = data.get("audit_report", {})
                reports.append({
                    "file_name": file.name,
                    "recording_id": audit_rep.get("recording_id"),
                    "class_title": audit_rep.get("class_title"),
                    "date": audit_rep.get("class_date"),
                    "pacing_status": audit_rep.get("pacing_diagnosis", {}).get("pacing_status")
                })
            except Exception:
                continue
    return {"reports": reports}
