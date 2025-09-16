import streamlit as st
from modules import downloader, transcriber, qa, notifier

def render(model="mistralai/mistral-nemo-instruct-2407"):
    st.subheader("❓ Question Answering")

    uploaded_file = st.file_uploader("📂 Upload audio/video", type=["mp3", "wav", "mp4", "mkv"])
    youtube_url = st.text_input("▶️ Or paste a YouTube link")
    lang_choice = st.selectbox("🌐 Transcription language", ["auto", "en", "ar"], index=0)

    question_input = st.text_input("🔍 Enter your question")

    # Initialize session states
    if "qa_transcript" not in st.session_state:
        st.session_state.qa_transcript = None
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []

    if st.button("🚀 Get Answer"):
        # 🔹 Step 1: Load or reuse transcript
        if st.session_state.qa_transcript is None:
            if uploaded_file:
                audio_path = downloader.save_file(uploaded_file)
            elif youtube_url:
                audio_path = downloader.download_youtube(youtube_url)
            else:
                st.warning("⚠️ Please upload a file or enter a YouTube URL.")
                return

            with st.spinner("📝 Transcribing (first time only)..."):
                st.session_state.qa_transcript = transcriber.transcribe(audio_path, lang=lang_choice)

        transcript = st.session_state.qa_transcript

        # 🔹 Step 2: Validate question
        if not question_input.strip():
            st.warning("⚠️ Please enter a question.")
            return

        # 🔹 Step 3: Get answer
        with st.spinner("🤖 Asking Mistral..."):
            answer = qa.answer_question(question_input, transcript, model=model)

        # Save Q&A in history
        st.session_state.qa_history.append({"q": question_input, "a": answer})

        # 🔹 Step 4: Display conversation
        st.success("✅ Answer added!")
        st.markdown("### 📝 Conversation so far")

        conversation_text = ""
        for i, qa_pair in enumerate(st.session_state.qa_history, 1):
            q, a = qa_pair["q"], qa_pair["a"]
            conversation_text += f"Q{i}: {q}\nA{i}: {a}\n\n"
            st.markdown(f"""
            <div style="background:#f0f2f6;padding:12px;border-radius:10px;margin:5px 0">
                <b>❓ Question{i}:</b> {q}<br><br>
                <b>✅ Answer{i}:</b> {a}
            </div>
            """, unsafe_allow_html=True)

        # Save full conversation for sharing
        st.session_state["qa_output"] = conversation_text.strip()

        # 📤 Share results (all Q&A)
        notifier.share_output("qa_output", "Q&A Session")
