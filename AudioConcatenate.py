import hashlib
import torch
from .AudioFlatten import AudioFlatten
from .AnyType import AnyType, ContainsAnyDict, get_last_audio_from_args


class AudioConcatenate:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio1": ("AUDIO",),
            },
            "optional": ContainsAnyDict(AnyType("*"))
        }

    RETURN_TYPES = ("AUDIO", )
    RETURN_NAMES = ("audio_out", )
    DESCRIPTION = "Concatenate audios into one"
    CATEGORY = "Audio"
    INPUT_IS_LIST = True

    FUNCTION = "concatenate"

    def concatenate(
        self,
        **kwargs
    ):
        upto = 1

        audios = []
        last_audio = get_last_audio_from_args(kwargs)

        for upto in range(1, last_audio + 1):
            audio_n = f"audio{upto}"
            if (audio_n not in kwargs):
                continue

            audio = kwargs[audio_n]
            if audio is None:
                continue

            for a in audio:
                audios.append([a, 1])

        (
            max_waveform_len,
            max_sample_rate,
            max_channels
        ) = AudioFlatten.get_audios_max(audios)

        out_audios = AudioFlatten.pad_resample_audios(
            audios,
            None,
            max_sample_rate,
            max_channels
        )
        out_audio = torch.cat(out_audios, 2)
        out_audio = {
            "waveform": out_audio,
            "sample_rate": max_sample_rate
        }
        return (out_audio, )

    @classmethod
    def IS_CHANGED(
        s,
        **kwargs
    ):
        m = hashlib.sha256()
        upto = 1
        while True:
            audio_n = f"audio{upto}"
            if audio_n not in kwargs:
                break

            audio = kwargs[audio_n]
            m.update(audio)

            upto = upto + 1
        return m.digest().hex()
