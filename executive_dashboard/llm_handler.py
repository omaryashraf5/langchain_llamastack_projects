from typing import Any, Dict, List


class QueryPromptBuilder:
    @staticmethod
    def build_system_prompt(data_context: Dict[str, Any]) -> str:
        return f"""You are an expert retail analytics assistant helping C-suite executives analyze business data.

**Available Data Context:**
- Total Stores: {data_context.get('total_stores', 'N/A')}
- Total Products: {data_context.get('total_products', 'N/A')}
- Regions: {', '.join(data_context.get('regions', []))}
- Date Range: {data_context.get('date_range', 'N/A')}
- Available Metrics: Revenue, Costs, Profit Margins, Inventory, Customer Satisfaction

**Data Columns Available:**
- Store Transactions: Date, StoreID, Location, Product, Quantity, UnitPrice, TotalPrice, PaymentType
- Product Sales by Region: Date, Region, Product, Quantity, UnitPrice, TotalPrice, UnitCost, Discount
- Inventory: ProductID, ProductName, QuantityInStock, ReorderPoint, UnitCost
- Customer Data: CustomerID, Product, PurchaseDate, TotalPrice, ReviewRating

**Your Role:**
1. Understand the executive's question
2. Determine what data analysis is needed
3. Provide clear, actionable insights
4. Use business language appropriate for C-suite executives

**Response Format:**
- Be concise and data-driven
- Include specific numbers and percentages
- Highlight key insights and recommendations
- Use markdown formatting for clarity"""

    @staticmethod
    def build_performance_query_prompt(
        question: str, data_summary: str
    ) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": """You are analyzing performance metrics for a retail chain.
Focus on: revenue trends, sales volumes, transaction counts, growth rates.
Provide specific numbers, percentages, and clear comparisons.""",
            },
            {
                "role": "user",
                "content": f"""Question: {question}

Available Data Summary:
{data_summary}

Please analyze the performance data and provide:
1. Key performance metrics
2. Trends (up/down, percentage changes)
3. Top performers
4. Areas of concern
5. Executive summary""",
            },
        ]

    @staticmethod
    def build_comparison_query_prompt(
        question: str, data_summary: str
    ) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": """You are comparing business metrics across different dimensions.
Focus on: period-over-period comparisons, regional differences, product category comparisons.
Highlight significant differences and provide context.""",
            },
            {
                "role": "user",
                "content": f"""Question: {question}

Available Data Summary:
{data_summary}

Please provide a comparison analysis including:
1. What is being compared (timeframes, regions, stores, etc.)
2. Percentage differences and absolute values
3. Winners and losers
4. Factors driving differences
5. Actionable recommendations""",
            },
        ]

    @staticmethod
    def build_anomaly_query_prompt(
        question: str, data_summary: str
    ) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": """You are identifying and explaining anomalies in retail business data.
Focus on: outliers, unusual patterns, underperformance, overperformance.
Provide statistical context (standard deviations, percentiles) when relevant.""",
            },
            {
                "role": "user",
                "content": f"""Question: {question}

Available Data Summary:
{data_summary}

Please identify and analyze anomalies:
1. Which entities (stores/products/regions) are outliers?
2. How significant is the deviation? (percentage, z-scores)
3. Possible root causes
4. Is this a concern or opportunity?
5. Recommended actions""",
            },
        ]

    @staticmethod
    def build_drilldown_query_prompt(
        question: str, data_summary: str
    ) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": """You are conducting a deep-dive analysis to understand root causes.
Focus on: cost drivers, revenue components, operational factors.
Break down complex metrics into understandable components.""",
            },
            {
                "role": "user",
                "content": f"""Question: {question}

Available Data Summary:
{data_summary}

