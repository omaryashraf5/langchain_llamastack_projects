# Starting LlamaStack Server

## 🚀 Quick Start

### Step 1: Build the Starter Distribution

```bash
cd ~/langchain_llamastack_project/executive_dashboard

# Build the starter distribution (only needs to be done once)
uv run --with llama-stack llama stack build --distro starter
```

This will:
- Register the Ollama provider
- Configure inference capabilities
- Set up the basic API endpoints

### Step 2: Run the LlamaStack Server

```bash
# Run the server on port 8321
uv run --with llama-stack llama stack run starter --port 8321
```

Or use the default port 5001:
```bash
uv run --with llama-stack llama stack run starter
```

### Step 3: Verify It's Running

Open a new terminal and test:

```bash
# Check if server is responding
curl http://localhost:8321/v1/models

# Test chat completions
curl -X POST http://localhost:8321/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3:70b-instruct",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

---

## 🔧 Troubleshooting

### Error: Provider 'basic' is already registered

**Solution:**
```bash
# Kill any existing LlamaStack processes
pkill -f "llama stack"

# Clean up and rebuild
rm -rf ~/.llama/
uv run --with llama-stack llama stack build --distro starter
```

### Error: Port already in use

**Solution:**
```bash
# Kill process on port 8321
lsof -ti:8321 | xargs kill -9

# Or use a different port
uv run --with llama-stack llama stack run starter --port 8322
```

### Error: Model not found

**Solution:**
```bash
# Make sure Ollama is running
curl http://localhost:11434/api/tags

# If not running
sudo systemctl start ollama
# or
ollama serve
```

---

## 📋 Configuration

### Default LlamaStack Config Location
```
~/.llama/builds/starter/
```

### View Current Config
```bash
cat ~/.llama/builds/starter/llama-stack-config.yaml
```

### Supported Models

LlamaStack will use models from your Ollama installation:
- `llama3:70b-instruct` (recommended)
- `llama3.1:8b`
- `llama3.2:3b`
- Any other models installed in Ollama

---

## 🎯 Integration with Dashboard

Once LlamaStack is running, the dashboard will automatically detect it:

1. **Start LlamaStack:**
   ```bash
   uv run --with llama-stack llama stack run starter --port 8321
   ```

2. **Start Dashboard:**
   ```bash
   streamlit run app.py
   ```

3. **Dashboard will show:**
   ```
   🤖 LLM Powered - Using LlamaStack (Ollama wrapper) with conversation memory
   ```

---

## 💡 Why Use LlamaStack?

### Benefits over Direct Ollama:

1. **Unified API** - OpenAI-compatible endpoints
2. **Better Error Handling** - More robust response parsing
3. **Request Management** - Built-in retry logic and timeouts
4. **Extensibility** - Easy to add more providers (AWS Bedrock, Together, etc.)
5. **Monitoring** - Better logging and debugging

### Architecture:

```
Dashboard → LlamaStack (port 8321) → Ollama (port 11434) → Llama Model
```

---

## 🔄 Restart LlamaStack

If you need to restart:

```bash
# Stop
pkill -f "llama stack"

# Start
uv run --with llama-stack llama stack run starter --port 8321
```

---

## 📊 Health Check

Create a simple health check script:

```bash
#!/bin/bash
echo "Checking LlamaStack health..."

if curl -s http://localhost:8321/v1/models > /dev/null; then
    echo "✅ LlamaStack is running"
else
    echo "❌ LlamaStack is not responding"
    echo "Starting LlamaStack..."
    uv run --with llama-stack llama stack run starter --port 8321 &
fi
```

---

## 🎛️ Advanced Options

### Run with Custom Config

```bash
uv run --with llama-stack llama stack run \
  --config ~/.llama/builds/starter/llama-stack-config.yaml \
  --port 8321
```

### Enable Debug Logging

```bash
export LLAMA_STACK_LOG_LEVEL=DEBUG
uv run --with llama-stack llama stack run starter --port 8321
```

### Run in Background

```bash
nohup uv run --with llama-stack llama stack run starter --port 8321 > llamastack.log 2>&1 &
```

---

## ✅ Quick Checklist

Before running the dashboard:

- [ ] Ollama is running (`curl http://localhost:11434/api/tags`)
- [ ] Model is loaded (`ollama list | grep llama3:70b`)
- [ ] LlamaStack is running (`curl http://localhost:8321/v1/models`)
- [ ] Port 8321 is accessible
- [ ] `.env` file has correct `LLAMASTACK_API_URL=http://localhost:8321`

---

## 🆘 Getting Help

If you encounter issues:

1. Check Ollama logs: `journalctl -u ollama -f`
2. Check LlamaStack output in terminal
3. Test endpoints with curl commands above
4. Try direct Ollama as fallback (dashboard will auto-fallback)

---

**Status:** Ready to start LlamaStack server
**Next Step:** Run `uv run --with llama-stack llama stack run starter --port 8321`
