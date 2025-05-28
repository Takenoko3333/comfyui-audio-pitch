import hashlib
import torchaudio


class AudioBassTreble:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "frequency_type": ([
                    "Bass",
                    "Treble",
                    ], {
                        "default": "Bass"
                    }),
                "gain": ("FLOAT", {
                    "default": 15,
                    "step": 0.1,
                    "tooltip": "desired gain at the boost (or attenuation) in dB.",  # noqa: E501
                    "min": -50,
                    }),
            },
            "optional": {
                "central_freq": ("FLOAT", {
                    "default": -1,
                    "step": 1,
                    "tooltip": "central frequency (in Hz). -1 = Use default (Bass: 100, Treble: 3000)",  # noqa: E501
                    "min": -1,
                    }),
                "Q": ("FLOAT", {
                    "default": 0.707,
                    "step": 0.001,
                    "tooltip": "https://en.wikipedia.org/wiki/Q_factor",
                    }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    DESCRIPTION = "Bass / Treble"
    CATEGORY = "Audio"

    FUNCTION = "bass_treble"

    def bass_treble(
        self,
        audio,
        frequency_type,
        gain,
        central_freq,
        Q=0.707,
    ):
        sample_rate = audio["sample_rate"]
        if central_freq < 0:
            typeDict = {
                "Bass": 100,
                "Treble": 3000,
            }
            if frequency_type in typeDict:
                central_freq = typeDict[frequency_type]

        if frequency_type == 'Bass':
            new_tensor = torchaudio.functional.bass_biquad(
                    audio["waveform"],
                    sample_rate,
                    gain,
                    central_freq,
                    Q,
                    )
        else:
            new_tensor = torchaudio.functional.treble_biquad(
                    audio["waveform"],
                    sample_rate,
                    gain,
                    central_freq,
                    Q,
                    )
        audio = {
            "waveform": new_tensor,
            "sample_rate": sample_rate,
        }
        return (audio, )

    @classmethod
    def IS_CHANGED(
        s, **kwargs,
    ):
        m = hashlib.sha256()
        keys = sorted(kwargs.keys())
        for key in keys:
            m.update(kwargs[key])

        return m.digest().hex()
