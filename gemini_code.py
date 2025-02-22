import google.generativeai as genai

# Set up the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Set your API key
GOOGLE_API_KEY = "AIzaSyB9hq8iaipp08G6vCtdYz_WQ4C_cgiLyXA"

# Configure the API with your key
genai.configure(api_key=GOOGLE_API_KEY)

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
