import hashlib
import torch
import numpy
import librosa


class AudioTrimSilenceRosa:
    """Trims silence from ends of audio.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
            },
            "optional": {
                "decibel": ("FLOAT", {
                    "default": 0,
                    "tooltip": "Either use decibel or bins, not both.\nSet to 0 to disable."  # noqa: E501
                }),
                "bins": ("INT", {
                    "default": 7,
                    "tooltip": "Bins will detect the decibel based on the middle bin.  Should be an odd number.\nThe more bins the lower the decibel and more of the audio will be trimmed.\nSet to 0 to disable."  # noqa: E501
                }),
            }
        }

    OUTPUT_TOOLTIPS = (
        "Audio",
        "Decibel number used only useful if you're using bins."
        )
    RETURN_TYPES = ("AUDIO", "FLOAT")
    RETURN_NAMES = ("audio", "decibel")
    CATEGORY = "Audio"
    DESCRIPTION = "Trim silence from audio."

    FUNCTION = "silence"

    def silence(
        self,
        audio,

        decibel: float = 60,
        bins: int = 7,
    ):
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        waveform_np = torch.Tensor.numpy(waveform)

        if bins > 0:
            if (bins % 2) == 0:
                bins = bins + 1
            S = numpy.abs(librosa.stft(waveform_np))
            decibel_np = librosa.power_to_db(S**2)
            (histogram, bin_edges) = numpy.histogram(decibel_np, bins=bins)
            edges_len2 = int(len(bin_edges)/2)
            edge1 = bin_edges[edges_len2]
            decibel = edge1 + ((bin_edges[edges_len2+1] - edge1) / 2)

        trimmed_np = librosa.effects.trim(waveform_np, top_db=decibel)
        new_waveform = torch.from_numpy(trimmed_np[0])

        # Bins must be an odd number to get the middle bin

        new_audio = {
            "waveform": new_waveform,
            "sample_rate": sample_rate,
        }
        return (new_audio, decibel)

    @classmethod
    def IS_CHANGED(
        cls,
        audio,
        decibel,
        bins,
    ):
        m = hashlib.sha256()
        m.update(audio)
        m.update(decibel)
        m.update(bins)
        return m.digest().hex()
