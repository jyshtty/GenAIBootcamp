# dial api client - talk to openai thru epam

import os
from openai import AzureOpenAI
from typing import List, Dict, Any, Optional


class DIALClient:
    # calls epam dial for completions

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        # api_key from env if not given
        self.api_key = api_key or os.getenv("DIAL_API_KEY", "<YOUR_API_KEY_HERE>")
        self.model = model
        self.azure_endpoint = "https://ai-proxy.lab.epam.com"
        self.api_version = "2024-02-01"

        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint
            )
            
            if not self.api_key or self.api_key == "<YOUR_API_KEY_HERE>":
                print("DIAL API Key not found. Please set the DIAL_API_KEY environment variable.")
                self.client = None
            else:
                print("DIAL Client initialized successfully!")
                
        except Exception as e:
            print(f"Error initializing DIAL client: {e}")
            self.client = None
    
    def get_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        # send messages get back text
        if not self.client:
            return "DIAL client not properly initialized. Please check your API key."
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=float(os.getenv("DIAL_TEMPERATURE", "0.7"))
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error calling DIAL API: {e}"
    
    def analyze_sentiment(self, text: str) -> str:
        # sentiment of text
        messages = [
            {
                "role": "system",
                "content": "You are a sentiment analysis expert. Analyze the sentiment of the given text and respond with: POSITIVE, NEGATIVE, or NEUTRAL, followed by a brief explanation."
            },
            {
                "role": "user",
                "content": f"Analyze the sentiment of this text: '{text}'"
            }
        ]
        return self.get_completion(messages)
    
    def generate_response(self, context: str, customer_query: str) -> str:
        # answer customer from context
        messages = [
            {
                "role": "system",
                "content": "You are a helpful hotel customer service agent. Provide friendly, professional responses to customer queries based on the given context."
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nCustomer Query: {customer_query}\n\nProvide a helpful response:"
            }
        ]
        return self.get_completion(messages)


def test_dial_connection():
    # quick test that dial works
    print("Testing DIAL API connection...")

    client = DIALClient()

    if not client.client:
        print("DIAL client initialization failed")
        return False

    test_messages = [
        {"role": "user", "content": "Explain the concept of 'technical debt' in one sentence."}
    ]
    
    response = client.get_completion(test_messages)
    print("Test Response:", response[:200] if len(response) > 200 else response)
    
    if "Error" not in response:
        print("DIAL API test successful!")
        return True
    else:
        print("DIAL API test failed")
        return False


if __name__ == "__main__":
    test_dial_connection()