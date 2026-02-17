"""
Autonomous Brain - ULTIMATE AI agent with full system access
Command-Line + GUI Automation + AI Vision
This is the core autonomous decision-making system for Pixie
"""
import google.generativeai as genai
import os
import json
import subprocess
import sys
from datetime import datetime
import time
import threading
from typing import Optional, Dict, Any, List
import base64
from io import BytesIO


class AutonomousBrain:
    """ULTIMATE autonomous agent with command-line + GUI + vision capabilities"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.conversation_history = []
        self.running_processes = {}
        self.callback = None  # For UI updates
        self.gui_available = False
        self.screenshot_count = 0
        
        # Setup GUI tools
        self._setup_gui_tools()
        
    def _setup_gui_tools(self):
        """Check and setup GUI automation tools"""
        try:
            import pyautogui
            import PIL
            self.gui_available = True
            self._log("✅ GUI automation ready", "success")
        except ImportError:
            self._log("⚠️  GUI automation not available (install pyautogui + pillow)", "warning")
            self.gui_available = False
    
    def set_callback(self, callback):
        """Set callback function for UI updates"""
        self.callback = callback
        
    def _log(self, message: str, type: str = "info"):
        """Log message and send to UI if callback is set"""
        print(message)
        if self.callback:
            self.callback(message, type)
    
    def execute_bash(self, command: str, reasoning: str = "", background: bool = False, timeout: int = 300) -> str:
        """Execute a bash command"""
        self._log(f"\n🔧 EXECUTING: {command}", "command")
        if reasoning:
            self._log(f"   Reasoning: {reasoning}", "info")
        
        # Dangerous command check
        dangerous_keywords = ['rm -rf', 'sudo rm', 'format', 'mkfs', 'dd if=']
        if any(keyword in command.lower() for keyword in dangerous_keywords):
            self._log("   ⚠️  Dangerous command detected - skipping for safety", "warning")
            return "Command blocked for safety reasons"
        
        try:
            if background:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.path.expanduser('~')
                )
                pid = process.pid
                self.running_processes[pid] = {
                    'process': process,
                    'command': command,
                    'start_time': time.time()
                }
                self._log(f"   ✓ Background process started (PID: {pid})", "success")
                return f"Process started in background with PID {pid}"
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=os.path.expanduser('~')
                )
                output = result.stdout + result.stderr
                if output:
                    if len(output) > 2000:
                        output = output[:1000] + f"\n... [truncated] ...\n" + output[-1000:]
                    self._log(f"   ✓ Output: {output}", "success")
                else:
                    self._log(f"   ✓ Command executed successfully", "success")
                return output if output else "Command executed successfully"
                
        except subprocess.TimeoutExpired:
            error = f"Command timed out after {timeout} seconds"
            self._log(f"   ✗ {error}", "error")
            return error
        except Exception as e:
            error = f"Error: {str(e)}"
            self._log(f"   ✗ {error}", "error")
            return error
    
    def take_screenshot(self, description: str = "") -> Dict[str, Any]:
        """Take a screenshot and return data"""
        if not self.gui_available:
            return {"success": False, "error": "GUI automation not available"}
        
        self._log(f"\n📸 Taking screenshot", "info")
        if description:
            self._log(f"   Purpose: {description}", "info")
        
        try:
            import pyautogui
            from PIL import Image
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Save to temp
            self.screenshot_count += 1
            temp_path = os.path.join(os.path.expanduser('~'), f"pixie_screenshot_{self.screenshot_count}.png")
            screenshot.save(temp_path)
            
            # Convert to base64
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            self._log(f"   ✓ Screenshot saved: {temp_path}", "success")
            
            return {
                "success": True,
                "path": temp_path,
                "base64": img_base64,
                "size": screenshot.size
            }
        except Exception as e:
            error = f"Error taking screenshot: {str(e)}"
            self._log(f"   ✗ {error}", "error")
            return {"success": False, "error": error}
    
    def analyze_screenshot(self, screenshot_data: Dict, question: str) -> str:
        """Use vision model to analyze a screenshot"""
        if not screenshot_data.get("success"):
            return "Cannot analyze - screenshot failed"
        
        self._log(f"\n🔍 Analyzing screenshot", "info")
        self._log(f"   Question: {question}", "info")
        
        try:
            from PIL import Image
            
            # Load image
            img = Image.open(screenshot_data["path"])
            
            # Use vision model
            response = self.vision_model.generate_content([question, img])
            
            self._log(f"   ✓ Analysis complete", "success")
            return response.text
        except Exception as e:
            error = f"Error analyzing screenshot: {str(e)}"
            self._log(f"   ✗ {error}", "error")
            return error
    
    def find_on_screen(self, description: str) -> Dict[str, Any]:
        """Take screenshot and use AI vision to find element coordinates"""
        self._log(f"\n🔍 Finding on screen: {description}", "info")
        
        # Take screenshot
        screenshot = self.take_screenshot(f"Finding: {description}")
        if not screenshot.get("success"):
            return {"success": False, "error": "Screenshot failed"}
        
        # Ask vision model to find it
        question = f"""Look at this screenshot and find: {description}

