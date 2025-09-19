from flask import Flask, request, jsonify
import time

app = Flask(__name__)

class Pipeline:
    """Simple pipeline implementation to demonstrate pipeline concepts"""
    
    def __init__(self):
        self.steps = []
        self.results = []
    
    def step(self, func):
        """Add a step to the pipeline"""
        self.steps.append(func)
        return self
    
    def run(self):
        """Execute all steps in the pipeline"""
        result = None
        self.results = []
        
        for i, step in enumerate(self.steps):
            if callable(step):
                if result is None:
                    result = step()
                else:
                    # For demonstration, pass previous result to next step if it accepts parameters
                    try:
                        result = step(result)
                    except TypeError:
                        # If step doesn't accept parameters, just call it
                        result = step()
            
            self.results.append({
                "step": i + 1,
                "function": step.__name__ if hasattr(step, '__name__') else str(step),
                "result": result
            })
        
        return result

def hello_step():
    """Simple hello world step for demonstration"""
    return "Hello, World from Pypelyne!"

def add_timestamp():
    """Add current timestamp to demonstrate pipeline functionality"""
    return f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}"

def process_input(input_text="CS2 Analysis System"):
    """Process input text to show pipeline data flow"""
    return f"Processing: {input_text} - Status: Complete"

def transform_message(message):
    """Transform the message for demonstration"""
    if isinstance(message, str):
        return f"🚀 Transformed: {message.upper()}"
    return f"🚀 Transformed: {message}"

@app.route("/")
def index():
    return jsonify({
        "service": "Pypelyne Hello World Service (Mock Implementation)",
        "status": "running",
        "endpoints": ["/hello", "/pipeline", "/health"],
        "note": "This demonstrates pipeline concepts using a simple mock implementation"
    })

@app.route("/hello", methods=["GET"])
def hello():
    """Simple hello world endpoint using Pipeline"""
    try:
        # Create a simple pipeline with hello step
        pipeline = Pipeline()
        result = pipeline.step(hello_step).run()
        
        return jsonify({
            "message": result,
            "pipeline": "hello_pipeline",
            "status": "success",
            "steps_executed": len(pipeline.results),
            "pipeline_results": pipeline.results
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route("/pipeline", methods=["GET", "POST"])
def pipeline_demo():
    """Demonstrate a multi-step pipeline"""
    try:
        # Get input from query parameter or POST body
        if request.method == "POST":
            data = request.get_json() or {}
            input_text = data.get("input", "CS2 Analysis System")
        else:
            input_text = request.args.get("input", "CS2 Analysis System")
        
        # Create a multi-step pipeline
        pipeline = Pipeline()
        
        # Add steps to the pipeline in sequence
        result = (pipeline
                 .step(lambda: process_input(input_text))
                 .step(add_timestamp)
                 .step(transform_message)
                 .step(hello_step)
                 .run())
        
        return jsonify({
            "input": input_text,
            "pipeline_steps": ["process_input", "add_timestamp", "transform_message", "hello_step"],
            "final_result": result,
            "status": "success",
            "execution_details": pipeline.results
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"ok": True, "service": "pypelyne_service"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)