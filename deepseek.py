"""
DeepSeek API Utility Module
Shared utility for calling DeepSeek API across all ML APIs.
"""

import json
import os
import urllib.request
import urllib.error


DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


def call_deepseek(prompt: str, system_prompt: str = "", max_tokens: int = 500, temperature: float = 0.7) -> dict:
    """
    Call DeepSeek API and return the response.
    
    Args:
        prompt: User message
        system_prompt: System instructions
        max_tokens: Maximum response length
        temperature: Creativity (0-1)
    
    Returns:
        dict with 'success', 'content', or 'error'
    """
    if not DEEPSEEK_API_KEY:
        return {"success": False, "error": "DEEPSEEK_API_KEY not set"}
    
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = json.dumps({
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }).encode("utf-8")
        
        req = urllib.request.Request(
            DEEPSEEK_API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]
            return {"success": True, "content": content}
    
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        return {"success": False, "error": f"API error: {e.code} - {error_body}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_json_response(content: str) -> dict:
    """Extract JSON from DeepSeek response (handles markdown code blocks)."""
    try:
        # Try direct parse first
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # Try extracting from code blocks
    if "```json" in content:
        start = content.index("```json") + 7
        end = content.index("```", start)
        return json.loads(content[start:end].strip())
    elif "```" in content:
        start = content.index("```") + 3
        end = content.index("```", start)
        return json.loads(content[start:end].strip())
    
    return {"raw_response": content}
