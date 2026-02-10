import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
print(f"API Key found: {api_key is not None}")
print(f"API Key (first 10 chars): {api_key[:10] if api_key else 'None'}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Test with the newest model
        print("\n🧪 Testing gemini-2.5-flash...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model.generate_content("Say hello in a professional manner!")
        print(f"✅ Success! Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ No API key found!")