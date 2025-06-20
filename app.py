from flask import Flask, render_template, request, jsonify
from generate_meme import generate_meme_image
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Root route to render the index page
@app.route("/")
def index():
    return render_template("index.html")

# Route to generate the meme
@app.route("/generate", methods=["POST"])
def generate():
    # Get context and style from the form
    context = request.form.get("context")
    style = request.form.get("style")

    # Record start time for performance measurement
    start = time.time()

    try:
        # Generate meme image
        meme_path = generate_meme_image(context, style)

        # Calculate time taken to generate meme
        duration = round(time.time() - start, 2)

        # Return meme path and time taken in JSON response
        return jsonify({"meme_path": meme_path, "time_taken": duration})
    except Exception as e:
        # In case of error, return error message in JSON response
        print("Error:", e)  # Log the error
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Ensure the 'static/memes' directory exists
    os.makedirs("static/memes", exist_ok=True)

    # Run the Flask app in debug mode
    app.run(debug=True)
 