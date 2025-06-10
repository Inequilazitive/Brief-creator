from transformers import pipeline, LlavaForConditionalGeneration, AutoProcessor, AutoModelForVision2Seq
from transformers.image_utils import load_image
from typing import List, Optional, Dict, Any
import os
from PIL import Image
import torch
from app.config import VLM_MODEL_NAME, LLM_MODEL_NAME, MAX_NEW_TOKENS
from app.prompts import PromptBuilder
from app.io import process_swipe_csv, prepare_reference_images, extract_image_urls_from_csv
import traceback
#import spaces

class CreativeBriefGenerator:
    @spaces.GPU
    def __init__(self):
        """Initialize the vision-language model pipeline"""
        self.vlm_model_name = VLM_MODEL_NAME
        self.llm_model_name = LLM_MODEL_NAME
        self.llm_pipe = None
        self.max_tokens = MAX_NEW_TOKENS
        self.vlm_processor = None
        self.model = None
        self._load_model()
        
    @spaces.GPU
    def _load_model(self):
        """Load the LLaVA model and processor"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Loading {self.vlm_model_name} on {device}...")
            
            # Load processor and model separately for better control
            DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
            self.vlm_model = AutoModelForVision2Seq.from_pretrained(
                self.vlm_model_name,
                torch_dtype=torch.float16,
                #device_map="auto",
                _attn_implementation="flash_attention_2" if DEVICE == "cuda" else "eager"
            ).to(DEVICE)
            self.vlm_processor = AutoProcessor.from_pretrained(self.vlm_model_name)
            # if device == "cpu":
            #     self.model = self.model.to(device)                
            print("VLM Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")  
            # Fallback to a text-only model if vision model fails
            self._load_fallback_model()
            
        try:
            print(f"Loading {self.llm_model_name} for text generation...")
            self.llm_pipe = pipeline(
                "text-generation",
                model=self.llm_model_name,
                max_new_tokens=self.max_tokens,
                do_sample=True,
                temperature=0.7,
            )
            print("Text generation model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")  
            # Fallback to a text-only model if vision model fails
            self._load_fallback_model()
    @spaces.GPU
    def _load_fallback_model(self):
        """Load a fallback text-only model if vision model fails"""
        try:
            print("Loading fallback text-generation model...")
            self.pipe = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                max_new_tokens=self.max_tokens,
                do_sample=True,
                temperature=0.4
            )
            self.model = None  # Signal that we're using fallback
            print("Fallback model loaded successfully!")
        except Exception as e:
            print(f"Error loading fallback model: {e}")
            raise
        
    @spaces.GPU    
    def _get_image_description(self, image_paths: str) -> str:
        try:
            DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
            primary_image_path = image_paths[0] if image_paths else None
            print(f"Primary image path: {primary_image_path}")            
            
            image = load_image(primary_image_path)
            print(image)

            conversation = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": "Give a brief 5-10 line description of this image, including any relevant context or information that can help in generating a creative brief."},
                    ],
                },
            ]

            prompt = self.vlm_processor.apply_chat_template(conversation, add_generation_prompt=True)
            print(f"Processed prompt: {prompt}")
            
            inputs = self.vlm_processor(images=[image], text=prompt, return_tensors="pt").to(DEVICE)

            output = self.vlm_model.generate(
                **inputs,
                max_new_tokens=1000,
            )

            generated_text = self.vlm_processor.batch_decode(output, skip_special_tokens=True)[0]
            print(f"Generated description: {generated_text}")

            # Clean up: strip any user/assistant role text
            if "Assistant:" in generated_text:
                # Only keep the text after "Assistant:"
                generated_text = generated_text.split("Assistant:", 1)[-1].strip()

            return generated_text

        except Exception as e:
            print(f"Error in generating image description: {e}")
            return "Failed to generate image description."

        
        except Exception as e:
            print(f"Error generating image description: {e}")
            print("Traceback:")
            print(traceback.format_exc())
            return "Error generating image description"
        
        
    @spaces.GPU
    def generate_creative_briefs(
        self,
        brand_name: str,
        product_name: str,
        website_url: str,
        target_audience: str,
        tone: str,
        angle_description: str,
        user_template_path: str,
        system_template_path: str,
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
        image_description = self._get_image_description(reference_image_paths) if reference_image_paths else ""
        # Build the text prompt
        prompt_builder = PromptBuilder(user_template_path)
        user_text_prompt = prompt_builder.build_prompt(
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
            csv_data=csv_text,
            reference_image_description=image_description
        )
        
        # Generate briefs using the model
        if reference_image_paths and self.llm_pipe is not None:
            # Use vision model with images
            print(f"Generating briefs with images: {reference_image_paths}")
            return self._generate_with_images(user_text_prompt, system_template_path, reference_image_paths)
        else:
            # Use text-only generation (fallback or no images)
            return self._generate_text_only(user_text_prompt)
    
    
    @spaces.GPU
    def _generate_with_images(self, user_text_prompt: str,sys_text_prompt: str, image_paths: List[str]) -> str:
        """Generate briefs using images and text with LLaVA"""
        try:
            
            llm_message =  [
                {"role": "system", "content": sys_text_prompt},
                {"role": "user", "content": user_text_prompt},
            ]
            print(f'Final user prompt: {user_text_prompt}')
            output_brief = self.llm_pipe(
                llm_message,
                max_new_tokens=self.max_tokens,
                temperature=0.7,
            )
            print("Generated output brief:", output_brief)
            
            print(f"clened output brief", output_brief[0]["generated_text"][-1])
            # Extract only the new generated part
            #prompt_length = len(self.processor.decode(inputs['input_ids'][0], skip_special_tokens=True))
            #result = generated_text[prompt_length:].strip()
            
            return output_brief[0]["generated_text"][-1]['content'] if output_brief else "Error: No response generated"
                
        except Exception as e:
            print(f"Error generating with images: {e}")
            print("Traceback:")
            print(traceback.format_exc())
            return f"Error during generation: {str(e)}"
    @spaces.GPU
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
    @spaces.GPU
    def save_brief_to_file(self, brief_content: str, filename: str, output_dir: str = "../outputs/markdown") -> str:
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

@spaces.GPU
def get_generator() -> CreativeBriefGenerator:
    """Get singleton instance of the generator"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = CreativeBriefGenerator()
    return _generator_instance