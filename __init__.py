from .AudioInfo import AudioInfo
from .AudioSampleRate import AudioSampleRate
from .AudioPitch import AudioPitch
from .AudioTrimSilenceVAD import AudioTrimSilenceVAD
from .AudioTrimSilenceRosa import AudioTrimSilenceRosa
from .AudioMix import AudioMix
from .AudioConcatenate import AudioConcatenate
from .AudioBassTreble import AudioBassTreble
from .AudioSpeed import AudioSpeed

WEB_DIRECTORY = "./js"

NODE_CLASS_MAPPINGS = {
    "AudioInfo": AudioInfo,
    "AudioSampleRate": AudioSampleRate,
    "AudioPitch": AudioPitch,
    "AudioMix": AudioMix,
    "AudioConcat": AudioConcatenate,
    "AudioTrimSilenceVAD": AudioTrimSilenceVAD,
    "AudioTrimSilenceRosa": AudioTrimSilenceRosa,
    "AudioBassTreble": AudioBassTreble,
    "AudioSpeed": AudioSpeed,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "AudioInfo": "Audio Info",
    "AudioSampleRate": "Audio Pitch (Sample Rate)",
    "AudioPitch": "Audio Pitch",
    "AudioMix": "Audio Mix",
    "AudioConcat": "Audio Concatenate",
    "AudioTrimSilenceVAD": "Audio Trim Silence (Voice Activity)",
    "AudioTrimSilenceRosa": "Audio Trim Silence (dB)",
    "AudioBassTreble": "Audio Bass/Treble",
    "AudioSpeed": "Audio Speed",
}
