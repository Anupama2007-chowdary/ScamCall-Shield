
import os
import requests
import streamlit as st

from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from scam_detector import analyze_scam

load_dotenv()

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="ScamCall Shield",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ ScamCall Shield")
st.subheader("AI-Powered Multilingual Voice Scam Detection")

st.write(
    "Upload a call recording or enter a transcript "
    "to identify suspicious patterns and potential scams."
)

# ---------------- LANGUAGE OPTIONS ----------------

language_options = {
    "Automatic Detection": "indic-auto",
    "Telugu": "te-IN",
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Bengali": "bn-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Punjabi": "pa-IN"
}

translation_languages = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa"
}

language = st.selectbox(
    "Recording Language",
    list(language_options.keys())
)

language_code = language_options[language]

selected_language = st.selectbox(
    "Select Translation Language",
    list(translation_languages.keys())
)

selected_language_code = translation_languages[selected_language]

# ---------------- INPUT ----------------

uploaded_audio = st.file_uploader(
    "Upload a call recording (maximum 30 seconds)",
    type=["wav", "mp3", "m4a", "ogg"]
)

transcript = st.text_area(
    "Or enter a transcript manually",
    placeholder="Paste the words spoken during the call..."
)

# ---------------- BATCH TRANSLATION ----------------

@st.cache_data(show_spinner=False)
def translate_batch_cached(texts, target_language):

    translator = GoogleTranslator(
        source="auto",
        target=target_language
    )

    return translator.translate_batch(list(texts))


def translate_many(texts, target_language):

    if not texts:
        return []

    try:
        results = translate_batch_cached(
            tuple(texts),
            target_language
        )

        if not isinstance(results, list):
            results = [results]

        if len(results) != len(texts):
            raise Exception("Unexpected translation response")

        return results

    except Exception as error:
        st.error(f"Translation error: {error}")
        return [None] * len(texts)


# ---------------- LANGUAGE CODE ----------------

def get_language_code(detected_language):

    if not detected_language:
        return None

    code = detected_language.lower().split("-")[0]

    if code in translation_languages.values():
        return code

    return None


# ---------------- ANALYSIS DISPLAY ----------------

def display_analysis(
    original_text,
    english_text,
    original_language_code=None
):

    combined_text = original_text

    if english_text:
        combined_text += " " + english_text

    risk_level, warning_signs = analyze_scam(combined_text)

    st.subheader("Scam Risk Assessment")

    if risk_level == "HIGH":
        st.error("🚨 HIGH RISK — Multiple warning signs found")

    elif risk_level == "MEDIUM":
        st.warning("⚠️ MEDIUM RISK — Suspicious patterns found")

    else:
        st.success(
            "LOW RISK — Few listed warning signs found"
        )

    if warning_signs:

        st.subheader("Warning Signs")

        warning_text = "\n".join(
            "- " + sign for sign in warning_signs
        )

        st.markdown("**English Warning**")
        st.write(warning_text)

        # Original audio language warning
        if original_language_code and original_language_code != "en":

            original_result = translate_many(
                [warning_text],
                original_language_code
            )[0]

            st.markdown("**Original Audio Language Warning**")

            if original_result:
                st.write(original_result)
            else:
                st.warning("Warning translation unavailable.")

        elif original_language_code == "en":

            st.markdown("**Original Audio Language Warning**")
            st.write(warning_text)

        # Selected language warning
        if selected_language_code != "en":

            if selected_language_code == original_language_code:
                selected_warning = original_result if original_language_code != "en" else warning_text
            else:
                selected_warning = translate_many(
                    [warning_text],
                    selected_language_code
                )[0]

            st.markdown(
                f"**{selected_language} Warning**"
            )

            if selected_warning:
                st.write(selected_warning)
            else:
                st.warning("Selected language warning unavailable.")

    else:

        st.info("No listed scam indicators were found.")

        advice = (
            "No listed scam indicators were detected. "
            "Still be careful and never share confidential information."
        )

        st.markdown("**English Safety Advice**")
        st.write(advice)

        if selected_language_code != "en":

            translated_advice = translate_many(
                [advice],
                selected_language_code
            )[0]

            st.markdown(
                f"**{selected_language} Safety Advice**"
            )

            if translated_advice:
                st.write(translated_advice)
            else:
                st.warning("Safety advice translation unavailable.")

    st.caption(
        "Prototype only. This rule-based assessment may produce "
        "false positives or miss scams. Low risk does not mean safe."
    )


