"""
Brain - Multi-provider AI interface with structured output validation
Supports: Gemini, Kimi (k2.5)
"""
import google.generativeai as genai
import requests
from dotenv import load_dotenv
import os
import json
from typing import Optional
from .schemas import Decision, Plan

load_dotenv()

class Brain:
    """AI brain with multi-provider support"""
    
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "gemini").lower()
        
        if self.provider == "kimi":
            # Kimi k2.5 via NVIDIA API
            api_key = os.getenv("KIMI_API_KEY")
            if not api_key or api_key == "your_kimi_api_key_here":
                raise ValueError("KIMI_API_KEY not configured")
            
            self.api_key = api_key
            self.api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
            self.model = "moonshotai/kimi-k2.5"
            self.client = None
            print("✓ Brain initialized with Kimi k2.5 (via NVIDIA)")
            print(f"  Model: {self.model}")
            
        elif self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                raise ValueError("GEMINI_API_KEY not configured")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
            self.client = None
            self.api_key = None
            self.api_url = None
            print("✓ Brain initialized with Gemini")
            
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    def _generate_with_kimi(self, prompt: str, temperature: float = 0.3) -> str:
        """Generate response using Kimi k2.5 via NVIDIA API"""
        try:
            print(f"DEBUG: Calling Kimi k2.5 via NVIDIA API")
            
            # API key should already have nvapi- prefix
            auth_key = self.api_key if self.api_key.startswith("nvapi-") else f"nvapi-{self.api_key}"
            
            headers = {
                "Authorization": f"Bearer {auth_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are Pixie, a desktop AI operator. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 16384,
                "temperature": temperature,
                "top_p": 1.0,
                "stream": False
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120  # Increased timeout for Kimi's thinking process
            )
            
            if response.status_code != 200:
                print(f"DEBUG: Kimi API error: {response.status_code}")
                print(f"DEBUG: Response: {response.text}")
                raise Exception(f"Kimi API error: {response.status_code} - {response.text}")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Kimi might include thinking process, extract just the JSON
            if "```json" in content:
                # Extract JSON from markdown code block
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            
            return content
            
        except Exception as e:
            print(f"DEBUG: Kimi API error: {e}")
            raise
    
    def _generate_with_gemini(self, prompt: str, temperature: float = 0.3) -> str:
        """Generate response using Gemini API"""
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=temperature)
        )
        return response.text
    
    def create_plan(self, goal: str, context: Optional[str] = None) -> Plan:
        """
        Create a structured plan for achieving a goal
        
        Args:
            goal: User's goal in natural language
            context: Additional context (screen state, preferences, etc.)
        
        Returns:
            Validated Plan object
        """
        system_prompt = """You are Pixie, a desktop AI operator.
Your job is to break down user goals into clear, executable steps.

Rules:
1. Each step must be verifiable
2. Classify risk level: LOW (safe), MEDIUM (needs approval), HIGH (dangerous)
3. Be specific about what to click/type
4. Include verification criteria
5. Estimate realistic time

IMPORTANT - Approval Requirements:
- Set requires_approval to FALSE for: opening apps, typing text, clicking UI elements, navigating websites, sending messages
- Set requires_approval to TRUE only for: deleting files, system changes, financial transactions, accessing sensitive data
- Most user tasks are LOW risk and should NOT require approval

IMPORTANT - WhatsApp Desktop:
When creating plans for WhatsApp messages:
- Step 1: Click the search box at the TOP of WhatsApp Desktop window
- Step 2: Type the contact name in that search box
- Step 3: Wait for search results to appear in WhatsApp
- Step 4: Click on the contact from the search results
- Step 5: Type the message in the chat input
- Step 6: Press Enter to send

DO NOT use system contacts or phone contacts. Use WhatsApp's built-in search only.

Return ONLY valid JSON matching the Plan schema."""

        user_prompt = f"""Goal: {goal}

{f"Context: {context}" if context else ""}

Create a detailed plan with steps to achieve this goal.

IMPORTANT - For opening applications:
Use action type "open_app" with the app name as the target. Do NOT break it into separate steps.
Example:
{{
  "step_number": 1,
  "action": {{
    "type": "open_app",
    "target": "notepad",
    "description": "Open Notepad application"
  }},
  "risk_level": "LOW",
  "expected_state": "Notepad window is open",
  "verification": "Notepad window visible"
}}

Return as JSON with this structure:
{{
  "goal": "the goal",
  "steps": [
    {{
      "step_number": 1,
      "action": {{
        "type": "open_app",
        "target": "Chrome",
        "description": "Open Chrome browser"
      }},
      "risk_level": "LOW",
      "expected_state": "Chrome window is open",
      "verification": "Chrome window visible in taskbar"
    }},
    {{
      "step_number": 2,
      "action": {{
        "type": "type_text",
        "value": "text to type here",
        "description": "Type the text"
      }},
      "risk_level": "LOW",
      "expected_state": "Text is typed",
      "verification": "Text visible on screen"
    }},
    {{
      "step_number": 3,
      "action": {{
        "type": "press_key",
        "value": "enter",
        "description": "Press Enter key"
      }},
      "risk_level": "LOW",
      "expected_state": "Action completed",
      "verification": "Expected result visible"
    }}
  ],
  "estimated_time": 30,
  "requires_approval": false,
  "risk_summary": "All steps are low risk"
}}"""

        try:
            # Generate response based on provider
            if self.provider == "kimi":
                text = self._generate_with_kimi(f"{system_prompt}\n\n{user_prompt}", temperature=0.3)
            else:  # gemini
                text = self._generate_with_gemini(f"{system_prompt}\n\n{user_prompt}", temperature=0.3)
            
            # Clean response
            text = text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            # Parse and validate
            plan_dict = json.loads(text)
            plan = Plan(**plan_dict)
            
            print(f"✓ Created plan with {len(plan.steps)} steps")
            return plan
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON from {self.provider}: {e}")
            print(f"Response: {text[:200]}")
            raise ValueError(f"{self.provider} returned invalid JSON")
        except Exception as e:
            print(f"❌ Error creating plan: {e}")
            raise
    
    def decide_next_action(
        self,
        goal: str,
        current_step: int,
        plan: Plan,
        observation: str,
        failures: int = 0
    ) -> Decision:
        """
        Decide the next action based on current state
        
        Args:
            goal: Overall goal
            current_step: Current step number
            plan: The overall plan
            observation: Current screen observation
            failures: Number of recent failures
        
        Returns:
            Validated Decision object
        """
        system_prompt = """You are Pixie, a desktop AI operator.
You are executing a plan step-by-step.

Your job:
1. Look at the current screen state
2. Decide the exact next action
3. Assess confidence and risk
4. Provide fallback if action fails

Return ONLY valid JSON matching the Decision schema."""

        step = plan.steps[current_step] if current_step < len(plan.steps) else None
        
        user_prompt = f"""Goal: {goal}
Current Step: {current_step + 1}/{len(plan.steps)}
Planned Action: {step.action.description if step else "Complete"}

Current Screen State:
{observation}

Recent Failures: {failures}

Decide the exact next action to take.
Return as JSON with this structure:
{{
  "reasoning": "why this action is needed",
  "action": {{
    "type": "click",
    "target": "button[id='submit']",
    "description": "Click the submit button"
  }},
  "confidence": 0.85,
  "risk_level": "LOW",
  "expected_outcome": "Form will be submitted",
  "fallback_plan": "If button not found, try keyboard shortcut"
}}"""

        try:
            # Generate response based on provider
            if self.provider == "kimi":
                text = self._generate_with_kimi(f"{system_prompt}\n\n{user_prompt}", temperature=0.2)
            else:  # gemini
                text = self._generate_with_gemini(f"{system_prompt}\n\n{user_prompt}", temperature=0.2)
            
            # Clean response
            text = text.strip()
            
            # Clean markdown
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            # Parse and validate
            decision_dict = json.loads(text)
            decision = Decision(**decision_dict)
            
            print(f"✓ Decision: {decision.action.description} (confidence: {decision.confidence:.2f})")
            return decision
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON from {self.provider}: {e}")
            raise ValueError(f"{self.provider} returned invalid JSON")
        except Exception as e:
            print(f"❌ Error making decision: {e}")
            raise
    
    def replan(
        self,
        original_goal: str,
        completed_steps: list,
        current_observation: str,
        failure_reason: str
    ) -> Plan:
        """
        Create a new plan when the original plan fails
        
        Args:
            original_goal: The original goal
            completed_steps: Steps completed so far
            current_observation: Current screen state
            failure_reason: Why the plan failed
        
        Returns:
            New Plan object
        """
        context = f"""Previous attempt failed.
Completed steps: {len(completed_steps)}
Current state: {current_observation}
Failure reason: {failure_reason}

Create a NEW plan that accounts for the current state and avoids the previous failure."""

        return self.create_plan(original_goal, context)
