import google.generativeai as genai

API_KEY = "AIzaSyDOE1i5S_UBFQvatM4pawfdWkOciWu43GU"

try:
    genai.configure(api_key=API_KEY)
    print("Available models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"FAILURE: {e}")
