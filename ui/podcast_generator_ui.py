import streamlit as st
import json
from modules import podcast_generator, notifier

def render(model="mistralai/mistral-7b-instruct"):
    st.subheader("🎙️ Podcast Generator")

    topic = st.text_input("📌 Enter a topic (e.g., Business, Education, Tech)")
    style = st.selectbox(
        "🎭 Choose style",
        ["informative", "fun", "business", "educational"],
        index=0
    )
    duration = st.number_input("⏱️ Expected duration (minutes)", min_value=1, max_value=60, value=5)

    if "podcast_script" not in st.session_state:
        st.session_state.podcast_script = None
        st.session_state.podcast_json = None
        st.session_state.notification_message = None

    if st.button("🚀 Generate Podcast Script"):
        if not topic.strip():
            st.warning("⚠️ Please enter a topic.")
            return

        with st.spinner("📝 Generating podcast dialogue..."):
            cleaned_text = podcast_generator.generate_dialogue_script(
                topic, style=style, duration=duration, model=model
            )
            script_json = podcast_generator.script_to_json(cleaned_text, topic, style)

            st.session_state.podcast_script = cleaned_text
            st.session_state.podcast_json = script_json

            # Notification message
            notification_lines = [
                f"🎙️ New Podcast Script Generated!",
                f"📝 Topic: {topic}",
                f"🎨 Style: {style}",
                f"⏱️ Duration: {duration} min (approx.)",
                f"📊 Word Count: {len(cleaned_text.split())}",
                podcast_generator.format_pretty_output(script_json)
            ]
            st.session_state.notification_message = "\n\n".join(notification_lines)

        st.success("✅ Script generated!")

    # Dialogue Display
    if st.session_state.podcast_json and st.session_state.podcast_json.get("dialogue"):
        st.markdown("### 🎤 Conversation")

        for i, turn in enumerate(st.session_state.podcast_json["dialogue"], start=1):
            speaker_label = turn.get("speaker", f"Speaker {i}")
            text = turn.get("text", "")

            bg = "#f0f2f6" if i % 2 == 0 else "#dff9fb"
            st.markdown(f"""
            <div style="background:{bg};padding:12px;border-radius:10px;margin:6px 0;">
                <b>{speaker_label}:</b> {text}
            </div>
            """, unsafe_allow_html=True)


        # Downloads
        podcast_json = json.dumps(st.session_state.podcast_json, ensure_ascii=False, indent=2)
        st.download_button(
            "💾 Download JSON",
            data=podcast_json,
            file_name="podcast_script.json",
            mime="application/json"
        )
        st.download_button(
            "📄 Download Script (TXT)",
            data=st.session_state.podcast_script,
            file_name="podcast_script.txt",
            mime="text/plain"
        )

        # 🎧 Convert to Audio
        if st.button("🎧 Convert to Audio"):
            with st.spinner("🔊 Converting to audio..."):
                audio_path = podcast_generator.dialogue_to_audio(
                    st.session_state.podcast_json["dialogue"],
                    host_lang="en",
                    guest_lang="en"
                )
            st.audio(audio_path, format="audio/mp3")

            st.session_state.notification_message = (
                f"🎧 Audio narration generated for {topic} ({style} style, {duration} min)."
            )
    else:
        st.info("👉 Generate a script to see it here.")

        # 📤 Share results via notifier
        notifier.share_output("notification_message", title="Podcast Script Notification")
