import streamlit as st
from modules import downloader, transcriber, summarizer, notifier

def render(model="mistralai/mistral-7b-instruct"):
    st.subheader("📝 Summarize")

    uploaded_file = st.file_uploader("📂 Upload audio/video", type=["mp3", "wav", "mp4", "mkv"])
    youtube_url = st.text_input("▶️ Or paste a YouTube link")
    lang_choice = st.selectbox("🌐 Select language", ["auto", "en", "ar"], index=0)
    mode = st.radio("⚙️ Summarization Mode", ["classic", "llm"], index=1)

    # Session cache
    if "sum_transcript" not in st.session_state:
        st.session_state.sum_transcript = None
    if "sum_summary" not in st.session_state:
        st.session_state.sum_summary = None

    if st.button("🚀 Summarize"):
        if st.session_state.sum_transcript is None:
            if uploaded_file:
                audio_path = downloader.save_file(uploaded_file)
            elif youtube_url:
                audio_path = downloader.download_youtube(youtube_url)
            else:
                st.warning("⚠️ Please upload a file or enter a YouTube URL.")
                return

            with st.spinner("📝 Transcribing..."):
                st.session_state.sum_transcript = transcriber.transcribe(audio_path, lang=lang_choice)

        with st.spinner("📌 Summarizing..."):
            st.session_state.sum_summary = summarizer.summarize_text(
                st.session_state.sum_transcript, lang=lang_choice, mode=mode
            )

        st.success("✅ Summary generated!")

    # Show transcript + summary
    if st.session_state.sum_transcript:
        st.subheader("Transcript")
        st.text_area("Transcript", st.session_state.sum_transcript, height=200)

    if st.session_state.sum_summary:
        st.subheader("📌 Summary")
        st.markdown(st.session_state.sum_summary)

        # Save formatted text for sharing
        share_text = f"📝 Transcript & Summary\n\n---\n\n📜 Transcript:\n{st.session_state.sum_transcript[:2000]}...\n\n📌 Summary:\n{st.session_state.sum_summary}"
        st.session_state["summary_output"] = share_text

        # 📤 Share via Telegram/Email
        notifier.share_output("summary_output", "Transcript & Summary")
