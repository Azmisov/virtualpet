from flask import Flask
from flask_cors import CORS
from flask import request, send_file

import torch
from diffusers import StableDiffusionPipeline

huggingface_token = "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"
model_id = "CompVis/stable-diffusion-v1-4"
device = "cuda"
dtype = torch.float16
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    use_auth_token=huggingface_token,
    torch_dtype=dtype
).to(device)
pipe.enable_attention_slicing()

app = Flask(__name__)
CORS(app)

@app.route("/")
def generate_prompt():
    prompt = request.args.get("prompt","")
    with torch.autocast(device, dtype=dtype):
        image = pipe(prompt).images[0]
    image.save("prompt.png")
    return send_file("prompt.png", mimetype="image/png")