Please identify the approximate center coordinates (x, y) of this element.
The screen size is {screenshot['size'][0]}x{screenshot['size'][1]} pixels.

Respond ONLY with JSON in this exact format:
{{"found": true, "x": 123, "y": 456, "confidence": "high"}}

If you cannot find it, respond:
{{"found": false, "reason": "explanation"}}"""
        
        analysis = self.analyze_screenshot(screenshot, question)
        
        try:
            # Parse JSON response
            result = json.loads(analysis)
            if result.get("found"):
                self._log(f"   ✓ Found at ({result['x']}, {result['y']})", "success")
            else:
                self._log(f"   ✗ Not found: {result.get('reason', 'unknown')}", "warning")
            return result
        except:
            self._log(f"   ✗ Could not parse vision response", "error")
            return {"success": False, "error": "Could not parse vision response"}
    
    def click_screen(self, x: int, y: int, reasoning: str = "") -> str:
        """Click at screen coordinates"""
        if not self.gui_available:
            return "Error: GUI automation not available"
        
        self._log(f"\n🖱️  Clicking at ({x}, {y})", "command")
        if reasoning:
            self._log(f"   Reasoning: {reasoning}", "info")
        
        try:
            import pyautogui
            pyautogui.click(x, y)
            self._log(f"   ✓ Clicked successfully", "success")
            return f"Successfully clicked at ({x}, {y})"
        except Exception as e:
            error = f"Error clicking: {str(e)}"
            self._log(f"   ✗ {error}", "error")
            return error
    
    def type_text(self, text: str, reasoning: str = "") -> str:
        """Type text using keyboard simulation"""
        if not self.gui_available:
            return "Error: GUI automation not available"
        
        self._log(f"\n⌨️  Typing text: {text[:50]}...", "command")
        if reasoning:
            self._log(f"   Reasoning: {reasoning}", "info")
        
        try:
            import pyautogui
            pyautogui.write(text, interval=0.05)
            self._log(f"   ✓ Typed {len(text)} characters", "success")
            return f"Successfully typed {len(text)} characters"
        except Exception as e:
            error = f"Error typing: {str(e)}"
            self._log(f"   ✗ {error}", "error")
            return error
    
    def press_key(self, key: str, reasoning: str = "") -> str:
        """Press a specific key"""
        if not self.gui_available:
            return "Error: GUI automation not available"
        
        self._log(f"\n⌨️  Pressing key: {key}", "command")
        if reasoning:
            self._log(f"   Reasoning: {reasoning}", "info")
        
        try:
            import pyautogui
            pyautogui.press(key)
            self._log(f"   ✓ Pressed {key}", "success")
            return f"Successfully pressed {key}"
        except Exception as e:
            error = f"Error pressing key: {str(e)}"
            self._log(f"   ✗ {error}", "error")
            return error
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> str:
        """Move mouse to coordinates"""
        if not self.gui_available:
            return "Error: GUI automation not available"
        
        self._log(f"\n🖱️  Moving mouse to ({x}, {y})", "command")
        
        try:
            import pyautogui
            pyautogui.moveTo(x, y, duration=duration)
            self._log(f"   ✓ Moved successfully", "success")
            return f"Successfully moved mouse to ({x}, {y})"
        except Exception as e:
            error = f"Error moving mouse: {str(e)}"
            self._log(f"   ✗ {error}", "error")
            return error
    
    def check_process(self, pid: int) -> str:
        """Check status of a background process"""
        if pid not in self.running_processes:
            return f"No process found with PID {pid}"
        
        proc_info = self.running_processes[pid]
        process = proc_info['process']
        
        if process.poll() is None:
            elapsed = time.time() - proc_info['start_time']
            return f"Process {pid} still running (elapsed: {elapsed:.1f}s)"
        else:
            stdout, stderr = process.communicate()
            output = (stdout or "") + (stderr or "")
            returncode = process.returncode
            del self.running_processes[pid]
            return f"Process {pid} completed with return code {returncode}\nOutput: {output[:1000]}"
    
    def write_file(self, path: str, content: str) -> str:
        """Write content to a file"""
        self._log(f"\n✍️  Writing file: {path}", "file")
        try:
            expanded_path = os.path.expanduser(path)
            # Handle relative paths
            if not os.path.isabs(expanded_path):
                expanded_path = os.path.abspath(expanded_path)
            
            # Create directory if needed
            dir_path = os.path.dirname(expanded_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(content)
            size = len(content)
            self._log(f"   ✓ Wrote {size} bytes", "success")
            return f"Successfully wrote {size} bytes to {path}"
        except Exception as e:
            error = f"Error writing file: {str(e)}"
            self._log(f"   ✗ {error}", "error")
            return error
    
    def read_file(self, path: str) -> str:
        """Read a file"""
        self._log(f"\n📖 Reading file: {path}", "file")
        try:
            expanded_path = os.path.expanduser(path)
            with open(expanded_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if len(content) > 5000:
                content = content[:2500] + f"\n... [truncated] ...\n" + content[-2500:]
            self._log(f"   ✓ Read {len(content)} characters", "success")
            return content
        except Exception as e:
            error = f"Error reading file: {str(e)}"
            self._log(f"   ✗ {error}", "error")
            return error
    
    def process_function_call(self, function_call) -> Any:
        """Process a function call from the model"""
        function_name = function_call.name
        args = function_call.args
        
        if function_name == "execute_command":
            return self.execute_bash(
                args.get("command", ""),
                args.get("reasoning", ""),
                args.get("background", False),
                args.get("timeout", 300)
            )
        elif function_name == "take_screenshot":
            return self.take_screenshot(args.get("description", ""))
        elif function_name == "find_on_screen":
            return self.find_on_screen(args.get("description", ""))
        elif function_name == "click_screen":
            return self.click_screen(
                args.get("x"),
                args.get("y"),
                args.get("reasoning", "")
            )
        elif function_name == "type_text":
            return self.type_text(
                args.get("text", ""),
                args.get("reasoning", "")
            )
        elif function_name == "press_key":
            return self.press_key(
                args.get("key", ""),
                args.get("reasoning", "")
            )
        elif function_name == "move_mouse":
            return self.move_mouse(
                args.get("x"),
                args.get("y"),
                args.get("duration", 0.5)
            )
        elif function_name == "check_process":
            return self.check_process(args.get("pid"))
        elif function_name == "write_file":
            return self.write_file(args.get("path"), args.get("content"))
        elif function_name == "read_file":
            return self.read_file(args.get("path"))
        elif function_name == "task_complete":
            return {
                "complete": True,
                "summary": args.get("summary", "Task completed")
            }
        else:
            return f"Unknown function: {function_name}"
    
    def execute_task(self, task: str, max_iterations: int = 50) -> str:
        """Execute a task autonomously"""
        self._log(f"\n{'='*70}", "info")
        self._log(f"🎯 TASK: {task}", "task")
        self._log(f"{'='*70}\n", "info")
        
        # Define tools
        tools = [{
            "function_declarations": [
                {
                    "name": "execute_command",
                    "description": "Execute bash/shell command. PREFERRED for file ops, installs, running programs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "The bash command"},
                            "reasoning": {"type": "string", "description": "Why running this"},
                            "background": {"type": "boolean", "description": "Run in background"},
                            "timeout": {"type": "integer", "description": "Timeout seconds"}
                        },
                        "required": ["command"]
                    }
                },
                {
                    "name": "take_screenshot",
                    "description": "Take screenshot to verify actions or see current state",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "Why taking screenshot"}
                        }
                    }
                },
                {
                    "name": "find_on_screen",
                    "description": "Use AI vision to find element and get coordinates. Returns {found: bool, x: int, y: int}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "What to find (button, icon, window)"}
                        },
                        "required": ["description"]
                    }
                },
                {
                    "name": "click_screen",
                    "description": "Click at screen coordinates",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "reasoning": {"type": "string"}
                        },
                        "required": ["x", "y"]
                    }
                },
                {
                    "name": "type_text",
                    "description": "Type text using keyboard",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "reasoning": {"type": "string"}
                        },
                        "required": ["text"]
                    }
                },
                {
                    "name": "press_key",
                    "description": "Press key (enter, tab, escape, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"},
                            "reasoning": {"type": "string"}
                        },
                        "required": ["key"]
                    }
                },
                {
                    "name": "move_mouse",
                    "description": "Move mouse to coordinates",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "duration": {"type": "number"}
                        },
                        "required": ["x", "y"]
                    }
                },
                {
                    "name": "check_process",
                    "description": "Check status of background process",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pid": {"type": "integer"}
                        },
                        "required": ["pid"]
                    }
                },
                {
                    "name": "write_file",
                    "description": "Write content to file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["path", "content"]
                    }
                },
                {
                    "name": "read_file",
                    "description": "Read a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"}
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "task_complete",
                    "description": "Call when task fully complete",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string"}
                        },
                        "required": ["summary"]
                    }
                }
            ]
        }]
        
        system_instruction = """You are Pixie with MOLT (Multiple Options Loop Testing) verification.