Please provide a drill-down analysis:
1. What are the main components/drivers?
2. Breakdown by relevant dimensions (products, time, location)
3. Which factors contribute most?
4. Root cause analysis
5. Specific recommendations to address issues""",
            },
        ]

    @staticmethod
    def classify_query(question: str) -> str:
        question_lower = question.lower()

        performance_keywords = [
            "sales",
            "revenue",
            "performance",
            "trend",
            "growth",
            "volume",
            "q1",
            "q2",
            "q3",
            "q4",
            "quarter",
            "month",
            "year",
        ]
        comparison_keywords = [
            "compare",
            "versus",
            "vs",
            "difference",
            "better",
            "worse",
            "than",
            "last year",
            "this year",
        ]
        anomaly_keywords = [
            "underperforming",
            "overperforming",
            "outlier",
            "unusual",
            "anomaly",
            "spike",
            "drop",
            "concern",
            "problem",
        ]
        drilldown_keywords = [
            "why",
            "what's driving",
            "cause",
            "reason",
            "breakdown",
            "detail",
            "explain",
            "factors",
        ]

        scores = {
            "performance": sum(
                1 for kw in performance_keywords if kw in question_lower
            ),
            "comparison": sum(1 for kw in comparison_keywords if kw in question_lower),
            "anomaly": sum(1 for kw in anomaly_keywords if kw in question_lower),
            "drilldown": sum(1 for kw in drilldown_keywords if kw in question_lower),
        }

        if max(scores.values()) == 0:
            return "general"

        return max(scores, key=scores.get)


class DataContextBuilder:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def build_context(self) -> Dict[str, Any]:
        context = {}

        if self.data_loader.store_transactions is not None:
            stores = self.data_loader.store_transactions["StoreID"].unique()
            context["total_stores"] = len(stores)

            if "Date" in self.data_loader.store_transactions.columns:
                dates = self.data_loader.store_transactions["Date"]
                context["date_range"] = f"{dates.min()} to {dates.max()}"

        if self.data_loader.product_sales is not None:
            regions = self.data_loader.product_sales["Region"].unique()
            context["regions"] = list(regions)

            products = self.data_loader.product_sales["Product"].unique()
            context["total_products"] = len(products)

        if self.data_loader.inventory_data is not None:
            context["inventory_items"] = len(self.data_loader.inventory_data)

        return context

    def build_data_summary(self, query_type: str = "general") -> str:
        summary_parts = []

        if self.data_loader.store_transactions is not None:
            df = self.data_loader.store_transactions
            total_revenue = df["TotalPrice"].sum()
            avg_transaction = df["TotalPrice"].mean()
            transaction_count = len(df)

            store_summary = (
                df.groupby("StoreID")["TotalPrice"]
                .agg(["sum", "count", "mean"])
                .round(2)
            )
            top_stores = store_summary.nlargest(3, "sum")
            bottom_stores = store_summary.nsmallest(3, "sum")

            summary_parts.append(
                f"""**Store Performance:**
- Total Revenue: ${total_revenue:,.2f}
- Total Transactions: {transaction_count:,}
- Average Transaction: ${avg_transaction:.2f}

Top 3 Stores by Revenue:
{top_stores.to_string()}

Bottom 3 Stores by Revenue:
{bottom_stores.to_string()}
"""
            )

        if self.data_loader.product_sales is not None:
            df = self.data_loader.product_sales

            regional_summary = (
                df.groupby("Region")
                .agg({"TotalPrice": "sum", "Quantity": "sum"})
                .round(2)
            )

            summary_parts.append(
                f"""**Regional Performance:**
{regional_summary.to_string()}
"""
            )

        if self.data_loader.inventory_data is not None:
            df = self.data_loader.inventory_data
            low_stock_count = len(df[df["QuantityInStock"] < df["ReorderPoint"]])

            summary_parts.append(
                f"""**Inventory Status:**
- Total Items: {len(df)}
- Low Stock Items: {low_stock_count}
- Average Stock Level: {df['QuantityInStock'].mean():.0f}
"""
            )

        if self.data_loader.customer_data is not None:
            df = self.data_loader.customer_data
            if "ReviewRating" in df.columns:
                avg_rating = df["ReviewRating"].mean()
                summary_parts.append(
                    f"""**Customer Metrics:**
- Average Rating: {avg_rating:.2f}/5.0
- Total Customers: {df['CustomerID'].nunique()}
"""
                )

        return "\n".join(summary_parts)
