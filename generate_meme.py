from diffusers import StableDiffusionPipeline
import torch
from PIL import Image, ImageDraw, ImageFont
import uuid
import os
import requests

# Load the Stable Diffusion model from the local path
MODEL_PATH = "./models/sd-turbo"

pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    local_files_only=True,
    safety_checker=None  # Optional: disable if needed
)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

# Function to generate meme caption using local LLM (Ollama)
def generate_meme_text_from_ollama(context, style):
    # Optimized and enhanced prompt for meme caption generation
    prompt = (
        f"Write a humorous, short, and witty meme caption based on the following context: '{context}'. "
        f"The caption should be relatable and appropriate for a meme, with a {style} tone. "
        f"Ensure the caption is brief, punchy, and follows typical meme conventions (puns, irony, or sarcasm). "
        f"Only output the caption, with no explanations, hashtags, or headings. The caption should "
        f"be perfect for an image-based meme, ensuring maximum impact in the shortest possible sentence."
    )

    try:
        # Sending the prompt to Ollama API
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",  # Use a lighter model like mistral for faster response
            "prompt": prompt,
            "stream": False
        })
        result = response.json()
        caption = result.get("response", "").strip()

        # Return a fallback caption if the API fails to generate a valid one
        if not caption:
            return "When AI tries to be funny..."
        return caption
    except Exception as e:
        print("Ollama API error:", e)
        return "When AI tries to be funny..."

# Add caption to the generated image
def add_meme_text(image, caption):
    draw = ImageDraw.Draw(image)
    try:
        # Adjust font size based on image dimensions
        font_size = max(20, image.width // 18)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    max_width = image.width - 40
    words = caption.split()
    lines, line = [], ""

    # Split caption into multiple lines if necessary
    for word in words:
        test = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    # Calculate total height of the text
    total_height = sum(draw.textbbox((0, 0), l, font=font)[3] + 10 for l in lines)
    y = image.height - total_height - 30  # Ensure text is at the bottom of the image

    # Draw the text on the image
    for l in lines:
        bbox = draw.textbbox((0, 0), l, font=font)
        x = (image.width - (bbox[2] - bbox[0])) / 2  # Center-align text
        draw.text((x, y), l, fill="white", font=font, stroke_width=2, stroke_fill="black")
        y += bbox[3] + 10  # Move down for the next line

    return image

# Generate meme image from context and style
def generate_meme_image(context, style):
    # Generate the image based on the context using Stable Diffusion
    prompt = (
    f"A vibrant, highly detailed digital painting that captures the essence of: {context}. "
    f"The image should feature rich colors, dynamic brushstrokes, and artistic textures. "
    f"The composition should evoke emotion, with stylized lighting and imaginative elements. "
    f"The scene should look hand-painted, emphasizing creativity over realism. No text, no logos."
)


    image = pipe(prompt, height=512, width=512).images[0]

    # Generate meme caption using Ollama API
    meme_text = generate_meme_text_from_ollama(context, style)

    # Add the generated caption to the image
    final_image = add_meme_text(image, meme_text)

    # Save the final meme image
    filename = f"{uuid.uuid4()}.png"
    save_path = os.path.join("static/memes", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    final_image.save(save_path)

    return save_path