# Conversation Follow-ups Guide

## 🎯 Overview

The dashboard now supports **conversation memory** allowing you to ask follow-up questions without repeating context. This makes the interaction more natural and efficient, similar to chatting with a human analyst.

---

## ✨ Key Features

### 1. **Conversation History**
- Remembers up to **10 question/answer exchanges** (configurable)
- Maintains context across multiple questions
- Automatically manages memory to avoid overwhelming the LLM

### 2. **Smart Context Retention**
- System message (role definition) set once at start
- Previous exchanges included in each new request
- Data context refreshed with each query

### 3. **Session Management**
- Track session duration
- Count total exchanges
- Clear history to start fresh
- Undo last exchange if needed

---

## 💬 How to Use Follow-ups

### Example Conversation Flow:

**Q1:** "Which stores are underperforming?"

**A1:**
```
Query Type: Anomaly

Bottom 5 Underperforming Stores:
1. Store 12: $45,231 (15% below average)
2. Store 8: $47,892 (12% below average)
3. Store 23: $49,105 (10% below average)
...
```

**Q2:** "Why is Store 12 performing so poorly?" *(Follow-up - no need to repeat context)*

**A2:**
```
Query Type: Drilldown

Analysis of Store 12's Performance:

Root Causes:
- Location in low-traffic area
- Higher operational costs than average
- Limited product selection
- Declining foot traffic (down 20%)
...
```

**Q3:** "What should we do about it?" *(Another follow-up)*

**A3:**
```
Recommended Actions for Store 12:

1. Immediate (0-30 days):
   - Conduct local market analysis
   - Review product mix vs customer demand
   - Assess staffing levels

2. Short-term (1-3 months):
   - Implement targeted marketing campaign
   - Optimize inventory based on local preferences
   - Consider promotional events

3. Long-term (3-6 months):
   - Evaluate store location viability
   - Consider relocation or closure if trends continue
...
```

---

## 🎮 UI Controls

### Location: "Ask Questions" Tab

#### 1. **Clear History Button** (🔄)
- **Purpose:** Start a fresh conversation
- **When to use:**
  - Changing to a completely different topic
  - Conversation became confusing
  - Want to reset context

#### 2. **Undo Last Button** (↩️)
- **Purpose:** Remove the last question and answer
- **When to use:**
  - Made a typo in question
  - Got unexpected response
  - Want to rephrase question

#### 3. **Session Info Expander** (📊)
- **Shows:**
  - Number of exchanges in current session
  - Session duration
  - Model being used

---

## 📝 Best Practices

### 1. **Start with Specific Questions**
```
✅ Good: "Show me Q3 sales by region"
❌ Vague: "Tell me about sales"
```

### 2. **Use Follow-ups for Depth**
```
Initial: "Which regions have declining profits?"
Follow-up 1: "Why is Region West declining?"
Follow-up 2: "What's the trend over the last 6 months?"
Follow-up 3: "What actions do you recommend?"
```

### 3. **Clear History When Changing Topics**
```
Topic 1: Store performance questions (3-4 exchanges)
[Clear History] 🔄
Topic 2: Inventory analysis questions (new conversation)
```

### 4. **Use Pronouns and References**
```
Q1: "Show underperforming stores"
Q2: "Why are they underperforming?" (✅ "they" refers to previous answer)
Q3: "Show me more details about the first one" (✅ refers to Store #1)
```

---

## 🔧 Technical Implementation

### How It Works:

1. **User asks question** → Stored in conversation history
2. **LLM generates response** → Stored in conversation history
3. **Next question** → Sent with full conversation history
4. **LLM has context** → Can understand references and follow-ups

### Message Structure:

```python
[
    {"role": "system", "content": "You are a retail analytics expert..."},
    {"role": "user", "content": "Which stores are underperforming?"},
    {"role": "assistant", "content": "Bottom 5 stores: Store 12..."},
    {"role": "user", "content": "Why is Store 12 doing poorly?"},  # Follow-up
    # LLM understands "Store 12" from previous exchange
]
```

### Memory Management:

- **Max History:** 10 exchanges (20 messages)
- **Auto-trimming:** Oldest exchanges removed when limit reached
- **System message:** Preserved throughout conversation

---

## 💡 Example Conversations

### Example 1: Deep-Dive Analysis

```
User: Which regions have the highest costs?
Bot: West region has the highest cost ratio at 65%...

User: Why is that?  [Follow-up]
Bot: West region's high costs are driven by...

User: What can we do to reduce them?  [Follow-up]
Bot: Here are 3 strategies to reduce costs in West region...
```

### Example 2: Comparative Analysis

