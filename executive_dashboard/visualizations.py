import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class DashboardVisualizations:
    def __init__(self, data_loader, metrics_calculator):
        self.data_loader = data_loader
        self.metrics_calculator = metrics_calculator

    def create_revenue_trend_chart(self):
        transactions = self.data_loader.store_transactions

        if transactions is None:
            return None

        date_col = None
        for col in transactions.columns:
            if "date" in col.lower():
                date_col = col
                break

        if date_col is None:
            daily_revenue = (
                transactions.groupby(transactions.index // 100)["TotalPrice"]
                .sum()
                .reset_index()
            )
            daily_revenue.columns = ["Day", "Revenue"]
            fig = px.line(
                daily_revenue,
                x="Day",
                y="Revenue",
                title="Revenue Trend Over Time",
                labels={"Day": "Period", "Revenue": "Revenue ($)"},
            )
        else:
            transactions[date_col] = pd.to_datetime(transactions[date_col])
            daily_revenue = (
                transactions.groupby(date_col)["TotalPrice"].sum().reset_index()
            )
            fig = px.line(
                daily_revenue,
                x=date_col,
                y="TotalPrice",
                title="Revenue Trend Over Time",
                labels={date_col: "Date", "TotalPrice": "Revenue ($)"},
            )

        fig.update_layout(height=400)
        return fig

    def create_store_performance_chart(self):
        store_perf = self.metrics_calculator.get_store_performance()

        if store_perf.empty:
            return None

        top_stores = store_perf.head(10)

        fig = px.bar(
            top_stores.reset_index(),
            x="StoreID",
            y="Total_Revenue",
            title="Top 10 Stores by Revenue",
            labels={"Total_Revenue": "Total Revenue ($)", "StoreID": "Store ID"},
            color="Total_Revenue",
            color_continuous_scale="Blues",
        )

        fig.update_layout(height=400)
        return fig

    def create_regional_heatmap(self):
        regional_perf = self.metrics_calculator.get_regional_performance()

        if regional_perf.empty:
            return None

        fig = go.Figure(
            data=go.Heatmap(
                z=regional_perf[["TotalPrice", "TotalCost", "Profit"]].values.T,
                x=regional_perf.index,
                y=["Revenue", "Cost", "Profit"],
                colorscale="RdYlGn",
                text=regional_perf[["TotalPrice", "TotalCost", "Profit"]].values.T,
                texttemplate="$%{text:,.0f}",
                textfont={"size": 10},
            )
        )

        fig.update_layout(
            title="Regional Performance Heatmap",
            xaxis_title="Region",
            yaxis_title="Metric",
            height=400,
        )

        return fig

    def create_profit_margin_chart(self):
        regional_perf = self.metrics_calculator.get_regional_performance()

        if regional_perf.empty:
            return None

        fig = px.bar(
            regional_perf.reset_index(),
            x="Region",
            y="Margin_%",
            title="Profit Margins by Region",
            labels={"Margin_%": "Profit Margin (%)", "Region": "Region"},
            color="Margin_%",
            color_continuous_scale="Viridis",
        )

        fig.update_layout(height=400)
        return fig

    def create_inventory_status_chart(self):
        inventory = self.data_loader.inventory_data

        if inventory is None or "QuantityInStock" not in inventory.columns:
            return None

        stock_ranges = pd.cut(
            inventory["QuantityInStock"],
            bins=[0, 50, 100, 200, float("inf")],
            labels=[
                "Critical (0-50)",
                "Low (51-100)",
                "Medium (101-200)",
                "High (200+)",
            ],
        )

        stock_distribution = stock_ranges.value_counts()

        fig = px.pie(
            values=stock_distribution.values,
            names=stock_distribution.index,
            title="Inventory Stock Level Distribution",
            color_discrete_sequence=px.colors.sequential.RdBu,
        )

        fig.update_layout(height=400)
        return fig

    def create_customer_metrics_chart(self):
        customers = self.data_loader.customer_data

        if customers is None:
            return None

        # Look for purchase amount column
        amount_col = None
        for col in customers.columns:
            if any(
                keyword in col.lower()
                for keyword in ["spent", "amount", "price", "total"]
            ):
                amount_col = col
                break

        if amount_col is None:
            return None

        fig = px.histogram(
            customers,
            x=amount_col,
            title="Customer Purchase Distribution",
            labels={amount_col: "Purchase Amount ($)"},
            nbins=50,
            color_discrete_sequence=["#636EFA"],
        )

        fig.update_layout(height=400)
        return fig

    def create_kpi_summary(self):
        all_metrics = self.metrics_calculator.get_all_key_metrics()

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Revenue Metrics",
                "Profit Metrics",
                "Inventory Status",
                "Customer Metrics",
            ),
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "indicator"}],
            ],
        )

        revenue = all_metrics.get("revenue", {})
        profit = all_metrics.get("profit", {})
        inventory = all_metrics.get("inventory", {})
        customer = all_metrics.get("customer_satisfaction", {})

        fig.add_trace(
            go.Indicator(
                mode="number",
                value=revenue.get("total_revenue", 0),
                title={"text": "Total Revenue"},
                number={"prefix": "$", "valueformat": ",.2f"},
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=profit.get("overall_margin", 0),
                title={"text": "Profit Margin"},
                number={"suffix": "%", "valueformat": ".2f"},
            ),
            row=1,
            col=2,
        )

        fig.add_trace(
            go.Indicator(
                mode="number",
                value=inventory.get("total_inventory", 0),
                title={"text": "Total Inventory"},
                number={"valueformat": ",.0f"},
            ),
            row=2,
            col=1,
        )

        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=customer.get("avg_satisfaction", 0),
                title={"text": "Avg. Customer Satisfaction"},
                number={"valueformat": ".2f"},
            ),
            row=2,
            col=2,
        )

        fig.update_layout(height=500)

        return fig
