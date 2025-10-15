import pandas as pd
import streamlit as st
from data_loader import RetailDataLoader
from metrics_calculator import MetricsCalculator
from query_agent import QueryAgent
from visualizations import DashboardVisualizations

st.set_page_config(
    page_title="Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def load_data():
    loader = RetailDataLoader()
    loader.load_all_data()
    return loader


@st.cache_resource
def initialize_components(_loader):
    metrics_calc = MetricsCalculator(_loader)
    viz = DashboardVisualizations(_loader, metrics_calc)
    query_agent = QueryAgent(_loader)
    return metrics_calc, viz, query_agent


def main():
    st.title("🎯 Executive Dashboard - Retail Chain Analytics")
    st.markdown("---")

    try:
        data_loader = load_data()
        metrics_calc, viz, query_agent = initialize_components(data_loader)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📈 Overview",
            "🏪 Store Performance",
            "🗺️ Regional Analysis",
            "💬 Ask Questions",
        ]
    )

    with tab1:
        st.header("Key Performance Indicators")

        all_metrics = metrics_calc.get_all_key_metrics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            revenue = all_metrics.get("revenue", {})
            total_rev = revenue.get("total_revenue", 0)
            st.metric(
                label="Total Revenue",
                value=f"${total_rev:,.2f}",
                delta=f"{revenue.get('transaction_count', 0)} transactions",
            )

        with col2:
            profit = all_metrics.get("profit", {})
            margin = profit.get("overall_margin", 0)
            st.metric(
                label="Profit Margin",
                value=f"{margin:.2f}%",
                delta=f"${profit.get('gross_profit', 0):,.2f} profit",
            )

        with col3:
            inventory = all_metrics.get("inventory", {})
            total_inv = inventory.get("total_inventory", 0)
            st.metric(
                label="Total Inventory",
                value=f"{total_inv:,.0f} units",
                delta=f"{inventory.get('low_stock_items', 0)} low stock",
            )

        with col4:
            customer = all_metrics.get("customer_satisfaction", {})
            satisfaction = customer.get("avg_satisfaction", 0)
            st.metric(
                label="Customer Satisfaction",
                value=f"{satisfaction:.2f}/5.0",
                delta=f"${customer.get('customer_lifetime_value', 0):,.2f} CLV",
            )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Revenue Trend")
            revenue_chart = viz.create_revenue_trend_chart()
            if revenue_chart:
                st.plotly_chart(revenue_chart, use_container_width=True)
            else:
                st.info("Revenue trend data not available")

        with col2:
            st.subheader("Customer Purchase Distribution")
            customer_chart = viz.create_customer_metrics_chart()
            if customer_chart:
                st.plotly_chart(customer_chart, use_container_width=True)
            else:
                st.info("Customer data not available")

        st.markdown("---")
        st.subheader("🚨 Alerts & Anomalies")

        anomalies = metrics_calc.detect_anomalies()

        if anomalies:
            for anomaly in anomalies:
                severity = anomaly.get("severity", "medium")
                icon = "🔴" if severity == "high" else "🟡"
                st.warning(f"{icon} {anomaly['message']}")
        else:
            st.success(
                "✅ No anomalies detected. All metrics are within normal ranges."
            )

    with tab2:
        st.header("Store Performance Analysis")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Top Stores by Revenue")
            store_chart = viz.create_store_performance_chart()
            if store_chart:
                st.plotly_chart(store_chart, use_container_width=True)
            else:
                st.info("Store performance data not available")

        with col2:
            st.subheader("Store Metrics")
            store_perf = metrics_calc.get_store_performance()
            if not store_perf.empty:
                st.dataframe(
                    store_perf.head(10).style.format(
                        {
                            "Total_Revenue": "${:,.2f}",
                            "Avg_Transaction": "${:,.2f}",
                            "Transaction_Count": "{:,.0f}",
                        }
                    ),
                    use_container_width=True,
                )
            else:
                st.info("Store data not available")

        st.markdown("---")

        st.subheader("Detailed Store Data")
        if data_loader.store_transactions is not None:
            # Hide Location column as it contains inconsistent data
            display_cols = [
                col
                for col in data_loader.store_transactions.columns
                if col != "Location"
            ]
            st.dataframe(
                data_loader.store_transactions[display_cols].head(100),
                use_container_width=True,
            )
            st.caption(
                "Note: Location column hidden due to data quality issues. Use StoreID for store identification."
            )

    with tab3:
        st.header("Regional Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Regional Performance Heatmap")
            heatmap = viz.create_regional_heatmap()
            if heatmap:
                st.plotly_chart(heatmap, use_container_width=True)
            else:
                st.info("Regional data not available")

        with col2:
            st.subheader("Profit Margins by Region")
            margin_chart = viz.create_profit_margin_chart()
            if margin_chart:
                st.plotly_chart(margin_chart, use_container_width=True)
            else:
                st.info("Regional margin data not available")

        st.markdown("---")

        st.subheader("Regional Performance Table")
        regional_perf = metrics_calc.get_regional_performance()
        if not regional_perf.empty:
            st.dataframe(
                regional_perf.style.format(
                    {
                        "TotalPrice": "${:,.2f}",
                        "TotalCost": "${:,.2f}",
                        "Profit": "${:,.2f}",
                        "Margin_%": "{:.2f}%",
                    }
                ),
                use_container_width=True,
            )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Inventory Status")
            inventory_chart = viz.create_inventory_status_chart()
            if inventory_chart:
                st.plotly_chart(inventory_chart, use_container_width=True)
            else:
                st.info("Inventory data not available")

    with tab4:
        st.header("Ask Questions About Your Data")

        col1, col2 = st.columns([3, 1])

        with col1:
            if query_agent.llm_available:
                provider = (
                    query_agent.get_conversation_summary().get("provider", "Unknown")
                    if query_agent.get_conversation_summary()
                    else "LLM"
                )
                st.success(
                    f"🤖 LLM Powered - Using {provider} with conversation memory"
                )
            else:
                st.warning("⚠️ LLM Not Available - Using fallback query methods")

        with col2:
            if query_agent.llm_available:
                conv_summary = query_agent.get_conversation_summary()
                if conv_summary and conv_summary["message_count"] > 0:
                    st.info(
                        f"💬 {conv_summary['message_count']//2} exchanges in session"
                    )

        st.markdown(
            "Ask natural language questions about your retail data. **Follow-up questions are supported!**"
        )
        st.markdown("- **Performance:** Show Q3 sales by region")
        st.markdown("- **Comparison:** Compare this quarter vs last quarter")
        st.markdown("- **Anomaly:** Which stores are underperforming?")
        st.markdown("- **Drill-down:** What's driving high costs in Region X?")
        st.markdown("- **Follow-ups:** Why? / Tell me more / What should we do?")

        st.markdown("---")

        # Always use code generation mode (only LLM-based approach)
        use_code_gen = True

        # Conversation controls
        if query_agent.llm_available:
            col1, col2, col3 = st.columns([4, 1, 1])

            with col2:
                if st.button("🔄 Clear History", help="Start a fresh conversation"):
                    query_agent.clear_conversation()
                    st.success("Conversation cleared!")
                    st.rerun()

            with col3:
                if st.button("↩️ Undo Last", help="Remove last question/answer"):
                    if query_agent.undo_last_query():
                        st.success("Last exchange removed!")
                        st.rerun()
                    else:
                        st.warning("No history to undo")

        question = st.text_input(
            "Enter your question:",
            placeholder="e.g., Which stores are underperforming in Q3 2025?",
            key="question_input",
        )

        col1, col2 = st.columns([4, 1])
        with col1:
            ask_button = st.button(
                "Get Answer", type="primary", use_container_width=True
            )
        with col2:
            if query_agent.llm_available:
                conv_summary = query_agent.get_conversation_summary()
                if conv_summary:
                    with st.expander("📊 Session Info"):
                        st.write(f"**Exchanges:** {conv_summary['message_count']//2}")
                        st.write(f"**Duration:** {conv_summary['session_duration']}")
                        st.write(f"**Model:** {conv_summary['model']}")

        if ask_button:
            if question:
                with st.spinner(
                    "Analyzing data..."
                    if not use_code_gen
                    else "Generating and executing code..."
                ):
                    answer, viz = query_agent.query(question, use_code_gen=use_code_gen)

                    # Handle both dictionary and string responses
                    if isinstance(answer, dict):
                        analysis = answer.get("analysis", "")
                        code = answer.get("code", "")
                        result_type = answer.get("result_type", "Unknown")

                        # Display answer in left column, viz in right if available
                        if viz is not None:
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.markdown("### Answer:")
                                st.success(analysis)

                                # Show code in expander
                                with st.expander("🔍 View Generated Code"):
                                    st.code(code, language="python")
                                    st.caption(f"**Result Type:** {result_type}")
                            with col2:
                                st.markdown("### Visualization:")
                                st.plotly_chart(viz, use_container_width=True)
                        else:
                            st.markdown("### Answer:")
                            st.success(analysis)

                            # Show code in expander
                            with st.expander("🔍 View Generated Code"):
                                st.code(code, language="python")
                                st.caption(f"**Result Type:** {result_type}")
                    else:
                        # Handle string responses (fallback mode)
                        if viz is not None:
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.markdown("### Answer:")
                                st.success(answer)
                            with col2:
                                st.markdown("### Visualization:")
                                st.plotly_chart(viz, use_container_width=True)
                        else:
                            st.markdown("### Answer:")
                            st.success(answer)

                    # Show conversation tip
                    if query_agent.llm_available:
                        st.info(
                            "💡 **Tip:** You can now ask follow-up questions like 'Why is that?' or 'What should we do about it?'"
                        )
            else:
                st.warning("Please enter a question first.")

        st.markdown("---")

        st.subheader("Quick Insights")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Show Underperforming Stores"):
                with st.spinner("Analyzing..."):
                    result = query_agent._get_underperforming_stores()
                    st.info(result)

        with col2:
            if st.button("Show Top Performers"):
                with st.spinner("Analyzing..."):
                    result = query_agent._get_top_stores()
                    st.info(result)

        col3, col4 = st.columns(2)

        with col3:
            if st.button("Analyze Regional Costs"):
                with st.spinner("Analyzing..."):
                    result = query_agent._analyze_regional_costs()
                    st.info(result)

        with col4:
            if st.button("Show Profit Leaders"):
                with st.spinner("Analyzing..."):
                    result = query_agent._get_top_stores_by_profit()
                    st.info(result)

    with st.sidebar:
        st.header("Dashboard Controls")

        st.markdown("---")

        st.subheader("Data Overview")
        summary = data_loader.get_data_summary()

        for dataset_name, info in summary.items():
            with st.expander(f"📊 {dataset_name.title()}"):
                st.write(f"**Rows:** {info['shape'][0]}")
                st.write(f"**Columns:** {info['shape'][1]}")
                st.write("**Fields:**")
                for col in info["columns"][:5]:
                    st.write(f"- {col}")
                if len(info["columns"]) > 5:
                    st.write(f"... and {len(info['columns']) - 5} more")

        st.markdown("---")

        st.subheader("About")
        st.info(
            """
        This executive dashboard provides comprehensive insights into:
        - Revenue and profitability metrics
        - Store and regional performance
        - Inventory management
        - Customer satisfaction trends
        - Anomaly detection and alerts
        """
        )


if __name__ == "__main__":
    main()
