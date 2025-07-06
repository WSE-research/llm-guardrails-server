#!/usr/bin/env python3
"""
Example client for testing the moderation server.
"""

import requests
import json
import sys


def test_moderation_api(server_url: str = "http://localhost:8000"):
    """Test the moderation API with various inputs."""
    
    # Test cases for  PII detection
    test_cases = [
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {text}")
        
        # Prepare request
        payload = {
            "model": "omni-moderation-latest",
            "input": text
        }
        
        try:
            # Make request
            response = requests.post(
                f"{server_url}/v1/moderations",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                moderation_result = result["results"][0]
                
                print(f"Flagged: {moderation_result['flagged']}")
                print("Categories:")
                for category, flagged in moderation_result["categories"].items():
                    if flagged:
                        score = moderation_result["category_scores"][category]
                        print(f"  - {category}: {flagged} (score: {score:.4f})")
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")


def test_health_endpoint(server_url: str = "http://localhost:8000"):
    """Test the health endpoint."""
    try:
        response = requests.get(f"{server_url}/health", timeout=10)
        if response.status_code == 200:
            print("Health check:", response.json())
        else:
            print(f"Health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")


def test_models_endpoint(server_url: str = "http://localhost:8000"):
    """Test the models endpoint."""
    try:
        response = requests.get(f"{server_url}/v1/models", timeout=10)
        if response.status_code == 200:
            print("Available models:", json.dumps(response.json(), indent=2))
        else:
            print(f"Models endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Models endpoint failed: {e}")


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print("Testing LLM Guardrails Server")
    print(f"Base URL: {base_url}")
    
    print("\n=== Health Check ===")
    test_health_endpoint(base_url)
    
    print("\n=== Models Endpoint ===")
    test_models_endpoint(base_url)
    
    print("\n=== Moderation API Tests ===")
    test_moderation_api(base_url)