# ---------------- COMMON TRANSCRIPT DISPLAY ----------------

def process_transcript(original_transcript, original_code):

    st.subheader("Original Transcript")
    st.write(original_transcript)

    # English translation
    if original_code == "en":

        english_transcript = original_transcript

    else:

        with st.spinner("Translating transcript into English..."):

            english_transcript = translate_many(
                [original_transcript],
                "en"
            )[0]

    st.subheader("English Transcript")

    if english_transcript:
        st.write(english_transcript)
    else:
        st.warning("English translation unavailable.")

    # Selected language translation
    if selected_language_code != "en":

        if selected_language_code == original_code:

            selected_transcript = original_transcript

        else:

            with st.spinner(
                f"Translating into {selected_language}..."
            ):

                selected_transcript = translate_many(
                    [original_transcript],
                    selected_language_code
                )[0]

        st.subheader(
            f"{selected_language} Transcript"
        )

        if selected_transcript:
            st.write(selected_transcript)
        else:
            st.warning(
                f"{selected_language} translation unavailable."
            )

    # Risk assessment and warnings
    display_analysis(
        original_transcript,
        english_transcript,
        original_code
    )


# ---------------- AUDIO TRANSCRIPTION ----------------

if st.button("Transcribe & Analyze Recording"):

    if uploaded_audio is None:

        st.warning("Please upload a recording first.")

    elif not os.getenv("GNANI_API_KEY"):

        st.error(
            "Gnani API key not found. Check your .env file."
        )

    else:

        try:

            with st.spinner("Transcribing audio with Gnani AI..."):

                if language_code == "indic-auto":

                    request_data = {
                        "model": "prisma-v3.0",
                        "language_code": "indic-auto",
                        "format": "codemix",
                        "itn_native_numerals": "true"
                    }

                else:

                    request_data = {
                        "language_code": language_code,
                        "preferred_language": language_code,
                        "format": "codemix",
                        "itn_native_numerals": "true"
                    }

                response = requests.post(
                    "https://api.vachana.ai/stt/v3",

                    headers={
                        "X-API-Key-ID": os.getenv("GNANI_API_KEY")
                    },

                    data=request_data,

                    files={
                        "audio_file": (
                            uploaded_audio.name,
                            uploaded_audio.getvalue(),
                            uploaded_audio.type
                        )
                    },

                    timeout=120
                )

                response.raise_for_status()

                result = response.json()

                original_transcript = result.get(
                    "transcript", ""
                )

                detected_language = result.get(
                    "detected_language_code",
                    language_code
                )

            if not original_transcript.strip():

                st.error("No transcript was returned by Gnani.")

            else:

                # Use selected recording language when specified
                if language_code != "indic-auto":

                    original_code = language_code.split("-")[0]

                else:

                    original_code = get_language_code(
                        detected_language
                    )

                st.success("Audio transcription completed!")

                st.caption(
                    f"Detected language: {detected_language}"
                )

                if original_code is None:
                    st.warning(
                        "Could not identify the audio language reliably. "
                        "Select the recording language manually for "
                        "more accurate language-specific output."
                    )

                process_transcript(
                    original_transcript,
                    original_code
                )

        except requests.exceptions.HTTPError as error:

            response = error.response

            st.error(
                f"Gnani returned HTTP {response.status_code}"
            )

            try:
                details = response.json()
            except ValueError:
                details = response.text[:500]

            st.write("Gnani error message:", details)

        except requests.exceptions.RequestException as error:

            st.error(
                "Could not connect to Gnani. "
                "Check your internet connection."
            )

            st.caption(str(error))

        except Exception as error:

            st.error("An unexpected error occurred.")
            st.caption(str(error))


# ---------------- MANUAL TRANSCRIPT ANALYSIS ----------------

if st.button("Analyze Entered Transcript"):

    if not transcript.strip():

        st.warning("Please enter a transcript first.")

    else:

        process_transcript(
            transcript,
            language_code.split("-")[0]
            if language_code != "indic-auto"
            else None
        )
