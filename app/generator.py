from transformers import pipeline
from typing import List, Optional, Dict, Any
import os
from PIL import Image
import torch
from app.config import MODEL_NAME, MAX_NEW_TOKENS
from app.prompts import PromptBuilder
from app.io import process_swipe_csv, prepare_reference_images, extract_image_urls_from_csv

class CreativeBriefGenerator:
    def __init__(self):
        """Initialize the LLaVA model pipeline"""
        self.model_name = MODEL_NAME
        self.max_tokens = MAX_NEW_TOKENS
        self.pipe = None
        self._load_model()
    
    def _load_model(self):
        """Load the LLaVA model pipeline"""
        try:
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Loading {self.model_name} on {device}...")
            
            self.pipe = pipeline(
                "image-text-to-text", 
                model=self.model_name,
                device=0 if device == "cuda" else -1,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            )
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
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
        Generate creative briefs using LLaVA model with images and text.
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
        if reference_image_paths:
            # Use the first image as primary reference (or combine multiple)
            return self._generate_with_images(text_prompt, reference_image_paths)
        else:
            # Generate with text only (fallback)
            return self._generate_text_only(text_prompt)
    
    def _generate_with_images(self, text_prompt: str, image_paths: List[str]) -> str:
        """Generate briefs using images and text with LLaVA"""
        try:
            # Prepare messages for the model
            # For now, use the first image as primary reference
            # In a more advanced version, we could process multiple images
            primary_image_path = image_paths[0] if image_paths else None
            
            if not primary_image_path or not os.path.exists(primary_image_path):
                return self._generate_text_only(text_prompt)
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "url": f"file://{os.path.abspath(primary_image_path)}"},
                        {"type": "text", "text": text_prompt}
                    ]
                }
            ]
            
            # Generate response
            result = self.pipe(messages, max_new_tokens=self.max_tokens)
            
            if result and isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', 'Error: No text generated')
            else:
                return 'Error: Invalid response from model'
                
        except Exception as e:
            print(f"Error generating with images: {e}")
            return f"Error during generation: {str(e)}"
    
    def _generate_text_only(self, text_prompt: str) -> str:
        """Fallback: Generate briefs using text only"""
        try:
            # For text-only generation, we'll create a simple message
            messages = [
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": text_prompt}
                    ]
                }
            ]
            
            result = self.pipe(messages, max_new_tokens=self.max_tokens)
            
            if result and isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', 'Error: No text generated')
            else:
                return 'Error: Invalid response from model'
                
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