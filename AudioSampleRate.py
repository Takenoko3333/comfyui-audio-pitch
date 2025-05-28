import hashlib


class AudioSampleRate:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "change": ("FLOAT", {
                    "tooltip": "Less than 1.0 for a lower pitch. More than 1.0 for a higher pitch",  # noqa: E501
                    "default": 1.0,
                    "step": 0.01,
                    }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    DESCRIPTION = "Quickly change the pitch by changing the sample rate"
    CATEGORY = "Audio"

    FUNCTION = "pitch"

    def pitch(
        self,
        audio,
        change
    ):
        sample_rate = audio["sample_rate"]
        audio = {
            "waveform": audio["waveform"],
            "sample_rate": int(sample_rate * change),
        }
        return (audio,)

    @classmethod
    def IS_CHANGED(
        s, audio,
        change
    ):
        m = hashlib.sha256()
        m.update(audio)
        m.update(change)
        return m.digest().hex()
