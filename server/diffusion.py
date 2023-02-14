import torch
from diffusers import StableDiffusionPipeline

huggingface_token = "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"
model_id = "CompVis/stable-diffusion-v1-4"
device = "cuda"
dtype = torch.bfloat16

prompt = "a creature from another planet, age 10"

pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    use_auth_token=huggingface_token,
    torch_dtype=torch.bfloat16
).to(device)

with torch.autocast(device, dtype=dtype):
    image = pipe(prompt)["sample"][0]
    
image.save("prompt.png")