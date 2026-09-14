from faster_whisper import WhisperModel


# Load the Whisper model
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(audio_path):
    """
    Convert an audio file into text.
    """

    segments, info = model.transcribe(audio_path)

    transcript = ""

    for segment in segments:
        transcript += segment.text + " "

    return transcript.strip()


if __name__ == "__main__":

    audio_file = "data/audio/contact_001.wav"

    text = transcribe_audio(audio_file)

    print("\nTranscript:")
    print(text)