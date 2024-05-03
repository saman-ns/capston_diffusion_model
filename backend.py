import base64
import os
import requests
API_Key = input("Press Enter to continue...")
engine_id = "stable-diffusion-v1-6"
api_host = os.getenv('API_HOST', 'https://api.stability.ai')
api_key = os.getenv('API_key', 'STABILITY_API_KEY')

    
if api_key is None:
    raise Exception("Missing Stability API key.")

response = requests.post(
    f"{api_host}/v1/generation/{engine_id}/image-to-image/masking",
    headers={
        "Accept": 'application/json',
        "Authorization": f"Bearer {api_key}"
    },
    files={
        'init_image': open("Image0002.png", 'rb'),
        'mask_image': open("Image0001.png", 'rb'),
    },
    data={
        "mask_source": "MASK_IMAGE_BLACK",
        "text_prompts[0][text]": "A large spiral galaxy with a bright central bulge and a ring of stars around it",
        "cfg_scale": 7,
        "clip_guidance_preset": "FAST_BLUE",
        "samples": 1,
        "steps": 30,
    }
)

if response.status_code != 200:
    raise Exception("Non-200 response: " + str(response.text))

data = response.json()

for i, image in enumerate(data["artifacts"]):
    with open(f"./out/v1_img2img_masking_{i}.png", "wb") as f:
        f.write(base64.b64decode(image["base64"]))
