"""
Operator Engine - Bridges the agent brain with the chat UI
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agent.planner import Planner
from src.core.memory_simple import ChatMemorySimple
from src.control.executor import execute_action
from src.vision.capture import capture_screen
from src.vision.vision_summary import create_summary
from src.agent.learned_tools import get_learned_tools
from src.agent.autonomous_brain import AutonomousBrain
import time
import os
from dotenv import load_dotenv

load_dotenv()


class OperatorEngine:
    """Operator mode engine for task execution"""
    
    def __init__(self):
        self.planner = Planner()
        self.memory = ChatMemorySimple()
        self.learned_tools = get_learned_tools()
        self.operator_mode = False
        self.executing = False
        self.current_execution = None
        
        # Initialize autonomous brain
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.autonomous_brain = AutonomousBrain(api_key)
        else:
            self.autonomous_brain = None
            print("⚠️  GEMINI_API_KEY not found - autonomous mode disabled")
        self.root_access = False  # Root access mode bypasses all approvals
        print("✓ Operator Engine initialized")
    
    def is_operator_command(self, text: str) -> bool:
        """Check if this is an operator-style command"""
        # Operator commands are action-oriented
        operator_keywords = [
            "open", "close", "click", "type", "send", "download",
            "navigate", "go to", "search for", "find", "create",
            "delete", "move", "copy", "run", "execute", "launch"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in operator_keywords)
    
    def create_plan(self, goal: str) -> dict:
        """
        Create a plan and return it in a chat-friendly format
        
        Returns:
            dict with plan info for the UI
        """
        try:
            plan = self.planner.create_plan(goal)
            
            # Format for UI
            return {
                "success": True,
                "goal": plan.goal,
                "steps": [
                    {
                        "number": i + 1,
                        "description": step.action.description,
                        "type": step.action.type,
                        "risk": step.risk_level,
                        "expected": step.expected_state
                    }
                    for i, step in enumerate(plan.steps)
                ],
                "total_steps": len(plan.steps),
                "estimated_time": plan.estimated_time,
                "requires_approval": plan.requires_approval,
                "risk_summary": plan.risk_summary
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_plan_summary(self) -> str:
        """Get a formatted plan summary for chat display"""
        if not self.planner.current_plan:
            return "No active plan"
        
        plan = self.planner.current_plan
        progress = self.planner.get_progress()
        
        summary = f"📋 **{plan.goal}**\n\n"
        summary += f"Progress: {progress['current_step']}/{progress['total_steps']} steps "
        summary += f"({progress['progress_percent']}%)\n\n"
        
        for i, step in enumerate(plan.steps):
            if i < progress['current_step'] - 1:
                status = "✅"
            elif i == progress['current_step'] - 1:
                status = "▶️"
            else:
                status = "⏸️"
            
            risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
            risk = risk_emoji.get(step.risk_level, "⚪")
            
            summary += f"{status} {risk} **Step {i + 1}**: {step.action.description}\n"
        
        return summary
    
    def format_plan_for_chat(self, plan_data: dict) -> str:
        """Format plan data as a nice chat message"""
        if not plan_data.get("success"):
            return f"❌ Failed to create plan: {plan_data.get('error', 'Unknown error')}"
        
        msg = f"📋 **Plan Created**\n\n"
        msg += f"**Goal:** {plan_data['goal']}\n"
        msg += f"**Steps:** {plan_data['total_steps']}\n"
        msg += f"**Time:** ~{plan_data['estimated_time']}s\n"
        msg += f"**Risk:** {plan_data['risk_summary']}\n\n"
        
        # Debug logging
        print(f"DEBUG: requires_approval = {plan_data['requires_approval']}")
        print(f"DEBUG: root_access = {self.root_access}")
        
        if plan_data['requires_approval']:
            msg += "⚠️ **This plan requires your approval**\n\n"
        
        msg += "**Steps:**\n"
        for step in plan_data['steps']:
            risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
            risk = risk_emoji.get(step['risk'], "⚪")
            msg += f"{risk} {step['number']}. {step['description']}\n"
        
        if plan_data['requires_approval']:
            msg += "\n✅ Click Approve to execute\n"
            msg += "❌ Click Cancel to abort"
        else:
            msg += "\n💡 Auto-executing (all steps are low risk)..."
        
        return msg
    
    def execute_plan(self, update_callback=None) -> str:
        """
        Execute the current plan step by step with real-time updates
        
        Args:
            update_callback: Function to call with status updates
        
        Returns:
            Execution summary message
        """
        if not self.planner.current_plan:
            return "❌ No plan to execute"
        
        if self.executing:
            return "⚠️ Already executing a plan"
        
        self.executing = True
        results = []
        start_time = time.time()
        
        try:
            plan = self.planner.current_plan
            total_steps = len(plan.steps)
            
            print(f"\n🚀 Starting execution: {plan.goal}")
            
            if update_callback:
                update_callback(f"🚀 Starting execution...\n")
            
            for i, step in enumerate(plan.steps):
                step_num = i + 1
                print(f"\n▶️ Step {step_num}/{total_steps}: {step.action.description}")
                
                # Send real-time update
                if update_callback:
                    update_callback(f"▶️ Step {step_num}/{total_steps}: {step.action.description}")
                
                # Execute the action
                result = execute_action(step.action)
                
                # Send result update
                if update_callback:
                    status = "✅" if result["success"] else "❌"
                    conf = f" ({result['confidence']:.0%})" if result["success"] else ""
                    update_callback(f"{status} {step.action.description}{conf}")
                
                # Store result
                results.append({
                    "step": step_num,
                    "action": step.action.description,
                    "success": result["success"],
                    "confidence": result["confidence"],
                    "message": result["message"]
                })
                
                # Update planner
                if result["success"]:
                    self.planner.mark_step_complete(i, result)
                else:
                    self.planner.mark_step_failed(i, result["message"])
                    
                    # Check if we should retry or abort
                    if result["confidence"] < 0.5:
                        print(f"⚠️ Low confidence ({result['confidence']:.2f}), aborting")
                        if update_callback:
                            update_callback(f"⚠️ Aborting due to low confidence")
                        break
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Check if all steps succeeded
            successful = sum(1 for r in results if r["success"])
            all_success = successful == total_steps
            
            # Calculate average confidence
            avg_confidence = sum(r["confidence"] for r in results) / len(results) if results else 0
            
            # Save as learned tool if successful
            if all_success and avg_confidence >= 0.7:
                print(f"\n📚 Saving as learned tool (confidence: {avg_confidence:.0%})")
                
                if update_callback:
                    update_callback(f"📚 Saved as learned tool!")
                
                # Convert results to simple step format
                learned_steps = [
                    {
                        "action": r["action"],
                        "confidence": r["confidence"]
                    }
                    for r in results
                ]
                
                self.learned_tools.save_successful_workflow(
                    goal=plan.goal,
                    steps=learned_steps,
                    execution_time=execution_time,
                    confidence=avg_confidence
                )
            
            # Generate summary
            summary = self._format_execution_summary(results, plan.goal, execution_time)
            
        except Exception as e:
            summary = f"❌ Execution error: {e}"
            print(f"❌ {summary}")
            if update_callback:
                update_callback(f"❌ Error: {e}")
        
        finally:
            self.executing = False
        
        return summary
    
    def _format_execution_summary(self, results: list, goal: str, execution_time: float = 0) -> str:
        """Format execution results for chat"""
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        
        msg = f"🎯 **Execution Complete**\n\n"
        msg += f"**Goal:** {goal}\n"
        msg += f"**Success Rate:** {successful}/{total} steps\n"
        msg += f"**Time:** {execution_time:.1f}s\n\n"
        
        msg += "**Results:**\n"
        for r in results:
            status = "✅" if r["success"] else "❌"
            confidence = f"({r['confidence']:.0%})" if r["success"] else ""
            msg += f"{status} Step {r['step']}: {r['action']} {confidence}\n"
        
        if successful == total:
            msg += "\n🎉 **All steps completed successfully!**"
            msg += "\n📚 **Saved as learned tool** - Next time will be faster!"
        elif successful > 0:
            msg += f"\n⚠️ **Partial success** - {total - successful} step(s) failed"
        else:
            msg += "\n❌ **Execution failed**"
        
        return msg


# Global operator engine instance
_operator_engine = None

def get_operator_engine() -> OperatorEngine:
    """Get or create the global operator engine"""
    global _operator_engine
    if _operator_engine is None:
        _operator_engine = OperatorEngine()
    return _operator_engine


def get_response_operator(user_text: str) -> str:
    """
    Get response in operator mode
    
    Args:
        user_text: User's message
    
    Returns:
        Formatted response for chat
    """
    engine = get_operator_engine()
    
    # Check for root access grant
    text_lower = user_text.lower().strip()
    if "you have root access" in text_lower or "root access" in text_lower:
        engine.root_access = True
        return "🔓 **Root access granted!** All approval checks disabled. I can now execute any task without asking for permission."
    
    # Check for special commands
    if text_lower == "approve":
        if engine.planner.current_plan:
            # Execute the plan
            return engine.execute_plan()
        else:
            return "❌ No plan to approve"
    
    if text_lower == "cancel":
        if engine.planner.current_plan:
            engine.planner.current_plan = None
            return "❌ Plan cancelled"
        else:
            return "⚠️ No active plan to cancel"
    
    if text_lower in ["status", "progress"]:
        return engine.get_plan_summary()
    
    if text_lower in ["tools", "learned tools", "show tools"]:
        return engine.learned_tools.get_tools_summary()
    
    # Check if this is a WhatsApp message - use tool-based approach
    if "whatsapp" in text_lower and any(word in text_lower for word in ["message", "send", "tell", "text"]):
        from src.core.ai_engine_tools import execute_with_tools
        print("\n🔧 Using tool-based execution for WhatsApp")
        return execute_with_tools(user_text)
    
    # Check for complex autonomous tasks (use autonomous brain)
    autonomous_keywords = [
        "build", "create app", "develop", "compile", "install",
        "complex", "multi-step", "automate", "workflow"
    ]
    
    if engine.autonomous_brain and any(keyword in text_lower for keyword in autonomous_keywords):
        print("\n🧠 Using autonomous brain for complex task")
        result = engine.autonomous_brain.execute_task(user_text)
        return f"🤖 **Autonomous Execution Complete**\n\n{result}"
    
    # Check if this is an operator command
    if engine.is_operator_command(user_text):
        # Create a plan
        print(f"\n{'='*60}")
        print(f"DEBUG: Creating plan for: {user_text}")
        plan_data = engine.create_plan(user_text)
        
        print(f"DEBUG: Plan created successfully: {plan_data.get('success')}")
        print(f"DEBUG: Total steps: {plan_data.get('total_steps')}")
        print(f"DEBUG: Requires approval (initial): {plan_data.get('requires_approval')}")
        
        # Override approval requirement if root access is enabled
        if engine.root_access and plan_data.get("success"):
            plan_data["requires_approval"] = False
            plan_data["risk_summary"] = "Root access - approval bypassed"
            print("DEBUG: Root access - approval bypassed")
        
        # Also override if all steps are LOW risk (Gemini sometimes sets requires_approval incorrectly)
        if plan_data.get("success") and plan_data.get("steps"):
            all_low_risk = all(step.get("risk") == "LOW" for step in plan_data["steps"])
            print(f"DEBUG: All steps LOW risk: {all_low_risk}")
            if all_low_risk:
                print("DEBUG: Forcing auto-execute for LOW risk steps")
                plan_data["requires_approval"] = False
        
        print(f"DEBUG: Requires approval (final): {plan_data.get('requires_approval')}")
        
        plan_message = engine.format_plan_for_chat(plan_data)
        
        # Auto-execute if low risk or root access
        if plan_data.get("success") and not plan_data.get("requires_approval"):
            print("DEBUG: ✅ AUTO-EXECUTING PLAN NOW...")
            print(f"{'='*60}\n")
            execution_result = engine.execute_plan()
            plan_message += "\n\n" + execution_result
        else:
            print("DEBUG: ⏸️ Waiting for approval...")
            print(f"{'='*60}\n")
        
        return plan_message
    else:
        # Fall back to regular chat
        from src.core.ai_engine_gemini import get_response
        return get_response(user_text)
