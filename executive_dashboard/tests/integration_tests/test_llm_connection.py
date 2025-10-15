#!/usr/bin/env python3
"""Test script to diagnose LLM connection issues

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

sys.path.insert(0, "/home/omara/langchain_llamastack_projects/executive_dashboard")

from llamastack_handler import LlamaStackLLM

print("=" * 60)
print("Testing LlamaStack LLM Connection")
print("=" * 60)

# Initialize LLM
llm = LlamaStackLLM()

print(f"\nConfiguration:")
print(f"  API URL: {llm.api_url}")
print(f"  Model: {llm.model}")

# Test availability
print(f"\nTesting availability...")
available = llm.is_available()
print(f"  LLM Available: {available}")

if available:
    print(f"\n✅ LLM is available! Testing chat completion...")

    # Test simple chat completion
    messages = [{"role": "user", "content": "Say 'hello' in one word"}]
    try:
        response = llm.chat_completion(messages, max_tokens=5)
        print(f"  Response: {response}")
        print(f"\n✅ LLM is working correctly!")
    except Exception as e:
        print(f"  ❌ Error during chat completion: {e}")
else:
    print(f"\n❌ LLM is NOT available!")
    print(f"\nTroubleshooting:")
    print(f"1. Check if llama stack server is running:")
    print(f"   lsof -i:8321 -P")
    print(f"2. Check server health:")
    print(f"   curl -s {llm.api_url}/v1/health")
    print(f"3. Try starting the server:")
    print(f"   llama stack run /home/omara/server1-starter.yaml --port 8321")

print("\n" + "=" * 60)
