# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd /home/omara/langchain_llamastack_project/executive_dashboard
pip install -r requirements.txt
```

### Step 2: Run the Dashboard
```bash
# Option A: Use the launcher script
./run_dashboard.sh

# Option B: Run directly
streamlit run app.py
```

### Step 3: Access the Dashboard
Open your browser to `http://localhost:8501`

---

## 📊 What You'll See

### Overview Tab
- **4 KPI Cards**: Revenue, Profit Margin, Inventory, Customer Satisfaction
- **Charts**: Revenue trends and customer purchase distribution
- **Alerts**: Real-time anomaly detection

### Store Performance Tab
- **Bar Chart**: Top 10 stores by revenue
- **Data Table**: Detailed store metrics with formatting
- **Raw Data**: Full transaction history

### Regional Analysis Tab
- **Heatmap**: Regional performance across Revenue, Cost, and Profit
- **Bar Chart**: Profit margins by region
- **Tables**: Detailed regional breakdowns
- **Pie Chart**: Inventory distribution

### Ask Questions Tab
- **Text Input**: Ask questions in natural language
- **Quick Buttons**: One-click insights for common queries
- Examples:
  - "Which stores are underperforming?"
  - "Show top stores by profit"
  - "What's driving high costs in Region X?"

---

## 🎯 Sample Questions to Try

1. Which stores are underperforming?
2. Show top stores by profit
3. Analyze regional costs
4. Which region has the highest profit margin?

---

## 📁 Project Files Overview

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit dashboard application |
| `data_loader.py` | Loads and manages Excel data files |
| `metrics_calculator.py` | Calculates KPIs and business metrics |
| `visualizations.py` | Creates interactive Plotly charts |
| `query_agent.py` | Handles natural language queries |
| `requirements.txt` | Python package dependencies |

---

## 🔧 Troubleshooting

**Problem: Module not found errors**
```bash
pip install -r requirements.txt
```

**Problem: Data not loading**
- Check that Excel files are in `/home/omara/langchain_llamastack_project/executive_dashboard/data/sales_data/`
- Verify file names match exactly

**Problem: Port already in use**
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

**Problem: Charts not displaying**
- Clear browser cache
- Try a different browser
- Check browser console for errors

---

## 🎨 Features Implemented

✅ Revenue, profit, inventory, and customer satisfaction metrics
✅ Time-series revenue trends
✅ Store performance rankings (bar charts)
✅ Regional performance heatmaps
✅ Profit margin analysis by region
✅ Inventory distribution (pie chart)
✅ Natural language query interface
✅ Anomaly detection with alerts
✅ Interactive drill-down capabilities
✅ Formatted data tables with currency/percentages
✅ Sidebar with data overview

---

## 📚 Next Steps

1. **Customize**: Edit the Python files to add your own metrics or visualizations
2. **Integrate LLM**: Add LangChain/LlamaStack for advanced query capabilities
3. **Extend**: Add time-based filtering, export features, or predictive analytics
4. **Deploy**: Host on Streamlit Cloud, AWS, or your preferred platform

---

## 💡 Tips

- Use the sidebar to see data summaries
- Click on charts to interact (zoom, pan, hover for details)
- The dashboard auto-refreshes when you change data files
- All monetary values are formatted with dollar signs and commas
- Percentages are shown with 2 decimal places

---

## 🆘 Need Help?

Refer to the full `README.md` for detailed documentation on:
- Architecture and components
- Customization guides
- API references
- Advanced features

Happy analyzing! 📊
