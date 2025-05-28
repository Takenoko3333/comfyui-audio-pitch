import hashlib
import torchaudio


class AudioPitch:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "n_steps": ("INT", {
                    "default": 2,
                    "display": "number",
                    "step": 1,
                    "tooltip": "The (fractional) steps to shift waveform.",
                    }),
            },
            "optional": {
                "bins_per_octave": ("INT", {
                    "default": 12,
                    "step": 1,
                    "tooltip": "The number of steps per octave (Default : 12).",  # noqa: E501
                    }),
                "n_fft": ("INT", {
                    "default": 512,
                    "step": 16,
                    "tooltip": "Size of FFT, creates n_fft // 2 + 1 bins (Default: 512).",  # noqa: E501
                    }),
                "win_length": ("INT", {
                    "default": -1,
                    "display": "number",
                    "min": -1,
                    "tooltip": "Window size. If -1, then n_fft is used",
                    }),
                "hop_length": ("INT", {
                    "default": -1,
                    "min": -1,
                    "tooltip": "Length of hop between STFT windows. If None, then win_length // 4 is used",  # noqa: E501
                    }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    DESCRIPTION = "Change the pitch with torchaudio"
    CATEGORY = "Audio"

    FUNCTION = "pitch"

    def pitch(
        self,
        audio,
        n_steps,
        bins_per_octave,
        n_fft,
        win_length,
        hop_length,
    ):
        sample_rate = audio["sample_rate"]
        transform = torchaudio.transforms.PitchShift(
                sample_rate,
                n_steps,
                bins_per_octave,
                None if n_fft < 0 else n_fft,
                None if win_length < 0 else win_length,
                None if hop_length < 0 else hop_length,
                )
        new_audio = {
            "waveform": transform(audio["waveform"]),
            "sample_rate": sample_rate,
        }
        return (new_audio, )

    @classmethod
    def IS_CHANGED(
        s, audio,
        n_steps,
        bins_per_octave,
        n_fft,
        win_length,
        hop_length,
    ):
        m = hashlib.sha256()
        m.update(audio)
        m.update(n_steps)
        m.update(bins_per_octave)
        m.update(n_fft)
        m.update(win_length)
        m.update(hop_length)
        return m.digest().hex()
