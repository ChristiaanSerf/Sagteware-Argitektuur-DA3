from flask import Flask, request, jsonify
from google import genai
from google.genai import types
from PIL import Image
import io
import base64
from functions import save_cs2_scoreboard

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


app = Flask(__name__)

# Default configuration
client_config = {
    "system_instruction": "You are a helpful assistant and expert eSports analyst. You are specifically knowledgeable on Counter-Strike 2",
    "temperature": 0.2,
    "top_p": 1.0,
    "top_k": 1,
    "max_output_tokens": 1024
}

client = genai.Client()

def get_generate_content_config():
    return {
        "system_instruction": client_config.get("system_instruction", "You are a helpful assistant."),
        "temperature": client_config.get("temperature", 0.7),
        "top_p": client_config.get("top_p", 1.0),
        "top_k": client_config.get("top_k", 1),
        "max_output_tokens": client_config.get("max_output_tokens", 1024)
    }
    

def get_function_calling_config():
    import json
    import os

    functions_json_path = os.path.join(os.path.dirname(__file__), "functions.json")
    with open(functions_json_path, "r") as f:
        functions_list = json.load(f)

    tools = types.Tool(function_declarations=functions_list)
    config = get_generate_content_config()
    config["tools"] = [tools]
    return config

@app.route('/configure', methods=['POST'])
def configure():
    data = request.json
    if not data:
        return jsonify({"error": "No configuration provided"}), 400
    # Update only provided keys
    for key in ["system_instruction", "temperature", "top_p", "top_k", "max_output_tokens"]:
        if key in data:
            client_config[key] = data[key]
    return jsonify({"message": "Configuration updated", "config": client_config})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    if not data or "prompt" not in data:
        return jsonify({"error": "No prompt provided"}), 400
    prompt = data["prompt"]
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=client_config["system_instruction"],
                temperature=client_config["temperature"],
                top_p=client_config["top_p"],
                top_k=client_config["top_k"],
                max_output_tokens=client_config["max_output_tokens"],
                thinking_config=types.ThinkingConfig(thinking_budget=0)),
            contents=prompt
        )
        print(response)
        return jsonify({"text": getattr(response, "text", str(response))})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/describe_image', methods=['POST'])
def describe_image():
    data = request.json
    if not data or "image_base64" not in data:
        return jsonify({"error": "No image_base64 provided"}), 400
    image_b64 = data["image_base64"]
    try:
        image_bytes = base64.b64decode(image_b64)
        image = types.Part.from_bytes(
            data=image_bytes, mime_type="image/jpeg"
            )
        # Optionally, you can check for a custom prompt
        prompt = data.get("prompt", "Analyze this Counter-Strike 2 scoreboard image and extract all player information, team scores, and statistics. Use the save_cs2_scoreboard function to store this data.")
        
        # Use function calling configuration
        config = get_function_calling_config()
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=config,
            contents=[image, prompt]
        )
        
        # Check for function call in the response
        if (hasattr(response, 'candidates') and 
            response.candidates and 
            hasattr(response.candidates[0], 'content') and
            response.candidates[0].content.parts and
            hasattr(response.candidates[0].content.parts[0], 'function_call') and
            response.candidates[0].content.parts[0].function_call):
            
            function_call = response.candidates[0].content.parts[0].function_call
            
            if function_call.name == "save_cs2_scoreboard":
                try:
                    # Call the function with the extracted arguments
                    function_result = save_cs2_scoreboard(**function_call.args)
                    
                    return jsonify({
                        "text": response.text,
                        "function_called": function_call.name,
                        "function_arguments": function_call.args,
                        "function_result": function_result
                    })
                except Exception as func_error:
                    return jsonify({
                        "text": response.text,
                        "function_called": function_call.name,
                        "function_arguments": function_call.args,
                        "function_error": str(func_error)
                    }), 500
            else:
                return jsonify({
                    "text": response.text,
                    "function_called": function_call.name,
                    "function_arguments": function_call.args,
                    "message": "Unknown function called"
                })
        else:
            # No function call found, return regular response
            return jsonify({"text": getattr(response, "text", str(response))})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
