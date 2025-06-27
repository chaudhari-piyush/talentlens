import google.generativeai as genai
import os


def gemini_api_key(api_key):
    """Test Gemini API key with Flash 2.5"""
    try:
        # Configure the API
        genai.configure(api_key=api_key)

        # Initialize the model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Test with a simple prompt
        response = model.generate_content("Hello! Can you confirm you're working?")

        print("✅ API Key is working!")
        print(f"Model: gemini-2.0-flash-exp")
        print(f"Response: {response.text}")
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")

        # Handle specific errors
        if "API_KEY_INVALID" in str(e):
            print("🔑 Fix: Check your API key")
        elif "PERMISSION_DENIED" in str(e):
            print("🚫 Fix: API key doesn't have permission")
        elif "QUOTA_EXCEEDED" in str(e):
            print("📊 Fix: API quota exceeded")
        elif "MODEL_NOT_FOUND" in str(e):
            print("🤖 Fix: Model not available - try gemini-1.5-flash")

        return False


# Usage
if __name__ == "__main__":
    API_KEY = "AIzaSyAmI1Y_667GclFEwcuQPMeUes5TJ-_6pw8"  # Replace with your actual API key

    if API_KEY == "your-gemini-api-key":
        print("❌ Please replace API_KEY with your actual Gemini API key")
        print("🔑 Get it from: https://aistudio.google.com/app/apikey")
        exit(1)

    gemini_api_key(API_KEY)