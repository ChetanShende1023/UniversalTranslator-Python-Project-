import streamlit as st
import os
import tempfile
from io import BytesIO
from gtts import gTTS
import PyPDF2
import docx
from googletrans import Translator, LANGUAGES
from deep_translator import GoogleTranslator as DeepGoogleTranslator

# ---------------------- Configuration ----------------------
st.set_page_config(
    page_title="Multi-lingual Translator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Language mapping for display
LANG_LIST = {v: k for k, v in LANGUAGES.items()}  # {'english':'en', ...}

# ---------------------- Helper Functions ----------------------
@st.cache_data(show_spinner=False)
def translate_text(text, src_lang, dest_lang, engine='googletrans'):
    """
    Translate text using specified engine with fallback.
    """
    if not text.strip():
        return "", None
    try:
        if engine == 'googletrans':
            translator = Translator()
            result = translator.translate(text, src=src_lang, dest=dest_lang)
            return result.text, result.pronunciation
        else:  # deep-translator fallback
            translated = DeepGoogleTranslator(source=src_lang, target=dest_lang).translate(text)
            return translated, None
    except Exception as e:
        st.error(f"Translation failed: {e}")
        # Try fallback engine if available
        if engine == 'googletrans':
            st.warning("Trying fallback engine...")
            return translate_text(text, src_lang, dest_lang, engine='deep')
        else:
            return "", None

def text_to_speech(text, lang, filename='audio.mp3'):
    """
    Convert text to speech and return audio bytes.
    """
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            tts.save(tmp.name)
            with open(tmp.name, 'rb') as f:
                audio_bytes = f.read()
        os.unlink(tmp.name)
        return audio_bytes
    except Exception as e:
        st.error(f"TTS failed: {e}")
        return None

def extract_text_from_file(uploaded_file):
    """
    Extract text from uploaded TXT, PDF, or DOCX file.
    """
    text = ""
    try:
        if uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(BytesIO(uploaded_file.getvalue()))
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            st.error("Unsupported file type.")
    except Exception as e:
        st.error(f"Error extracting text: {e}")
    return text

def detect_language(text):
    """
    Detect language of given text using googletrans.
    """
    try:
        translator = Translator()
        detection = translator.detect(text)
        lang_code = detection.lang
        lang_name = LANGUAGES.get(lang_code, 'unknown')
        return lang_code, lang_name
    except:
        return 'en', 'english'  # default

# ---------------------- Session State Initialization ----------------------
if 'history' not in st.session_state:
    st.session_state.history = []  # list of dicts: {'src_text', 'translated_text', 'src_lang', 'dest_lang'}

# ---------------------- UI Layout ----------------------
st.title("🌍 Advanced Language Translator")
st.markdown("Translate text between multiple languages with speech, file support, and history.")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    translation_engine = st.selectbox("Translation Engine", ['googletrans', 'deep-translator (fallback)'])
    enable_tts = st.checkbox("Enable Text-to-Speech", value=True)
    max_chars = st.number_input("Max characters per chunk", min_value=500, max_value=5000, value=1500, step=100,
                                help="For long texts, they are split into chunks.")

    st.markdown("---")
    st.markdown("### Translation History")
    if st.button("Clear History"):
        st.session_state.history = []
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-5:])):  # show last 5
            st.text(f"{i+1}. {item['src_text'][:30]}... -> {item['translated_text'][:30]}...")
    else:
        st.info("No history yet.")

