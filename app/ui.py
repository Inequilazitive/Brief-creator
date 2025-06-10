import gradio as gr
from app.form_models import generate_headlines, generate_subheadlines
import spaces

def build_ui(generate_callback):
    with gr.Blocks() as demo:
        gr.Markdown("# 📄 Creative Brief Generator")

        with gr.Accordion("📝 Brief Info", open=True):
            brand_name = gr.Text(label="Brand Name", placeholder="e.g., Azuna Fresh", interactive=True)
            product_name = gr.Text(label="Product Name", placeholder="e.g., Natural Air Purifier", interactive=True)
            website_url = gr.Text(label="Website URL (Optional)", placeholder="https://...", interactive=True)
            target_audience = gr.Text(label="Target Audience (Optional)", placeholder="e.g., New moms, pet owners", interactive=True)
            voiceover_tone = gr.Text(label="Voiceover Tone (Optional)", placeholder="e.g., Calm and friendly", interactive=True)
            tone = gr.Text(label="Brand Tone or Style", placeholder="e.g., Clean, natural, friendly", interactive=True)
            content_bank = gr.Text(label="Content Bank (Optional)", placeholder="e.g., Previous ad copy, brand messaging", interactive=True)
        
        with gr.Accordion("📌 Angle + Content Input", open=True):
            campaign_type = gr.Radio(["Evergreen", "Promo"], label="Campaign Type")
            swipe_csv = gr.File(label="Upload Swipe CSV", file_types=[".csv"])
            reference_images = gr.File(label="Upload Reference Images", file_types=[".png", ".jpg", ".jpeg"], file_count="multiple")

            angle_description = gr.Textbox(label="Angle Description", lines=3, placeholder="e.g., Emphasize natural air purification without harsh chemicals.")
            angle_and_benefits = gr.Textbox(label="Product Benefits with this angle", lines=3, placeholder="e.g., Azuna purifies air with plant-based technology...")

            gr.Markdown("### 🔤 Headlines")
            generate_headlines_btn = gr.Button("🪄 Generate Headlines")
            headlines_df = gr.Dataframe(headers=["Headline"], label="Headline Examples", interactive=True)

            gr.Markdown("### 🧾 Subheadlines")
            generate_subheadlines_btn = gr.Button("🪄 Generate Subheadlines")
            subheadlines_df = gr.Dataframe(headers=["Subheadline"], label="Subheadline Examples", interactive=True)

            social_proof = gr.Textbox(label="Social Proof (Optional)", lines=2, placeholder="e.g., 10,000+ happy customers")

            brand_guide = gr.File(label="Upload Brand Guide", file_types=[".pdf"])
            campaign_deck = gr.File(label="Upload Campaign Deck", file_types=[".pdf", ".ppt", ".pptx"])
            misc_assets = gr.File(label="Upload Misc Assets", file_types=[".zip", ".pdf", ".ppt", ".pptx", ".doc", ".docx"], file_count="multiple")

        with gr.Accordion("⚙️ Output Settings", open=True):
            num_image_briefs = gr.Slider(label="Number of Static Briefs", minimum=1, maximum=20, value=10, step=1)
            num_video_briefs = gr.Slider(label="Number of Video Briefs", minimum=1, maximum=20, value=10, step=1)

        generate_btn = gr.Button("🚀 Generate Brief", variant="primary")
        
        # Output section
        output_markdown = gr.Markdown("### Brief Output will appear here...")
        
        # Download section - initially hidden
        with gr.Row(visible=False) as download_row:
            gr.Markdown("### 📥 Download Your Brief")
            with gr.Column():
                download_md = gr.File(label="📄 Download Markdown (.md)", visible=False)
                download_txt = gr.File(label="📄 Download Text (.txt)", visible=False)
                download_pdf = gr.File(label="📄 Download PDF (.pdf)", visible=False)

        # Hidden state to store file paths
        md_file_state = gr.State()
        txt_file_state = gr.State()
        pdf_file_state = gr.State()

        # Headline/Subheadline generation callbacks
        generate_headlines_btn.click(
            fn=lambda brand, angle: (
                generate_headlines(brand, angle) if brand and angle else gr.update()
            ),
            inputs=[brand_name, angle_description],
            outputs=headlines_df,
        )

        generate_subheadlines_btn.click(
            fn=lambda brand, angle: (
                generate_subheadlines(brand, angle) if brand and angle else gr.update()
            ),
            inputs=[brand_name, angle_description],
            outputs=subheadlines_df,
        )

        # Final prompt generation with download functionality
        def handle_generation_and_downloads(*args):
            # Call the original generate callback
            result = generate_callback(*args)
            
            if isinstance(result, tuple) and len(result) == 4:
                output_text, md_path, txt_path, pdf_path = result
                
                # If generation was successful and files were created
                if md_path and txt_path and pdf_path:
                    return (
                        output_text,
                        gr.update(visible=True),  # Show download row
                        gr.update(value=md_path, visible=True),  # MD download
                        gr.update(value=txt_path, visible=True),  # TXT download
                        gr.update(value=pdf_path, visible=True),  # PDF download
                        md_path,  # Store in state
                        txt_path,  # Store in state
                        pdf_path   # Store in state
                    )
                else:
                    # Generation failed
                    return (
                        output_text,
                        gr.update(visible=False),  # Hide download row
                        gr.update(visible=False),  # Hide MD download
                        gr.update(visible=False),  # Hide TXT download
                        gr.update(visible=False),  # Hide PDF download
                        None, None, None  # Clear states
                    )
            else:
                # Handle old format or errors
                return (
                    result if isinstance(result, str) else "Error occurred",
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    None, None, None
                )

        generate_btn.click(
            handle_generation_and_downloads,
            inputs=[
                brand_name, product_name, website_url, target_audience, tone,
                content_bank, campaign_type, swipe_csv, reference_images,
                angle_description, angle_and_benefits,
                headlines_df, gr.State(True),  # always treat as auto_headlines = True
                subheadlines_df, gr.State(True),  # always treat as auto_subheadlines = True
                social_proof, voiceover_tone,
                num_image_briefs, num_video_briefs,
                brand_guide, campaign_deck, misc_assets
            ],
            outputs=[
                output_markdown,
                download_row,
                download_md,
                download_txt,
                download_pdf,
                md_file_state,
                txt_file_state,
                pdf_file_state
            ]
        )

    return demo