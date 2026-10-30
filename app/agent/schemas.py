from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class TopicCovered(BaseModel):
    topic: str = Field(description="Name of the topic or concept addressed in class")
    syllabus_module: str = Field(description="Associated official syllabus module and class number")
    coverage_level: Literal["Introduced", "Partially Covered", "Fully Mastered"] = Field(
        default="Fully Mastered",
        description="Depth to which the concept was taught"
    )
    key_takeaways: str = Field(description="Summary of how it was explained and examples used")

class ActionItem(BaseModel):
    category: Literal["Student Homework", "Professor Commitment", "Grading / Review", "Pending Doubt"] = Field(
        description="Type of task or commitment"
    )
    description: str = Field(description="Clear, actionable task description")
    assignee: Literal["Students", "Professor", "Both"] = Field(description="Owner of the task")
    deadline: Optional[str] = Field(default=None, description="Due date or session if mentioned")
    priority: Literal["Low", "Medium", "High", "Critical"] = Field(default="Medium")

class SyllabusPacingDiagnosis(BaseModel):
    scheduled_class_num: int = Field(description="Class number expected according to calendar date")
    actual_taught_class_num: float = Field(description="Effective class progress number (can be e.g. 8.5)")
    pacing_status: Literal["Ahead of Schedule", "On Track", "Behind Schedule"] = Field(
        description="Current pacing diagnostic"
    )
    session_gap_delta: str = Field(description="Delta explanation, e.g., '1 session behind schedule'")
    pacing_analysis: str = Field(description="Detailed pedagogical explanation of pace status")
    pedagogical_recommendation: str = Field(description="Strategic adjustment recommended for the next class")

class ClassAuditReport(BaseModel):
    course_id: str
    recording_id: str
    class_title: str
    class_date: str
    executive_summary: str
    pacing_diagnosis: SyllabusPacingDiagnosis
    topics_covered: List[TopicCovered]
    action_items: List[ActionItem]
    missing_or_delayed_topics: List[str] = Field(default_factory=list)

class NextClassLessonPlan(BaseModel):
    target_class_number: int
    title: str
    focus_objective: str
    time_allocation_minutes: Dict[str, int]
    demonstration_code: str = Field(description="Python executable code script for class demo")
    student_exercises: List[str]
    homework_assignment: str

class AgentStepTrace(BaseModel):
    step_number: int
    thought: str
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: str

class AgentRunResult(BaseModel):
    success: bool
    final_response: str
    audit_report: Optional[ClassAuditReport] = None
    next_class_package: Optional[NextClassLessonPlan] = None
    execution_trace: List[AgentStepTrace] = Field(default_factory=list)
