import streamlit as st
import json
import time
from modules import downloader, transcriber, diarization, notifier


def render(model="mistralai/mistral-nemo-instruct-2407"):
    st.subheader("🗣️ Speaker Diarization")

    uploaded_file = st.file_uploader("📂 Upload audio/video", type=["mp3", "wav", "mp4", "mkv"])
    youtube_url = st.text_input("▶️ Or paste a YouTube link")
    lang_choice = st.selectbox("🌐 Transcription language", ["auto", "en", "ar"], index=0)

    if st.button("🚀 Diarize Speakers"):
        if uploaded_file:
            audio_path = downloader.save_file(uploaded_file)
        elif youtube_url:
            audio_path = downloader.download_youtube(youtube_url)
        else:
            st.warning("⚠️ Please upload a file or enter a YouTube URL.")
            return

        total_start = time.time()

        # 📝 Transcription
        with st.spinner("📝 Transcribing..."):
            t1 = time.time()
            transcript = transcriber.transcribe(audio_path, lang=lang_choice)
            t2 = time.time()
            transcription_time = t2 - t1

        # 🤖 Diarization
        with st.spinner("🤖 Splitting speakers..."):
            t3 = time.time()
            segments = diarization.diarize_transcript(transcript, model=model)
            t4 = time.time()
            diarization_time = t4 - t3

        total_time = time.time() - total_start

        st.success(f"✅ Done! ⏱️ Total: {total_time:.2f}s")
        st.info(f"📝 Transcription: {transcription_time:.2f}s | 🤖 Diarization: {diarization_time:.2f}s")

        # 🎤 Pretty chat-style display
        st.markdown("### 🎤 Conversation")
        output_text = ""
        for i, seg in enumerate(segments):
            speaker = seg["speaker"]
            text = seg["text"]
            output_text += f"{speaker}: {text}\n"

            bg = "#f0f2f6" if i % 2 == 0 else "#dff9fb"
            st.markdown(f"""
            <div style="background:{bg};padding:10px;border-radius:10px;margin:5px 0;direction:rtl if '{lang_choice}'=='ar' else 'ltr'">
                <b>{speaker}:</b> {text}
            </div>
            """, unsafe_allow_html=True)

        # Save JSON + formatted text
        diarized_json = json.dumps(segments, ensure_ascii=False, indent=2)
        pretty_output = diarization.format_pretty_output(segments)

        st.session_state["diarization_output"] = pretty_output

        # 💾 Download JSON
        st.download_button(
            "💾 Download JSON",
            data=diarized_json,
            file_name="diarization.json",
            mime="application/json"
        )

        # 📤 Share results via notifier
        notifier.share_output("diarization_output", "Diarization Result")
