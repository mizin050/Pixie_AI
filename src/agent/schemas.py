"""
Action and decision schemas for structured AI responses
"""
from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class Action(BaseModel):
    """Single action to execute"""
    type: Literal[
        "click", "type", "type_text", "navigate", "open_app", "press_key",
        "keyboard_shortcut", "wait", "scroll", "screenshot", "read_screen", "verify"
    ]
    target: Optional[str] = Field(None, description="Element selector or app name")
    value: Optional[str] = Field(None, description="Text to type or key to press")
    coordinates: Optional[tuple[int, int]] = Field(None, description="X, Y coordinates")
    description: str = Field(..., description="Human-readable action description")


class Decision(BaseModel):
    """AI decision for next action"""
    reasoning: str = Field(..., description="Why this action is needed")
    action: Action
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(..., description="Risk assessment")
    expected_outcome: str = Field(..., description="What should happen after this action")
    fallback_plan: Optional[str] = Field(None, description="What to do if this fails")


class Step(BaseModel):
    """Single step in a plan"""
    step_number: int
    action: Action
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    expected_state: str = Field(..., description="Expected screen state after this step")
    verification: str = Field(..., description="How to verify success")


class Plan(BaseModel):
    """Complete task plan"""
    goal: str
    steps: List[Step]
    estimated_time: int = Field(..., description="Estimated seconds to complete")
    requires_approval: bool = Field(..., description="Does this plan need user approval?")
    risk_summary: str = Field(..., description="Overall risk assessment")


class Observation(BaseModel):
    """Screen observation result"""
    screen_text: str = Field(..., description="Visible text on screen")
    active_window: Optional[str] = Field(None, description="Active window title")
    detected_elements: List[str] = Field(default_factory=list, description="Detected UI elements")
    errors: List[str] = Field(default_factory=list, description="Detected errors")
    state: Literal["normal", "loading", "error", "success", "blocked"] = "normal"
    confidence: float = Field(..., ge=0.0, le=1.0, description="Observation confidence")


class EvaluationResult(BaseModel):
    """Action evaluation result"""
    success: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    actual_outcome: str
    matches_expected: bool
    errors: List[str] = Field(default_factory=list)
    should_retry: bool
    retry_strategy: Optional[str] = None
