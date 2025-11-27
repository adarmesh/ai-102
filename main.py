import os
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env file

# === CONFIG ===
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g. "https://<your-resource-name>.openai.azure.com"
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = "2023-10-01-preview"  # per Azure REST API docs
DEPLOYMENT_NAME = "dall-e-3"  # the deployment name you created for DALL·E on your resource

# === Helper to generate an image ===
def generate_image(prompt: str,
                   n: int = 1,
                   size: str = "1024x1024",
                   quality: str = "hd",
                   style: str = "vivid") -> dict:
    """
    Returns the parsed JSON response from Azure OpenAI images/generations:submit endpoint.
    The result contains a 'data' list, each element having 'url' and 'revised_prompt' keys.
    """
    if not AZURE_ENDPOINT or not API_KEY:
        raise RuntimeError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY must be set in environment")

    url = AZURE_ENDPOINT
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }

    body = {
        "model": DEPLOYMENT_NAME,
        "prompt": prompt,
        "n": n,
        "size": size,
        "quality": quality,
        "style": style
    }

    resp = requests.post(url, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    return resp.json()


# === Helper to download the generated image URL ===
def download_image_from_url(url: str, out_path: str):
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            if chunk:
                f.write(chunk)


# === Example usage ===
if __name__ == "__main__":
    prompt = "A badger wearing a tuxedo, photorealistic"
    print("Submitting image generation request...")
    result = generate_image(prompt, n=1, size="1024x1024", quality="hd", style="vivid")
    # Example response shape:
    # {
    #   "created": 1686780744,
    #   "data": [
    #       {"url": "https://...", "revised_prompt": "..."}
    #   ]
    # }
    data = result.get("data", [])
    if not data:
        raise RuntimeError("No image returned: " + str(result))

    image_url = data[0].get("url")
    revised_prompt = data[0].get("revised_prompt")
    print("Revised prompt:", revised_prompt)
    print("Image URL:", image_url)

    out_file = "generated_image.png"
    print(f"Downloading image to {out_file} ...")
    download_image_from_url(image_url, out_file)
    print("Saved:", out_file)
