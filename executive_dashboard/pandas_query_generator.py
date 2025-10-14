import re
import traceback
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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

**CRITICAL: Use ONLY the dataframes and columns listed below.**

**Available DataFrames and Their Columns:**

1. **product_sales** - Regional sales data
   - Columns: Date, Region, Product, Quantity, UnitPrice, TotalPrice, Discount, StoreLocation, CustomerType, Salesperson, PaymentMethod, Promotion, Returned, OrderID, CustomerName, ShippingCost, OrderDate, DeliveryDate, RegionManager
   - Use for: Regional sales/revenue analysis, customer patterns
   - Join key: Product (to join with inventory_data.ProductName)

2. **store_transactions** - Store-level transactions
   - Columns: Date, Time, StoreID, Product, Quantity, UnitPrice, TotalPrice, PaymentType, TransactionID, Cashier, StoreManager, TimeOfDay, DayOfWeek
   - Use for: Store performance, transaction patterns
   - NOTE: Location column has data quality issues - use StoreID instead

3. **inventory_data** - Product inventory with cost data
   - Columns: ProductID, ProductName, QuantityInStock, ReorderPoint, Supplier, SupplierContact, LeadTime, StorageLocation, UnitCost
   - Use for: Cost analysis (has UnitCost), inventory levels
   - Join key: ProductName (to join with product_sales.Product or store_transactions.Product)

4. **customer_data** - Customer purchase history
   - Columns: CustomerID, Product, PurchaseDate, Quantity, UnitPrice, CustomerName, ProductCategory, PaymentMethod, ReviewRating, TotalPrice
   - Use for: Customer behavior, product preferences

**MANDATORY RULES:**

1. **For COST questions** (expenses, costs, margins):
   - MUST merge product_sales or store_transactions with inventory_data
   - Join on: product_sales.Product = inventory_data.ProductName
   - Calculate: TotalCost = UnitCost × Quantity

2. **For REVENUE/SALES questions** (revenue, sales, income):
   - Use TotalPrice from product_sales or store_transactions
   - NO merge needed

3. **For PROFIT/MARGIN questions**:
   - Merge to get both TotalPrice (revenue) and UnitCost
   - Calculate: Profit = TotalPrice - (UnitCost × Quantity)
   - Calculate: Margin = (Profit / TotalPrice) × 100

4. **CRITICAL:** Always store final result in a SINGLE variable called `result`
   - NEVER create multiple result variables like result_x, result_y
   - Choose the most relevant dataframe to compare and assign it to `result`

5. **NO print statements** - only assign to `result`

6. Use .reset_index() after groupby for cleaner output

7. Add brief comments explaining key steps

**Output Format:**
Return ONLY the Python code, no explanations, no print statements.

**Example 1 - Cost Analysis (requires merge):**
```python
# Merge product_sales with inventory_data to get cost information
merged = product_sales.merge(
    inventory_data[['ProductName', 'UnitCost']],
    left_on='Product',
    right_on='ProductName',
    how='left'
)

# Filter for the specified region
region_data = merged[merged['Region'] == 'East']

# Calculate total cost by product
product_costs = region_data.groupby('Product').agg({
    'UnitCost': 'mean',
    'Quantity': 'sum'
}).reset_index()

product_costs['TotalCost'] = product_costs['UnitCost'] * product_costs['Quantity']

# Get top 10 products driving high costs
result = product_costs.nlargest(10, 'TotalCost')[['Product', 'TotalCost', 'Quantity', 'UnitCost']]
```

**Example 2 - Revenue Analysis (no merge needed):**
```python
# Filter for the specified region
region_data = product_sales[product_sales['Region'] == 'East']

# Calculate total revenue by product
product_revenue = region_data.groupby('Product').agg({
    'TotalPrice': 'sum',
    'Quantity': 'sum'
}).reset_index()

# Get top 10 products by revenue
result = product_revenue.nlargest(10, 'TotalPrice')
```

**Example 3 - Profit Analysis (requires merge):**
```python
# Merge to get both revenue and cost data
merged = product_sales.merge(
    inventory_data[['ProductName', 'UnitCost']],
    left_on='Product',
    right_on='ProductName',
    how='left'
)

# Calculate profit
merged['Profit'] = merged['TotalPrice'] - (merged['UnitCost'] * merged['Quantity'])

# Filter by region and analyze
region_profit = merged[merged['Region'] == 'East'].groupby('Product').agg({
    'Profit': 'sum',
    'TotalPrice': 'sum'
}).reset_index()

region_profit['Margin'] = (region_profit['Profit'] / region_profit['TotalPrice'] * 100).round(2)

# Get top 10 most profitable products
result = region_profit.nlargest(10, 'Profit')
```

