---
title: Ads4you
sdk: gradio  # or streamlit
app_file: app/main.py
---


# Brief Generator

# 🎨 Creative Brief Generator

**Live App:** [Try it on Hugging Face Spaces 🚀](https://huggingface.co/spaces/Wtvman/Ads4you)

A multi-model AI-powered **Creative Brief Generator** designed for marketers, advertisers, and creatives. Generate compelling, brand-aligned creative briefs for static and video campaigns using structured brand data and reference images — all from a sleek Gradio/Streamlit UI.

---

## 🧠 Models Used

| Purpose | Model |
|--------|-------|
| 🖼️ Image-based Creative Description | `HuggingFaceTB/SmolVLM-Instruct` |
| 📰 Headline/Subheadline Generation | `google/gemma-3-1b-it` |
| 🧾 Creative Brief Writing | `meta-llama/Llama-3.2-3B-Instruct` |

You can click the "Generate Headlines" button as many times as needed for variety.

---

## ✨ Features

- Upload visual references
- Input structured campaign details
- AI-generated headlines & subheadlines
- Dynamic creative brief creation (static + video)
- Multi-format download (TXT, PDF, Markdown)
- Fully powered by open-source models on Hugging Face

---

## 📝 How to Use

1. **Go to the App**  
   [Creative Brief Generator (Live)](https://huggingface.co/spaces/Wtvman/Ads4you)

2. **Enter Campaign Info**
   - Brand Name, Product Name, Website URL
   - Target Audience
   - Tone of Voice, Brand Style
   - Campaign Type (Evergreen or Promo)
   - Upload reference images
   - Provide product benefits, angle, social proof

3. **Generate Headlines/Subheadlines**
   - Click the **Generate Headlines** and **Generate Subheadlines** button
   - You can regenerate for more variations
   - Edit or approve your favorites

4. **Set Brief Parameters**
   - Choose number of **Static Briefs**
   - Choose number of **Video Briefs**

5. **Generate & Download**
   - Click **Generate Brief**
   - Wait ~10 minutes
   - Download briefs in `.txt`, `.pdf`, or `.md`

---

## 🛠️ Tech Stack

### 1. Gradio
Interactive UI built using Gradio with components like:
- `gr.Textbox`, `gr.Image`, `gr.Button`, `gr.File`, `gr.Download`, `gr.State`

### 2. Python Backend
Handles:
- Form logic and session state
- File processing and format conversion
- Multi-model inference pipeline

### 3. Hugging Face Transformers

#### 🖼️ SmolVLM-Instruct (VLM)
- Extracts creative-relevant descriptions from uploaded images
- Outputs mood, visual composition, brand tone alignment

#### 📰 Gemma 3.1B
- Dynamically generates headlines/subheadlines
- Context-aware (brand tone, angle, benefits)
- Regenerable with one click

#### 🧾 LLaMA 3B
- Takes complete form data + VLM + headlines
- Produces structured, industry-grade creative briefs
- Differentiates static vs video campaign briefs

---

## 📤 Export Formats

- `.txt` — Easy to edit
- `.pdf` — Client-ready
- `.md` — Dev-friendly format (ideal for GitHub, Notion, Docs)

---

## ⚙️ Architecture

```plaintext
User Input
   ↓
Gradio Interface
   ↓
Form State Manager
   ↓
Multi-Model Inference Pipeline
   ↓
Brief Generator
   ↓
Multi-Format Export

---

## Models work in the following pipeline:

VLM (SmolVLM-Instruct) — Image analysis

Gemma — Headline & subheadline generation

LLaMA — Final creative brief writing

