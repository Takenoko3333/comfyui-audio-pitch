import hashlib
import torchaudio


class AudioTrimSilenceVAD:
    """Trims silence from ends of audio.
        Using torchaudio.functional.vad(...)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
            },
            "optional": {
                "trigger_level": ("FLOAT", {
                    "default": 7.0,
                    "tooltip": "The measurement level used to trigger activity detection. This may need to be cahnged depending on the noise level, signal level, and other characteristics of the input audio. (Default: 7.0)",  # noqa: E501
                }),
                "trigger_time": ("FLOAT", {
                    "default": 0.25,
                    "step": 0.05,
                    "tooltip": "The time constant (in seconds) used to help ignore short bursts of sound. (Default: 0.25)",  # noqa: E501
                    }),
                "search_time": ("FLOAT", {
                    "default": 1.0,
                    "step": 0.1,
                    "tooltip": "The amount of audio (in seconds) to search for quieter/shorter bursts of audio to include prior to the detected trigger point. (Default: 1.0)",  # noqa: E501
                    }),
                "allowed_gap": ("FLOAT", {
                    "default": 0.25, "step": 0.05,
                    "tooltip": "The allowed gap (in seconds) between quieter/shorter bursts of audio to include prior to the detected trigger point. (Default: 0.25)",  # noqa: E501
                    }),
                "pre_trigger_time": ("FLOAT", {
                    "default": 0.0, "step": 0.01,
                    "tooltip": "The amount of audio (in seconds) to preserve before the trigger point and any found quieter/shorter bursts. (Default: 0.0)",  # noqa: E501
                    }),
                "boot_time": ("FLOAT", {
                    "default": 0.35, "step": 0.05,
                    "tooltip": "estimation/reduction in order to detect the start of the wanted audio. This option sets the time for the initial noise estimate. (Default: 0.35)",  # noqa: E501
                    }),
                "noise_up_time": ("FLOAT", {
                    "default": 0.1, "step": 0.01,
                    "tooltip": "for when the noise level is increasing. (Default: 0.1)",  # noqa: E501
                    }),
                "noise_down_time": ("FLOAT", {
                    "default": 0.01, "step": 0.001,
                    "tooltip": "for when the noise level is decreasing. (Default: 0.01)",  # noqa: E501
                    }),
                "noise_reduction_amount": ("FLOAT", {
                    "default": 1.35, "step": 0.05,
                    "tooltip": "the detection algorithm (e.g. 0, 0.5, …). (Default: 1.35)",  # noqa: E501
                }),
                "measure_freq": ("FLOAT", {
                    "default": 20.0, "step": 0.5,
                    "tooltip": "processing/measurements. (Default: 20.0)",  # noqa: E501
                    }),
                "measure_smooth_time": ("FLOAT", {
                    "default": 0.4, "step": 0.05,
                    "tooltip": "spectral measurements. (Default: 0.4)",  # noqa: E501
                }),
                "hp_filter_freq": ("FLOAT", {
                    "default": 50.0, "step": 1,
                    }),
                "lp_filter_freq": ("FLOAT", {
                    "default": 6000.0,
                    "max": 1000000,
                    "step": 1,
                    "tooltip": "Put this number down if there is high frequency background noise."  # noqa: E501
                }),
                "hp_lifter_freq": ("FLOAT", {
                    "default": 150.0, "step": 1,
                    }),
                "lp_lifter_freq": ("FLOAT", {
                    "default": 2000.0, "step": 1,
                    }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    CATEGORY = "Audio"
    DESCRIPTION = "Trim silence from audio using torchaudio's Voice Activity Detector.  Lower lp_filter_freq if you have high frequency background noise."  # noqa: E501

    FUNCTION = "silence"

    def silence(
        self,
        audio,

        trigger_level: float = 7.0,
        trigger_time: float = 0.25,
        search_time: float = 1.0,
        allowed_gap: float = 0.25,
        pre_trigger_time: float = 0.0,
        boot_time: float = 0.35,
        noise_up_time: float = 0.1,
        noise_down_time: float = 0.01,
        noise_reduction_amount: float = 1.35,
        measure_freq: float = 20.0,
        measure_smooth_time: float = 0.4,

        hp_filter_freq: float = 50.0,
        lp_filter_freq: float = 6000.0,
        hp_lifter_freq: float = 150.0,
        lp_lifter_freq: float = 2000.0,
    ):
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]

        new_waveform = torchaudio.functional.vad(
            waveform, sample_rate,
            trigger_level=trigger_level,
            trigger_time=trigger_time,
            search_time=search_time,
            allowed_gap=allowed_gap,
            pre_trigger_time=pre_trigger_time,
            boot_time=boot_time,
            noise_up_time=noise_up_time,
            noise_down_time=noise_down_time,
            noise_reduction_amount=noise_reduction_amount,
            measure_freq=measure_freq,
            measure_smooth_time=measure_smooth_time,
            hp_filter_freq=hp_filter_freq,
            lp_filter_freq=lp_filter_freq,
            hp_lifter_freq=hp_lifter_freq,
            lp_lifter_freq=lp_lifter_freq,
        )
        new_waveform = new_waveform.flip(2)
        new_waveform = torchaudio.functional.vad(
            new_waveform, sample_rate,
            trigger_level=trigger_level,
            trigger_time=trigger_time,
            search_time=search_time,
            allowed_gap=allowed_gap,
            pre_trigger_time=pre_trigger_time,
            boot_time=boot_time,
            noise_up_time=noise_up_time,
            noise_down_time=noise_down_time,
            noise_reduction_amount=noise_reduction_amount,
            measure_freq=measure_freq,
            measure_smooth_time=measure_smooth_time,
            hp_filter_freq=hp_filter_freq,
            lp_filter_freq=lp_filter_freq,
            hp_lifter_freq=hp_lifter_freq,
            lp_lifter_freq=lp_lifter_freq,
        )
        new_waveform = new_waveform.flip(2)
        new_audio = {
            "waveform": new_waveform,
            "sample_rate": sample_rate,
        }
        return (new_audio,)

    @classmethod
    def IS_CHANGED(
        cls,
        audio,
        trigger_level,
        trigger_time,
        search_time,
        allowed_gap,
        pre_trigger_time,
        boot_time,
        noise_up_time,
        noise_down_time,
        noise_reduction_amount,
        measure_freq,
        measure_smooth_time,
        hp_filter_freq,
        lp_filter_freq,
        hp_lifter_freq,
        lp_lifter_freq,
    ):
        m = hashlib.sha256()
        m.update(audio)
        m.update(trigger_level)
        m.update(trigger_time)
        m.update(search_time)
        m.update(allowed_gap)
        m.update(pre_trigger_time)
        m.update(boot_time)
        m.update(noise_up_time)
        m.update(noise_down_time)
        m.update(noise_reduction_amount)
        m.update(measure_freq)
        m.update(measure_smooth_time)
        m.update(hp_filter_freq)
        m.update(lp_filter_freq)
        m.update(hp_lifter_freq)
        m.update(lp_lifter_freq)
        return m.digest().hex()
