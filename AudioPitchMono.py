# AudioPitchMono.py
# Drop-in replacement: same UI/params.
# Pitch shift via STFT + phase vocoder + linear resample (no torchaudio PitchShift).
# ALWAYS returns waveform as (1, 1, T) float32 CPU to satisfy PreviewAudio.

import hashlib
import gc
import math
import torch


class AudioPitchMono:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "n_steps": ("INT", {
                    "default": 0,
                    "display": "number",
                    "step": 1,
                    "min": -24,
                    "max": 24,
                    "tooltip": "Semitone shift (−24 to +24 ≈ ±2 octaves).",
                }),
            },
            "optional": {
                "bins_per_octave": ("INT", {
                    "default": 12,
                    "step": 1,
                    "tooltip": "The number of steps per octave (Default : 12).",
                }),
                "n_fft": ("INT", {
                    "default": 1024,
                    "step": 16,
                    "tooltip": "Size of FFT, creates n_fft // 2 + 1 bins (Default: 1024). Larger = smoother, but heavier.",
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
                    "tooltip": "Length of hop between STFT windows. If None, then win_length // 4 is used",
                }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    DESCRIPTION = "Change the pitch without torchaudio PitchShift (phase vocoder)"
    CATEGORY = "AudioPitch"

    FUNCTION = "pitch"

    # ---- lightweight digest for AUDIO (avoid hashing whole waveform) ----
    @staticmethod
    def _audio_digest(audio, head_samples: int = 16000) -> bytes:
        m = hashlib.sha256()
        try:
            wf = audio["waveform"]
            sr = int(audio.get("sample_rate", 0))
            numel = int(wf.numel())
            shape = tuple(int(s) for s in wf.shape)
            m.update(f"{sr}|{shape}|{numel}".encode())
            if numel > 0:
                take = min(numel, max(4096, head_samples))
                head = wf.reshape(-1)[:take]
                if head.dtype != torch.float32:
                    head = head.to(torch.float32)
                if head.device.type != "cpu":
                    head = head.cpu()
                m.update(head.numpy().tobytes())
        except Exception:
            m.update(b"AUDIO")
        return m.digest()

    # ---- time-stretch by phase vocoder (CPU, float32), input (C, T) -> output (C, T') ----
    @staticmethod
    def _time_stretch_phase_vocoder(wf: torch.Tensor, n_fft: int, win_length: int, hop_length: int, rate: float) -> torch.Tensor:
        if rate <= 0:
            return wf.clone()

        win = torch.hann_window(win_length, periodic=True, dtype=wf.dtype, device=wf.device)
        stft = torch.stft(
            wf, n_fft=n_fft, hop_length=hop_length, win_length=win_length,
            window=win, return_complex=True, center=True, pad_mode="reflect"
        )  # (C, F, T)
        C, F, T = stft.shape
        if T < 2:
            return wf.clone()

        k = torch.arange(F, device=stft.device, dtype=stft.real.dtype)
        omega = 2 * math.pi * hop_length * k / n_fft  # (F,)

        t_steps = torch.arange(0, T - 1, step=rate, device=stft.device, dtype=stft.real.dtype)
        T_out = t_steps.numel()

        out_spec = torch.zeros((C, F, T_out), dtype=stft.dtype, device=stft.device)
        phase_acc = torch.angle(stft[:, :, 0])  # (C, F)

        t0 = t_steps.floor().to(torch.long)
        t1 = t0 + 1
        frac = (t_steps - t0).to(stft.real.dtype)

        for i in range(T_out):
            t = int(t0[i])
            tn = int(t1[i])
            a = float(frac[i])

            s0 = stft[:, :, t]
            s1 = stft[:, :, tn]

            mag = (1.0 - a) * torch.abs(s0) + a * torch.abs(s1)
            dphase = torch.angle(s1) - torch.angle(s0) - omega
            dphase = (dphase + math.pi) % (2 * math.pi) - math.pi

            phase_acc = phase_acc + omega + dphase
            out_spec[:, :, i] = mag * torch.exp(1j * phase_acc)

        out = torch.istft(
            out_spec, n_fft=n_fft, hop_length=hop_length, win_length=win_length,
            window=win, center=True, length=int(round(wf.shape[-1] / rate))
        )  # (C, T')
        return out

    # ---- channel-wise linear resample to target length (C, new_len) ----
    @staticmethod
    def _linear_resample_len(wf: torch.Tensor, new_len: int) -> torch.Tensor:
        if new_len == wf.shape[-1]:
            return wf
        import torch.nn.functional as F
        x = wf.unsqueeze(0)                  # (1, C, T)
        x2 = F.interpolate(x, size=new_len, mode="linear", align_corners=False)
        return x2.squeeze(0)                 # (C, new_len)

    # ---- hard normalizer to (1, 1, T) ----
    @staticmethod
    def _to_bct(wf: torch.Tensor) -> torch.Tensor:
        """
        Force to (1, 1, T) float32 CPU no matter what comes in.
        """
        wf = wf.detach().to(torch.float32).cpu().contiguous()
        # flatten to mono time
        if wf.ndim == 0:
            wf = wf.reshape(1)
        if wf.ndim == 1:
            # (T,) -> (1, 1, T)
            return wf.unsqueeze(0).unsqueeze(0)
        if wf.ndim == 2:
            # (C, T) -> (1, 1, T) by mixing down to mono
            # here: simply take first channel (fast & deterministic)
            wf = wf[0:1, :]                  # (1, T)
            return wf.unsqueeze(0)           # (1, 1, T)
        # wf.ndim >= 3
        T = wf.shape[-1]
        wf = wf.reshape(-1, T)               # (C_flat, T)
        wf = wf[0:1, :]                      # (1, T)  (mixdown: pick first)
        return wf.unsqueeze(0)               # (1, 1, T)

    def pitch(
        self,
        audio,
        n_steps,
        bins_per_octave,
        n_fft,
        win_length,
        hop_length,
    ):
        sample_rate = int(audio["sample_rate"])
        wf_in = audio["waveform"]

        # ---- normalize input to (C, T) on CPU float32 ----
        with torch.no_grad():
            wf = wf_in
            if hasattr(wf, "requires_grad") and wf.requires_grad:
                wf = wf.detach()
            if wf.device.type != "cpu":
                wf = wf.cpu()
            if wf.dtype != torch.float32:
                wf = wf.to(torch.float32)
            if wf.ndim == 3 and wf.shape[0] == 1:
                wf = wf.squeeze(0)           # (C, T)
            if wf.ndim == 1:
                wf = wf.unsqueeze(0)         # (1, T)
            wf = wf.contiguous()

        # ---- n_steps == 0 is full bypass (shape adjustment only)----
        if int(n_steps) == 0:
            out = self._to_bct(wf)           # (1, 1, T)
            return ({"waveform": out, "sample_rate": sample_rate}, )

        # ---- resolve STFT params ----
        if n_fft < 0:
            n_fft = 512
        if win_length < 0:
            win_length = n_fft
        if hop_length < 0:
            hop_length = max(1, win_length // 4)

        # ---- pitch factor r; time-stretch by ts=1/r, then resample back ----
        r = 2.0 ** (float(n_steps) / float(bins_per_octave))
        ts = 1.0 / r

        with torch.no_grad():
            stretched = self._time_stretch_phase_vocoder(
                wf, int(n_fft), int(win_length), int(hop_length), rate=ts
            )                                # (C, T')
            out = self._linear_resample_len(stretched, new_len=wf.shape[-1])  # (C, T)

        del stretched
        gc.collect()

        # ---- FINAL: force (1, 1, T) for PreviewAudio ----
        out = self._to_bct(out)              # (1, 1, T)

        new_audio = {"waveform": out, "sample_rate": sample_rate}
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
        m.update(AudioPitchMono._audio_digest(audio))
        for v in (n_steps, bins_per_octave, n_fft, win_length, hop_length):
            m.update(int(v).to_bytes(8, "little", signed=True))
        return m.hexdigest()