**Example 4 - Quarter over Quarter Comparison:**
```python
# Convert date column to datetime
store_transactions['Date'] = pd.to_datetime(store_transactions['Date'])

# Get the latest date and define quarters
latest_date = store_transactions['Date'].max()
last_quarter_start = latest_date - pd.DateOffset(months=3)
quarter_before_start = latest_date - pd.DateOffset(months=6)

# Filter data for each quarter
last_quarter = store_transactions[store_transactions['Date'] >= last_quarter_start]
quarter_before = store_transactions[(store_transactions['Date'] >= quarter_before_start) &
                                   (store_transactions['Date'] < last_quarter_start)]

# Calculate metrics for each quarter
comparison = pd.DataFrame({
    'Quarter': ['Q-1 (Recent)', 'Q-2 (Previous)'],
    'Revenue': [last_quarter['TotalPrice'].sum(), quarter_before['TotalPrice'].sum()],
    'Transactions': [len(last_quarter), len(quarter_before)],
    'Avg_Transaction': [last_quarter['TotalPrice'].mean(), quarter_before['TotalPrice'].mean()]
})

# Calculate changes
comparison['Revenue_Change_%'] = ((comparison['Revenue'].iloc[0] - comparison['Revenue'].iloc[1]) /
                                  comparison['Revenue'].iloc[1] * 100).round(2)

# Single result variable
result = comparison
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

    def query_with_code_generation(
        self, question: str
    ) -> Tuple[str, Optional[go.Figure]]:
        """Complete pipeline: generate code, execute, analyze, and create visualization

        Returns:
            Tuple of (analysis_text, plotly_figure)
        """

        # Get data context
        data_context = self._build_data_context()

        # Generate pandas code
        code = self.generate_code(question, data_context)

        # Execute code
        execution_result = self.execute_code(code)

        # If execution failed, return error
        if not execution_result["success"]:
            error_msg = f"""**Code Generation Approach**

I generated pandas code to answer your question, but execution failed:

**Generated Code:**
```python
{code}
```

**Error:**
{execution_result['error']}

Let me try a different approach or please rephrase your question."""
            return (error_msg, None)

        # Analyze results
        analysis = self.analyze_results(question, execution_result)

        # Generate visualization
        viz = self.create_visualization(question, execution_result)

        # Return analysis and metadata separately for better UI rendering
        response = {
            "analysis": analysis,
            "code": code,
            "result_type": execution_result["result_type"],
        }

        return (response, viz)

    def create_visualization(
        self, question: str, execution_result: Dict[str, Any]
    ) -> Optional[go.Figure]:
        """Automatically create appropriate visualization based on query results"""

        if not execution_result["success"]:
            return None

        result = execution_result["result"]

        # Only visualize DataFrames and Series
        if not isinstance(result, (pd.DataFrame, pd.Series)):
            return None

        try:
            # Convert Series to DataFrame for easier handling
            if isinstance(result, pd.Series):
                df = result.reset_index()
                df.columns = ["Category", "Value"]
            else:
                df = result.copy()

            # Skip if result is too small or empty
            if len(df) == 0:
                return None

            # Determine visualization type based on data structure
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

            if len(numeric_cols) == 0:
                return None

            # Case 1: Single numeric column - bar chart
            if len(numeric_cols) == 1:
                value_col = numeric_cols[0]

                # Get categorical column (first non-numeric)
                cat_cols = [c for c in df.columns if c not in numeric_cols]
                if cat_cols:
                    cat_col = cat_cols[0]

                    # Limit to top 15 entries for readability
                    if len(df) > 15:
                        df_plot = df.nlargest(15, value_col)
                    else:
                        df_plot = df

                    fig = px.bar(
                        df_plot,
                        x=cat_col,
                        y=value_col,
                        title=f"{value_col} by {cat_col}",
                        labels={value_col: value_col.replace("_", " ").title()},
                        color=value_col,
                        color_continuous_scale="Blues",
                    )
                    fig.update_layout(height=400, xaxis_tickangle=-45)
                    return fig

            # Case 2: Multiple numeric columns - grouped bar chart or line chart
            elif len(numeric_cols) >= 2:
                cat_cols = [c for c in df.columns if c not in numeric_cols]

                if cat_cols:
                    cat_col = cat_cols[0]

                    # Limit data
                    if len(df) > 15:
                        # Sum numeric columns and take top entries
                        df["_total"] = df[numeric_cols].sum(axis=1)
                        df_plot = df.nlargest(15, "_total").drop("_total", axis=1)
                    else:
                        df_plot = df

                    # Check if we should use line chart (time series) or bar chart
                    if "date" in cat_col.lower() or "time" in cat_col.lower():
                        # Line chart for time series
                        fig = px.line(
                            df_plot,
                            x=cat_col,
                            y=numeric_cols,
                            title=f"Trend Analysis",
                            labels={cat_col: cat_col.replace("_", " ").title()},
                        )
                    else:
                        # Grouped bar chart
                        fig = px.bar(
                            df_plot,
                            x=cat_col,
                            y=numeric_cols,
                            title=f"Comparison Across {cat_col.replace('_', ' ').title()}",
                            barmode="group",
                        )

                    fig.update_layout(height=400, xaxis_tickangle=-45)
                    return fig
                else:
                    # No categorical column - use index
                    if len(numeric_cols) == 2:
                        # Scatter plot for two numeric columns
                        fig = px.scatter(
                            df,
                            x=numeric_cols[0],
                            y=numeric_cols[1],
                            title=f"{numeric_cols[1]} vs {numeric_cols[0]}",
                            trendline="ols",
                        )
                        fig.update_layout(height=400)
                        return fig

            return None

        except Exception as e:
            # If visualization creation fails, return None silently
            print(f"Visualization error: {e}")
            return None

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
