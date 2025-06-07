import gradio as gr
from app.form_models import generate_headlines, generate_subheadlines

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

        with gr.Accordion("📌 Angle + Content Input", open=True):
            campaign_type = gr.Radio(["Evergreen", "Promo"], label="Campaign Type")
            swipe_csv = gr.File(label="Upload Swipe CSV", file_types=[".csv"])
            reference_images = gr.File(label="Upload Reference Images", file_types=[".png", ".jpg", ".jpeg"], file_count="multiple")

            angle_description = gr.Textbox(label="Angle Description", lines=3, placeholder="e.g., Emphasize natural air purification without harsh chemicals.")
            angle_and_benefits = gr.Textbox(label="Angle Summary with Benefits (Optional)", lines=3, placeholder="e.g., Azuna purifies air with plant-based technology...")

            gr.Markdown("### 🔤 Headlines")
            headlines_df = gr.Dataframe(headers=["Headline 1", "Headline 2", "Headline 3"], row_count=1, col_count=3, label="Headline Examples")
            auto_headlines = gr.Checkbox(label="Auto-generate Headlines", value=True)
            regenerate_headlines_btn = gr.Button("🔁 Regenerate Headlines", visible=False)

            gr.Markdown("### 🧾 Subheadlines")
            subheadlines_df = gr.Dataframe(headers=["Subheadline 1", "Subheadline 2"], row_count=1, col_count=2, label="Subheadline Examples")
            auto_subheadlines = gr.Checkbox(label="Auto-generate Subheadlines", value=True)
            regenerate_subheadlines_btn = gr.Button("🔁 Regenerate Subheadlines", visible=False)

            social_proof = gr.Textbox(label="Social Proof (Optional)", lines=2, placeholder="e.g., 10,000+ happy customers")

            brand_guide = gr.File(label="Upload Brand Guide", file_types=[".pdf"])
            campaign_deck = gr.File(label="Upload Campaign Deck", file_types=[".pdf", ".ppt", ".pptx"])
            misc_assets = gr.File(label="Upload Misc Assets", file_types=[".zip", ".pdf", ".ppt", ".pptx", ".doc", ".docx"], file_count="multiple")

        with gr.Accordion("⚙️ Output Settings", open=True):
            num_image_briefs = gr.Slider(label="Number of Static Briefs", minimum=1, maximum=20, value=10, step=1)
            num_video_briefs = gr.Slider(label="Number of Video Briefs", minimum=1, maximum=20, value=10, step=1)

        generate_btn = gr.Button("🚀 Generate Prompt")
        output_markdown = gr.Markdown("### Prompt Output will appear here...")

        # Auto-generate on checkbox
        auto_headlines.change(
            fn=lambda checked, brand, angle: (
                gr.update(visible=True if checked else False),
                generate_headlines(brand, angle) if checked and brand and angle else gr.update()
            ),
            inputs=[auto_headlines, brand_name, angle_description],
            outputs=[regenerate_headlines_btn, headlines_df],
        )


        auto_subheadlines.change(
            fn=lambda checked, brand, angle: (
                gr.update(visible=True if checked else False),
                generate_subheadlines(brand, angle) if checked and brand and angle else gr.update()
            ),
            inputs=[auto_subheadlines, brand_name, angle_description],
            outputs=[regenerate_subheadlines_btn, subheadlines_df],
        )

        # Regenerate buttons
        regenerate_headlines_btn.click(
            fn=lambda brand, angle, checkbox: generate_headlines(brand, angle) if checkbox and brand and angle else gr.update(),
            inputs=[brand_name, angle_description, auto_headlines],
            outputs=headlines_df,
        )

        regenerate_subheadlines_btn.click(
            fn=lambda brand, angle, checkbox: generate_subheadlines(brand, angle) if checkbox and brand and angle else gr.update(),
            inputs=[brand_name, angle_description, auto_subheadlines],
            outputs=subheadlines_df,
        )

        # Final prompt generation
        generate_btn.click(
            generate_callback,
            inputs=[
                brand_name, product_name, website_url, target_audience, tone,
                campaign_type, swipe_csv, reference_images,
                angle_description, angle_and_benefits,
                headlines_df, auto_headlines,
                subheadlines_df, auto_subheadlines,
                social_proof, voiceover_tone,
                num_image_briefs, num_video_briefs,
                brand_guide, campaign_deck, misc_assets
            ],
            outputs=output_markdown
        )

    return demo