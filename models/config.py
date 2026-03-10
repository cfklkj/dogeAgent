"""
模型配置
"""
from typing import Dict, Any

MODEL_CONFIG: Dict[str, Dict[str, Any]] = {
    "nvidia": {
        "model": "z-ai/glm5",
        "provider": "nvidia",
        "capabilities": ["basic_reasoning", "calculation", "chinese"],
        "max_tokens": 2048,
        "temperature": 0.7,
    },
    "google": {
        "model": "gemini-2.0-flash-exp",
        "provider": "google",
        "capabilities": ["web_search", "creative", "multilingual", "vision"],
        "max_tokens": 4096,
        "temperature": 0.7,
    }
}

# 默认配置
DEFAULT_CONFIG = {
    "provider": "nvidia",
    "model": MODEL_CONFIG["nvidia"]["model"],
    "temperature": 0.7,
    "max_tokens": 2048,
}
