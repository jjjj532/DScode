from __future__ import annotations

from cscode.core.config import Config
from cscode.providers.base import LLMProvider


def create_provider(config: Config) -> LLMProvider:
    match config.provider:
        case "openai":
            from cscode.providers.openai import OpenAIProvider

            return OpenAIProvider(config)
        case "anthropic":
            from cscode.providers.anthropic import AnthropicProvider

            return AnthropicProvider(config)
        case "ollama":
            from cscode.providers.ollama import OllamaProvider

            return OllamaProvider(config)
        case _:
            msg = f"Unknown provider: {config.provider}. Supported: openai, anthropic, ollama"
            raise ValueError(msg)
