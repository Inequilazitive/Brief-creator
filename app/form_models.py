from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, pipeline, set_seed

import re
import torch
# Use a more powerful model (make sure it's installed or use Hugging Face Inference API)
generator = pipeline(
    "text-generation",
    model="google/gemma-3-1b-it",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

def clean_generated_text(text, original_prompt):
    """Clean the generated text by removing the original prompt and extracting relevant content."""
    # Remove the original prompt from the generated text
    if original_prompt in text:
        text = text.replace(original_prompt, "").strip()
    
    # Split by newlines and filter out empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Extract lines that look like headlines (remove bullet points, numbers, etc.)
    cleaned_lines = []
    for line in lines:
        # Remove common prefixes
        #line = re.sub(r'^[-•*]\s*', '', line)  # Remove bullet points
        #line = re.sub(r'^\d+\.\s*', '', line)  # Remove numbers
        line = re.sub(r'^Headlines?:?\s*', '', line, flags=re.IGNORECASE)  # Remove "Headlines:" prefix
        line = re.sub(r'^Subheadlines?:?\s*', '', line, flags=re.IGNORECASE)  # Remove "Subheadlines:" prefix
        
        if line and len(line) > 0:  # Only keep substantial content
            cleaned_lines.append(line)
    
    return cleaned_lines

def generate_headlines(brand_name, angle_description):
    """Generate headlines compatible with Gradio dataframe format."""
    try:
        if not brand_name or not angle_description:
            return [["Please provide brand name and angle description"]]
        
        prompt = (
            f"Generate 3 compelling Facebook ad headlines for '{brand_name}' "
            f"based on this angle: {angle_description}\n\n"
            f"Headlines:\n"
        )
        
        messages= [
            [
                {
                "role": "system",
                "content": "You are a professional writer specializing in creating engaging and engaging headlines for advertisements. Your task is to generate compelling headlines for given brands in the tone specified that capture attention and drive clicks."
                },
                {
                "role": "user",
                "content": prompt
                },
            ],
        ]
        
        #print(f"Headlines prompt: {prompt}")
        
        # Generate text
        #result = generator(prompt, max_length=500, do_sample=True, top_k=10, num_return_sequences=1,eos_token_id=tokenizer.eos_token_id)
        result=generator(messages, max_new_tokens=500)
        #generated_text = result[0]["generated_text"]
        print('result for headlines:', result)
        #print(f"Raw generated text: {generated_text}")
        
        # Clean and extract headlines
        headlines = clean_generated_text(result, prompt)
        
        print(f"Cleaned headlines: {headlines}")
        
        # Ensure we have exactly 3 headlines, pad with empty strings if needed
        # Take only first 3
        headlines = headlines[:3]
        
        # Format for Gradio dataframe: each headline as a separate row
        formatted_headlines = [[headline] for headline in headlines if headline]
        
        print(f"Formatted headlines: {formatted_headlines}")
        
        return formatted_headlines if formatted_headlines else [["No headlines generated"]]
        
    except Exception as e:
        print(f"Error generating headlines: {e}")
        return [["Error generating headlines. Please try again."]]

def generate_subheadlines(brand_name, angle_description):
    """Generate subheadlines compatible with Gradio dataframe format."""
    try:
        if not brand_name or not angle_description:
            return [["Please provide brand name and angle description"]]
        
        prompt = (
            f"Generate persuasive Facebook ad subheadlines for '{brand_name}' "
            f"based on this angle: {angle_description}\n\n"
            f"Subheadlines:\n"
            f"1. "
        )
        
        subheadlines_messages= [
            [
                {
                "role": "system",
                "content": "You are a professional writer specializing in creating engaging and engaging headlines for advertisements. Your task is to generate compelling subheadlines for given brands in the tone specified that capture attention and drive clicks."
                },
                {
                "role": "user",
                "content": prompt
                },
            ],
        ]
        result=generator(subheadlines_messages, max_new_tokens=600)
        #print(f"Subheadlines prompt: {prompt}")
        
        # Generate text
        #result = generator(prompt, max_length=500, do_sample=True, top_k=10, num_return_sequences=1,eos_token_id=tokenizer.eos_token_id)
        #generated_text = result[0]["generated_text"]
        
        print(f"Raw generated text: {result}")
        
        # Clean and extract subheadlines
        subheadlines = clean_generated_text(result, prompt)
        
        print(f"Cleaned subheadlines: {subheadlines}")
        
        # Ensure we have exactly 2 subheadlines, pad with empty strings if needed
        
        # Take only first 2
        subheadlines = subheadlines[:3]
        
        # Format for Gradio dataframe: each subheadline as a separate row
        formatted_subheadlines = [[subheadline] for subheadline in subheadlines if subheadline]
        
        print(f"Formatted subheadlines: {formatted_subheadlines}")
        
        return formatted_subheadlines if formatted_subheadlines else [["No subheadlines generated"]]
        
    except Exception as e:
        print(f"Error generating subheadlines: {e}")
        return [["Error generating subheadlines. Please try again."]]

# Alternative implementation using a more direct approach
def generate_headlines_simple(brand_name, angle_description):
    """Simplified version that returns hardcoded examples if model fails."""
    try:
        return generate_headlines(brand_name, angle_description)
    except:
        # Fallback to example headlines
        return [
            [f"Transform Your Space with {brand_name}"],
            [f"Discover the Power of {brand_name}"],
            [f"Why {brand_name} is Different"]
        ]

def generate_subheadlines_simple(brand_name, angle_description):
    """Simplified version that returns hardcoded examples if model fails."""
    try:
        return generate_subheadlines(brand_name, angle_description)
    except:
        # Fallback to example subheadlines
        return [
            [f"Experience the benefits of {brand_name} today"],
            [f"Join thousands who trust {brand_name}"]
        ]