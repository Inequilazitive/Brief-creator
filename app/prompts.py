import pandas as pd
import re
from typing import Optional, List, Dict, Any

class PromptBuilder:
    def __init__(self, template_path: str):
        """Initialize with the path to the prompt template file."""
        self.template_path = template_path
        self.base_template = self._load_template()

    def _load_template(self) -> str:
        """Load the base prompt template from file."""
        with open(self.template_path, "r", encoding="utf-8") as f:
            return f.read()

    def build_prompt(
        self,
        brand_name: str,
        website_url: str,
        product_name: str,
        target_audience: str,
        tone: str,
        angle_description: str,
        headlines: Optional[List[str]] = None,
        subheadlines: Optional[List[str]] = None,
        customer_reviews: Optional[str] = None,
        benefits: Optional[List[str]] = None,
        pain_points: Optional[List[str]] = None,
        social_proof: Optional[List[str]] = None,
        content_bank: Optional[List[str]] = None,
        voiceover_tone: Optional[str] = None,
        angle_and_benefits: Optional[str] = None,
        num_image_briefs: int = 10,
        num_video_briefs: int = 10,
        csv_data: Optional[str] = None,
        reference_image_description: Optional[str] = None,
    ) -> str:
        """
        Build the complete prompt by formatting the template and removing unavailable sections.
        """
        prompt = self.base_template

        # Replace placeholders with actual values
        prompt = self._replace_placeholders(prompt, {
            'brand_name': brand_name,
            'website_url': website_url,
            'product_name': product_name,
            'target_audience': target_audience,
            'tone': tone,
            'angle_description': angle_description,
            'num_image_briefs': num_image_briefs,
            'num_video_briefs': num_video_briefs,
            'angle_and_benefits': angle_and_benefits if angle_and_benefits else '',
            'reference_image_description': reference_image_description if reference_image_description else '',
        })

        # Format list sections
        prompt = self._format_headlines_section(prompt, headlines)
        prompt = self._format_subheadlines_section(prompt, subheadlines)
        prompt = self._format_customer_reviews_section(prompt, customer_reviews)
        prompt = self._format_benefits_section(prompt, benefits)
        prompt = self._format_social_proof_section(prompt, social_proof)
        prompt = self._format_content_bank_section(prompt, content_bank)

        # Add CSV data if provided
        if csv_data:
            prompt = self._add_csv_data_section(prompt, csv_data)

        # Clean up any remaining placeholder sections
        prompt = self._clean_empty_sections(prompt)

        return prompt

    def _replace_placeholders(self, prompt: str, replacements: Dict[str, Any]) -> str:
        """Replace placeholder values in the prompt."""
        for key, value in replacements.items():
            placeholder = '{' + key + '}'
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
        return prompt

    def _format_headlines_section(self, prompt: str, headlines: Optional[List[str]]) -> str:
        """Format or remove ONLY the 'Headlines Options' section, preserving the rest."""
        if not headlines:
            # Safely remove just the 'Headlines Options' section if no headlines are given
            prompt = re.sub(
                r'(Headlines Options:\n)(.*?)(\n(?:\w|[A-Z][a-z]+|Subheadline|Benefits|Social|Content|$))',
                r'\3',  # preserve the following section header
                prompt,
                flags=re.DOTALL
            )
            return prompt

        # Only the lines, not the section title
        headlines_lines = ""
        for i, headline in enumerate(headlines, 1):
            headlines_lines += f"[Headline {i}] {headline}\n"

        # Replace existing section if present
        if "Headlines Options:" in prompt:
            prompt = re.sub(
                r'(Headlines Options:\n)(.*?)(\n(?:\w|[A-Z][a-z]+|Subheadline|Benefits|Social|Content|$))',
                r'\1' + headlines_lines.strip() + r'\3',
                prompt,
                flags=re.DOTALL
            )
        else:
            # No section exists – insert before Subheadline/Explainer Options or Benefits or Content Bank
            insert_point = re.search(r'(?=\nSubheadline|Benefits of the product|Social Proof|Content Bank)', prompt)
            if insert_point:
                idx = insert_point.start()
                prompt = prompt[:idx] + "\nHeadlines Options:\n" + headlines_lines.strip() + "\n" + prompt[idx:]
            else:
                # Fallback: append at the end
                prompt += "\nHeadlines Options:\n" + headlines_lines.strip()

        return prompt

    def _format_subheadlines_section(self, prompt: str, subheadlines: Optional[List[str]]) -> str:
        """Format or remove the subheadlines section."""
        if not subheadlines:
            prompt = re.sub(
                r'Subheadline/Explainer Options.*?(?=\n\n|\n[A-Z]|\nCustomer|\nBenefits|\nSocial|\nContent|$)',
                '',
                prompt,
                flags=re.DOTALL
            )
            return prompt

        subheadlines_text = "Subheadline/Explainer Options (often Explainer type lines):\n"
        for i, subheadline in enumerate(subheadlines, 1):
            subheadlines_text += f"[Subheadline {i}] {subheadline}\n"

        prompt = re.sub(
            r'Subheadline/Explainer Options.*?(?=\n\n|\n[A-Z]|\nCustomer|\nBenefits|\nSocial|\nContent|$)',
            subheadlines_text.strip(),
            prompt,
            flags=re.DOTALL
        )

        return prompt

    def _format_customer_reviews_section(self, prompt: str, customer_reviews: Optional[str]) -> str:
        """Format or remove the customer reviews section."""
        if not customer_reviews:
            prompt = re.sub(
                r'Customer Reviews for.*?(?=\n\n|\n[A-Z]|\nBenefits|\nSocial|\nContent|$)',
                '',
                prompt,
                flags=re.DOTALL
            )
            return prompt

        reviews_text = f"Customer Reviews for [Angle]: \n{customer_reviews}"
        prompt = re.sub(
            r'Customer Reviews for.*?(?=\n\n|\n[A-Z]|\nBenefits|\nSocial|\nContent|$)',
            reviews_text,
            prompt,
            flags=re.DOTALL
        )

        return prompt

    def _format_benefits_section(self, prompt: str, benefits: Optional[List[str]]) -> str:
        """Format or remove the benefits section."""
        if not benefits:
            prompt = re.sub(
                r'Benefits of the product.*?(?=\n\n|\n[A-Z]|\nSocial|\nContent|$)',
                '',
                prompt,
                flags=re.DOTALL
            )
            return prompt

        benefits_text = "Benefits of the product for this angle:\n"
        for i, benefit in enumerate(benefits, 1):
            benefits_text += f"[Benefit {i}] {benefit}\n"

        prompt = re.sub(
            r'Benefits of the product.*?(?=\n\n|\n[A-Z]|\nSocial|\nContent|$)',
            benefits_text.strip(),
            prompt,
            flags=re.DOTALL
        )

        return prompt

    def _format_social_proof_section(self, prompt: str, social_proof: Optional[List[str]]) -> str:
        """Format or remove the social proof section."""
        if not social_proof:
            prompt = re.sub(
                r'Social Proof Points.*?(?=\n\n|\n[A-Z]|\nContent|$)',
                '',
                prompt,
                flags=re.DOTALL
            )
            return prompt

        social_proof_text = "Social Proof Points (# of customers, PR logos, or very notable PR quotes, any other social proof points)\n"
        for i, proof in enumerate(social_proof, 1):
            social_proof_text += f"Social proof point {i}: {proof}\n"

        prompt = re.sub(
            r'Social Proof Points \(# of customers, PR logos,.*?(?=\n\n|\n[A-Z]|\nContent|$)',
            social_proof_text.strip(),
            prompt,
            flags=re.DOTALL
        )

        return prompt

    def _format_content_bank_section(self, prompt: str, content_bank: Optional[List[str]]) -> str:
        """Format the content bank section."""
        if not content_bank:
            # Use default content bank from template
            return prompt

        content_bank_text = "Content Bank - Please limit your visual recommendations to the following types of content, and anything that deviates from this list must only be very realistically accessible stock images/videos:\n"
        for content_type in content_bank:
            content_bank_text += f"{content_type}\n"

        prompt = re.sub(
            r'Content Bank - Please limit.*?(?=\n\nAI Prompt Output|$)',
            content_bank_text.strip(),
            prompt,
            flags=re.DOTALL
        )

        return prompt


    def _add_csv_data_section(self, prompt: str, csv_data: str) -> str:
        """Add CSV data section to the prompt after a specific reference sentence."""

        csv_section = f"\n\nReference Menu CSV Data:\n{csv_data}\n"

        # Define the marker sentence (or part of it if you want to be more flexible)
        marker = (
            "Also attached is a CSV file for the Reference Menu of the same ad creative style names "
            "as the image, but with a proper description and content requirements per brief"
        )

        if marker in prompt:
            # Insert the csv_section right after the marker sentence
            prompt = prompt.replace(marker, marker + csv_section)
        else:
            # Fallback: just append it at the end
            prompt += csv_section

        return prompt


    def _clean_empty_sections(self, prompt: str) -> str:
        """Clean up any remaining empty sections or multiple newlines."""
        # Remove multiple consecutive newlines
        prompt = re.sub(r'\n{3,}', '\n\n', prompt)
        
        return prompt.strip()

def create_ad_brief_prompt(
    brand_name: str,
    template_path: str = "templates/evergreen_template.txt",
    **kwargs
) -> str:
    """
    Convenience function to create an ad brief prompt.
    Args:
        brand_name: Name of the brand
        template_path: Path to the prompt template file
        **kwargs: All other optional parameters for the prompt
    Returns:
        Formatted prompt string
    """
    builder = PromptBuilder(template_path)
    return builder.build_prompt(brand_name=brand_name, **kwargs)