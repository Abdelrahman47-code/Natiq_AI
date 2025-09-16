import streamlit as st
from dotenv import load_dotenv
import os

# Import UI modules
from ui import (
    diarization_ui,
    podcast_generator_ui,
    video_script_generator_ui,
    qa_ui,
    summarizer_ui,
    translation_ui,
    sentiment_ui,
)

# Load API keys
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# App branding
st.set_page_config(
    page_title="Natiq 🗣️💡",
    page_icon="🗣️",
    layout="wide"
)

# =======================
# Sidebar Navigation
# =======================
if "feature_choice" not in st.session_state:
    st.session_state["feature_choice"] = "🏠 Home"

sidebar_options = [
    "🏠 Home",
    "🗣️ Speaker Diarization",
    "🎙️ Podcast Generator",
    "🎬 Video Script Generator",
    "❓ Q&A",
    "📝 Summarize",
    "🌐 Translation",
    "💭 Sentiment Analysis"
]

feature_choice = st.sidebar.radio(
    "Select a feature",
    sidebar_options,
    index=sidebar_options.index(st.session_state["feature_choice"])
)

# Sync session state with sidebar
st.session_state["feature_choice"] = feature_choice

# Sidebar model selection
openrouter_model = st.sidebar.selectbox(
    "🧠 Choose OpenRouter model",
    [
        "mistralai/mistral-7b-instruct",
        "meta-llama/llama-3-8b-instruct",
        "anthropic/claude-3-sonnet",
        "openai/gpt-4o-mini"
    ],
    index=0
)

# Footer in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Built by:** Abdelrahman Eldaba  
    *AI Engineer & Data Scientist*  
    🔗 [LinkedIn](https://www.linkedin.com/in/abdelrahmaneldaba/)
    """
)

# =======================
# Render Pages
# =======================
if st.session_state["feature_choice"] == "🏠 Home":
    st.title("🎉 Welcome to Natiq AI 🗣️💡")
    st.markdown("Your AI-powered audio & text assistant!")

    # Banner image
    st.image("assets/images/bg.png", width="stretch")

    st.subheader("🚀 Choose a feature to get started:")

    # 7 feature buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗣️ Speaker Diarization"):
            st.session_state["feature_choice"] = "🗣️ Speaker Diarization"
            st.rerun()
        if st.button("🎙️ Podcast Generator"):
            st.session_state["feature_choice"] = "🎙️ Podcast Generator"
            st.rerun()
        if st.button("🎬 Video Script Generator"):
            st.session_state["feature_choice"] = "🎬 Video Script Generator"
            st.rerun()

    with col2:
        if st.button("❓ Q&A"):
            st.session_state["feature_choice"] = "❓ Q&A"
            st.rerun()
        if st.button("📝 Summarize"):
            st.session_state["feature_choice"] = "📝 Summarize"
            st.rerun()

    with col3:
        if st.button("🌐 Translation"):
            st.session_state["feature_choice"] = "🌐 Translation"
            st.rerun()
        if st.button("💭 Sentiment Analysis"):
            st.session_state["feature_choice"] = "💭 Sentiment Analysis"
            st.rerun()

elif st.session_state["feature_choice"] == "🗣️ Speaker Diarization":
    diarization_ui.render(model=openrouter_model)

elif st.session_state["feature_choice"] == "🎙️ Podcast Generator":
    podcast_generator_ui.render(model=openrouter_model)

elif st.session_state["feature_choice"] == "🎬 Video Script Generator":
    video_script_generator_ui.render(model=openrouter_model)

elif st.session_state["feature_choice"] == "❓ Q&A":
    qa_ui.render(model=openrouter_model)

elif st.session_state["feature_choice"] == "📝 Summarize":
    summarizer_ui.render(model=openrouter_model)

elif st.session_state["feature_choice"] == "🌐 Translation":
    translation_ui.render(model=openrouter_model)

elif st.session_state["feature_choice"] == "💭 Sentiment Analysis":
    sentiment_ui.render(model=openrouter_model)
