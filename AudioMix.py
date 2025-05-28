import hashlib
import torch
import copy
from .AudioFlatten import AudioFlatten
from .AnyType import AnyType, ContainsAnyDict, get_last_audio_from_args


class AudioMix:
    @classmethod
    def INPUT_TYPES(s):
        volume_tooltip = "Example: 0 = silent, 0.5 = half, 1 = normal, 2 = twice volume"  # noqa: E501
        start_secs_tooltip = "Number of seconds to wait before starting audio"  # noqa: E501
        return {
            "required": {
                "constant_volume": ("BOOLEAN", {"default": False}),
                "audio1": ("AUDIO",),
                "volume1": ("FLOAT", {
                    "default": 1,
                    "step": 0.05,
                    "display": "number",
                    "tooltip": volume_tooltip,
                    }),
                "start_secs1": ("FLOAT", {
                    "default": 0,
                    "step": 0.1,
                    "display": "number",
                    "min": 0,
                    "tooltip": start_secs_tooltip,
                    }),
            },
            "optional": ContainsAnyDict(AnyType("*"))
        }

    RETURN_TYPES = ("AUDIO", )
    RETURN_NAMES = ("audio", )
    DESCRIPTION = "Mix audios into one"
    CATEGORY = "Audio"
    INPUT_IS_LIST = True

    FUNCTION = "mix"

    def mix(
        self,
        constant_volume,
        **kwargs
    ):
        last_audio = get_last_audio_from_args(kwargs)

        audios = []
        for upto in range(1, last_audio + 1):
            audio_n = f"audio{upto}"
            volume_n = f"volume{upto}"
            start_secs_n = f"start_secs{upto}"
            if (
                audio_n not in kwargs or
                start_secs_n not in kwargs or
                volume_n not in kwargs
            ):
                continue

            audio_l = kwargs[audio_n]
            volume = kwargs[volume_n]
            start_secs = kwargs[start_secs_n]

            audio_l_len = len(audio_l)
            if len(volume) != audio_l_len:
                volume = [volume[0]] * audio_l_len
            if len(start_secs) != audio_l_len:
                start_secs = [start_secs[0]] * audio_l_len

            l_upto = 0
            for audio in audio_l:
                new_audio = copy.copy(audio)

                if start_secs[l_upto] > 0:
                    pad = (int(start_secs[l_upto] * audio["sample_rate"]), 0)

                    new_audio["waveform"] = torch.nn.functional.pad(
                        new_audio["waveform"],
                        pad=pad
                    )

                audios.append([new_audio, volume[l_upto]])
                l_upto += 1

        (
            max_waveform_len,
            max_sample_rate,
            max_channels,
        ) = AudioFlatten.get_audios_max(audios)

        out_audios = AudioFlatten.pad_resample_audios(
            audios,
            max_waveform_len,
            max_sample_rate,
            max_channels
        )
        out_audios = torch.cat(out_audios, 0)
        out_audio = torch.sum(out_audios, 0)

        if constant_volume:
            out_audio = out_audio.divide(len(out_audios))
        else:
            non_zeroes = torch.count_nonzero(out_audios, dim=0)
            non_zeroes = torch.where(non_zeroes == 0, 1, non_zeroes)
            out_audio = out_audio.divide(non_zeroes)
        out_audio = out_audio[None, :, :]
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
        keys = sorted(kwargs.keys())
        for key in keys:
            m.update(kwargs[key])

        return m.digest().hex()
