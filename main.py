import gradio as gr
import requests
import datetime
import os
import json
import dotenv

api_key = dotenv.get_key('.env', 'STABILITY_API_KEY')

def generate_image(prompt, mode, uploaded_image, strength, aspect_ratio, seed, output_format, model, negative_prompt):
    api_url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
    headers = {
        "authorization": "Bearer " + api_key,  # Replace with your actual API key
        "accept": "image/*" if output_format == 'png' or output_format == 'jpeg' else "application/json"
    }
    data = {
        "prompt": prompt,
        "mode": mode,
        "aspect_ratio": aspect_ratio,
        "seed": seed,
        "output_format": output_format,
        "model": model,
        "negative_prompt": negative_prompt
    }
    files = {
    "data": ('', json.dumps(data), 'application/json'),  # Add this line
    }   
    if mode == "image-to-image":
        if uploaded_image is not None:
            files["image"] = uploaded_image
            data["strength"] = strength

    response = requests.post(api_url, headers=headers, data=data, files=files)

    if response.status_code == 200:
        # Save the file with a unique timestamp-based name
        file_extension = output_format if output_format in ['jpeg', 'png'] else 'txt'
        filename = f"./generated_images/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_image.{file_extension}"
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(data)
        return filename
    else:
        # Handle possible API errors
        raise Exception("Failed to generate image: " + str(response.json()))

def main():
    if not os.path.exists('generated_images'):
        os.makedirs('generated_images')

    with gr.Blocks() as interface:
        with gr.Row():
            prompt = gr.Textbox(label="Prompt", placeholder="Enter a description for the image...")
            mode = gr.Radio(choices=["text-to-image", "image-to-image"], value="text-to-image", label="Mode")
        with gr.Row():
            uploaded_image = gr.File(label="Upload Image")
            strength = gr.Slider(minimum=0, maximum=1, step=0.01, value=0.5, label="Strength")
        with gr.Row():
            aspect_ratio = gr.Dropdown(choices=["1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"], label="Aspect Ratio", value="1:1")
            seed = gr.Number(label="Seed", value=0)
        with gr.Row():
            output_format = gr.Dropdown(choices=["jpeg", "png", "application/json"], label="Output Format", value="jpeg")
            model = gr.Dropdown(choices=["sd3", "sd3-turbo"], label="Model", value="sd3")
        with gr.Row():
            negative_prompt = gr.Textbox(label="Negative Prompt", placeholder="Describe what you do NOT want to see...")
        submit_button = gr.Button("Generate")
        
        submit_button.click(
            generate_image, 
            inputs=[prompt, mode, uploaded_image, strength, aspect_ratio, seed, output_format, model, negative_prompt],
            outputs=gr.Image(label="Generated Image")
        )

    interface.launch()

if __name__ == "__main__":
    main()
