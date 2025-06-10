from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, pipeline, set_seed

import re
import torch
import spaces

# Use a more powerful model (make sure it's installed or use Hugging Face Inference API)
generator = pipeline(
    "text-generation",
    model="google/gemma-3-1b-it",
    device="cuda",
    torch_dtype=torch.bfloat16,
)

import re

def clean_generated_text(text, original_prompt):
    """Extract actual subheadline text from generated content, including markdown-style and bolded formats."""
    if original_prompt in text:
        text = text.replace(original_prompt, "").strip()

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    subheadlines = []

    for line in lines:
        # Match: * **subheadline text**
        bold_match = re.search(r'\*\*\s*(.*?)\s*\*\*', line)

        # Match: ###SubheadlineX: subheadline text
        hash_match = re.search(r'^#+Subheadline\d*:\s*(.+)', line, re.IGNORECASE)
        hash_headline_match = re.search(r'^#+Headline\d*:\s*(.+)', line, re.IGNORECASE)
        hash_headline_match2= re.search(r'^#+\s*Headline\s*\d*\.\s*(.+)', line, re.IGNORECASE)
        hash_subheadline_match2= re.search(r'^#+\s*Subheadline\s*\d*\.\s*(.+)', line, re.IGNORECASE)
        numbered_match = re.search(r'^\d+\.\s*(.+)', line)
        if bold_match:
            subheadlines.append(bold_match.group(1).strip())
        elif hash_match:
            subheadlines.append(hash_match.group(1).strip())
        elif hash_headline_match:
            subheadlines.append(hash_headline_match.group(1).strip())
        elif hash_headline_match2:
            subheadlines.append(hash_headline_match2.group(1).strip())
        elif numbered_match:
            subheadlines.append(numbered_match.group(1).strip())
        elif hash_subheadline_match2:
            subheadlines.append(hash_subheadline_match2.group(1).strip())
    return subheadlines

@spaces.GPU
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
        
        messages = [
            [
                {
                    "role": "system",
                    "content": "You are a professional writer specializing in creating engaging and engaging headlines for advertisements. Your task is to generate compelling headlines for given brands in the tone specified that capture attention and drive clicks. You will give the response like ###Headline 1. <Headline>, ### Headline 2. <Headline> and no explanations, just the headlines one by one."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
        ]
        
        retries = 5
        for attempt in range(retries):
            try:
                # Generate text
                result = generator(messages, max_new_tokens=500)
                result = result[0][0]['generated_text'][-1]['content']
                
                print('Result for headlines:', result)
                
                # Clean and extract headlines
                headlines = clean_generated_text(result, prompt)
                
                print(f"Cleaned headlines: {headlines}")
                
                # Ensure we have exactly 3 headlines, pad with empty strings if needed
                headlines = headlines[:3]
                
                # Format for Gradio dataframe: each headline as a separate row
                formatted_headlines = [[headline] for headline in headlines if headline]
                
                print(f"Formatted headlines: {formatted_headlines}")
                
                return formatted_headlines if formatted_headlines else [["No headlines generated"]]
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise
        
    except Exception as e:
        print(f"Error generating headlines: {e}")
        return [["Error generating headlines. Please try again."]]
@spaces.GPU
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
        
        subheadlines_messages = [
            [
                {
                    "role": "system",
                    "content": "You are a professional writer specializing in creating engaging and engaging headlines for advertisements. Your task is to generate compelling subheadlines for given brands in the tone specified that capture attention and drive clicks. You will give the response like ###SubHeadline 1. <SubHeadline>, ###SubHeadline 2. <SubHeadline> and no explanations, just the headlines one by one."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
        ]
        
        retries = 5
        for attempt in range(retries):
            try:
                # Generate text
                result = generator(subheadlines_messages, max_new_tokens=600)
                result = result[0][0]['generated_text'][-1]['content']
                
                print(f"Raw generated text: {result}")
                
                # Clean and extract subheadlines
                subheadlines = clean_generated_text(result, prompt)
                
                print(f"Cleaned subheadlines: {subheadlines}")
                
                # Ensure we have exactly 2 subheadlines, pad with empty strings if needed
                subheadlines = subheadlines[:3]
                
                # Format for Gradio dataframe: each subheadline as a separate row
                formatted_subheadlines = [[subheadline] for subheadline in subheadlines if subheadline]
                
                print(f"Formatted subheadlines: {formatted_subheadlines}")
                
                return formatted_subheadlines if formatted_subheadlines else [["No subheadlines generated"]]
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise
        
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