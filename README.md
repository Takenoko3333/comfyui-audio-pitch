## Nodes...

- Audio Pitch (Mono)

## Install

Move to ComfyUI\custom_nodes

```
git clone https://github.com/Takenoko3333/comfyui-audio-pitch.git
```

Restart ComfyUI.

## How to Use

- Search for "Audio Pitch" in the Node Library and place the Audio Pitch (Mono) node.
- Adjusting the pitch is basically achieved by changing only the n_steps value. Increasing the value raises the pitch, while decreasing it lowers the pitch.
- The adjustment range for n_steps is -24 to +24.

## Examples

example_workflows\audio-pitch-sample.json

## Purpose

- Avoids memory leaks in torchaudio's PitchShift when using MMAudio output
- Stable pitch shifting processing in ComfyUI environments
- Mono processing optimization focused on integration with MMAudio

## Origin

- This project is based on audio-general-comfyui
- Originally licensed under the MIT License.
- Forked and modified to improve stability, reduce RAM usage, and ensure PreviewAudio compatibility.

## Main Changes

- Removed all torchaudio dependencies
- Implemented pure-CPU phase vocoder time-stretch
- Fixed RAM overflow issue when use MMAudio output on repeated execution
- Output shape fixed to (1, 1, T) (Mono)
- Added bypass at n_steps=0
- Default FFT size = 1024 (smoother output for short clips)

## License

- MIT
