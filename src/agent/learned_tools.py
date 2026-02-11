"""
Learned Tools - Save and reuse successful workflows
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class LearnedToolsManager:
    """Manages learned workflows that can be reused"""
    
    def __init__(self, tools_file: str = "learned_tools.json"):
        # Save in project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.tools_file = os.path.join(project_root, tools_file)
        self.tools = {}
        self._load_tools()
        print(f"✓ Learned tools manager initialized ({len(self.tools)} tools loaded)")
    
    def _load_tools(self):
        """Load learned tools from file"""
        if os.path.exists(self.tools_file):
            try:
                with open(self.tools_file, 'r', encoding='utf-8') as f:
                    self.tools = json.load(f)
                print(f"📚 Loaded {len(self.tools)} learned tools")
            except Exception as e:
                print(f"⚠ Error loading tools: {e}")
                self.tools = {}
        else:
            print("📚 No learned tools yet - will create on first success")
    
    def _save_tools(self):
        """Save learned tools to file"""
        try:
            with open(self.tools_file, 'w', encoding='utf-8') as f:
                json.dump(self.tools, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(self.tools)} learned tools")
        except Exception as e:
            print(f"⚠ Error saving tools: {e}")
    
    def save_successful_workflow(
        self,
        goal: str,
        steps: List[Dict],
        execution_time: float,
        confidence: float
    ):
        """
        Save a successful workflow as a learned tool
        
        Args:
            goal: The goal that was achieved
            steps: List of steps that worked
            execution_time: How long it took
            confidence: Average confidence score
        """
        # Create a tool key from the goal
        tool_key = self._create_tool_key(goal)
        
        # Check if we should save (only if confidence is high enough)
        if confidence < 0.7:
            print(f"⚠ Confidence too low ({confidence:.2f}) - not saving as tool")
            return
        
        # Create tool entry
        tool = {
            "goal": goal,
            "steps": steps,
            "execution_time": execution_time,
            "confidence": confidence,
            "created": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "use_count": 1,
            "success_rate": 1.0
        }
        
        # If tool exists, update it
        if tool_key in self.tools:
            existing = self.tools[tool_key]
            
            # Update statistics
            tool["use_count"] = existing["use_count"] + 1
            tool["created"] = existing["created"]
            
            # Update success rate (weighted average)
            old_rate = existing["success_rate"]
            new_rate = (old_rate * existing["use_count"] + 1.0) / tool["use_count"]
            tool["success_rate"] = new_rate
            
            print(f"📚 Updated learned tool: '{goal}' (used {tool['use_count']} times)")
        else:
            print(f"📚 Saved new learned tool: '{goal}'")
        
        self.tools[tool_key] = tool
        self._save_tools()
    
    def get_tool(self, goal: str) -> Optional[Dict]:
        """Get a learned tool for a goal"""
        tool_key = self._create_tool_key(goal)
        
        if tool_key in self.tools:
            tool = self.tools[tool_key]
            
            # Update last used
            tool["last_used"] = datetime.now().isoformat()
            self._save_tools()
            
            print(f"📚 Using learned tool: '{goal}' (success rate: {tool['success_rate']:.0%})")
            return tool
        
        return None
    
    def find_similar_tool(self, goal: str) -> Optional[Dict]:
        """Find a similar tool based on goal keywords"""
        goal_lower = goal.lower()
        keywords = set(goal_lower.split())
        
        best_match = None
        best_score = 0
        
        for tool_key, tool in self.tools.items():
            tool_keywords = set(tool["goal"].lower().split())
            
            # Calculate similarity (Jaccard similarity)
            intersection = keywords & tool_keywords
            union = keywords | tool_keywords
            
            if union:
                similarity = len(intersection) / len(union)
                
                if similarity > best_score and similarity > 0.5:
                    best_score = similarity
                    best_match = tool
        
        if best_match:
            print(f"📚 Found similar tool: '{best_match['goal']}' (similarity: {best_score:.0%})")
            return best_match
        
        return None
    
    def _create_tool_key(self, goal: str) -> str:
        """Create a normalized key from goal"""
        # Normalize: lowercase, remove extra spaces, basic words
        key = goal.lower().strip()
        
        # Remove common words
        common_words = ["the", "a", "an", "to", "and", "or", "in", "on", "at"]
        words = [w for w in key.split() if w not in common_words]
        
        return "_".join(words)
    
    def get_all_tools(self) -> List[Dict]:
        """Get all learned tools"""
        return list(self.tools.values())
    
    def get_tools_summary(self) -> str:
        """Get a summary of learned tools"""
        if not self.tools:
            return "No learned tools yet"
        
        summary = f"📚 **Learned Tools** ({len(self.tools)} total)\n\n"
        
        # Sort by use count
        sorted_tools = sorted(
            self.tools.values(),
            key=lambda t: t["use_count"],
            reverse=True
        )
        
        for tool in sorted_tools[:10]:  # Show top 10
            summary += f"• **{tool['goal']}**\n"
            summary += f"  Used: {tool['use_count']} times | "
            summary += f"Success: {tool['success_rate']:.0%} | "
            summary += f"Time: ~{tool['execution_time']:.0f}s\n"
        
        return summary
    
    def clear_tools(self):
        """Clear all learned tools"""
        self.tools = {}
        self._save_tools()
        print("✓ Cleared all learned tools")


# Global instance
_learned_tools = None

def get_learned_tools() -> LearnedToolsManager:
    """Get or create global learned tools manager"""
    global _learned_tools
    if _learned_tools is None:
        _learned_tools = LearnedToolsManager()
    return _learned_tools
