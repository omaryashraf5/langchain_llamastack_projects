from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd


class RetailDataLoader:
    def __init__(self, data_dir: str = "data/sales_data"):
        self.data_dir = Path(data_dir)
        self.customer_data = None
        self.inventory_data = None
        self.online_orders = None
        self.product_sales = None
        self.store_transactions = None

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        self.customer_data = pd.read_excel(
            self.data_dir / "Customer-Purchase-History.xlsx"
        )
        self.inventory_data = pd.read_excel(self.data_dir / "Inventory-Tracking.xlsx")
        self.online_orders = pd.read_excel(self.data_dir / "Online-Store-Orders.xlsx")
        self.product_sales = pd.read_excel(self.data_dir / "Product-Sales-Region.xlsx")
        self.store_transactions = pd.read_excel(
            self.data_dir / "Retail-Store-Transactions.xlsx"
        )

        return {
            "customers": self.customer_data,
            "inventory": self.inventory_data,
            "online_orders": self.online_orders,
            "product_sales": self.product_sales,
            "store_transactions": self.store_transactions,
        }

    def get_data_summary(self) -> Dict[str, dict]:
        if self.customer_data is None:
            self.load_all_data()

        return {
            "customers": {
                "shape": self.customer_data.shape,
                "columns": list(self.customer_data.columns),
            },
            "inventory": {
                "shape": self.inventory_data.shape,
                "columns": list(self.inventory_data.columns),
            },
            "online_orders": {
                "shape": self.online_orders.shape,
                "columns": list(self.online_orders.columns),
            },
            "product_sales": {
                "shape": self.product_sales.shape,
                "columns": list(self.product_sales.columns),
            },
            "store_transactions": {
                "shape": self.store_transactions.shape,
                "columns": list(self.store_transactions.columns),
            },
        }
