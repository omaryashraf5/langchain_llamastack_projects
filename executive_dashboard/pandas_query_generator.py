import re
import traceback
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd


class PandasCodeGenerator:
    """Generate and execute pandas code based on natural language queries using LLM"""

    def __init__(self, llm_backend, data_loader):
        self.llm = llm_backend
        self.data_loader = data_loader
        self.safe_imports = {
            "pd": pd,
            "np": np,
        }

    def generate_code(self, question: str, data_context: str) -> str:
        """Ask LLM to generate pandas code for the query"""

        system_prompt = """You are an expert Python data analyst. Generate pandas code to answer questions about retail data.

**Available DataFrames:**
- `store_transactions`: Columns = Date, StoreID, Location, Product, Quantity, UnitPrice, TotalPrice, PaymentType
- `product_sales`: Columns = Date, Region, Product, Quantity, UnitPrice, TotalPrice, UnitCost, Discount
- `inventory_data`: Columns = ProductID, ProductName, QuantityInStock, ReorderPoint, UnitCost
- `customer_data`: Columns = CustomerID, Product, PurchaseDate, TotalPrice, ReviewRating

**Rules:**
1. Write clean, executable pandas code
2. Use descriptive variable names
3. Store the final result in a variable called `result`
4. Include calculations, aggregations, filtering as needed
5. Handle missing data gracefully
6. Return result as a DataFrame or Series when possible
7. Add brief comments explaining key operations

**Output Format:**
Return ONLY the Python code, no explanations before or after.
Start directly with the code.

**Example:**
Question: "Which stores have revenue above $50,000?"
Code:
```python
# Calculate total revenue by store
store_revenue = store_transactions.groupby('StoreID')['TotalPrice'].sum()

# Filter stores above threshold
result = store_revenue[store_revenue > 50000].sort_values(ascending=False)
```
"""

        user_message = f"""Question: {question}

Data Context:
{data_context}

Generate pandas code to answer this question using the available dataframes."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        response = self.llm.chat_completion(messages, temperature=0.1, max_tokens=800)

        # Extract code from markdown code blocks if present
        code = self._extract_code(response)

        return code

    def _extract_code(self, response: str) -> str:
        """Extract Python code from LLM response, handling markdown code blocks"""
        # Try to extract from ```python ... ``` blocks
        pattern = r"```python\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Try to extract from ``` ... ``` blocks
        pattern = r"```\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Return as-is if no code blocks found
        return response.strip()

    def execute_code(self, code: str) -> Dict[str, Any]:
        """Safely execute generated pandas code"""

        # Prepare execution environment with dataframes
        exec_globals = self.safe_imports.copy()
        exec_globals.update(
            {
                "store_transactions": self.data_loader.store_transactions,
                "product_sales": self.data_loader.product_sales,
                "inventory_data": self.data_loader.inventory_data,
                "customer_data": self.data_loader.customer_data,
            }
        )

        exec_locals = {}

        try:
            # Execute the code
            exec(code, exec_globals, exec_locals)

            # Get the result
            result = exec_locals.get("result", None)

            if result is None:
                return {
                    "success": False,
                    "error": "Code did not produce a `result` variable",
                    "code": code,
                }

            return {
                "success": True,
                "result": result,
                "code": code,
                "result_type": type(result).__name__,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "code": code,
            }

    def format_result(self, execution_result: Dict[str, Any]) -> str:
        """Format execution result for LLM to analyze"""

        if not execution_result["success"]:
            return f"Error executing code:\n{execution_result['error']}"

        result = execution_result["result"]

        # Format based on result type
        if isinstance(result, pd.DataFrame):
            if len(result) > 20:
                formatted = f"DataFrame with {len(result)} rows and {len(result.columns)} columns\n\n"
                formatted += "First 10 rows:\n"
                formatted += result.head(10).to_string()
                formatted += f"\n\n... (showing 10 of {len(result)} rows)"
            else:
                formatted = result.to_string()

        elif isinstance(result, pd.Series):
            if len(result) > 20:
                formatted = f"Series with {len(result)} values\n\n"
                formatted += "First 10 values:\n"
                formatted += result.head(10).to_string()
                formatted += f"\n\n... (showing 10 of {len(result)} values)"
            else:
                formatted = result.to_string()

        elif isinstance(result, (int, float, str)):
            formatted = f"Result: {result}"

        elif isinstance(result, dict):
            formatted = "Result (dictionary):\n"
            for k, v in result.items():
                formatted += f"  {k}: {v}\n"

        else:
            formatted = str(result)

        return formatted

    def analyze_results(self, question: str, execution_result: Dict[str, Any]) -> str:
        """Have LLM analyze the execution results and provide insights"""

        formatted_result = self.format_result(execution_result)

        system_prompt = """You are a retail analytics expert. Analyze data query results and provide clear insights for C-suite executives.

**Your Response Should Include:**
1. Direct answer to the question
2. Key insights and patterns
3. Specific numbers and percentages
4. Business implications
5. Recommendations (if applicable)

Be concise, data-driven, and executive-friendly."""

        user_message = f"""Original Question: {question}

Code Executed:
```python
{execution_result.get('code', 'N/A')}
```

Results:
{formatted_result}

Provide a clear analysis and answer."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        response = self.llm.chat_completion(messages, temperature=0.3, max_tokens=1000)

        return response

    def query_with_code_generation(self, question: str) -> str:
        """Complete pipeline: generate code, execute, analyze"""

        # Get data context
        data_context = self._build_data_context()

        # Generate pandas code
        code = self.generate_code(question, data_context)

        # Execute code
        execution_result = self.execute_code(code)

        # If execution failed, return error
        if not execution_result["success"]:
            return f"""**Code Generation Approach**

I generated pandas code to answer your question, but execution failed:

**Generated Code:**
```python
{code}
```

**Error:**
{execution_result['error']}

Let me try a different approach or please rephrase your question."""

        # Analyze results
        analysis = self.analyze_results(question, execution_result)

        # Format response
        response = f"""**Dynamic Code Execution**

{analysis}

<details>
<summary>🔍 View Generated Code</summary>

```python
{code}
```

**Result Type:** {execution_result['result_type']}
</details>"""

        return response

    def _build_data_context(self) -> str:
        """Build minimal data context for code generation"""
        context = []

        if self.data_loader.store_transactions is not None:
            df = self.data_loader.store_transactions
            context.append(
                f"store_transactions: {len(df)} rows, date range: {df['Date'].min()} to {df['Date'].max()}"
            )

        if self.data_loader.product_sales is not None:
            df = self.data_loader.product_sales
            regions = df["Region"].unique()
            context.append(
                f"product_sales: {len(df)} rows, regions: {', '.join(regions)}"
            )

        if self.data_loader.inventory_data is not None:
            df = self.data_loader.inventory_data
            context.append(f"inventory_data: {len(df)} products")

        if self.data_loader.customer_data is not None:
            df = self.data_loader.customer_data
            context.append(f"customer_data: {len(df)} transactions")

        return "\n".join(context)
