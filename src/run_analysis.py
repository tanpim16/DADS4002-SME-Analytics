import google.generativeai as genai
genai.configure(api_key="AIzaSyBMzMcmpkzaBN8MnqgfuhG3UC9KII6wPIc")

model = genai.GenerativeModel("models/gemini-2.5-flash")
response = model.generate_content("hello")
print(response.text)
