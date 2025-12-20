from PIL import Image
import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration

class Blip2Captioner:
    """
    Load BLIP-2 once, then call caption(image) many times.
    """
    def __init__(self, model_name: str = "Salesforce/blip2-opt-2.7b"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = Blip2Processor.from_pretrained(model_name)

        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.model = Blip2ForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=dtype,
            device_map=None,  # keep simple
        ).to(self.device)

        self.model.eval()

    @torch.inference_mode()
    def caption(self, image: Image.Image, prompt: str = "Describe the image.", max_new_tokens: int = 50) -> str:
        """
        image: PIL.Image (RGB recommended)
        prompt: optional instruction (makes it more like VQA)
        """
        if image.mode != "RGB":
            image = image.convert("RGB")

        inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.device)
        output_ids = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        text = self.processor.decode(output_ids[0], skip_special_tokens=True).strip()
        return text


if __name__ == "__main__":
    cap = Blip2Captioner()

    img = Image.open("assets/1901.jpeg")
    print(cap.caption(img, prompt="Describe the image in one sentence."))
    print(cap.caption(img, prompt="List up to 5 objects you see, coma-separated.", max_new_tokens=30))

