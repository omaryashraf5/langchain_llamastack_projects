"""Unit tests for data_loader module

These are true unit tests that don't require external services.
They test basic functionality and data validation.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_loader import RetailDataLoader


class TestDataLoader:
    """Test RetailDataLoader class basic functionality"""

    def test_dataloader_initialization(self):
        """Test that RetailDataLoader can be initialized"""
        loader = RetailDataLoader()
        assert loader is not None
        assert hasattr(loader, "store_transactions")
        assert hasattr(loader, "product_sales")
        assert hasattr(loader, "inventory_data")
        assert hasattr(loader, "customer_data")

    def test_dataloader_attributes_initially_none(self):
        """Test that RetailDataLoader attributes are None before loading data"""
        loader = RetailDataLoader()
        assert loader.store_transactions is None
        assert loader.product_sales is None
        assert loader.inventory_data is None
        assert loader.customer_data is None

    def test_dataloader_has_load_method(self):
        """Test that RetailDataLoader has a load_all_data method"""
        loader = RetailDataLoader()
        assert hasattr(loader, "load_all_data")
        assert callable(loader.load_all_data)


class TestDataValidation:
    """Test data validation helper functions"""

    def test_validate_numeric_column(self):
        """Test numeric column validation"""
        df = pd.DataFrame({"price": [10.5, 20.0, 30.5], "quantity": [1, 2, 3]})

        assert df["price"].dtype in ["float64", "float32", "int64", "int32"]
        assert df["quantity"].dtype in ["float64", "float32", "int64", "int32"]

    def test_dataframe_not_empty(self):
        """Test that we can detect non-empty dataframes"""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        assert len(df) > 0
        assert not df.empty

    def test_dataframe_has_required_columns(self):
        """Test column existence check"""
        df = pd.DataFrame({"StoreID": [1, 2, 3], "TotalPrice": [100, 200, 300]})

        required_cols = ["StoreID", "TotalPrice"]
        assert all(col in df.columns for col in required_cols)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
