#!/usr/bin/env python3

# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import typing

import ffmpeg_normalize
import prefixed


def which(path: typing.Union[str, bytes, os.PathLike]) -> str:
  binary = shutil.which(path)
  if binary is None:
    raise FileNotFoundError("Missing binary: {}".format(path))
  return binary


def ffprobe(path: typing.Union[str, bytes, os.PathLike]):
  proc = subprocess.run([
      which("ffprobe"), "-v", "quiet", "-print_format", "json", "-show_format",
      "-show_streams", path
  ],
                        capture_output=True,
                        check=True)
  return json.loads(proc.stdout)


def normalize(path: typing.Union[str, bytes, os.PathLike],
              output: typing.Union[str, bytes,
                                   os.PathLike], samplerate: int, bitrate: int):
  runner = ffmpeg_normalize.FFmpegNormalize(
      audio_codec="libopus",
      audio_bitrate=str(bitrate),
      sample_rate=str(samplerate),
      keep_lra_above_loudness_range_target=True,
      extra_output_options=["-map_metadata", "0"])
  runner.add_media_file(path, output)
  runner.run_normalization()


def main():
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--bitrate",
                      type=prefixed.Float,
                      default=32768,
                      help="The target bitrate.")
  parser.add_argument("--samplerate",
                      type=prefixed.Float,
                      default=48000,
                      help="The target sample rate - must be within the "
                      "acceptable range depending on --bitrate.")
  parser.add_argument("input", help="The input audio file.")
  parser.add_argument("output", help="The output OPUS audio file.")
  args = parser.parse_args()

  info = ffprobe(args.input)
  logging.debug("ffprobe result:\n%s", json.dumps(info, indent=2))
  try:
    bitrate = int(info["format"]["bit_rate"])
    samplerate = info["streams"][0].get("sample_rate")
  except (IndexError, KeyError) as ex:
    raise ValueError("ffprobe result: {}".format(info)) from ex
  print("Input bitrate: {}".format(bitrate))
  if bitrate <= 2 * args.bitrate:
    print("Target bitrate is already low enough (<= {})".format(2 *
                                                                args.bitrate))
    relative = os.path.relpath(args.input, start=os.path.dirname(args.output))
    try:
      os.unlink(args.output)
    except FileNotFoundError:
      pass
    os.symlink(relative, args.output)
  else:
    print("Input sample rate: {}".format(samplerate))
    samplerate = sys.maxsize if samplerate is None else int(samplerate)
    if samplerate != args.samplerate:
      print("Resampling to rate {}".format(args.samplerate))
      samplerate = args.samplerate
    normalize(args.input, args.output, int(samplerate), int(args.bitrate))


if __name__ == "__main__":
  main()
