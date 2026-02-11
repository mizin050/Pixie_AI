"""
Planner - Task decomposition and plan management
"""
from typing import Optional
from .brain import Brain
from .schemas import Plan, Step
import json


class Planner:
    """Manages task planning and re-planning"""
    
    def __init__(self):
        self.brain = Brain()
        self.current_plan: Optional[Plan] = None
        self.current_step = 0
        self.completed_steps = []
        self.failed_steps = []
    
    def create_plan(self, goal: str, context: Optional[str] = None) -> Plan:
        """
        Create a new plan for a goal
        
        Args:
            goal: User's goal
            context: Additional context
        
        Returns:
            Plan object
        """
        print(f"\n📋 Creating plan for: {goal}")
        
        plan = self.brain.create_plan(goal, context)
        self.current_plan = plan
        self.current_step = 0
        self.completed_steps = []
        self.failed_steps = []
        
        print(f"✓ Plan created with {len(plan.steps)} steps")
        print(f"  Estimated time: {plan.estimated_time}s")
        print(f"  Requires approval: {plan.requires_approval}")
        print(f"  Risk: {plan.risk_summary}")
        
        return plan
    
    def get_current_step(self) -> Optional[Step]:
        """Get the current step to execute"""
        if not self.current_plan:
            return None
        
        if self.current_step >= len(self.current_plan.steps):
            return None  # Plan complete
        
        return self.current_plan.steps[self.current_step]
    
    def mark_step_complete(self, step_number: int, result: dict):
        """Mark a step as completed"""
        self.completed_steps.append({
            "step": step_number,
            "result": result,
            "timestamp": self._get_timestamp()
        })
        self.current_step += 1
        
        print(f"✓ Step {step_number + 1} complete ({self.current_step}/{len(self.current_plan.steps)})")
    
    def mark_step_failed(self, step_number: int, reason: str):
        """Mark a step as failed"""
        self.failed_steps.append({
            "step": step_number,
            "reason": reason,
            "timestamp": self._get_timestamp()
        })
        
        print(f"❌ Step {step_number + 1} failed: {reason}")
    
    def should_replan(self) -> bool:
        """Determine if we should create a new plan"""
        if not self.current_plan:
            return False
        
        # Replan if we've failed the same step 3 times
        recent_failures = [f for f in self.failed_steps[-3:] if f["step"] == self.current_step]
        if len(recent_failures) >= 3:
            print("⚠ Too many failures on current step, replanning...")
            return True
        
        # Replan if we've failed 5 steps total
        if len(self.failed_steps) >= 5:
            print("⚠ Too many total failures, replanning...")
            return True
        
        return False
    
    def replan(self, current_observation: str, failure_reason: str) -> Plan:
        """
        Create a new plan based on current state
        
        Args:
            current_observation: Current screen state
            failure_reason: Why we need to replan
        
        Returns:
            New Plan object
        """
        print(f"\n🔄 Replanning due to: {failure_reason}")
        
        new_plan = self.brain.replan(
            original_goal=self.current_plan.goal,
            completed_steps=self.completed_steps,
            current_observation=current_observation,
            failure_reason=failure_reason
        )
        
        # Reset state with new plan
        self.current_plan = new_plan
        self.current_step = 0
        self.failed_steps = []  # Clear failures for new plan
        
        print(f"✓ New plan created with {len(new_plan.steps)} steps")
        return new_plan
    
    def is_complete(self) -> bool:
        """Check if the plan is complete"""
        if not self.current_plan:
            return False
        
        return self.current_step >= len(self.current_plan.steps)
    
    def get_progress(self) -> dict:
        """Get current progress information"""
        if not self.current_plan:
            return {"status": "no_plan"}
        
        return {
            "status": "complete" if self.is_complete() else "in_progress",
            "current_step": self.current_step + 1,
            "total_steps": len(self.current_plan.steps),
            "completed": len(self.completed_steps),
            "failed": len(self.failed_steps),
            "progress_percent": int((self.current_step / len(self.current_plan.steps)) * 100)
        }
    
    def get_plan_summary(self) -> str:
        """Get a human-readable plan summary"""
        if not self.current_plan:
            return "No active plan"
        
        summary = f"Goal: {self.current_plan.goal}\n"
        summary += f"Progress: {self.current_step}/{len(self.current_plan.steps)} steps\n\n"
        
        for i, step in enumerate(self.current_plan.steps):
            status = "✓" if i < self.current_step else "○"
            if i == self.current_step:
                status = "→"
            
            summary += f"{status} Step {i + 1}: {step.action.description}\n"
        
        return summary
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
