"""
Ollama LLM integration for local inference.
Uses LLaMA 3 8B model for text generation.
"""

import os
import requests
from typing import Optional


class OllamaLLM:
    """Wrapper for Ollama local LLM inference."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3"
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Base URL of Ollama server (default: localhost:11434)
            model: Model name to use (default: llama3)
        """
        self.base_url = base_url
        self.model = model
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: Input prompt for the model
            temperature: Sampling temperature (0-1). Lower = more deterministic
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(
                    f"Ollama error: {response.status_code} - {response.text}"
                )
            
            result = response.json()
            return result.get("response", "").strip()
        
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running locally."
            )
