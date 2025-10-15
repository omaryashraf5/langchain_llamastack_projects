"""Unit tests for pandas operations and calculations

These are true unit tests that test data processing logic
without requiring external services.
"""

import pandas as pd
import pytest


class TestBasicCalculations:
    """Test basic pandas calculations used in the dashboard"""

    def test_revenue_calculation(self):
        """Test revenue calculation (sum of TotalPrice)"""
        df = pd.DataFrame({"StoreID": [1, 1, 2, 2], "TotalPrice": [100, 150, 200, 250]})

        revenue_by_store = df.groupby("StoreID")["TotalPrice"].sum()

        assert revenue_by_store[1] == 250
        assert revenue_by_store[2] == 450

    def test_profit_margin_calculation(self):
        """Test profit margin calculation"""
        total_revenue = 1000
        total_cost = 600

        profit = total_revenue - total_cost
        margin = (profit / total_revenue) * 100

        assert profit == 400
        assert margin == 40.0

    def test_cost_calculation_with_quantity(self):
        """Test cost calculation (UnitCost * Quantity)"""
        df = pd.DataFrame(
            {
                "Product": ["A", "B", "C"],
                "UnitCost": [10, 20, 30],
                "Quantity": [5, 3, 2],
            }
        )

        df["TotalCost"] = df["UnitCost"] * df["Quantity"]

        assert df["TotalCost"].tolist() == [50, 60, 60]
        assert df["TotalCost"].sum() == 170


class TestDataGrouping:
    """Test data grouping and aggregation operations"""

    def test_groupby_single_column(self):
        """Test grouping by a single column"""
        df = pd.DataFrame(
            {"Region": ["East", "West", "East", "West"], "Sales": [100, 200, 150, 250]}
        )

        grouped = df.groupby("Region")["Sales"].sum()

        assert grouped["East"] == 250
        assert grouped["West"] == 450

    def test_groupby_multiple_aggregations(self):
        """Test multiple aggregations on grouped data"""
        df = pd.DataFrame({"StoreID": [1, 1, 2, 2], "TotalPrice": [100, 200, 150, 250]})

        result = df.groupby("StoreID").agg({"TotalPrice": ["sum", "mean", "count"]})

        assert result.loc[1, ("TotalPrice", "sum")] == 300
        assert result.loc[1, ("TotalPrice", "mean")] == 150
        assert result.loc[1, ("TotalPrice", "count")] == 2

    def test_sort_values(self):
        """Test sorting dataframe by values"""
        df = pd.DataFrame({"Product": ["A", "B", "C"], "Revenue": [300, 100, 200]})

        sorted_df = df.sort_values("Revenue", ascending=False)

        assert sorted_df.iloc[0]["Product"] == "A"
        assert sorted_df.iloc[1]["Product"] == "C"
        assert sorted_df.iloc[2]["Product"] == "B"


class TestDataFiltering:
    """Test data filtering operations"""

    def test_filter_by_condition(self):
        """Test filtering rows by condition"""
        df = pd.DataFrame(
            {
                "Region": ["East", "West", "East", "Central"],
                "Sales": [100, 200, 150, 300],
            }
        )

        east_sales = df[df["Region"] == "East"]

        assert len(east_sales) == 2
        assert east_sales["Sales"].sum() == 250

    def test_filter_top_n(self):
        """Test getting top N records"""
        df = pd.DataFrame(
            {"Product": ["A", "B", "C", "D", "E"], "Revenue": [100, 500, 300, 200, 400]}
        )

        top_3 = df.nlargest(3, "Revenue")

        assert len(top_3) == 3
        assert top_3.iloc[0]["Product"] == "B"  # 500
        assert top_3.iloc[1]["Product"] == "E"  # 400
        assert top_3.iloc[2]["Product"] == "C"  # 300


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
