import google.generativeai as genai
import sys

API_KEY = "AIzaSyDOE1i5S_UBFQvatM4pawfdWkOciWu43GU"

try:
    genai.configure(api_key=API_KEY)
    # Using the name without models/ prefix as the SDK often handles it
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content("Say hello")
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"FAILURE: {e}")
    sys.exit(1)
