import math
import torch
import torchaudio


class AudioFlatten:
    @classmethod
    def get_audios_max(cls, audios):
        max_time_len = 0
        max_sample_rate = 0
        max_channels = 0
        for audioArr in audios:
            (audio, _) = audioArr
            (audio_count, channels, waveform_len) = audio["waveform"].shape
            sample_rate = audio["sample_rate"]
            if sample_rate > max_sample_rate:
                max_sample_rate = sample_rate
            time_len = waveform_len / sample_rate
            if time_len > max_time_len:
                max_time_len = time_len
            if channels > max_channels:
                max_channels = channels
            max_waveform_len = int(math.ceil(max_time_len * max_sample_rate))
        print(f"max channels:{max_channels}, max_sample_rate:{max_sample_rate}, max_waveform: {max_waveform_len}")  # noqa: E501
        return (max_waveform_len, max_sample_rate, max_channels)

    @classmethod
    def pad_resample_audios(
        cls, audios, max_waveform_len, max_sample_rate, max_channels
    ):
        """pad and resample audio and make the channels the same

        Parameters:
            audios: list of (audio_tensor, volume) tuples.

        Returns:
            out_audios: list of audio_tensors.
                All with the same sample_rate, channels, length
        """
        out_audios = []
        for audioArr in audios:
            (audio, volume) = audioArr
            waveform = audio["waveform"]
            sample_rate = audio["sample_rate"]
            (audio_count, channels, waveform_len) = waveform.shape
            if (
                max_channels is not None and
                channels < max_channels
            ):
                waveform = waveform.expand(
                    audio_count, max_channels,
                    waveform_len
                    )

            if sample_rate < max_sample_rate:
                resample = torchaudio.transforms.Resample(
                    sample_rate, max_sample_rate)
                waveform = resample(waveform)

            (audio_count, channels, waveform_len) = waveform.shape
            if (
                max_waveform_len is not None and
                waveform_len < max_waveform_len
            ):
                pad = int(max_waveform_len - waveform_len)
                waveform = torch.nn.functional.pad(
                    waveform,
                    pad=(0, pad)
                )

            if volume != 1.0:
                waveform = waveform.multiply(volume)
            if volume > 0.0:
                out_audios.append(waveform)
        return out_audios
