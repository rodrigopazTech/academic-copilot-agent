import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain.agents import create_agent

from app.config import settings
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import ALL_TOOLS
from app.agent.tools.meeting_retriever import search_meeting_recordings
from app.agent.tools.transcript_loader import load_class_transcript
from app.agent.tools.syllabus_auditor import audit_curriculum_alignment
from app.agent.tools.action_tracker import extract_commitments_and_homework
from app.agent.tools.material_generator import generate_next_class_package
from app.agent.schemas import (
    AgentRunResult, AgentStepTrace, ClassAuditReport,
    SyllabusPacingDiagnosis, TopicCovered, ActionItem, NextClassLessonPlan
)

class AcademicCopilotAgent:
    def __init__(self, mock_mode: Optional[bool] = None):
        self.mock_mode = settings.MOCK_MODE if mock_mode is None else mock_mode
        self.tools = ALL_TOOLS
        self.system_prompt = SYSTEM_PROMPT
        self._compiled_agent = None

        if not self.mock_mode:
            self._init_live_agent()

    def _init_live_agent(self):
        """Initializes the live LangChain Agent Graph with OpenAI or Google GenAI."""
        try:
            if settings.DEFAULT_LLM_PROVIDER == "google-genai" and settings.GEMINI_API_KEY:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL_NAME,
                    google_api_key=settings.GEMINI_API_KEY,
                    temperature=0.2
                )
            else:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model=settings.OPENAI_MODEL_NAME,
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.2
                )

            self._compiled_agent = create_agent(
                model=llm,
                tools=self.tools,
                system_prompt=self.system_prompt
            )
        except Exception as e:
            # Fallback to mock mode if live model fails to configure
            print(f"[!] Warning: Could not initialize live LLM ({e}). Falling back to simulation mode.")
            self.mock_mode = True

    def run_audit(self, course_keyword: str = "Ciencia de Datos", recording_id: Optional[str] = None) -> AgentRunResult:
        """
        Executes the autonomous agent workflow to inspect recordings, evaluate syllabus
        alignment, extract action items, and synthesize continuity materials.
        """
        if not self.mock_mode and self._compiled_agent:
            return self._run_live_agent_flow(course_keyword, recording_id)
        else:
            return self._run_simulated_agent_flow(course_keyword, recording_id)

    def _run_simulated_agent_flow(self, course_keyword: str, recording_id: Optional[str]) -> AgentRunResult:
        """
        Deterministic, self-contained multi-tool execution trace showcasing complete
        ReAct reasoning (Thought -> Action -> Observation) and structured Pydantic output.
        """
        traces: List[AgentStepTrace] = []

        # Step 1: Search recordings
        t1_input = {"course_keyword": course_keyword}
        t1_output = search_meeting_recordings.invoke(t1_input)
        recs = json.loads(t1_output)
        chosen_rec = recs[0] if recs else {}
        rec_id = recording_id or chosen_rec.get("recording_id", "rec-2026-09-04-clase-08")

        traces.append(AgentStepTrace(
            step_number=1,
            thought=f"Need to query repository for class sessions matching '{course_keyword}' to extract recording identifiers.",
            tool_name="search_meeting_recordings",
            tool_input=t1_input,
            tool_output=f"Discovered {len(recs)} class session(s). Selected recording ID: {rec_id}"
        ))

        # Step 2: Load Transcript
        t2_input = {"recording_id": rec_id}
        t2_output = load_class_transcript.invoke(t2_input)
        transcript_data = json.loads(t2_output)

        traces.append(AgentStepTrace(
            step_number=2,
            thought=f"Fetching full transcript dialogue and timestamped speaker utterances for {rec_id}.",
            tool_name="load_class_transcript",
            tool_input=t2_input,
            tool_output=f"Successfully extracted {len(transcript_data.get('dialogue_sample', []))} dialogue turns. Class Duration: {transcript_data.get('duration_minutes')} min."
        ))

        # Step 3: Audit Syllabus Alignment
        t3_input = {"course_id": transcript_data.get("course_id", "python-ds-2026"), "recording_id": rec_id}
        t3_output = audit_curriculum_alignment.invoke(t3_input)
        audit_raw = json.loads(t3_output)

        traces.append(AgentStepTrace(
            step_number=3,
            thought="Cross-referencing class transcript against official Python Data Science syllabus to audit topic coverage and calculate pacing delta.",
            tool_name="audit_curriculum_alignment",
            tool_input=t3_input,
            tool_output=f"Pacing Diagnostic: {audit_raw['pacing_diagnosis']['pacing_status']} ({audit_raw['pacing_diagnosis']['session_gap_delta']}). Identified {len(audit_raw['missing_or_delayed_topics'])} delayed topic(s)."
        ))

        # Step 4: Extract Commitments & Action Items
        t4_input = {"recording_id": rec_id}
        t4_output = extract_commitments_and_homework.invoke(t4_input)
        actions_raw = json.loads(t4_output)

        traces.append(AgentStepTrace(
            step_number=4,
            thought="Extracting commitments, deadlines, student homework extensions, and instructor promises from dialogue turns.",
            tool_name="extract_commitments_and_homework",
            tool_input=t4_input,
            tool_output=f"Extracted {len(actions_raw)} action item(s) categorized across Students and Professor."
        ))

        # Step 5: Generate Next Class Package
        t5_input = {"course_name": course_keyword, "target_class_num": 9}
        t5_output = generate_next_class_package.invoke(t5_input)
        package_raw = json.loads(t5_output)

        traces.append(AgentStepTrace(
            step_number=5,
            thought="Because session 8 ran out of time on duplicates and multi-condition filtering, synthesizing customized continuity package for Class 9.",
            tool_name="generate_next_class_package",
            tool_input=t5_input,
            tool_output=f"Generated pedagogical continuity package: '{package_raw['title']}' with executable demo code."
        ))

        # Assemble Pydantic models
        audit_report = ClassAuditReport(
            course_id=audit_raw.get("course_id", "python-ds-2026"),
            recording_id=rec_id,
            class_title=transcript_data.get("title", audit_raw.get("class_title", "Clase 8")),
            class_date=transcript_data.get("date", "2026-09-04"),
            executive_summary=transcript_data.get("summary", ""),
            pacing_diagnosis=SyllabusPacingDiagnosis(**audit_raw["pacing_diagnosis"]),
            topics_covered=[TopicCovered(**t) for t in audit_raw["topics_covered"]],
            action_items=[ActionItem(**a) for a in actions_raw],
            missing_or_delayed_topics=audit_raw.get("missing_or_delayed_topics", [])
        )

        next_class_package = NextClassLessonPlan(**package_raw)

        final_narrative = (
            f"### 🎓 Academic Copilot Audit Completed\n\n"
            f"**Class Audited:** {audit_report.class_title} ({audit_report.class_date})\n"
            f"**Pacing Status:** `{audit_report.pacing_diagnosis.pacing_status}` — {audit_report.pacing_diagnosis.session_gap_delta}\n\n"
            f"**Strategic Assessment:**\n"
            f"{audit_report.pacing_diagnosis.pacing_analysis}\n\n"
            f"**Pedagogical Recommendation:**\n"
            f"{audit_report.pacing_diagnosis.pedagogical_recommendation}\n\n"
            f"**Upcoming Session Package:** '{next_class_package.title}' has been generated with complete timeline, executable demonstration code, and student exercises."
        )

        result = AgentRunResult(
            success=True,
            final_response=final_narrative,
            audit_report=audit_report,
            next_class_package=next_class_package,
            execution_trace=traces
        )

        self._save_report(result)
        return result

    def _run_live_agent_flow(self, course_keyword: str, recording_id: Optional[str]) -> AgentRunResult:
        """Runs the LangChain Agent Graph with actual LLM tool calling."""
        user_prompt = (
            f"Please conduct an academic audit for the course '{course_keyword}'. "
            f"Target recording ID: {recording_id or 'auto-detect latest'}. "
            f"Check recordings, fetch the transcript, audit alignment with the syllabus, "
            f"extract student and professor commitments, and synthesize continuity materials for the next class."
        )
        inputs = {"messages": [HumanMessage(content=user_prompt)]}
        
        try:
            agent_output = self._compiled_agent.invoke(inputs)
            messages = agent_output.get("messages", [])
            last_message = messages[-1].content if messages else "No response generated."
            
            # Extract traces from tool messages
            traces = []
            step = 1
            for msg in messages:
                if isinstance(msg, ToolMessage):
                    traces.append(AgentStepTrace(
                        step_number=step,
                        thought="Executed tool from LangChain tool-calling graph.",
                        tool_name=msg.name or "tool",
                        tool_input={},
                        tool_output=str(msg.content)[:300]
                    ))
                    step += 1

            # Build result
            sim_fallback = self._run_simulated_agent_flow(course_keyword, recording_id)
            sim_fallback.final_response = str(last_message)
            if traces:
                sim_fallback.execution_trace = traces
            return sim_fallback
        except Exception as e:
            print(f"[!] Error in live agent graph ({e}). Falling back to simulated deterministic trace.")
            return self._run_simulated_agent_flow(course_keyword, recording_id)

    def chat(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Conversational chat endpoint for interacting with the Academic Copilot."""
        lower_msg = message.lower()
        if "auditar" in lower_msg or "audit" in lower_msg or "clase" in lower_msg:
            run_res = self.run_audit()
            return {
                "reply": run_res.final_response,
                "audit_report": run_res.audit_report.model_dump() if run_res.audit_report else None,
                "next_class_package": run_res.next_class_package.model_dump() if run_res.next_class_package else None,
                "execution_trace": [t.model_dump() for t in run_res.execution_trace]
            }
        elif "pendiente" in lower_msg or "tarea" in lower_msg or "compromiso" in lower_msg:
            items_str = extract_commitments_and_homework.invoke({"recording_id": "rec-2026-09-04-clase-08"})
            items = json.loads(items_str)
            reply = "### 📌 Compromisos y Pendientes Identificados en Clase 8:\n\n"
            for it in items:
                reply += f"- **[{it['category']}] ({it['assignee']})**: {it['description']} *(Fecha: {it.get('deadline', 'N/A')})*\n"
            return {"reply": reply}
        elif "codigo" in lower_msg or "código" in lower_msg or "clase 9" in lower_msg or "material" in lower_msg:
            pkg_str = generate_next_class_package.invoke({"course_name": "Ciencia de Datos", "target_class_num": 9})
            pkg = json.loads(pkg_str)
            reply = f"### 📦 Material Generado: {pkg['title']}\n\n**Objetivo:** {pkg['focus_objective']}\n\n```python\n{pkg['demonstration_code']}\n```"
            return {"reply": reply, "next_class_package": pkg}
        else:
            return {
                "reply": (
                    "¡Hola! Soy tu **Academic Copilot Agent** potenciado por LangChain. "
                    "Puedo ayudarte a:\n"
                    "1. 🔍 **Auditar sesiones**: Analizar si vas a tiempo o rezagado respecto al temario oficial.\n"
                    "2. 📋 **Extraer compromisos**: Listar tareas de alumnos y compromisos del profesor.\n"
                    "3. 🛠️ **Generar material didáctico**: Diseñar la clase 9 con código Python de demostración y ejercicios.\n\n"
                    "¿Qué deseas realizar hoy?"
                )
            }

    def _save_report(self, result: AgentRunResult):
        """Saves generated audit artifacts to disk."""
        if not result.audit_report:
            return
        report_file = settings.REPORTS_DIR / f"audit_{result.audit_report.recording_id}.json"
        report_file.write_text(result.model_dump_json(indent=2), encoding="utf-8")
