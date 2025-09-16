import streamlit as st
from modules import downloader, transcriber, translator, notifier

def render(model="mistralai/mistral-7b-instruct"):
    st.subheader("🌍 Translate Audio/Video")

    uploaded_file = st.file_uploader("📂 Upload audio/video", type=["mp3", "wav", "mp4", "mkv"])
    youtube_url = st.text_input("▶️ Or paste a YouTube link")
    target_lang = st.selectbox("🌐 Translate into", ["en", "ar"], index=1)
    mode = st.radio("⚙️ Translation Mode", ["classic", "llm"], index=1)

    # Session cache
    if "transcript" not in st.session_state:
        st.session_state.transcript = None
    if "translation" not in st.session_state:
        st.session_state.translation = None

    if st.button("🚀 Translate"):
        if st.session_state.transcript is None:
            if uploaded_file:
                audio_path = downloader.save_file(uploaded_file)
            elif youtube_url:
                audio_path = downloader.download_youtube(youtube_url)
            else:
                st.warning("⚠️ Please upload a file or enter a YouTube URL.")
                return

            with st.spinner("📝 Transcribing..."):
                st.session_state.transcript = transcriber.transcribe(audio_path)

        with st.spinner("🌍 Translating..."):
            st.session_state.translation = translator.translate_text(
                st.session_state.transcript, target_lang=target_lang, mode=mode
            )

        st.success("✅ Translation completed!")

    # Show transcript
    if st.session_state.transcript:
        st.subheader("Transcript")
        st.text_area("Transcript", st.session_state.transcript, height=200)

    # Show translation
    if st.session_state.translation:
        st.subheader("🌍 Translation")
        align = "rtl" if target_lang == "ar" else "ltr"
        st.markdown(
            f"<div style='direction:{align}; text-align:justify;'>{st.session_state.translation.replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True
        )

        # Save formatted text for sharing
        share_text = (
            f"🌍 Translation Output\n\n"
            f"📜 Transcript:\n{st.session_state.transcript[:2000]}...\n\n"
            f"🌍 Translation:\n{st.session_state.translation}"
        )
        st.session_state["translation_output"] = share_text

        # 📤 Share via Telegram/Email
        notifier.share_output("translation_output", "Transcript & Translation")
