# LLM Integration Setup Guide

This guide explains how to integrate LlamaStack LLM for advanced query handling in the Executive Dashboard.

## 🤖 LLM Query Capabilities

The dashboard now supports LLM-powered queries in **4 categories**:

### 1. **Performance Queries**
Ask about trends, metrics, and KPIs:
- "Show Q3 sales by region"
- "What's our revenue trend this quarter?"
- "How many transactions did we process in September?"

### 2. **Comparison Queries**
Compare metrics across dimensions:
- "Compare this year vs last year profits"
- "How does Region North compare to Region South?"
- "Which stores improved the most quarter-over-quarter?"

### 3. **Anomaly Queries**
Identify outliers and unusual patterns:
- "Which stores are underperforming?"
- "Are there any unusual spikes in expenses?"
- "Which products have abnormal inventory levels?"

### 4. **Drill-down Queries**
Deep-dive into root causes:
- "What's driving costs in Region X?"
- "Why is Store 5's revenue declining?"
- "What factors contribute to high customer satisfaction in Region Y?"

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
cd /home/omara/langchain_llamastack_project/executive_dashboard
pip install requests
```

The `requests` library is already included in `requirements-minimal.txt`.

### Step 2: Configure LlamaStack Endpoint

Edit the `.env` file (or create one from `.env.example`):

```bash
cp .env.example .env
nano .env
```

Add your LlamaStack configuration:

```bash
# LlamaStack API Configuration
LLAMASTACK_API_URL=http://localhost:8000
LLAMASTACK_MODEL=llama-3.1-8b
```

**Common Configurations:**

| Setup | API URL | Model |
|-------|---------|-------|
| Local LlamaStack | `http://localhost:8000` | `llama-3.1-8b` |
| Remote LlamaStack | `http://your-server:8000` | `llama-3.1-70b` |
| Custom Port | `http://localhost:5000` | `llama-3.2-3b` |

### Step 3: Verify LlamaStack is Running

Check if your LlamaStack instance is accessible:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

### Step 4: Test the Integration

Start the dashboard:

```bash
streamlit run app.py
```

Navigate to the **"Ask Questions"** tab. If LLM is available, you'll see:
```
🤖 LLM Powered - Using LlamaStack for advanced analytics
```

If not available:
```
⚠️ LLM Not Available - Using fallback query methods
```

---

## 📋 LlamaStack Endpoints

The dashboard uses the **OpenAI-compatible Chat Completions API**:

### Primary Endpoint: `/v1/chat/completions`

**Why this endpoint?**
- ✅ OpenAI-compatible format
- ✅ Supports conversational context
- ✅ Handles system prompts for role-based instructions
- ✅ Returns structured responses

**Request Format:**
```json
{
  "model": "llama-3.1-8b",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert retail analytics assistant..."
    },
    {
      "role": "user",
      "content": "Which stores are underperforming?"
    }
  ],
  "temperature": 0.3,
  "max_tokens": 1500
}
```

**Response Format:**
```json
{
  "choices": [
    {
      "message": {
        "content": "Based on the data analysis..."
      }
    }
  ]
}
```

---

## 🎯 Prompt Engineering

The system uses specialized prompts for each query category. Here's how they work:

### Performance Query Prompt
```python
System: "You are analyzing performance metrics for a retail chain..."
User: "Question: Show Q3 sales by region

Available Data Summary:
[Real data from your Excel files]

Please analyze the performance data and provide:
1. Key performance metrics
2. Trends (up/down, percentage changes)
3. Top performers
4. Areas of concern
5. Executive summary"
```

### Comparison Query Prompt
```python
System: "You are comparing business metrics across dimensions..."
User: "Question: Compare this year vs last year

Please provide a comparison analysis including:
1. What is being compared
2. Percentage differences and absolute values
3. Winners and losers
4. Factors driving differences
5. Actionable recommendations"
```

### Anomaly Query Prompt
```python
System: "You are identifying anomalies in retail data..."
User: "Question: Which stores are underperforming?

Please identify and analyze anomalies:
1. Which entities are outliers?
2. How significant is the deviation?
3. Possible root causes
4. Is this a concern or opportunity?
5. Recommended actions"
```

### Drill-down Query Prompt
```python
System: "You are conducting deep-dive analysis..."
User: "Question: What's driving costs in Region X?

Please provide a drill-down analysis:
1. What are the main components/drivers?
2. Breakdown by relevant dimensions
3. Which factors contribute most?
4. Root cause analysis
5. Specific recommendations"
```

---

## 🔧 Customization

### Change LLM Parameters

Edit `/home/omara/langchain_llamastack_project/executive_dashboard/llm_handler.py`:

```python
class LlamaStackLLM:
    def __init__(
        self,
        api_url: str = None,
        model: str = "llama-3.1-8b",
        temperature: float = 0.7,      # Adjust creativity (0.0-1.0)
        max_tokens: int = 1000,        # Adjust response length
    ):
```

### Add Custom Prompts

Add new prompt builders in `llm_handler.py`:

