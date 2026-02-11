from mem0 import Memory
import os
import sys
from datetime import datetime
import json

# Add project root to path if needed
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class ChatMemoryMem0:
    """Manages persistent chat history using Mem0 with local storage"""
    
    def __init__(self):
        # Configure Mem0 to use local storage with Qdrant
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "pixie_chat",
                    "path": "./mem0_db",  # Local storage path
                    "on_disk": True
                }
            },
            "version": "v1.1"
        }
        
        try:
            self.memory = Memory.from_config(config)
            self.user_id = "pixie_user"
            print("✓ Mem0 initialized with local Qdrant storage")
        except Exception as e:
            print(f"⚠ Mem0 initialization failed, using JSON fallback: {e}")
            self.memory = None
            self.history = []
            self.history_file = "chat_history.json"
            self._load_fallback_history()
    
    def _load_fallback_history(self):
        """Load history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"Error loading fallback history: {e}")
                self.history = []
    
    def _save_fallback_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving fallback history: {e}")
    
    def add_message(self, role, content, metadata=None):
        """Add a message to memory"""
        message_data = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        if self.memory:
            try:
                # Add to Mem0 with structured data
                self.memory.add(
                    messages=[{
                        "role": role,
                        "content": content
                    }],
                    user_id=self.user_id,
                    metadata=message_data
                )
            except Exception as e:
                print(f"Error adding to Mem0: {e}")
                self.history.append(message_data)
                self._save_fallback_history()
        else:
            # Fallback mode
            self.history.append(message_data)
            self._save_fallback_history()
    
    def get_context(self, max_messages=10):
        """Get recent conversation context for AI"""
        if self.memory:
            try:
                # Get all memories for the user
                memories = self.memory.get_all(user_id=self.user_id)
                
                # Extract messages from memories
                messages = []
                for mem in memories[-max_messages:]:
                    if 'metadata' in mem and 'role' in mem['metadata']:
                        messages.append({
                            "role": mem['metadata']['role'],
                            "content": mem['metadata']['content']
                        })
                
                return messages
            except Exception as e:
                print(f"Error getting context from Mem0: {e}")
                return self._get_fallback_context(max_messages)
        else:
            return self._get_fallback_context(max_messages)
    
    def _get_fallback_context(self, max_messages):
        """Fallback context retrieval"""
        recent = self.history[-max_messages:] if len(self.history) > max_messages else self.history
        return [{"role": msg["role"], "content": msg["content"]} for msg in recent]
    
    def get_all_messages(self):
        """Get all messages for display"""
        if self.memory:
            try:
                memories = self.memory.get_all(user_id=self.user_id)
                messages = []
                for mem in memories:
                    if 'metadata' in mem:
                        messages.append(mem['metadata'])
                return messages
            except Exception as e:
                print(f"Error getting all messages: {e}")
                return self.history
        else:
            return self.history
    
    def search_history(self, query):
        """Search through chat history using Mem0's semantic search"""
        if self.memory:
            try:
                # Use Mem0's search capability
                results = self.memory.search(
                    query=query,
                    user_id=self.user_id,
                    limit=10
                )
                
                messages = []
                for result in results:
                    if 'metadata' in result:
                        messages.append(result['metadata'])
                
                return messages
            except Exception as e:
                print(f"Error searching with Mem0: {e}")
                return self._fallback_search(query)
        else:
            return self._fallback_search(query)
    
    def _fallback_search(self, query):
        """Fallback search using simple text matching"""
        query_lower = query.lower()
        results = [msg for msg in self.history if query_lower in msg["content"].lower()]
        return results
    
    def clear_history(self):
        """Clear all chat history"""
        if self.memory:
            try:
                # Delete all memories for the user
                memories = self.memory.get_all(user_id=self.user_id)
                for mem in memories:
                    if 'id' in mem:
                        self.memory.delete(memory_id=mem['id'])
                print("✓ Mem0 history cleared")
            except Exception as e:
                print(f"Error clearing Mem0 history: {e}")
        
        # Also clear fallback
        self.history = []
        self._save_fallback_history()
    
    def get_relevant_context(self, query, max_results=5):
        """Get contextually relevant memories based on current query"""
        if self.memory:
            try:
                results = self.memory.search(
                    query=query,
                    user_id=self.user_id,
                    limit=max_results
                )
                
                context = []
                for result in results:
                    if 'metadata' in result and 'content' in result['metadata']:
                        context.append({
                            "role": result['metadata'].get('role', 'user'),
                            "content": result['metadata']['content']
                        })
                
                return context
            except Exception as e:
                print(f"Error getting relevant context: {e}")
                return []
        else:
            return []
