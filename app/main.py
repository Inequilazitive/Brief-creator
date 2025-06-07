import gradio as gr
import pandas as pd
from pathlib import Path
from app.generator import get_generator
from app.io import parse_csv_file
from app.config import EVERGREEN_TEMPLATE_PATH, PROMO_TEMPLATE_PATH
from app.ui import build_ui

def process_dataframe_input(df_data):
    """Convert Gradio dataframe input to list format"""
    if df_data is None or len(df_data) == 0:
        return None
    
    # Extract the first row of data (flatten nested lists if needed)
    row_data = df_data[0] if isinstance(df_data[0], list) else df_data
    # Filter out empty strings and None values
    return [item for item in row_data if item and str(item).strip()]

def generate_brief_callback(
    brand_name, product_name, website_url, target_audience, tone,
    campaign_type, swipe_csv, reference_images,
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
            return "❌ **Error**: Please fill in Brand Name, Product Name, and Angle Description."
        
        # Process CSV file
        csv_df = None
        if swipe_csv is not None:
            csv_df = parse_csv_file(swipe_csv)
            if csv_df is None:
                return "❌ **Error**: Could not parse the uploaded CSV file."
        
        # Process headlines and subheadlines from dataframes
        headlines = process_dataframe_input(headlines_df) if auto_headlines else None
        subheadlines = process_dataframe_input(subheadlines_df) if auto_subheadlines else None
        
        # Determine template path based on campaign type
        template_path = EVERGREEN_TEMPLATE_PATH if campaign_type == "Evergreen" else PROMO_TEMPLATE_PATH
        
        # Check if template exists
        if not Path(template_path).exists():
            return f"❌ **Error**: Template file not found at {template_path}. Please create the template file."
        
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
            template_path=str(template_path),
            csv_df=csv_df,
            uploaded_images=reference_images,
            headlines=headlines,
            subheadlines=subheadlines,
            social_proof=[social_proof] if social_proof else None,
            angle_and_benefits=angle_and_benefits,
            num_image_briefs=int(num_image_briefs),
            num_video_briefs=int(num_video_briefs)
        )
        
        # Save the result to file
        output_filename = f"{brand_name.lower().replace(' ', '_')}_brief.md"
        saved_path = generator.save_brief_to_file(result, output_filename)
        
        # Format the output with file info
        output_text = f"""
## ✅ Creative Brief Generated Successfully!

**Saved to:** `{saved_path}`

---

{result}
        """
        
        return output_text
        
    except Exception as e:
        error_msg = f"❌ **Error during generation**: {str(e)}"
        print(f"Generation error: {e}")
        return error_msg

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
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )

if __name__ == "__main__":
    main()