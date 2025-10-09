import os
from datetime import datetime
from typing import Dict, List, Optional

import requests


class LlamaStackLLM:
    """LlamaStack integration with conversation history for follow-ups

    LlamaStack acts as a wrapper around Ollama, providing a unified API
    for inference with better request/response handling.
    """

    def __init__(
        self,
        api_url: str = None,
        model: str = "llama3:70b-instruct",
        temperature: float = 0.7,
        max_history: int = 10,
    ):
        self.api_url = api_url or os.getenv(
            "LLAMASTACK_API_URL", "http://localhost:8321"
        )
        self.model = model or os.getenv("LLAMASTACK_MODEL", "llama3:70b-instruct")
        self.temperature = temperature
        self.endpoint = f"{self.api_url}/v1/chat/completions"

        # Conversation history management
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []
        self.session_start = datetime.now()

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str:
        """Send chat completion request to LlamaStack

        LlamaStack uses OpenAI-compatible API format.
        """

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "stream": stream,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120,  # LlamaStack can be slow on first request
            )
            response.raise_for_status()

            result = response.json()

            # Extract content from OpenAI-compatible format
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            return f"Error calling LlamaStack API: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Error parsing LlamaStack response: {str(e)}"

    def is_available(self) -> bool:
        """Check if LlamaStack is available"""
        try:
            # Try a minimal chat completion to verify service
            test_payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 1,
                "stream": False,
            }
            response = requests.post(
                self.endpoint,
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            return response.status_code == 200
        except:
            return False

    def chat_with_history(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send a message with conversation history for follow-ups"""

        # Build messages list with history
        messages = []

        # Add system message if provided (only at start)
        if system_message and len(self.conversation_history) == 0:
            messages.append({"role": "system", "content": system_message})

        # Add conversation history (keep only recent messages based on max_history)
        start_idx = max(0, len(self.conversation_history) - self.max_history * 2)
        messages.extend(self.conversation_history[start_idx:])

        # Add new user message
        messages.append({"role": "user", "content": user_message})

        # Get response
        response = self.chat_completion(messages, temperature, max_tokens)

        # Store in history (if not an error message)
        if not response.startswith("Error"):
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response})

            # Trim history if it gets too long
            if len(self.conversation_history) > self.max_history * 2:
                # Keep system message if present, then trim oldest exchanges
                self.conversation_history = self.conversation_history[
                    -(self.max_history * 2) :
                ]

        return response

    def clear_history(self):
        """Clear conversation history - useful for starting fresh"""
        self.conversation_history = []
        self.session_start = datetime.now()

    def get_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history"""
        return self.conversation_history.copy()

    def get_history_summary(self) -> Dict[str, any]:
        """Get summary of conversation state"""
        return {
            "message_count": len(self.conversation_history),
            "session_duration": str(datetime.now() - self.session_start),
            "session_start": self.session_start.strftime("%Y-%m-%d %H:%M:%S"),
            "model": self.model,
            "provider": "LlamaStack (Ollama wrapper)",
        }

    def undo_last_exchange(self):
        """Remove the last user message and assistant response"""
        if len(self.conversation_history) >= 2:
            self.conversation_history = self.conversation_history[:-2]
            return True
        return False
