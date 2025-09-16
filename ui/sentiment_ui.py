import streamlit as st
from modules import downloader, sentiment, transcriber, notifier

def render(model="mistralai/mistral-nemo-instruct-2407"):
    st.subheader("💭 Sentiment Analysis")

    input_text = st.text_area("✍️ Enter text (Arabic or English)", height=150)
    uploaded_file = st.file_uploader("📂 Or Upload audio/video", type=["mp3", "wav", "mp4", "mkv"])
    youtube_url = st.text_input("▶️ Or paste a YouTube link")
    lang_choice = st.selectbox("🌐 Transcription language", ["auto", "en", "ar"], index=0)

    if "sentiment_transcript" not in st.session_state:
        st.session_state.sentiment_transcript = None

    if st.button("🔍 Analyze Sentiment"):
        text_to_analyze = input_text.strip()

        if not text_to_analyze:
            if st.session_state.sentiment_transcript:
                text_to_analyze = st.session_state.sentiment_transcript
            else:
                if uploaded_file:
                    audio_path = downloader.save_file(uploaded_file)
                elif youtube_url:
                    audio_path = downloader.download_youtube(youtube_url)
                else:
                    st.warning("⚠️ Please enter text, upload a file, or paste a YouTube link.")
                    return

                with st.spinner("📝 Transcribing audio/video..."):
                    text_to_analyze = transcriber.transcribe(audio_path, lang=lang_choice)
                    st.session_state.sentiment_transcript = text_to_analyze

        with st.spinner("🔎 Running sentiment analysis..."):
            result = sentiment.analyze_sentiment(text_to_analyze, model=model)

        st.session_state["sentiment_result"] = result

        # Display
        st.markdown("### ✅ Sentiment Result")
        st.write(f"**Sentiment:** {result['label']}")
        st.write(f"**Confidence:** {round(result['score'] * 100, 2)}%")
        st.write(f"**Explanation:** {result['explanation'][:2000]}")

        st.progress(int(result["score"] * 100))
        if result["label"].upper() == "POSITIVE":
            st.success("This text expresses a **Positive** sentiment 🌟")
        elif result["label"].upper() == "NEGATIVE":
            st.error("This text expresses a **Negative** sentiment 💢")
        else:
            st.info("This text seems **Neutral** 😐")

    # Share results
    if st.session_state.get("sentiment_result"):
        res = st.session_state["sentiment_result"]

        # Prepare pretty message
        pretty_msg = f"""
💭 Sentiment Analysis Result
-----------------------------------
Sentiment: {res['label']}
Confidence: {round(res['score']*100, 2)}%
Explanation: 
{res['explanation'][:2000]}
"""

        # Save into session for notifier
        st.session_state["sentiment_message"] = pretty_msg  

        # 📤 Share results using the formatted message
        notifier.share_output("sentiment_message", "Sentiment Analysis Result")
