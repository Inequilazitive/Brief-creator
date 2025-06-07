from app.prompts import PromptBuilder
from app.generate import generate_response
from app.io import export_brief_files

def run_generator(all_inputs):
    prompt_builder = PromptBuilder()
    prompt = prompt_builder.build_prompt(**all_inputs)

    # Pass prompt to model
    response = generate_response(prompt, model="blip")  # Replace with actual model

    # Save outputs
    paths = export_brief_files(response, format="md_pdf_zip")

    return response, paths
