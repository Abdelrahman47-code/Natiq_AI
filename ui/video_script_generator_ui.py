import streamlit as st
import json
from modules import video_script_generator, notifier  

def render(model="mistralai/mistral-7b-instruct"):
    st.subheader("🎬 Video Script Generator")

    topic = st.text_input("Enter a video topic")
    style = st.selectbox("Choose style", ["educational", "informative", "motivational", "business", "fun"])
    lang = st.selectbox("Narration language", ["en", "ar"], index=0)
    duration = st.number_input("⏱️ Expected duration (minutes)", min_value=1, max_value=60, value=5)

    if "video_script" not in st.session_state:
        st.session_state.video_script = None
        st.session_state.video_json = None
        st.session_state.notification_message = None

    if st.button("🚀 Generate Video Script"):
        if not topic.strip():
            st.warning("⚠️ Please enter a topic.")
            return

        with st.spinner("📝 Generating structured video script..."):
            script_text, script_json = video_script_generator.generate_structured_video_script(
                topic, style, duration, model
            )
            st.session_state.video_script = script_text
            st.session_state.video_json = script_json

            # Use pre-generated chunks from JSON
            script_chunks_for_msg = script_json.get("chunks", [])

            notification_lines = [
                f"🎬 *New Video Script Generated!*",
                f"📝 Topic: {topic}",
                f"🎨 Style: {style}",
                f"⏱️ Duration: {duration} min (approx.)",
                f"📊 Word Count: {len(script_text.split())}",
                "\n".join(script_chunks_for_msg)
            ]
            st.session_state.notification_message = "\n\n".join(notification_lines)

        st.success("✅ Video script generated!")

    # Display results
    if st.session_state.video_json:
        with st.expander("👀 Preview Script", expanded=True):
            res = st.session_state.video_json
            st.markdown(f"""
            ### 🎬 {res['title']}
            Style: {res['style']}  
            Duration: {res['duration_minutes']} min  
            Word Count: {len(st.session_state.video_script.split())}  

            ---

            #### 📝 Introduction  
            {res['sections']['intro']}

            #### 📖 Body  
            {res['sections']['body']}

            #### 🎯 Conclusion  
            {res['sections']['conclusion']}
            """, unsafe_allow_html=True)

        # Downloads
        st.download_button(
            label="💾 Download Script (JSON)",
            data=json.dumps(st.session_state.video_json, ensure_ascii=False, indent=2),
            file_name="video_script.json",
            mime="application/json"
        )
        st.download_button(
            label="📄 Download Script (TXT)",
            data=st.session_state.video_script,
            file_name="video_script.txt",
            mime="text/plain"
        )

        # Audio
        if st.button("🎧 Convert to Audio"):
            with st.spinner("🔊 Converting to audio..."):
                audio_path = video_script_generator.video_to_audio(st.session_state.video_script, lang=lang)
            st.audio(audio_path, format="audio/mp3")

            st.session_state.notification_message = f"🎧 Audio narration generated for {topic} ({style} style)."

        # 📤 Share via Telegram/Email
        notifier.share_output("notification_message", title="Video Script Notification")
