import asyncio
import os
from pathlib import Path
from random import randint
from time import sleep

import requests
from PIL import Image
from dotenv import dotenv_values

# Resolve project paths relative to this file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
DATA_DIR = PROJECT_ROOT / "Data"
IMAGE_REQUEST_PATH = PROJECT_ROOT / "Frontend" / "Files" / "ImageGeneration.data"

# API details for Hugging Face inference models.
DEFAULT_MODELS = [
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-3.5-large",
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0",
]
env_vars = dotenv_values(ENV_PATH)
HF_API_KEY = env_vars.get("HuggingFaceAPIKey") or env_vars.get("HUGGINGFACE_API_KEY") or os.getenv("HuggingFaceAPIKey") or os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL = env_vars.get("HuggingFaceModel") or env_vars.get("HUGGINGFACE_MODEL")
headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}


def open_images(prompt: str) -> None:
    """Open generated images for a prompt."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    prompt_slug = prompt.replace(" ", "_")
    files = [f"{prompt_slug}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = DATA_DIR / jpg_file
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except OSError:
            print(f"Unable to open {image_path}")


def _model_candidates() -> list[str]:
    if HF_MODEL:
        return [HF_MODEL] + [m for m in DEFAULT_MODELS if m != HF_MODEL]
    return DEFAULT_MODELS


def _normalize_prompt(raw_prompt: str) -> str:
    """Clean routing prefixes and improve prompts for diagram/chart style outputs."""
    prompt = (raw_prompt or "").strip()
    lower = prompt.lower()
    if lower.startswith("generate image"):
        prompt = prompt[len("generate image"):].strip(" :,-")

    lower_clean = prompt.lower()
    diagram_keywords = (
        "diagram",
        "flowchart",
        "chart",
        "graph",
        "infographic",
        "mind map",
        "architecture diagram",
        "org chart",
    )
    if any(keyword in lower_clean for keyword in diagram_keywords):
        prompt = (
            f"{prompt}, clean white background, 2D vector style, "
            "clear labels, readable typography, presentation-ready layout"
        )
    return prompt


async def query(payload: dict) -> bytes:
    last_error = None
    for model in _model_candidates():
        api_url = f"https://router.huggingface.co/hf-inference/models/{model}"
        try:
            response = await asyncio.to_thread(
                requests.post,
                api_url,
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type.lower():
                text = response.text[:500]
                raise RuntimeError(f"Model '{model}' did not return an image. Response: {text}")
            return response.content
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"All image models failed. Last error: {last_error}")


async def generate_images(prompt: str) -> list[Path]:
    if not HF_API_KEY:
        raise RuntimeError("Missing Hugging Face API key. Set HuggingFaceAPIKey in .env.")

    prompt = _normalize_prompt(prompt)
    if not prompt:
        raise RuntimeError("Empty image prompt.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": (
                f"{prompt}, quality=4K, sharpness=maximum, "
                f"Ultra High details, high resolution, seed={randint(0, 1000000)}"
            )
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    saved_files = []
    prompt_slug = prompt.replace(" ", "_")
    for i, image_bytes in enumerate(image_bytes_list, start=1):
        out_path = DATA_DIR / f"{prompt_slug}{i}.jpg"
        with open(out_path, "wb") as f:
            f.write(image_bytes)
        saved_files.append(out_path)
    return saved_files


def GenerateImages(prompt: str) -> bool:
    try:
        asyncio.run(generate_images(prompt))
        open_images(prompt)
        return True
    except Exception as e:
        print(f"Image generation failed: {e}")
        return False


def process_image_request_file() -> bool:
    """Poll and process one image-generation request.
    Returns True if a request was processed.
    """
    IMAGE_REQUEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not IMAGE_REQUEST_PATH.exists():
        IMAGE_REQUEST_PATH.write_text("False,False", encoding="utf-8")
        return False

    data = IMAGE_REQUEST_PATH.read_text(encoding="utf-8").strip()
    if "," not in data:
        return False

    left, right = [x.strip() for x in data.split(",", 1)]
    # Accept both formats: "prompt,True" and "True,prompt".
    if right.lower() == "true" and left.lower() != "false":
        prompt, status = left, right
    elif left.lower() == "true" and right.lower() != "false":
        prompt, status = right, left
    else:
        return False

    if status.lower() != "true" or not prompt:
        return False

    print("Generating Images ...")
    ok = GenerateImages(prompt=prompt)
    IMAGE_REQUEST_PATH.write_text("False,False", encoding="utf-8")
    return ok


def run_service_loop() -> None:
    while True:
        try:
            processed = process_image_request_file()
            if processed:
                break
            sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Image service error: {e}")
            sleep(1)


if __name__ == "__main__":
    run_service_loop()
