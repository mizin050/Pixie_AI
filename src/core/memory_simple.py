import os
import json
from datetime import datetime

class ChatMemorySimple:
    """Simple JSON-based chat memory - no external dependencies"""
    
    def __init__(self, history_file=None):
        # Save history file in the project root directory
        if history_file is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.history_file = os.path.join(project_root, "chat_history.json")
        else:
            self.history_file = history_file
        
        self.history = []
        self._load_history()
        print(f"📁 History file location: {self.history_file}")
    
    def _load_history(self):
        """Load history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                print(f"✓ Loaded {len(self.history)} messages from history")
            except Exception as e:
                print(f"⚠ Error loading history: {e}")
                self.history = []
        else:
            print("✓ Starting with empty chat history")
    
    def _save_history(self):
        """Save history to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.history_file) if os.path.dirname(self.history_file) else '.', exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(self.history)} messages to history")
        except Exception as e:
            print(f"⚠ Error saving history: {e}")
            import traceback
            traceback.print_exc()
    
    def add_message(self, role, content, metadata=None):
        """Add a message to memory"""
        message_data = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.history.append(message_data)
        self._save_history()
    
    def get_context(self, max_messages=10):
        """Get recent conversation context for AI"""
        recent = self.history[-max_messages:] if len(self.history) > max_messages else self.history
        return [{"role": msg["role"], "content": msg["content"]} for msg in recent]
    
    def get_all_messages(self):
        """Get all messages for display"""
        return self.history
    
    def search_history(self, query):
        """Search through chat history using simple text matching"""
        query_lower = query.lower()
        results = [msg for msg in self.history if query_lower in msg["content"].lower()]
        return results
    
    def clear_history(self):
        """Clear all chat history"""
        self.history = []
        self._save_history()
        print("✓ Chat history cleared")
    
    def get_relevant_context(self, query, max_results=5):
        """Get contextually relevant messages based on query"""
        results = self.search_history(query)
        return [{"role": msg["role"], "content": msg["content"]} for msg in results[:max_results]]
