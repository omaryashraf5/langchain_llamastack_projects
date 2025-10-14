from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


class MetricsCalculator:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def calculate_revenue_metrics(self) -> Dict[str, float]:
        transactions = self.data_loader.store_transactions
        online = self.data_loader.online_orders

        metrics = {}

        if transactions is not None and "TotalPrice" in transactions.columns:
            metrics["store_revenue"] = transactions["TotalPrice"].sum()
            metrics["avg_transaction"] = transactions["TotalPrice"].mean()
            metrics["transaction_count"] = len(transactions)

        if online is not None:
            revenue_cols = [
                col
                for col in online.columns
                if "price" in col.lower()
                or "total" in col.lower()
                or "amount" in col.lower()
            ]
            if revenue_cols:
                metrics["online_revenue"] = online[revenue_cols[0]].sum()

        metrics["total_revenue"] = metrics.get("store_revenue", 0) + metrics.get(
            "online_revenue", 0
        )

        return metrics

    def calculate_profit_margins(self) -> Dict[str, float]:
        product_sales = self.data_loader.product_sales
        inventory_data = self.data_loader.inventory_data

        if product_sales is None:
            return {}

        metrics = {}

        # Merge with inventory_data to get UnitCost
        if (
            inventory_data is not None
            and "UnitCost" in inventory_data.columns
            and "TotalPrice" in product_sales.columns
        ):
            # Merge product_sales with inventory_data to get cost information
            merged = product_sales.merge(
                inventory_data[["ProductName", "UnitCost"]],
                left_on="Product",
                right_on="ProductName",
                how="left"
            )

            # Calculate totals
            total_revenue = merged["TotalPrice"].sum()
            total_cost = (
                merged["UnitCost"].fillna(0) * merged["Quantity"]
            ).sum()

            metrics["overall_margin"] = (
                ((total_revenue - total_cost) / total_revenue * 100)
                if total_revenue > 0
                else 0
            )
            metrics["gross_profit"] = total_revenue - total_cost

        return metrics

    def calculate_inventory_turnover(self) -> Dict[str, float]:
        inventory = self.data_loader.inventory_data

        if inventory is None:
            return {}

        metrics = {}

        if "QuantityInStock" in inventory.columns:
            metrics["total_inventory"] = inventory["QuantityInStock"].sum()
            metrics["avg_stock_level"] = inventory["QuantityInStock"].mean()
            metrics["low_stock_items"] = len(
                inventory[
                    inventory["QuantityInStock"]
                    < inventory["QuantityInStock"].quantile(0.25)
                ]
            )

        return metrics

    def calculate_customer_satisfaction(self) -> Dict[str, float]:
        customers = self.data_loader.customer_data

        if customers is None:
            return {}

        metrics = {}

        rating_cols = [
            col
            for col in customers.columns
            if "rating" in col.lower() or "satisfaction" in col.lower()
        ]
        if rating_cols:
            metrics["avg_satisfaction"] = customers[rating_cols[0]].mean()
            metrics["satisfaction_std"] = customers[rating_cols[0]].std()

        if "Total Spent" in customers.columns or "Purchase Amount" in customers.columns:
            amount_col = (
                "Total Spent"
                if "Total Spent" in customers.columns
                else "Purchase Amount"
            )
            metrics["customer_lifetime_value"] = customers[amount_col].mean()

        return metrics

    def get_all_key_metrics(self) -> Dict[str, any]:
        return {
            "revenue": self.calculate_revenue_metrics(),
            "profit": self.calculate_profit_margins(),
            "inventory": self.calculate_inventory_turnover(),
            "customer_satisfaction": self.calculate_customer_satisfaction(),
        }

    def get_store_performance(self) -> pd.DataFrame:
        transactions = self.data_loader.store_transactions

        if transactions is None or "StoreID" not in transactions.columns:
            return pd.DataFrame()

        store_metrics = (
            transactions.groupby("StoreID")
            .agg({"TotalPrice": ["sum", "mean", "count"]})
            .round(2)
        )

        store_metrics.columns = [
            "Total_Revenue",
            "Avg_Transaction",
            "Transaction_Count",
        ]
        store_metrics = store_metrics.sort_values("Total_Revenue", ascending=False)

        return store_metrics

    def get_regional_performance(self) -> pd.DataFrame:
        product_sales = self.data_loader.product_sales
        inventory_data = self.data_loader.inventory_data

        if product_sales is None or "Region" not in product_sales.columns:
            return pd.DataFrame()

        # Merge with inventory_data to get UnitCost
        if inventory_data is not None and "UnitCost" in inventory_data.columns:
            # Merge product_sales with inventory_data to get cost information
            merged = product_sales.merge(
                inventory_data[["ProductName", "UnitCost"]],
                left_on="Product",
                right_on="ProductName",
                how="left"
            )

            # Calculate total cost (handle NaN values from left join)
            merged["TotalCost"] = (
                merged["UnitCost"].fillna(0) * merged["Quantity"]
            )

            # Calculate regional metrics
            regional_metrics = (
                merged.groupby("Region")
                .agg({"TotalPrice": "sum", "TotalCost": "sum"})
                .round(2)
            )
        else:
            # Fallback: if no cost data available, set costs to 0
            regional_metrics = (
                product_sales.groupby("Region")
                .agg({"TotalPrice": "sum"})
                .round(2)
            )
            regional_metrics["TotalCost"] = 0

        regional_metrics["Profit"] = (
            regional_metrics["TotalPrice"] - regional_metrics["TotalCost"]
        )
        regional_metrics["Margin_%"] = (
            (regional_metrics["Profit"] / regional_metrics["TotalPrice"]) * 100
        ).round(2)

        return regional_metrics.sort_values("TotalPrice", ascending=False)

    def detect_anomalies(self, threshold: float = 1.5) -> List[Dict[str, any]]:
        anomalies = []

        transactions = self.data_loader.store_transactions
        if transactions is not None and "StoreID" in transactions.columns:
            store_totals = transactions.groupby("StoreID")["TotalPrice"].sum()
            mean_total = store_totals.mean()
            std_total = store_totals.std()

            for store_id, total in store_totals.items():
                z_score = abs((total - mean_total) / std_total) if std_total > 0 else 0
                if z_score > threshold:
                    pct_change = (total - mean_total) / mean_total * 100
                    anomalies.append(
                        {
                            "type": "store_revenue",
                            "store_id": store_id,
                            "message": f"Store {store_id}'s revenue is {abs(pct_change):.1f}% {'above' if pct_change > 0 else 'below'} average",
                            "severity": "high" if z_score > 2 else "medium",
                        }
                    )

        inventory = self.data_loader.inventory_data
        if inventory is not None and "QuantityInStock" in inventory.columns:
            low_stock = inventory[
                inventory["QuantityInStock"]
                < inventory["QuantityInStock"].quantile(0.1)
            ]
            if len(low_stock) > 0:
                anomalies.append(
                    {
                        "type": "inventory",
                        "message": f"{len(low_stock)} items have critically low stock levels",
                        "severity": "high",
                    }
                )

        return anomalies
