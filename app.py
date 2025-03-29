from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": prompt}]
    )
    # Format the response into paragraphs
    response_text = response.choices[0].message.content
    # Replace double newlines with paragraph breaks
    formatted_response = response_text.replace('\n\n', '</p><p>')
    # Wrap the text in paragraph tags
    formatted_response = f'<p>{formatted_response}</p>'
    return formatted_response

@app.route('/')
def home():
    if 'messages' not in session:
        session['messages'] = []
    return render_template('index.html', messages=session['messages'])

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message')
    if user_message:
        # Add user message to chat history
        session['messages'].append({"role": "user", "content": user_message})
        
        # Get bot response
        response = chat_with_gpt(user_message)
        
        # Add assistant response to chat history
        session['messages'].append({"role": "assistant", "content": response})
        
        return jsonify({"status": "success", "response": response})
    return jsonify({"status": "error", "message": "No message provided"})

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    session['messages'] = []
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)