```python
@staticmethod
def build_forecasting_query_prompt(question: str, data_summary: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "You are forecasting future trends..."
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nData: {data_summary}"
        }
    ]
```

### Modify Query Classification

Update the keyword matching in `QueryPromptBuilder.classify_query()`:

```python
forecasting_keywords = ['predict', 'forecast', 'future', 'next quarter', 'projection']
```

---

## 🐛 Troubleshooting

### LLM Not Available

**Symptom:** Dashboard shows "⚠️ LLM Not Available"

**Solutions:**
1. Check if LlamaStack is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Verify environment variables:
   ```bash
   echo $LLAMASTACK_API_URL
   echo $LLAMASTACK_MODEL
   ```

3. Check firewall/network access to LlamaStack server

4. Review logs for connection errors

### Slow Response Times

**Solutions:**
1. Reduce `max_tokens` in `llm_handler.py`
2. Use a smaller model (e.g., `llama-3.2-3b` instead of `llama-3.1-70b`)
3. Lower `temperature` for more deterministic responses
4. Cache responses for common queries

### Poor Quality Responses

**Solutions:**
1. Improve prompts with more specific instructions
2. Provide more relevant data context
3. Increase `temperature` for more creative responses
4. Use a larger model (e.g., `llama-3.1-70b`)
5. Add few-shot examples to prompts

### Connection Timeout

**Solutions:**
1. Increase timeout in `llm_handler.py`:
   ```python
   response = requests.post(
       self.endpoint,
       json=payload,
       headers={"Content-Type": "application/json"},
       timeout=60  # Increase from default
   )
   ```

2. Check network latency to LlamaStack server
3. Verify LlamaStack server has sufficient resources

---

## 📊 Data Context

The LLM receives the following data context automatically:

```python
{
    "total_stores": 50,
    "total_products": 200,
    "regions": ["North", "South", "East", "West"],
    "date_range": "2024-01-01 to 2024-12-31",
    "store_summary": "Top 3 and Bottom 3 stores with revenue",
    "regional_summary": "Revenue and quantity by region",
    "inventory_status": "Stock levels and low stock items",
    "customer_metrics": "Average ratings and customer counts"
}
```

This context is automatically built from your Excel data files and passed to the LLM with each query.

---

## 🔐 Security Considerations

1. **API Access:** Ensure LlamaStack endpoint is not publicly exposed
2. **Data Privacy:** LLM receives aggregated summaries, not raw customer data
3. **Rate Limiting:** Consider implementing request throttling for production
4. **Authentication:** Add API key authentication if needed

---

## 📚 Example Queries

Try these in the dashboard:

### Performance
- "What was our total revenue last quarter?"
- "Show sales trends by store location"
- "Which product categories are growing?"

### Comparison
- "Compare North region vs South region profitability"
- "How do online sales compare to in-store sales?"
- "Which stores improved most year-over-year?"

### Anomaly
- "Are there any stores with unusual expense patterns?"
- "Which products have abnormal inventory turnover?"
- "Identify stores with declining customer satisfaction"

### Drill-down
- "Why are costs higher in the West region?"
- "What products drive the most revenue in Store 5?"
- "Analyze factors affecting customer ratings"

---

## 🎓 Advanced Features

### Multi-turn Conversations

To enable conversation history, modify `query_agent.py` to maintain message history:

```python
self.conversation_history = []

def query(self, question: str) -> str:
    self.conversation_history.append({
        "role": "user",
        "content": question
    })

    response = self.llamastack_llm.chat_completion(
        self.conversation_history,
        temperature=0.3
    )

    self.conversation_history.append({
        "role": "assistant",
        "content": response
    })

    return response
```

### Function Calling

For structured data extraction, implement function calling:

```python
functions = [{
    "name": "get_store_revenue",
    "description": "Get revenue for a specific store",
    "parameters": {
        "type": "object",
        "properties": {
            "store_id": {"type": "integer"}
        }
    }
}]
```

---

## ✅ Verification Checklist

- [ ] LlamaStack is running and accessible
- [ ] Environment variables are set correctly
- [ ] `requests` library is installed
- [ ] Dashboard shows "🤖 LLM Powered" status
- [ ] Test queries return meaningful responses
- [ ] Response times are acceptable
- [ ] Prompts are customized for your use case

---

## 💡 Best Practices

1. **Start Simple:** Test with basic queries before complex ones
2. **Iterate on Prompts:** Refine prompts based on response quality
3. **Monitor Performance:** Track response times and accuracy
4. **Provide Context:** Include relevant data summaries in prompts
5. **Set Expectations:** Use lower temperature (0.2-0.4) for factual queries
6. **Handle Errors:** Always have fallback methods for when LLM is unavailable
7. **Document Patterns:** Keep a log of effective prompts and queries

---

## 📞 Need Help?

- **LlamaStack Docs:** [https://github.com/meta-llama/llama-stack](https://github.com/meta-llama/llama-stack)
- **API Reference:** Check your LlamaStack instance docs at `/docs`
- **Dashboard Issues:** Review `QUICKSTART.md` and `README.md`
