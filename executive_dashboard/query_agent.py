import os
from typing import Any, Dict

import pandas as pd

try:
    from llamastack_handler import LlamaStackLLM
    from llm_handler import DataContextBuilder, QueryPromptBuilder
    from pandas_query_generator import PandasCodeGenerator

    LLM_HANDLER_AVAILABLE = True
except ImportError:
    LLM_HANDLER_AVAILABLE = False
    LlamaStackLLM = None
    QueryPromptBuilder = None
    DataContextBuilder = None
    PandasCodeGenerator = None
    PandasCodeGenerator = None
    PandasCodeGenerator = None

try:
    from langchain_experimental.agents import create_pandas_dataframe_agent
    from langchain_experimental.agents.agent_toolkits import create_python_agent
    from langchain_experimental.tools.python.tool import PythonREPLTool

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    create_pandas_dataframe_agent = None
    create_python_agent = None
    PythonREPLTool = None


class QueryAgent:
    def __init__(self, data_loader, llm=None, use_llamastack=True):
        self.data_loader = data_loader
        self.llm = llm
        self.agent = None
        self.use_llamastack = use_llamastack

        if use_llamastack and LLM_HANDLER_AVAILABLE:
            self.llm_backend = LlamaStackLLM()
            self.prompt_builder = QueryPromptBuilder()
            self.context_builder = DataContextBuilder(data_loader)
            self.code_generator = PandasCodeGenerator(self.llm_backend, data_loader)
            self.llm_available = self.llm_backend.is_available()
            self.use_code_generation = True  # Enable dynamic code generation
        else:
            self.llm_backend = None
            self.code_generator = None
            self.llm_available = False
            self.use_code_generation = False

    def setup_agent(self):
        if not LANGCHAIN_AVAILABLE:
            print("Info: LangChain not installed. Using fallback query methods.")
            return

        if self.llm is None:
            print(
                "Warning: No LLM provided. Query agent functionality will be limited."
            )
            return

        all_data = self.data_loader.load_all_data()

        try:
            self.agent = create_pandas_dataframe_agent(
                self.llm,
                list(all_data.values()),
                verbose=True,
                allow_dangerous_code=True,
            )
        except Exception as e:
            print(f"Error setting up agent: {e}")

    def query(self, question: str, use_code_gen: bool = None):
        """Query the data and return (text_response, visualization_figure)

        Returns:
            Tuple of (str, Optional[plotly.graph_objects.Figure])
        """
        # Check if LLM is available
        if not self.llm_available:
            return (
                "❌ LLM is not available. Please ensure LlamaStack server is running and configured correctly.",
                None,
            )

        # Auto-enable code generation if not specified
        if use_code_gen is None:
            use_code_gen = self.use_code_generation

        # Try code generation approach if enabled
        if use_code_gen and self.code_generator:
            try:
                return self.code_generator.query_with_code_generation(question)
            except Exception as e:
                # Fallback to text-based LLM approach if code gen fails
                return (self._query_with_llm(question), None)
        else:
            # Use text-based LLM approach
            return (self._query_with_llm(question), None)

    def _query_with_llm(self, question: str, use_history: bool = True) -> str:
        try:
            query_type = self.prompt_builder.classify_query(question)
            data_summary = self.context_builder.build_data_summary(query_type)

            # Build system message based on query type
            if query_type == "performance":
                system_message = """You are analyzing performance metrics for a retail chain.
Focus on: revenue trends, sales volumes, transaction counts, growth rates.
Provide specific numbers, percentages, and clear comparisons."""
            elif query_type == "comparison":
                system_message = """You are comparing business metrics across different dimensions.
Focus on: period-over-period comparisons, regional differences, product category comparisons.
Highlight significant differences and provide context."""
            elif query_type == "anomaly":
                system_message = """You are identifying and explaining anomalies in retail business data.
Focus on: outliers, unusual patterns, underperformance, overperformance.
Provide statistical context (standard deviations, percentiles) when relevant."""
            elif query_type == "drilldown":
                system_message = """You are conducting a deep-dive analysis to understand root causes.
Focus on: cost drivers, revenue components, operational factors.
Break down complex metrics into understandable components."""
            else:
                data_context = self.context_builder.build_context()
                system_message = self.prompt_builder.build_system_prompt(data_context)

            # Use conversation history for follow-ups
            if use_history:
                # Build user message with data context
                user_message = (
                    f"Question: {question}\n\nAvailable Data Summary:\n{data_summary}"
                )

                response = self.llm_backend.chat_with_history(
                    user_message=user_message,
                    system_message=system_message,
                    temperature=0.3,
                    max_tokens=1500,
                )
            else:
                # One-off query without history
                if query_type == "performance":
                    messages = self.prompt_builder.build_performance_query_prompt(
                        question, data_summary
                    )
                elif query_type == "comparison":
                    messages = self.prompt_builder.build_comparison_query_prompt(
                        question, data_summary
                    )
                elif query_type == "anomaly":
                    messages = self.prompt_builder.build_anomaly_query_prompt(
                        question, data_summary
                    )
                elif query_type == "drilldown":
                    messages = self.prompt_builder.build_drilldown_query_prompt(
                        question, data_summary
                    )
                else:
                    messages = [
                        {"role": "system", "content": system_message},
                        {
                            "role": "user",
                            "content": f"Question: {question}\n\nData Summary:\n{data_summary}",
                        },
                    ]

                response = self.llm_backend.chat_completion(
                    messages, temperature=0.3, max_tokens=1500
                )

            return f"**Query Type:** {query_type.title()}\n\n{response}"

        except Exception as e:
            return f"Error with LLM query: {str(e)}\n\nFalling back to simple analysis...\n\n{self._fallback_query(question)}"

    def clear_conversation(self):
        """Clear conversation history"""
        if self.llm_backend:
            self.llm_backend.clear_history()

    def get_conversation_summary(self):
        """Get conversation history summary"""
        if self.llm_backend:
            return self.llm_backend.get_history_summary()
        return None

    def undo_last_query(self):
        """Undo the last query and response"""
        if self.llm_backend:
            return self.llm_backend.undo_last_exchange()
        return False
