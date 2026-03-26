Universal Translator 🌍
A high-performance, Streamlit-powered translation suite that handles everything from quick phrases to massive documents. Built with reliability in mind, it utilizes a dual-engine approach to ensure your translations never fail.
🚀 Features
Smart Translation: Support for all Google Translate languages with Auto-Detection capabilities.
Document Processing: Upload and translate .txt, .pdf, and .docx files instantly.
Dual-Engine Reliability: Uses googletrans with a deep-translator fallback for maximum uptime.
Audio Support: Integrated Text-to-Speech (TTS) for both source and translated text.
Large Text Handling: Intelligent chunking to process long-form content without hitting API limits.
Session History: Keep track of your recent translations in the sidebar during your session.
Export Ready: Download your results as clean text files.
🛠️ Tech Stack
Frontend: Streamlit
Translation Engines: googletrans, deep-translator
Document Parsing: PyPDF2, python-docx
Audio: gTTS
📦 Installation
Clone the repository:
bash
git clone https://github.com
cd UniversalTranslator-Python-Project
Use code with caution.

Install dependencies:
bash
pip install -r requirements.txt
Use code with caution.

Run the app:
bash
streamlit run app.py
Use code with caution.

📖 How to Use
Text Translation: Head to the main tab, select your target language, and type away.
File Translation: Upload a document; the app will parse, translate, and provide a download link.
Language Detection: Unsure of a source language? Use the Detection tab to identify it instantly.
History: Check the sidebar to revisit or copy previous translations from your current session.
Powered by Google Translate & Deep Translator.
