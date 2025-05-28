import hashlib
import torch
import math


class AudioSpeed:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "speed": ("FLOAT", {
                    "default": 1.5,
                    "step": 0.01,
                    "tooltip": "Speed. >1.0 slower. <1.0 faster",
                    }),
            },
            "optional": {
                "speed_type": (["torch-time-stretch", "TDHS"], {
                    "default": "torch-time-stretch",
                    "tooltip": "TDHS - Time-domain harmonic scaling. torch-time-stretch - torchaudio.transforms.TimeStretch.",  # noqa: E501
                }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    DESCRIPTION = "Change the speed of the audio"
    CATEGORY = "Audio"
    INPUT_IS_LIST = True

    FUNCTION = "time_shift"

    def time_shift_audiostretchy(self, audio, speed):
        from audiostretchy.stretch import AudioStretch

        rate = audio['sample_rate']
        waveform = audio['waveform']

        new_waveforms = []
        for channel in range(0, waveform.shape[0]):
            ta_audio16 = waveform[0][channel] * 32768

            audio_stretch = AudioStretch()
            audio_stretch.samples = audio_stretch.in_samples = \
                ta_audio16.numpy().astype('int16')
            audio_stretch.nchannels = 1
            audio_stretch.sampwidth = 2
            audio_stretch.framerate = rate
            audio_stretch.nframes = waveform.shape[2]
            audio_stretch.stretch(ratio=speed)

            new_waveforms.append(torch.from_numpy(audio_stretch.samples))
        new_waveform = torch.stack(new_waveforms)
        new_waveform = torch.stack([new_waveform])

        return {"waveform": new_waveform, "sample_rate": rate}

    def time_shift_torch_ts(self, audio, speed):
        import torch_time_stretch
        rate = audio['sample_rate']
        waveform = audio['waveform']

        new_waveform = torch_time_stretch.time_stretch(
            waveform,
            torch_time_stretch.Fraction(math.floor(speed*100), 100),
            rate
        )

        return {"waveform": new_waveform, "sample_rate": rate}

    def time_shift(
        self,
        audio,
        speed,
        speed_type="torch-time-shift",
    ):
        new_audios = []
        if not isinstance(speed, list):
            speed = [speed] * len(audio)
        i = 0
        for a in audio:
            if speed_type == "torch-time-shift":
                new_audio = self.time_shift_torch_ts(a, speed[i])
            else:
                new_audio = self.time_shift_audiostretchy(a, speed[i])
            i += 1

            new_audios.append(new_audio)
        return (new_audio, )

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
