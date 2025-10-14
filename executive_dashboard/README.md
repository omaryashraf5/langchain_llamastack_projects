# Executive Dashboard for Retail Chain Analytics

A comprehensive executive dashboard built with Streamlit, Pandas, and LangChain for C-suite executives to track sales, operational efficiency, and customer trends.

## Features

### Key Metrics
- **Revenue Tracking**: Total revenue, average transaction values, transaction counts
- **Profit Analysis**: Profit margins, gross profit calculations by region
- **Inventory Management**: Stock levels, inventory turnover, low stock alerts
- **Customer Satisfaction**: Average satisfaction scores, customer lifetime value

### Visualizations
- **Time-Series Charts**: Revenue trends over time
- **Bar Charts**: Store performance comparisons, regional profit margins
- **Heatmaps**: Regional performance metrics (Revenue, Cost, Profit)
- **Pie Charts**: Inventory distribution by stock levels
- **KPI Indicators**: Real-time metric displays

### Natural Language Queries
Ask questions in plain English:
- "Which stores are underperforming in Q3 2025?"
- "What's driving high costs in Region X?"
- "Show top stores by profit"
- "Which items have low stock levels?"

### Anomaly Detection
Automatic detection and alerts for:
- Stores with revenue significantly above/below average
- Critically low inventory levels
- Unusual expense spikes

## Data Sources

The dashboard uses five Excel datasets:
- `Customer-Purchase-History.xlsx` - Customer transactions and satisfaction scores
- `Inventory-Tracking.xlsx` - Stock levels and inventory data
- `Online-Store-Orders.xlsx` - Online sales transactions
- `Product-Sales-Region.xlsx` - Regional sales and cost data
- `Retail-Store-Transactions.xlsx` - Physical store transaction data

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your data files are in the correct location:
```
executive_dashboard/
├── data/
│   └── sales_data/
│       ├── Customer-Purchase-History.xlsx
│       ├── Inventory-Tracking.xlsx
│       ├── Online-Store-Orders.xlsx
│       ├── Product-Sales-Region.xlsx
│       └── Retail-Store-Transactions.xlsx
```

## Usage

Run the dashboard:
```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

## Dashboard Tabs

### 1. Overview
- High-level KPIs in metric cards
- Revenue trend visualization
- Customer purchase distribution
- Real-time anomaly alerts

### 2. Store Performance
- Top 10 stores by revenue (bar chart)
- Detailed store metrics table
- Transaction-level data view

### 3. Regional Analysis
- Regional performance heatmap
- Profit margins by region
- Detailed regional metrics table
- Inventory status distribution

### 4. Ask Questions
- Natural language query interface
- Pre-built quick insights:
  - Underperforming stores
  - Top performers
  - Regional cost analysis
  - Profit leaders

## Project Structure

```
executive_dashboard/
├── app.py                    # Main Streamlit application
├── data_loader.py           # Data loading and management
├── metrics_calculator.py    # Business metrics calculations
├── visualizations.py        # Chart and graph generation
├── query_agent.py          # Natural language query handling
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── data/                  # Data directory
    └── sales_data/        # Excel data files
```

## Components

### DataLoader (`data_loader.py`)
- Loads all Excel datasets
- Provides data summaries
- Manages data access for other components

### MetricsCalculator (`metrics_calculator.py`)
- Calculates revenue, profit, inventory, and customer metrics
- Aggregates store and regional performance
- Detects anomalies using statistical methods (z-scores)

### DashboardVisualizations (`visualizations.py`)
- Creates interactive Plotly charts
- Generates time-series, bar, heatmap, and pie charts
- Builds KPI indicator displays

### QueryAgent (`query_agent.py`)
- Processes natural language queries
- Provides fallback query handling
- Analyzes underperforming stores, regional costs, and profit leaders

## Example Queries

Try asking these questions in the "Ask Questions" tab:

1. **Performance Analysis**
   - "Which stores are underperforming?"
   - "Show me the top 5 stores by revenue"
   - "What stores have the highest profit margins?"

2. **Regional Insights**
   - "What's driving high costs in the Northeast region?"
   - "Compare revenue across all regions"
   - "Which region has the best profit margin?"

3. **Inventory Management**
   - "Which products have low stock levels?"
   - "Show inventory distribution"
   - "What items need restocking?"

## Customization

### Adding New Metrics
Edit `metrics_calculator.py` to add new calculation methods:
```python
def calculate_new_metric(self) -> Dict[str, float]:
    # Your calculation logic
    return metrics
```

### Creating New Visualizations
Add new chart methods in `visualizations.py`:
```python
def create_new_chart(self):
    # Your chart logic using Plotly
    return fig
```

### Extending Query Capabilities
Add new query handlers in `query_agent.py`:
```python
def _handle_custom_query(self, question: str) -> str:
    # Your query logic
    return result
```

## Dependencies

- `pandas` - Data manipulation and analysis
- `streamlit` - Web dashboard framework
- `plotly` - Interactive visualizations
- `openpyxl` - Excel file reading
- `langchain` - LLM integration for queries
- `numpy` - Numerical computations

## Performance Optimization

The dashboard uses Streamlit's caching mechanisms:
- `@st.cache_resource` for data loading (loads once per session)
- Efficient data aggregation with pandas
- Lazy loading of visualizations

## Troubleshooting

### Data Loading Issues
- Verify Excel files are in `data/sales_data/` directory
- Check file names match exactly (case-sensitive)
- Ensure openpyxl is installed: `pip install openpyxl`

### Visualization Errors
- Check that data columns exist in the datasets
- Verify Plotly is installed: `pip install plotly`
- Review browser console for JavaScript errors

### Query Agent Issues
- The agent uses fallback methods if LLM is not configured
- Check LangChain installation: `pip install langchain`
- Queries work without LLM using pattern matching


## License

MIT License