🎯 THE MOLT FORMULA - CRITICAL:

FOR EVERY ACTION:
1. Plan 3+ alternative strategies
2. Try strategy #1
3. take_screenshot() to verify
4. find_on_screen("expected result") to check
5. If NOT found → Try strategy #2
6. Repeat until SUCCESS ✅

EXAMPLE - Opening Chrome:
Strategy 1: execute_command("start chrome")
  → take_screenshot()
  → find_on_screen("Chrome window")
  → If found: SUCCESS ✅ | If not: Try #2

Strategy 2: execute_command("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
  → take_screenshot()
  → find_on_screen("Chrome window")
  → If found: SUCCESS ✅ | If not: Try #3

Strategy 3: find_on_screen("Chrome icon") → click_screen(x, y)
  → take_screenshot()
  → find_on_screen("Chrome window")
  → SUCCESS ✅

HYBRID APPROACH:
- Command-line FIRST (faster)
- GUI automation SECOND (fallback)
- ALWAYS verify with screenshot + find_on_screen

VERIFICATION RULES:
1. After EVERY action: take_screenshot + find_on_screen
2. Ask specific: "Chrome window", "Save button", "File created"
3. If verification fails: try next strategy
4. Never give up - try 3+ alternatives
5. Be persistent and creative

You're UNSTOPPABLE with MOLT!"""
        
        try:
            chat = self.model.start_chat(enable_automatic_function_calling=False)
            response = chat.send_message(
                task,
                tools=tools,
                safety_settings={
                    'HARASSMENT': 'block_none',
                    'HATE_SPEECH': 'block_none',
                    'SEXUALLY_EXPLICIT': 'block_none',
                    'DANGEROUS_CONTENT': 'block_none'
                }
            )
            
            iteration = 0
            while iteration < max_iterations:
                iteration += 1
                self._log(f"\n{'─'*70}", "info")
                self._log(f"Iteration {iteration}/{max_iterations}", "info")
                self._log(f"{'─'*70}", "info")
                
                # Display thinking
                if response.text:
                    self._log(f"\n💭 THINKING:\n{response.text}", "thinking")
                
                # Check for function calls
                if not response.candidates[0].content.parts:
                    self._log("\n✅ Task completed", "success")
                    break
                
                function_calls = [
                    part.function_call 
                    for part in response.candidates[0].content.parts 
                    if hasattr(part, 'function_call') and part.function_call
                ]
                
                if not function_calls:
                    self._log("\n✅ Task completed", "success")
                    break
                
                # Process function calls
                function_responses = []
                for fc in function_calls:
                    result = self.process_function_call(fc)
                    
                    # Check if task is complete
                    if isinstance(result, dict) and result.get("complete"):
                        self._log(f"\n{'='*70}", "info")
                        self._log(f"✅ TASK COMPLETE", "success")
                        self._log(f"{'='*70}", "info")
                        self._log(f"\n📋 Summary: {result['summary']}\n", "success")
                        
                        # Clean up processes
                        for pid in list(self.running_processes.keys()):
                            try:
                                self.running_processes[pid]['process'].terminate()
                            except:
                                pass
                        
                        return result['summary']
                    
                    # Add function response
                    function_responses.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fc.name,
                                response={"result": str(result)}
                            )
                        )
                    )
                
                # Send function results back
                response = chat.send_message(
                    genai.protos.Content(parts=function_responses),
                    tools=tools,
                    safety_settings={
                        'HARASSMENT': 'block_none',
                        'HATE_SPEECH': 'block_none',
                        'SEXUALLY_EXPLICIT': 'block_none',
                        'DANGEROUS_CONTENT': 'block_none'
                    }
                )
                
                time.sleep(0.5)  # Rate limiting
            
            if iteration >= max_iterations:
                msg = f"Reached maximum iterations ({max_iterations})"
                self._log(f"\n⚠️  {msg}", "warning")
                return msg
            
            return "Task completed"
            
        except Exception as e:
            error = f"Error: {str(e)}"
            self._log(f"\n❌ {error}", "error")
            import traceback
            traceback.print_exc()
            return error
        finally:
            # Clean up processes
            for pid in list(self.running_processes.keys()):
                try:
                    self.running_processes[pid]['process'].terminate()
                except:
                    pass
