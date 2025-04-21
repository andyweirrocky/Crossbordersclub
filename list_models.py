import os
from dotenv import load_dotenv
import google.generativeai as genai

def list_available_models():
    # Load environment variables
    load_dotenv()
    
    # Configure the API
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    
    try:
        # List available models
        print("\nAvailable Models:")
        print("=" * 50)
        for model in genai.list_models():
            print(f"\nModel Name: {model.name}")
            print(f"Display Name: {model.display_name}")
            print(f"Description: {model.description}")
            print(f"Generation Methods: {', '.join(model.supported_generation_methods)}")
            print(f"Input Token Limit: {model.input_token_limit}")
            print(f"Output Token Limit: {model.output_token_limit}")
            print("-" * 50)
    
    except Exception as e:
        print(f"Error listing models: {str(e)}")

if __name__ == "__main__":
    list_available_models() 