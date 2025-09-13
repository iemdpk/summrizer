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
from component.db import client

# A function to extract text from a PDF file
def extract_pdf_text(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

@st.dialog("Enter Your Email Address")
def email_dialog():
    """Dialog for collecting user email and processing PDF"""
    st.write("Please enter your email to receive the summary.")
    
    with st.form("email_form"):
        user_email = st.text_input(
            "Email", 
            placeholder="you@example.com",
            help="We'll send the summary to this email address"
        )
        submit_button = st.form_submit_button("Submit & Summarize")
        
        if submit_button:
            if user_email and "@" in user_email:
                try:
                    # Get the uploaded file from session state
                    pdf_file = BytesIO(st.session_state.uploaded_file_data)
                    extracted_text = extract_pdf_text(pdf_file)
                    
                    if extracted_text:
                        # Save to database
                        insert_result = client["llm"]["chat"].insert_one({
                            "task": extracted_text,
                            # "context": "Summarize the document into a concise summary highlighting key objectives",
                            # "required": "Provide a short, clear summary suitable for quick review.",
                            "context": "Analyze the extracted document text and generate a concise summary formatted as an HTML fragment with inline CSS, suitable for embedding directly into an email. Focus on the main objectives, key insights, and essential takeaways.",
                            "required": "Return only an HTML fragment (no markdown, no code fences). Structure: <div style=\"font-family: Arial, sans-serif; line-height: 1.6; color: #333;\"> containing: (1) a heading <h2 style=\"color:#2c3e50; font-size:18px;\"> with a one-line executive summary, (2) a short paragraph <p style=\"margin:8px 0;\"> with 1–2 sentence overview, (3) an unordered list <ul style=\"margin:8px 0; padding-left:18px;\"> of 3–5 concise key findings, and (4) a paragraph <p style=\"margin:8px 0; font-weight:bold;\"> with a one-line actionable recommendation. Keep it short (80–200 words).",
                            "email": user_email,
                            "filename": st.session_state.uploaded_file_name,
                            "status": False,
                            "timestamp": datetime.now(),
                            "sendEmail":False,
                        })
                        
                        st.success(f"✅ File uploaded successfully!")
                        st.info(f"📧 Summary will be sent to **{user_email}** shortly.")
                        
                        # Clean up session state
                        del st.session_state.uploaded_file_data
                        del st.session_state.uploaded_file_name
                        
                        time.sleep(2)
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
            else:
                st.warning("⚠️ Please enter a valid email address.")

# The main dashboard function
def dashboard():
    st.set_page_config(
        page_title="PDF Summarizer", 
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="📄"
    )
    
    # Create directories
    for dir_name in ["summaries", "uploads"]:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    
    # Initialize session state
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    
    # Sidebar stats
    with st.sidebar:
        st.header("📊 Quick Stats")
        summary_files = [f for f in os.listdir("summaries") if f.endswith("_summary.txt")]
        total_summaries = len(summary_files)
        
        st.metric("📄 Total Summaries", total_summaries)
        st.metric("📅 Files Today", len(st.session_state.processed_files))
        st.metric("🎯 Success Rate", "100%")
        st.divider()
        st.caption("Real-time analytics")
    
    # Main content
    st.title("📄 PDF Summarizer")
    st.markdown("Upload your PDF documents and get AI-powered summaries delivered to your email.")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Total Summaries", f"{total_summaries:,}")
    with col2:
        st.metric("💬 Processing Queue", "0")
    with col3:
        st.metric("📊 Avg Compression", "75%")
    with col4:
        st.metric("⏱️ Avg Time", "2 min")
    
    st.divider()
    
    # File upload section
    st.subheader("📤 Upload Document for Summarization")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF file to extract its text content and generate a summary",
        accept_multiple_files=False
    )
    
    # Handle file upload
    if uploaded_file is not None:
        st.session_state.uploaded_file_data = uploaded_file.getvalue()
        st.session_state.uploaded_file_name = uploaded_file.name
        
        # Show file info
        file_size = len(uploaded_file.getvalue()) / 1024  # KB
        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully ({file_size:.1f} KB)")
        
        # Show email dialog
        email_dialog()
    
    # Recent summaries section
    st.divider()
    st.subheader("📋 Recent Activity")
    
    if st.session_state.processed_files:
        for i, file_info in enumerate(reversed(st.session_state.processed_files[-5:])):
            with st.expander(f"📄 {file_info['name']} - {file_info['timestamp'].strftime('%H:%M:%S')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {file_info['email']}")
                    st.write(f"**Status:** ✅ Processed")
                with col2:
                    st.write(f"**Size:** {file_info['size']:.1f} KB")
                    st.write(f"**Time:** {file_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("No files processed yet. Upload a PDF to get started!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <small>Powered by AI • Secure & Fast Processing • Email Delivery</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard()
