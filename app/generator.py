from transformers import pipeline, LlavaNextProcessor, LlavaNextForConditionalGeneration
from typing import List, Optional, Dict, Any
import os
from PIL import Image
import torch
from app.config import MODEL_NAME, MAX_NEW_TOKENS
from app.prompts import PromptBuilder
from app.io import process_swipe_csv, prepare_reference_images, extract_image_urls_from_csv

class CreativeBriefGenerator:
    def __init__(self):
        """Initialize the vision-language model pipeline"""
        self.model_name = MODEL_NAME
        self.max_tokens = MAX_NEW_TOKENS
        self.processor = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the LLaVA model and processor"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Loading {self.model_name} on {device}...")
            
            # Load processor and model separately for better control
            self.processor = LlavaNextProcessor.from_pretrained(self.model_name)
            self.model = LlavaNextForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            if device == "cpu":
                self.model = self.model.to(device)
                
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to a text-only model if vision model fails
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """Load a fallback text-only model if vision model fails"""
        try:
            print("Loading fallback text-generation model...")
            self.pipe = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                max_new_tokens=self.max_tokens,
                do_sample=True,
                temperature=0.7
            )
            self.model = None  # Signal that we're using fallback
            print("Fallback model loaded successfully!")
        except Exception as e:
            print(f"Error loading fallback model: {e}")
            raise

    def generate_creative_briefs(
        self,
        brand_name: str,
        product_name: str,
        website_url: str,
        target_audience: str,
        tone: str,
        angle_description: str,
        template_path: str,
        csv_df=None,
        uploaded_images=None,
        headlines: Optional[List[str]] = None,
        subheadlines: Optional[List[str]] = None,
        benefits: Optional[List[str]] = None,
        social_proof: Optional[List[str]] = None,
        content_bank: Optional[List[str]] = None,
        angle_and_benefits: Optional[str] = None,
        num_image_briefs: int = 10,
        num_video_briefs: int = 10,
        **kwargs
    ) -> str:
        """
        Generate creative briefs using vision-language model with images and text.
        """
        
        # Process CSV data
        csv_text = ""
        reference_image_paths = []
        
        if csv_df is not None:
            csv_text = process_swipe_csv(csv_df)
            csv_image_urls = extract_image_urls_from_csv(csv_df)
            reference_image_paths = prepare_reference_images(uploaded_images, csv_image_urls)
        elif uploaded_images:
            reference_image_paths = prepare_reference_images(uploaded_images, [])
        
        # Build the text prompt
        prompt_builder = PromptBuilder(template_path)
        text_prompt = prompt_builder.build_prompt(
            brand_name=brand_name,
            product_name=product_name,
            website_url=website_url,
            target_audience=target_audience,
            tone=tone,
            angle_description=angle_description,
            headlines=headlines,
            subheadlines=subheadlines,
            benefits=benefits,
            social_proof=social_proof,
            content_bank=content_bank,
            angle_and_benefits=angle_and_benefits,
            num_image_briefs=num_image_briefs,
            num_video_briefs=num_video_briefs,
            csv_data=csv_text
        )
        
        # Generate briefs using the model
        if reference_image_paths and self.model is not None:
            # Use vision model with images
            print(f"Generating briefs with images: {reference_image_paths}")
            return self._generate_with_images(text_prompt, reference_image_paths)
        else:
            # Use text-only generation (fallback or no images)
            return self._generate_text_only(text_prompt)
    
    def _generate_with_images(self, text_prompt: str, image_paths: List[str]) -> str:
        """Generate briefs using images and text with LLaVA"""
        try:
            # Use the first image as primary reference
            primary_image_path = image_paths[0] if image_paths else None
            
            print(f"Primary image path: {primary_image_path}")
            print(f"Text prompt: {text_prompt}")
            if not primary_image_path or not os.path.exists(primary_image_path):
                return self._generate_text_only(text_prompt)
            
            # Load and process the image
            image = Image.open(primary_image_path).convert('RGB')
            
            # Prepare the conversation format
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": text_prompt}
                    ]
                }
            ]
            
            print(f"Conversation for generation: {conversation}")
            # Process inputs
            prompt = self.processor.apply_chat_template(conversation, add_generation_prompt=True)
            inputs = self.processor(images=image, text=prompt, return_tensors="pt")
            
            # Move to same device as model
            if torch.cuda.is_available():
                inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_tokens,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # Decode the response
            generated_text = self.processor.decode(output[0], skip_special_tokens=True)
            
            # Extract only the new generated part
            prompt_length = len(self.processor.decode(inputs['input_ids'][0], skip_special_tokens=True))
            result = generated_text[prompt_length:].strip()
            
            return result if result else "Error: No response generated"
                
        except Exception as e:
            print(f"Error generating with images: {e}")
            return f"Error during generation: {str(e)}"
    
    def _generate_text_only(self, text_prompt: str) -> str:
        """Fallback: Generate briefs using text only"""
        try:
            if hasattr(self, 'pipe'):  # Using fallback pipeline
                result = self.pipe(text_prompt, max_new_tokens=self.max_tokens, num_return_sequences=1)
                return result[0]['generated_text'] if result else "Error: No text generated"
            else:
                # Use the main model in text-only mode
                inputs = self.processor(text=text_prompt, return_tensors="pt")
                
                if torch.cuda.is_available():
                    inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    output = self.model.generate(
                        **inputs,
                        max_new_tokens=self.max_tokens,
                        do_sample=True,
                        temperature=0.7,
                        pad_token_id=self.processor.tokenizer.eos_token_id
                    )
                
                generated_text = self.processor.decode(output[0], skip_special_tokens=True)
                return generated_text.strip()
                
        except Exception as e:
            print(f"Error in text-only generation: {e}")
            return f"Error during generation: {str(e)}"
    
    def save_brief_to_file(self, brief_content: str, filename: str, output_dir: str = "outputs/markdown") -> str:
        """Save generated brief to a markdown file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(brief_content)
            
            return filepath
        except Exception as e:
            print(f"Error saving brief to file: {e}")
            return ""

# Global instance to avoid reloading the model multiple times
_generator_instance = None

def get_generator() -> CreativeBriefGenerator:
    """Get singleton instance of the generator"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = CreativeBriefGenerator()
    return _generator_instance