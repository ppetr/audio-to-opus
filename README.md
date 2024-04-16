# Reduce the size of audio files by converting them to the [Opus audio format](https://en.wikipedia.org/wiki/Opus_(audio_format))

_*Disclaimer:* This is not an officially supported Google product._

This is expecially convenient for audio-books that are often encoded with
unnecessarily high bandwidth. And Opus is very well suited for low-bandwidth
speech encoding.

The script first checks the bandwidth of an input file using FFmpeg's
[`ffprobe`](https://ffmpeg.org/ffprobe.html). If it's already low enough (at
most twice the target), it just creates a symlink to it. Otherwise it
re-encodes it using `ffmpeg` (or
[`ffmpeg-normalize`](https://github.com/slhck/ffmpeg-normalize) if present).
This makes the script [idempotent](https://en.wikipedia.org/wiki/Idempotence).

# Installation

Prerequisites:

- Installed [`pipx`](https://pipx.pypa.io/stable/).
- Installed [`ffmpeg`](https://ffmpeg.org/download.html).

After checking out the repository run this command inside the checked out
directory:

```sh
pipx install .
```

Append `--force` if reinstalling over a previous version.

## Usage

```sh
audio2opus [-h] [--bitrate BITRATE] [--samplerate SAMPLERATE] input output
```

## Contributions

Please see [Code of Conduct](docs/code-of-conduct.md) and
[Contributing](docs/contributing.md).