# Main area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Text Translation", "📁 File Translation", "🔍 Language Detection", "ℹ️ About"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        src_lang_name = st.selectbox("Source Language", options=list(LANG_LIST.keys()), index=21)  # English is near index 21
        src_lang_code = LANG_LIST[src_lang_name]
        src_text = st.text_area("Enter text to translate:", height=200, key="src_text")

        # Auto-detect button
        if st.button("🔍 Auto-detect Language", key="detect_btn"):
            if src_text.strip():
                detected_code, detected_name = detect_language(src_text)
                st.success(f"Detected: {detected_name.capitalize()} ({detected_code})")
                # Optionally set the source language dropdown
                # For simplicity, we just show the detection.
            else:
                st.warning("Please enter some text.")

    with col2:
        dest_lang_name = st.selectbox("Target Language", options=list(LANG_LIST.keys()), index=39)  # Hindi index approx
        dest_lang_code = LANG_LIST[dest_lang_name]

        if st.button("🚀 Translate", key="translate_btn"):
            if src_text.strip():
                # Split long text into chunks if necessary
                text_chunks = [src_text[i:i+max_chars] for i in range(0, len(src_text), max_chars)]
                translated_chunks = []
                pronunciation = None
                progress_bar = st.progress(0)
                for i, chunk in enumerate(text_chunks):
                    trans, pron = translate_text(chunk, src_lang_code, dest_lang_code,
                                                 engine=translation_engine.split()[0].lower())
                    translated_chunks.append(trans)
                    if pron and not pronunciation:
                        pronunciation = pron
                    progress_bar.progress((i+1)/len(text_chunks))
                translated_text = " ".join(translated_chunks)

                # Display result
                st.success("Translated Text:")
                st.write(translated_text)

                # Show pronunciation if available (only for googletrans)
                if pronunciation:
                    st.info(f"Pronunciation: {pronunciation}")

                # Add to history
                st.session_state.history.append({
                    'src_text': src_text,
                    'translated_text': translated_text,
                    'src_lang': src_lang_name,
                    'dest_lang': dest_lang_name
                })

                # Text-to-speech
                if enable_tts:
                    st.markdown("---")
                    st.subheader("🔊 Listen")
                    col_audio1, col_audio2 = st.columns(2)
                    with col_audio1:
                        st.caption("Original audio")
                        audio_orig = text_to_speech(src_text, src_lang_code)
                        if audio_orig:
                            st.audio(audio_orig, format='audio/mp3')
                    with col_audio2:
                        st.caption("Translated audio")
                        audio_trans = text_to_speech(translated_text, dest_lang_code)
                        if audio_trans:
                            st.audio(audio_trans, format='audio/mp3')

                # Download button
                st.download_button(
                    label="📥 Download Translation as TXT",
                    data=translated_text,
                    file_name=f"translated_{dest_lang_name}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("Please enter text to translate.")

with tab2:
    st.subheader("Upload a file to translate")
    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf', 'docx'])
    if uploaded_file:
        file_text = extract_text_from_file(uploaded_file)
        if file_text:
            st.info(f"Extracted {len(file_text)} characters.")
            with st.expander("Show extracted text"):
                st.write(file_text)

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                src_lang_file = st.selectbox("Source Language (file)", options=list(LANG_LIST.keys()), key="src_file")
            with col_f2:
                dest_lang_file = st.selectbox("Target Language (file)", options=list(LANG_LIST.keys()), key="dest_file")

            if st.button("Translate File"):
                with st.spinner("Translating..."):
                    src_code = LANG_LIST[src_lang_file]
                    dest_code = LANG_LIST[dest_lang_file]
                    # Split if needed
                    chunks = [file_text[i:i+max_chars] for i in range(0, len(file_text), max_chars)]
                    translated_chunks = []
                    prog = st.progress(0)
                    for i, chunk in enumerate(chunks):
                        trans, _ = translate_text(chunk, src_code, dest_code,
                                                  engine=translation_engine.split()[0].lower())
                        translated_chunks.append(trans)
                        prog.progress((i+1)/len(chunks))
                    full_translation = " ".join(translated_chunks)

                st.success("Translation complete!")
                st.text_area("Translated Text", full_translation, height=200)

                # Download
                st.download_button(
                    label="Download Translated File",
                    data=full_translation,
                    file_name=f"translated_{dest_lang_file}.txt",
                    mime="text/plain"
                )

with tab3:
    st.subheader("Language Detection")
    detect_text = st.text_area("Enter text to detect language:", height=100)
    if st.button("Detect"):
        if detect_text.strip():
            code, name = detect_language(detect_text)
            st.success(f"Detected language: **{name.capitalize()}** (code: {code})")
        else:
            st.warning("Enter some text.")

with tab4:
    st.markdown("""
    ## About This App
    This is an **Advanced Language Translator** built with Streamlit.

    ### Features:
    - Translate between **all languages** supported by Google Translate.
    - **Auto language detection**.
    - **Text-to-Speech** for original and translated text.
    - **File upload** (TXT, PDF, DOCX) with translation.
    - **Translation history** stored in session.
    - **Download translations** as text files.
    - **Chunk handling** for long texts.
    - **Fallback translation engine** for reliability.

    ### How to use:
    1. Go to the **Text Translation** tab, select languages, enter text, and click Translate.
    2. Use the **File Translation** tab to translate entire documents.
    3. The **Language Detection** tab can identify the language of any text.
    4. Your recent translations appear in the sidebar.

    Powered by Google Translate (googletrans) and deep-translator.
    """)

# Optional: Add a footer
st.markdown("---")
