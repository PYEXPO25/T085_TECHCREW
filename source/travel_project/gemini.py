from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai

# Configure Google Gemini AI
GOOGLE_API_KEY = "AIzaSyB9hq8iaipp08G6vCtdYz_WQ4C_cgiLyXA"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

def chat():
    print("Chat with the AI! Type 'exit' to quit.")
    
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Exit condition
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Get the response from the model
        response = model.generate_content(user_input)
        
        # Print the AI response
        print(f"AI: {response.text}")

# Run the chat function
chat()