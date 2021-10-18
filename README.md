# djconvert

Pioneer decks support .wav/.aiff playback at a maximum 48kHz/24bit.
This script recursively walks the input directory and converts applicable files to a compatible format.
Requires ffmpeg.

Example usage:
`python djconvert.py my_music_dir/ --in-place=1`