```
User: Compare North and South regions
Bot: North region: $1.2M revenue, South: $980K...

User: Which one is more profitable?  [Follow-up]
Bot: South region has higher profit margin (35% vs 28%)...

User: Show me the breakdown  [Follow-up]
Bot: Detailed breakdown by product category...
```

### Example 3: Troubleshooting

```
User: Which stores need attention?
Bot: Stores 5, 12, and 18 are underperforming...

User: Tell me more about Store 5  [Follow-up]
Bot: Store 5 details: Revenue down 15%, foot traffic...

User: Is this a recent trend?  [Follow-up]
Bot: This decline started 3 months ago...

User: What do you recommend?  [Follow-up]
Bot: Immediate actions: 1. Market analysis 2. Staffing review...
```

---

## ⚙️ Configuration

### Change History Length

Edit `ollama_handler.py`:

```python
self.ollama_llm = OllamaLLM(
    max_history=15  # Default is 10 exchanges
)
```

### Disable History (One-off queries)

In `query_agent.py`:

```python
response = self._query_with_llm(
    question,
    use_history=False  # Disable conversation memory
)
```

---

## 🚀 Advanced Usage

### API Usage

You can use the conversation features programmatically:

```python
from ollama_handler import OllamaLLM

llm = OllamaLLM()

# Start conversation
response1 = llm.chat_with_history(
    "Which stores are underperforming?",
    system_message="You are a retail expert"
)

# Follow-up (automatically uses history)
response2 = llm.chat_with_history("Why is that?")

# Get conversation summary
summary = llm.get_history_summary()
print(f"Exchanges: {summary['message_count']//2}")

# Clear when done
llm.clear_history()
```

### Custom History Management

```python
# Get full history
history = llm.get_history()

# Save history to file
import json
with open('conversation.json', 'w') as f:
    json.dump(history, f)

# Restore history
with open('conversation.json', 'r') as f:
    history = json.load(f)
    llm.conversation_history = history
```

---

## 🎯 Tips for Power Users

### 1. **Chain Multiple Follow-ups**
Ask 5-6 related questions without repeating context

### 2. **Use Conversational Language**
- "them", "that", "it", "those"
- "the first one", "the last store"
- "as you mentioned", "like before"

### 3. **Build on Previous Answers**
```
Q1: Show metrics
Q2: Focus on the worst one
Q3: Compare it to the best one
Q4: What's the difference?
Q5: How do we close the gap?
```

### 4. **Mix Query Types**
```
Q1 (Anomaly): Find outliers
Q2 (Drilldown): Why the top outlier?
Q3 (Comparison): Compare to average
Q4 (Performance): Show trend over time
```

---

## 📊 Monitoring Conversations

### Session Info Widget

The dashboard shows:
- **Exchange count:** How many Q&A pairs
- **Duration:** How long the session has been active
- **Model:** Which LLM is being used

### When to Clear History

- Switching to unrelated topic
- Conversation exceeds 10+ exchanges (older context gets trimmed anyway)
- Got confused responses
- Want fresh start

---

## 🐛 Troubleshooting

### Issue: LLM doesn't remember previous context

**Solution:**
- Check that "Clear History" wasn't pressed
- Verify session info shows > 0 exchanges
- History automatically trims after 10 exchanges (oldest removed)

### Issue: Responses getting worse over time

**Solution:**
- Long conversations can confuse the model
- Clear history and start fresh
- Or ask standalone question without follow-up

### Issue: Follow-up doesn't make sense

**Solution:**
- Be more explicit: "Why is Store 12 underperforming?" instead of "Why?"
- Clear history if context is wrong
- Rephrase using full context

---

## ✅ Feature Checklist

- [x] Conversation history (up to 10 exchanges)
- [x] Auto-trimming of old messages
- [x] Clear history button
- [x] Undo last exchange
- [x] Session info display
- [x] System message persistence
- [x] Follow-up support with pronouns
- [x] Context retention across queries
- [x] Memory efficient (max 20 messages)

---

## 🎓 Learning Curve

### Beginner: Standalone Questions
```
Each question is independent
"Show me sales"
"Which stores are best?"
```

### Intermediate: Simple Follow-ups
```
Q1: "Show underperforming stores"
Q2: "Why?" or "Tell me more"
```

### Advanced: Conversation Chains
```
Q1: Initial analysis
Q2: Drill into specific finding
Q3: Compare to benchmark
Q4: Request recommendations
Q5: Clarify recommendation
Q6: Ask for implementation steps
```

---

**Status:** ✅ Fully Implemented
**Files Modified:**
- `ollama_handler.py` - Added conversation history
- `query_agent.py` - Integrated history management
- `app.py` - Added UI controls

**Benefits:**
- 🚀 Faster analysis (no need to repeat context)
- 💬 Natural conversation flow
- 🎯 Deeper insights through follow-ups
- ⚡ More efficient executive interactions
