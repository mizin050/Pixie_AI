"""
Tool-Based Operator Engine - Claude-style adaptive execution
No pre-planning, just observe → decide → act → repeat
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.tools.computer_tools import get_computer_tools
from src.tools.whatsapp_tools import send_whatsapp_message
from src.agent.brain import Brain
import json
import re


class ToolBasedOperator:
    """Tool-based operator - adaptive execution like Claude"""
    
    def __init__(self):
        self.brain = Brain()
        self.computer = get_computer_tools()
        self.max_steps = 15  # Safety limit
        self.action_history = []
        print("✓ Tool-based operator initialized")
    
    def execute_goal(self, goal: str) -> str:
        """
        Execute a goal using adaptive tool-based approach
        
        Args:
            goal: User's goal in natural language
        
        Returns:
            Formatted result message
        """
        print(f"\n🎯 Goal: {goal}")
        print("="*60)
        
        # Check if this is a WhatsApp message request
        if self._is_whatsapp_message(goal):
            return self._handle_whatsapp_message(goal)
        
        # General tool-based execution
        return self._adaptive_execution(goal)
    
    def _is_whatsapp_message(self, goal: str) -> bool:
        """Check if goal is about sending WhatsApp message"""
        keywords = ["whatsapp", "message", "send", "tell", "text"]
        goal_lower = goal.lower()
        return any(k in goal_lower for k in keywords) and "whatsapp" in goal_lower
    
    def _handle_whatsapp_message(self, goal: str) -> str:
        """Handle WhatsApp message using specialized tool"""
        # Check if this is a screenshot request
        is_screenshot = "screenshot" in goal.lower() or "screen shot" in goal.lower()
        
        if is_screenshot:
            # Extract just the contact name for screenshot
            contact = self._extract_contact_name(goal)
            if not contact:
                return "❌ Could not find contact name. Please specify who to send the screenshot to."
            
            print(f"📸 WhatsApp Screenshot: {contact}")
            
            # Use WhatsApp screenshot tool
            from src.tools.whatsapp_tools import send_whatsapp_screenshot
            result = send_whatsapp_screenshot(contact)
            
            if result["success"]:
                return f"✅ **Screenshot Sent!**\n\nTo: {contact}\n\nScreenshot captured and sent successfully."
            else:
                return f"❌ **Failed to send screenshot**\n\n{result['message']}"
        
        # Regular text message
        contact, message = self._extract_whatsapp_info(goal)
        
        if not contact or not message:
            return "❌ Could not understand WhatsApp message request. Please specify contact and message."
        
        print(f"📱 WhatsApp: {contact} → '{message}'")
        
        # Use WhatsApp tool
        result = send_whatsapp_message(contact, message)
        
        if result["success"]:
            return f"✅ **Message Sent!**\n\nTo: {contact}\nMessage: {message}\n\nAll steps completed successfully."
        else:
            return f"❌ **Failed to send message**\n\n{result['message']}"
    
    def _extract_contact_name(self, goal: str) -> str:
        """Extract just the contact name from goal"""
        # Try pattern: "to NAME" or "send to NAME"
        contact_patterns = [
            r'(?:to|message)\s+(\w+)',
            r'(?:send|tell)\s+(?:to\s+)?(\w+)',
        ]
        
        for pattern in contact_patterns:
            match = re.search(pattern, goal, re.IGNORECASE)
            if match:
                potential_contact = match.group(1).lower()
                # Skip common words
                if potential_contact not in ['message', 'whatsapp', 'send', 'tell', 'text', 'on', 'screenshot', 'screen']:
                    return match.group(1)
        
        return None
    
    def _extract_whatsapp_info(self, goal: str) -> tuple:
        """Extract contact name and message from goal"""
        # Try to find quoted message first
        message_match = re.search(r'["\']([^"\']+)["\']', goal)
        message = message_match.group(1) if message_match else None
        
        # Extract contact name - look for name between "to" and the message/quotes
        # Pattern: "to <name>" or "message <name>"
        contact = None
        
        # Try pattern: "to NAME" or "message NAME" 
        contact_patterns = [
            r'(?:to|message)\s+(\w+)(?:\s+["\']|$)',  # "to adith" or "message adith"
            r'(?:send|tell)\s+(?:message\s+)?(?:to\s+)?(\w+)',  # "send to adith" or "tell adith"
        ]
        
        for pattern in contact_patterns:
            match = re.search(pattern, goal, re.IGNORECASE)
            if match:
                potential_contact = match.group(1).lower()
                # Skip common words
                if potential_contact not in ['message', 'whatsapp', 'send', 'tell', 'text', 'on']:
                    contact = match.group(1)
                    break
        
        # If still no message, try to extract everything after contact name
        if not message and contact:
            # Find where contact appears and take everything after it
            contact_pos = goal.lower().find(contact.lower())
            if contact_pos != -1:
                after_contact = goal[contact_pos + len(contact):].strip()
                # Remove common prefixes
                after_contact = re.sub(r'^[:\s"\']+', '', after_contact)
                after_contact = re.sub(r'["\']$', '', after_contact)
                if after_contact and len(after_contact) > 2:
                    message = after_contact
        
        return contact, message
    
    def _adaptive_execution(self, goal: str) -> str:
        """
        Adaptive execution loop - observe, decide, act, repeat
        
        Args:
            goal: User's goal
        
        Returns:
            Result message
        """
        self.action_history = []
        step_count = 0
        
        while step_count < self.max_steps:
            step_count += 1
            print(f"\n--- Step {step_count} ---")
            
            # 1. Observe: Take screenshot
            screenshot_result = self.computer.screenshot()
            if not screenshot_result["success"]:
                return f"❌ Failed to capture screen: {screenshot_result['message']}"
            
            screen_text = screenshot_result["text"]
            
            # 2. Decide: Ask AI what to do next
            next_action = self._decide_next_action(goal, screen_text, self.action_history)
            
            if not next_action:
                return "❌ Could not decide next action"
            
            # Check if goal is complete
            if next_action.get("complete"):
                print("\n✅ Goal achieved!")
                return self._format_success_message(goal, self.action_history)
            
            # 3. Act: Execute the action
            action_result = self._execute_action(next_action)
            
            # 4. Record: Add to history
            self.action_history.append({
                "step": step_count,
                "action": next_action,
                "result": action_result
            })
            
            print(f"Result: {action_result['message']}")
            
            # Check if action failed critically
            if not action_result["success"] and action_result.get("critical"):
                return f"❌ Critical failure: {action_result['message']}"
        
        return f"⚠️ Reached maximum steps ({self.max_steps}) without completing goal"
    
    def _decide_next_action(self, goal: str, screen_text: str, history: list) -> dict:
        """
        Ask AI to decide the next action based on current state
        
        Returns:
            Action dict or None
        """
        # Build prompt for AI
        prompt = f"""Goal: {goal}

