import spaces
import gradio as gr
import pandas as pd
from pathlib import Path
from app.generator import get_generator
from app.io import parse_csv_file
from app.config import EVERGREEN_TEMPLATE_PATH, PROMO_TEMPLATE_PATH, EVERGREEN_SYSTEM_PROMPT_PATH, EVERGREEN_USER_PROMPT_PATH
from app.ui import build_ui
import traceback
import re
import markdown
from weasyprint import HTML, CSS
from io import StringIO
import tempfile
import os
@spaces.GPU
def process_dataframe_input(df_data):
    """Convert Gradio dataframe input (Pandas DataFrame) to list"""
    if df_data is None or df_data.empty:
        return None
    return df_data.iloc[:, 0].dropna().astype(str).str.strip().tolist()
@spaces.GPU
def create_download_files(content, brand_name):
    """Create downloadable files in different formats"""
    try:
        # Create a temporary directory for files
        temp_dir = tempfile.mkdtemp()
        base_filename = f"{brand_name.lower().replace(' ', '_')}_brief"
        
        # 1. Create MD file
        md_path = os.path.join(temp_dir, f"{base_filename}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 2. Create TXT file (plain text version)
        txt_path = os.path.join(temp_dir, f"{base_filename}.txt")
        # Convert markdown to plain text (remove markdown formatting)
        plain_text = re.sub(r'#+\s*', '', content)  # Remove headers
        plain_text = re.sub(r'\*\*(.*?)\*\*', r'\1', plain_text)  # Remove bold
        plain_text = re.sub(r'\*(.*?)\*', r'\1', plain_text)  # Remove italic
        plain_text = re.sub(r'`(.*?)`', r'\1', plain_text)  # Remove code formatting
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        
        # 3. Create PDF file
        pdf_path = os.path.join(temp_dir, f"{base_filename}.pdf")
        
        # Convert markdown to HTML
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        
        # Add CSS styling for better PDF appearance
        css_content = """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
        }
        h1, h2, h3 {
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        h1 {
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        p {
            margin-bottom: 10px;
        }
        ul, ol {
            margin-left: 20px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
        }
        """
        
        # Create HTML with CSS
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Creative Brief - {brand_name}</title>
            <style>{css_content}</style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Generate PDF
        HTML(string=full_html).write_pdf(pdf_path)
        
        return md_path, txt_path, pdf_path
        
    except Exception as e:
        print(f"Error creating download files: {e}")
        return None, None, None
    
@spaces.GPU
def generate_brief_callback(
    brand_name, product_name, website_url, target_audience, tone,
    content_bank, campaign_type, swipe_csv, reference_images,
    angle_description, angle_and_benefits,
    headlines_df, auto_headlines,
    subheadlines_df, auto_subheadlines,
    social_proof, voiceover_tone,
    num_image_briefs, num_video_briefs,
    brand_guide, campaign_deck, misc_assets
):
    """Main callback function for generating creative briefs"""
    
    try:
        # Validate required inputs
        if not brand_name or not product_name or not angle_description:
            return "❌ **Error**: Please fill in Brand Name, Product Name, and Angle Description.", None, None, None
        
        # Process CSV file
        csv_df = None
        if swipe_csv is not None:
            csv_df = parse_csv_file(swipe_csv)
            if csv_df is None:
                return "❌ **Error**: Could not parse the uploaded CSV file.", None, None, None
        
        # Process headlines and subheadlines from dataframes
        headlines = process_dataframe_input(headlines_df) if auto_headlines else None
        subheadlines = process_dataframe_input(subheadlines_df) if auto_subheadlines else None
        
        # Determine template path based on campaign type
        template_path = EVERGREEN_USER_PROMPT_PATH if campaign_type == "Evergreen" else PROMO_TEMPLATE_PATH
        
        # Check if template exists
        if not Path(template_path).exists():
            return f"❌ **Error**: Template file not found at {template_path}. Please create the template file.", None, None, None
        
        content_bank = [i.strip() for i in re.split(r'[;,]', content_bank) if i.strip()]
        if angle_and_benefits:
            angle_and_benefits = [i.strip() for i in re.split(r'[;,]', angle_and_benefits) if i.strip()]
        if social_proof:
            social_proof = [i.strip() for i in re.split(r'[;,]', social_proof) if i.strip()]
        
        # Get generator instance
        generator = get_generator()
        
        # Generate the creative briefs
        result = generator.generate_creative_briefs(
            brand_name=brand_name,
            product_name=product_name,
            website_url=website_url or "",
            target_audience=target_audience or "",
            tone=tone or "",
            angle_description=angle_description,
            user_template_path=EVERGREEN_USER_PROMPT_PATH,
            system_template_path=EVERGREEN_SYSTEM_PROMPT_PATH,
            csv_df=csv_df,
            uploaded_images=reference_images,
            headlines=headlines,
            subheadlines=subheadlines,
            social_proof=social_proof if social_proof else None,
            angle_and_benefits=angle_and_benefits,
            num_image_briefs=int(num_image_briefs),
            num_video_briefs=int(num_video_briefs),
            content_bank=content_bank or "",
        )
        
        # Save the result to file
        output_filename = f"{brand_name.lower().replace(' ', '_')}_brief.md"
        saved_path = generator.save_brief_to_file(result, output_filename)
        
        # Create download files
        md_path, txt_path, pdf_path = create_download_files(result, brand_name)
        
        # Format the output with file info
        output_text = f"""
## ✅ Creative Brief Generated Successfully!

**Saved to:** `{saved_path}`

---

{result}
        """
        
        return output_text, md_path, txt_path, pdf_path
        
    except Exception as e:
        error_msg = f"❌ **Error during generation**: {str(e)}"
        print("Generation error:")
        traceback.print_exc()  # Prints the full traceback to stderr
        return error_msg, None, None, None

def generate_gradio_interface():
    """Return the Gradio Blocks interface for Modal deployment"""
    from app.config import UPLOADS_DIR, PROCESSED_DIR, BRIEFS_DIR
    for directory in [UPLOADS_DIR, PROCESSED_DIR, BRIEFS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    # Check and create dummy templates if missing
    template_files = [EVERGREEN_TEMPLATE_PATH, PROMO_TEMPLATE_PATH]
    missing_templates = [t for t in template_files if not Path(t).exists()]
    
    for template in missing_templates:
        Path(template).parent.mkdir(parents=True, exist_ok=True)
        with open(template, 'w') as f:
            f.write("""# Creative Brief Template

Brand: {brand_name}
Product: {product_name}
Angle: {angle_description}

Generate {num_image_briefs} static image briefs and {num_video_briefs} video briefs for this campaign.

Please create detailed creative briefs following the format specified in the assignment requirements.
""")

    demo = build_ui(generate_brief_callback)
    return demo
   
@spaces.GPU
def main():
    """Main function to launch the Gradio app"""
    
    # Create necessary directories
    from app.config import UPLOADS_DIR, PROCESSED_DIR, BRIEFS_DIR
    for directory in [UPLOADS_DIR, PROCESSED_DIR, BRIEFS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Check for required template files
    template_files = [EVERGREEN_TEMPLATE_PATH, PROMO_TEMPLATE_PATH]
    missing_templates = [t for t in template_files if not Path(t).exists()]
    
    if missing_templates:
        print("⚠️  Warning: Missing template files:")
        for template in missing_templates:
            print(f"   - {template}")
        print("Please create these template files before running the application.")
        
        # Create dummy templates for testing
        for template in missing_templates:
            Path(template).parent.mkdir(parents=True, exist_ok=True)
            with open(template, 'w') as f:
                f.write("""# Creative Brief Template

Brand: {brand_name}
Product: {product_name}
Angle: {angle_description}

Generate {num_image_briefs} static image briefs and {num_video_briefs} video briefs for this campaign.

Please create detailed creative briefs following the format specified in the assignment requirements.
""")
        print("✅ Created basic template files for testing.")
    
    # Build and launch the UI
    demo = build_ui(generate_brief_callback)
    
    print("🚀 Starting Creative Brief Generator...")
    print("📝 Loading AI model (this may take a few minutes)...")
    
    # Pre-load the model to show any errors early
    try:
        get_generator()
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("⚠️  The app will still launch, but generation may fail.")
    
    # Launch the app
    demo.launch(
        show_error=True,
        ssr_mode=False
    )

if __name__ == "__main__":
    main()