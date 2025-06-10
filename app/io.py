import pandas as pd
from typing import List, Optional, Union, Dict, Any
import os
import shutil
from pathlib import Path
import zipfile
import requests
from urllib.parse import urlparse
import re
import spaces

def flatten_dataframe(df: pd.DataFrame) -> List[str]:
    """Flatten a dataframe to a list of non-empty strings"""
    return [str(cell).strip() for row in df.values for cell in row if pd.notna(cell) and str(cell).strip()]

def parse_csv_file(file_obj) -> Optional[pd.DataFrame]:
    """Safely load a CSV file from Gradio's file input"""
    if file_obj is None:
        return None
    try:
        return pd.read_csv(file_obj.name)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

def process_swipe_csv(csv_df: pd.DataFrame) -> str:
    """
    Process the swipe CSV and format it for the LLaVA model.
    Expected columns: Creative Concept Names, Short Description, Content Requirements Per Variant, Format, Reference Image
    """
    if csv_df is None or csv_df.empty:
        return ""
    
    formatted_data = "Reference Menu CSV Data:\n\n"
    
    for idx, row in csv_df.iterrows():
        concept_name = row.get('Creative Concept Names', 'N/A')
        description = row.get('Short Description', 'N/A')
        content_req = row.get('Content Requirements Per Variant', 'N/A')
        format_type = row.get('Format', 'N/A')
        reference_image = row.get('Reference Image', 'N/A')
        
        formatted_data += f"Concept {idx + 1}:\n"
        formatted_data += f"- Name: {concept_name}\n"
        formatted_data += f"- Description: {description}\n"
        formatted_data += f"- Content Requirements: {content_req}\n"
        formatted_data += f"- Format: {format_type}\n"
        formatted_data += f"- Reference Image URL: {reference_image}\n\n"
    
    return formatted_data

def extract_image_urls_from_csv(csv_df: pd.DataFrame) -> List[str]:
    """Extract all image URLs from the CSV Reference Image column"""
    if csv_df is None or csv_df.empty:
        return []
    
    urls = []
    if 'Reference Image' in csv_df.columns:
        for url in csv_df['Reference Image'].dropna():
            if isinstance(url, str) and url.strip():
                # Handle Google Drive links and convert to direct download links
                url = convert_google_drive_url(url.strip())
                urls.append(url)
    
    return urls

def convert_google_drive_url(url: str) -> str:
    """Convert Google Drive sharing URL to direct download URL"""
    if 'drive.google.com' in url:
        # Extract file ID from various Google Drive URL formats
        file_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if file_id_match:
            file_id = file_id_match.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

def download_image_from_url(url: str, save_dir: str = "data/processed/images") -> Optional[str]:
    """Download image from URL and save locally"""
    try:
        os.makedirs(save_dir, exist_ok=True)
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Extract filename from URL or generate one
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename or '.' not in filename:
            filename = f"image_{hash(url) % 10000}.jpg"
        
        save_path = os.path.join(save_dir, filename)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return save_path
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None

def save_uploaded_files(files: Union[List, None], output_dir: str = "data/raw") -> List[str]:
    """Save uploaded files (like images or PDFs) and return paths"""
    if not files:
        return []

    os.makedirs(output_dir, exist_ok=True)
    saved_paths = []

    # Handle both single file and list of files
    if not isinstance(files, list):
        files = [files]

    for file in files:
        try:
            if hasattr(file, 'name'):  # Gradio file object
                filename = os.path.basename(file.name)
                save_path = os.path.join(output_dir, filename)
                shutil.copy(file.name, save_path)
                saved_paths.append(save_path)
            else:  # String path
                filename = os.path.basename(file)
                save_path = os.path.join(output_dir, filename)
                shutil.copy(file, save_path)
                saved_paths.append(save_path)
        except Exception as e:
            print(f"Error saving file {file}: {e}")

    return saved_paths

def extract_zip_assets(zip_path: str, extract_dir: str = "data/processed/unzipped") -> List[str]:
    """Extract contents of a ZIP file"""
    extracted_files = []
    try:
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
            extracted_files = [str(p) for p in Path(extract_dir).rglob("*") if p.is_file()]
    except Exception as e:
        print(f"Error extracting ZIP: {e}")
    return extracted_files

def prepare_reference_images(uploaded_images: List, csv_image_urls: List[str]) -> List[str]:
    """
    Prepare all reference images (uploaded + from CSV) for the model.
    Returns list of local image paths.
    """
    all_image_paths = []
    
    # Handle uploaded images
    if uploaded_images:
        uploaded_paths = save_uploaded_files(uploaded_images, "data/processed/uploaded_images")
        all_image_paths.extend(uploaded_paths)
    
    # Handle CSV image URLs
    for url in csv_image_urls:
        local_path = download_image_from_url(url)
        if local_path:
            all_image_paths.append(local_path)
    
    return all_image_paths

def validate_image_file(filepath: str) -> bool:
    """Validate if file is a supported image format"""
    supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return any(filepath.lower().endswith(fmt) for fmt in supported_formats)