Current screen shows: {screen_text[:500]}

Previous actions: {len(history)} steps taken

Decide the SINGLE next action to take. Return JSON:
{{
  "complete": false,
  "reasoning": "why this action",
  "tool": "tool_name",
  "args": {{"arg": "value"}}
}}

If goal is complete, return: {{"complete": true}}

Available tools:
- screenshot: Take screenshot
- left_click: Click at (x, y)
- type: Type text
- key: Press key (enter, escape, tab)
- open_application: Open app by name

Return ONLY the JSON, nothing else."""

        try:
            # Get AI decision (simplified - just return a basic action for now)
            # In full implementation, this would call the brain
            
            # For now, return a simple heuristic-based action
            if len(history) == 0:
                # First action: usually open an app or take screenshot
                if "open" in goal.lower():
                    app_name = self._extract_app_name(goal)
                    return {
                        "complete": False,
                        "tool": "open_application",
                        "args": {"app_name": app_name}
                    }
            
            # Placeholder - would use AI here
            return {"complete": True}
            
        except Exception as e:
            print(f"Error deciding action: {e}")
            return None
    
    def _execute_action(self, action: dict) -> dict:
        """Execute a tool action"""
        tool_name = action.get("tool")
        args = action.get("args", {})
        
        try:
            if tool_name == "screenshot":
                return self.computer.screenshot()
            elif tool_name == "left_click":
                return self.computer.left_click(**args)
            elif tool_name == "type":
                return self.computer.type(**args)
            elif tool_name == "key":
                return self.computer.key(**args)
            elif tool_name == "open_application":
                return self.computer.open_application(**args)
            else:
                return {"success": False, "message": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"success": False, "message": f"Error executing {tool_name}: {e}"}
    
    def _extract_app_name(self, goal: str) -> str:
        """Extract app name from goal"""
        words = goal.lower().split()
        if "open" in words:
            idx = words.index("open")
            if idx + 1 < len(words):
                return words[idx + 1]
        return "notepad"  # Default
    
    def _format_success_message(self, goal: str, history: list) -> str:
        """Format success message"""
        msg = f"✅ **Goal Achieved!**\n\n**Goal:** {goal}\n**Steps:** {len(history)}\n\n"
        for h in history:
            msg += f"✓ {h['action'].get('tool', 'action')}\n"
        return msg


# Global instance
_tool_operator = None

def get_tool_operator() -> ToolBasedOperator:
    """Get or create global tool operator"""
    global _tool_operator
    if _tool_operator is None:
        _tool_operator = ToolBasedOperator()
    return _tool_operator


def execute_with_tools(goal: str) -> str:
    """Execute a goal using tool-based approach"""
    return get_tool_operator().execute_goal(goal)
