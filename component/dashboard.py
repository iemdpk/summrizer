import streamlit as st
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import PyPDF2
from io import BytesIO
from component.db import client
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def extract_pdf_text(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Initialize text variable
        text = ""
        
        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
        
        return text
    
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None
    
    
    save_analytics_data(analytics)


def advanced_summarizer(text):
    """Enhanced summarizer with token counting"""
    sentences = text.split('. ')
    
    # Simple extractive summarization
    if len(sentences) <= 3:
        return text
    
    # Take first sentence, middle sentence, and last sentence
    summary_sentences = [
        sentences[0],
        sentences[len(sentences)//2],
        sentences[-1]
    ]
    
    summary = '. '.join(summary_sentences)
    return summary + '.' if not summary.endswith('.') else summary

def dashboard():
    # -----------------------
    # Setup & Configuration
    # -----------------------
    st.set_page_config(
        page_title="AI Summarizer Dashboard", 
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🤖"
    )
    
    # Custom CSS for Streamlit native styling
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Metric styling with borders */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 2px solid #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    div[data-testid="metric-container"] > div {
        width: fit-content;
        margin: auto;
    }
    
    div[data-testid="metric-container"] > div > div {
        width: fit-content;
        margin: auto;
    }
    
    /* Upload area styling */
    .uploadedFile {
        border: 2px dashed #ff4b4b;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #fafafa;
    }
    
    /* Success box styling */
    .element-container .stSuccess {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
    }
    
    /* Info box styling */
    .element-container .stInfo {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 8px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create directories first
    for dir_name in ["summaries", "uploads"]:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    
    # Load analytics
   
    
    # -----------------------
    # Sidebar (must come before main content)
    # -----------------------
    with st.sidebar:
        st.header("📊 Quick Stats")
        summary_files = [f for f in os.listdir("summaries") if f.endswith("_summary.txt")]
        total_summaries = len(summary_files)
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_stats = 0
        files_today = 0
        
        st.metric("📄 Total Summaries", total_summaries)
        st.metric("📅 Files Today", files_today)
        
        st.metric("🎯 Compression", "0%")
        
        st.divider()
        st.caption("Real-time analytics")
    
    st.title("🤖 AI Summarizer Dashboard")
    
    # Key Metrics Row with borders (using native st.metric)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Summaries", f"{total_summaries:,}",border=True)
    
    with col2:
        st.metric("💬 Words Saved", "0",border=True)
    
    with col3:
        st.metric("📊 Avg Compression", "0%",border=True)
    
    with col4:
        st.metric("📅 This Week", f"0",border=True)
    
    st.subheader("📤 Upload Document for Summarization")
    uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type="pdf",
    help="Upload a PDF file to extract its text content"
)
    
    if uploaded_file is not None:
        st.info(f"**File:** {uploaded_file.name} | **Size:** {uploaded_file.size} bytes")
        with st.spinner("Extracting text from PDF..."):
            # Extract text from PDF
            extracted_text = extract_pdf_text(uploaded_file)
            # Display statistics
            st.subheader("📊 PDF Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Characters", len(extracted_text),border=True)
            
            with col2:
                word_count = len(extracted_text.split())
                st.metric("Total Words", word_count,border=True)
            
            with col3:
                page_count = len(PyPDF2.PdfReader(uploaded_file).pages)
                st.metric("Total Pages", page_count,border=True)        
            
            st.info("We are getting ready to summarize your document!")
            st.info("We email you when your summary is ready.")

            insert = client["llm"]["chat"].insert_one({
                "task": extracted_text,
                "context": "Summarize the document into a concise summary highlighting key objectives",
                "required": "Provide a short, clear summary of the RFP suitable for quick review by management.",
                "status": False,
            })

    # Dummy dataframe
    df = pd.DataFrame({
        "Filename": ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
        "Tokens Generated": [120, 300, 450],
        "Total Tokens": [500, 1200, 2000]
    })

    st.title("📄 PDF Summarizer Token Report")

    # Render rows with inline download button
    for i, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

        # Display row values
        col1.write(row["Filename"])
        col2.write(row["Tokens Generated"])
        col3.write(row["Total Tokens"])

        # Convert row to CSV
        row_df = pd.DataFrame([row])
        csv = row_df.to_csv(index=False).encode("utf-8")

        # Download button
        col4.download_button(
            label="⬇️ Download",
            data=csv,
            file_name=f"{row['Filename'].replace('.pdf','')}_report.csv",
            mime="text/csv",
            key=f"download_{i}"
        )

