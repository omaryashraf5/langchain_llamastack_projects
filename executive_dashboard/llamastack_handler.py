import os
from datetime import datetime
from typing import Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_llama_stack import ChatLlamaStack


class LlamaStackLLM:
    """LlamaStack integration with conversation history for follow-ups

    Uses the official ChatLlamaStack from langchain-llama-stack package.
    """

    def __init__(
        self,
        api_url: str = None,
        model: str = "ollama/llama3.3:70b",
        temperature: float = 0.7,
        max_history: int = 10,
    ):
        self.api_url = api_url or os.getenv(
            "LLAMASTACK_API_URL", "http://localhost:8321"
        )
        self.model = model or os.getenv("LLAMASTACK_MODEL", "ollama/llama3.3:70b")
        self.temperature = temperature

        # ChatLlamaStack needs the OpenAI-compatible endpoint
        openai_endpoint = f"{self.api_url}/v1/openai/v1/"

        # Initialize ChatLlamaStack
        self.llm = ChatLlamaStack(
            model=self.model,
            base_url=openai_endpoint,
            temperature=self.temperature,
        )

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
        """Send chat completion request to LlamaStack using ChatLlamaStack"""

        try:
            # Convert messages format for LangChain
            lc_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    lc_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))

            # Create a temporary LLM instance with custom parameters if needed
            if temperature is not None or max_tokens is not None:
                openai_endpoint = f"{self.api_url}/v1/openai/v1/"
                kwargs = {"model": self.model, "base_url": openai_endpoint}
                if temperature is not None:
                    kwargs["temperature"] = temperature
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                temp_llm = ChatLlamaStack(**kwargs)
                response = temp_llm.invoke(lc_messages)
            else:
                response = self.llm.invoke(lc_messages)

            return response.content

        except Exception as e:
            return f"Error calling LlamaStack API: {str(e)}"

    def is_available(self) -> bool:
        """Check if LlamaStack is available"""
        try:
            # Try a minimal chat completion to verify service
            response = self.llm.invoke([HumanMessage(content="hi")])
            return bool(response.content)
        except Exception as e:
            # Print error for debugging
            print(f"LLM availability check failed: {e}")
            return False

    def send_message(
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
            "provider": "LlamaStack (ChatLlamaStack)",
        }

    def undo_last_exchange(self):
        """Remove the last user message and assistant response"""
        if len(self.conversation_history) >= 2:
            self.conversation_history = self.conversation_history[:-2]
            return True
        return False
