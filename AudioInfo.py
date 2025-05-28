

class AudioInfo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
            },
        }

    RETURN_TYPES = ("FLOAT", "int", "BOOLEAN")
    RETURN_NAMES = ("seconds", "sample_rate", "mono")
    CATEGORY = "Audio"

    FUNCTION = "info"

    def info(
        self,
        audio
    ):
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        seconds = len(waveform[0][0]) / sample_rate
        return (seconds, sample_rate, len(waveform[0]) == 1)
