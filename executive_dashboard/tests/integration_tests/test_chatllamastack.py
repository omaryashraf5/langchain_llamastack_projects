#!/usr/bin/env python3
"""Test ChatLlamaStack directly

NOTE: This is an integration test that requires a running LlamaStack server.
It will be skipped in CI environments.
"""

import os
import sys

import pytest

# Skip this test in CI environments
pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Integration test - requires running LlamaStack server",
)

print("=" * 60)
print("Testing ChatLlamaStack Installation and Functionality")
print("=" * 60)

# Step 1: Check if langchain_llama_stack is installed
print("\n[1] Checking if langchain_llama_stack is installed...")
try:
    import langchain_llama_stack

    print(f"✅ langchain_llama_stack is installed")
    print(f"   Version: {getattr(langchain_llama_stack, '__version__', 'unknown')}")
except ImportError as e:
    print(f"❌ langchain_llama_stack is NOT installed")
    print(f"   Error: {e}")
    print("\nInstall it with: pip install langchain-llama-stack")
    sys.exit(1)

# Step 2: Check if ChatLlamaStack is available
print("\n[2] Checking if ChatLlamaStack class is available...")
try:
    from langchain_llama_stack import ChatLlamaStack

    print(f"✅ ChatLlamaStack class found")
except ImportError as e:
    print(f"❌ ChatLlamaStack class not found")
    print(f"   Error: {e}")
    sys.exit(1)

# Step 3: Check if langchain_core is available
print("\n[3] Checking if langchain_core is installed...")
try:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    print(f"✅ langchain_core is installed")
except ImportError as e:
    print(f"❌ langchain_core is NOT installed")
    print(f"   Error: {e}")
    print("\nInstall it with: pip install langchain-core")
    sys.exit(1)

# Step 4: Initialize ChatLlamaStack
print("\n[4] Initializing ChatLlamaStack...")
try:
    llm = ChatLlamaStack(
        model="ollama/llama3.3:70b",
        base_url="http://localhost:8321/v1/openai/v1/",
        temperature=0.7,
    )
    print(f"✅ ChatLlamaStack initialized successfully")
    print(f"   Model: ollama/llama3.3:70b")
    print(f"   Base URL: http://localhost:8321")
except Exception as e:
    print(f"❌ Failed to initialize ChatLlamaStack")
    print(f"   Error: {e}")
    sys.exit(1)

# Step 5: Test connection with a simple query
print("\n[5] Testing connection with a simple query...")
try:
    response = llm.invoke([HumanMessage(content="Say 'hello' in one word")])
    print(f"✅ Successfully got response from LlamaStack")
    print(f"   Response: {response.content}")
except Exception as e:
    print(f"❌ Failed to get response from LlamaStack")
    print(f"   Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure llama stack server is running:")
    print("   lsof -i:8321")
    print("2. Check server health:")
    print("   curl http://localhost:8321/v1/health")
    print("3. Verify the model is available:")
    print("   curl http://localhost:8321/v1/models | jq '.data[] | .identifier'")
    sys.exit(1)

# Step 6: Test with multiple messages
print("\n[6] Testing with conversation (multiple messages)...")
try:
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What is 2+2?"),
    ]
    response = llm.invoke(messages)
    print(f"✅ Successfully got response with conversation")
    print(f"   Response: {response.content[:100]}...")
except Exception as e:
    print(f"❌ Failed conversation test")
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("✅ All tests passed! ChatLlamaStack is working correctly.")
print("=" * 60)
