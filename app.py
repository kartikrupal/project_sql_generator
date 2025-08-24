import os
import re
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# It's recommended to save your API key in a .env file
# in the same directory as this script.
# Create a file named .env and add the line:
# GEMINI_API_KEY="YOUR_API_KEY"
load_dotenv()

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Gemini API Configuration ---
try:
    # Configure the API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
    
    genai.configure(api_key=api_key)
    
    # Set up the model
    generation_config = {
        "temperature": 0.2,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
    )

except (ValueError, KeyError) as e:
    print(f"Error during Gemini initialization: {e}")
    # In a real application, you might want to handle this more gracefully
    # For now, we'll exit if the API key is not configured.
    exit()

# --- Route to Serve the Frontend ---
@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

# --- API Endpoint for SQL Generation ---
@app.route('/generate-sql', methods=['POST'])
def generate_sql():
    """
    Receives a natural language query and returns the generated SQL.
    """
    if not request.json or 'prompt' not in request.json:
        return jsonify({'error': 'Invalid request. "prompt" is required.'}), 400

    user_input = request.json['prompt']
    db_schema = request.json.get('schema', '') # Get optional schema

    # This prompt is designed to instruct the AI to only return SQL code.
    # Providing the schema gives the model context for more accurate queries.
    prompt_parts = [
        "You are an expert SQL generator. Translate the following natural language description into a SQL query.",
        "Only return the raw SQL code, with no explanations, comments, or markdown formatting.",
    ]

    if db_schema:
        prompt_parts.append(f"\nUse the following database schema for context:\n---\n{db_schema}\n---")

    prompt_parts.append(f'\nNatural Language Description: "{user_input}"')
    
    full_prompt = "\n".join(prompt_parts)

    try:
        # --- Call the Gemini API ---
        response = model.generate_content(full_prompt)
        raw_sql_code = response.text.strip()
        
        # --- Clean the Output ---
        # A more robust way to remove markdown code fences using regex
        # It handles ```sql, ```, and other variations.
        clean_sql_code = re.sub(r'^\s*```(sql)?\s*|\s*```\s*$', '', raw_sql_code, flags=re.MULTILINE).strip()
        clean_sql_code = clean_sql_code.lstrip(' |l').strip()      
        return jsonify({'sql_code': clean_sql_code})

    except Exception as e:
        print(f"Error generating SQL with Gemini: {e}")
        return jsonify({'error': 'Failed to generate SQL. See server logs for details.'}), 500

# --- Main Execution ---
if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible on your local network
    # Set debug=False for production environments
    app.run(host='0.0.0.0', port=5000, debug=True)
