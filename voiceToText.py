from google.cloud import speech_v1p1beta1 as speech
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google.json"

client = speech.SpeechClient()


def toText(file):
    speech_file = file
    first_lang = "he"  # Hebrew
    second_lang = "en-US"  # English US
    third_lang = "ru_RU"  # Russian
    fourth_lang = "ar"  # Arabic

    with open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=48000,
        language_code=first_lang,
        alternative_language_codes=[second_lang, third_lang, fourth_lang],
    )

    response = client.recognize(config=config, audio=audio)

    for i, result in enumerate(response.results):
        # alternative = result.alternatives[0]
        return result
