import gradio as gr
import requests
import datetime
import os
import json
import dotenv
import webbrowser

api_key = dotenv.get_key('.env', 'STABILITY_API_KEY')

def generate_image(prompt, mode, uploaded_image, strength, aspect_ratio, seed, output_format, model, negative_prompt):
    api_url = "https://api.stability.ai/v2beta/stable-image/generate/"
    headers = {
        "authorization": "Bearer " + api_key,  # Replace with your actual API key
        "accept": "image/*" if output_format == 'png' or output_format == 'jpeg' else "application/json"
    }
    
    data = {
        "prompt": prompt,
        "mode": mode,
        "seed": seed,
        "output_format": output_format,
        "model": model,
        "negative_prompt": negative_prompt
    }
    files = {
    "data": ('', json.dumps(data), 'application/json'),  # Add this line
    }   
    if mode == "image-to-image" and uploaded_image is not None:
        files["image"] = ('image', uploaded_image, 'application/octet-stream')
        data["strength"] = strength
    else:
        data["aspect_ratio"] = aspect_ratio,
    endpoint = "sd3" if model != "core" else "core"
    response = requests.post(api_url+endpoint, headers=headers, data=data, files=files)

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

    with gr.Blocks(title="Stable Diffusion 3") as interface:
        gr.Markdown('# Stable Diffusion 3')
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    prompt = gr.Textbox(label="Prompt", placeholder="Enter a description for the image...")
                with gr.Row():
                    negative_prompt = gr.Textbox(label="Negative Prompt", placeholder="Describe what you do NOT want to see...")
                with gr.Row():
                    aspect_ratio = gr.Dropdown(choices=["1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"], label="Aspect Ratio", value="1:1")
                    seed = gr.Number(label="Seed", value=0)
                with gr.Row():
                    output_format = gr.Dropdown(choices=["jpeg", "png", "application/json"], label="Output Format", value="jpeg")
                    model = gr.Dropdown(choices=["sd3", "sd3-turbo", "core"], label="Model", value="sd3")
                with gr.Row(visible=False):
                    uploaded_image = gr.File(label="Upload Image")
                    strength = gr.Slider(minimum=0, maximum=1, step=0.01, value=0.5, label="Strength")
                    mode = gr.Radio(choices=["text-to-image", "image-to-image"], value="text-to-image", label="Mode")
                submit_button = gr.Button("Generate")
            with gr.Column():
                image_display = gr.Image(label="Generated Image")

        submit_button.click(
            generate_image, 
            inputs=[prompt, mode, uploaded_image, strength, aspect_ratio, seed, output_format, model, negative_prompt],
            outputs=image_display
        )
    port = 7870
    webbrowser.open('http://127.0.0.1:' + str(port), new=2)
    interface.launch(server_port=port)

if __name__ == "__main__":
    main()
