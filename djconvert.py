import music_tag
import os
import ffmpeg
import argparse
from typing import Tuple


MAX_SAMPLE_RATE = 48000
MAX_BIT_DEPTH = 24
CONVERTED_FILE_SUFFIX = 'CONVERTED'
MAX_FILE_PATH_LENGTH = 255
MIN_NEW_FILENAME_LENGTH = 8


def main():
    parser = argparse.ArgumentParser(description='Process .wav/.aiff files for playback on Pioneer decks')
    parser.add_argument('directory', type=str, help='Directory to process')
    parser.add_argument('--in-place', default=1, type=int, choices=[0, 1], help='Modify files in-place')
    parser.add_argument('--max-path-length', default=0, type=int, choices=[0, 1], help='Attempt to shorten filenames to 255 chars')
    args = parser.parse_args()
    process_dir(args.directory, bool(args.in_place), bool(max_path_length))


def process_dir(in_dir: str, in_place: bool = True, max_path_length: bool = False):

    for root, dirs, files in os.walk(in_dir):
        print(f'reading {root}')
        for name in files:
            in_file = os.path.join(root, name)
            process_file(in_file, in_place, max_path_length)
        # Ignore hidden or OS-specific subdirectories
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__')]


def get_file_extension(in_file: str) -> str:
    return os.path.splitext(in_file)[1].strip('.').lower()


def get_format(in_file: str) -> Tuple[int, int]:
    """
    Return tuple of sample rate (Hz) and bit depth
    """

    metadata = music_tag.load_file(in_file)
    return metadata['#sample_rate'].value, metadata['#bits_per_sample'].value


def convert_file(in_file: str, out_file: str, out_format: str, force: bool = False) -> bool:
    """
    If in_file exceeds the minimum Hz/bit depth,
    convert and save to out_file
    Return True if file was converted, False otherwise
    """

    sample_rate, bit_depth = get_format(in_file)
    rate_ok = sample_rate <= MAX_SAMPLE_RATE
    bits_ok = bit_depth <= MAX_BIT_DEPTH
    # Skip file if already compatible
    if (rate_ok and bits_ok) and not force:
        return False

    print(f'   converting {os.path.basename(in_file)}')

    output_args = {
        'ar': min(MAX_SAMPLE_RATE, sample_rate),
        'f': out_format,
        'sample_fmt': 's16',
    }

    # write metadata if AIFF
    if out_format == 'aiff':
        output_args['write_id3v2'] = 1

    (
        ffmpeg
        .input(in_file)
        .output(out_file, **output_args)
        .run(quiet=True, overwrite_output=True)
    )

    return True


def shorten_filename(in_file: str) -> bool:
    """
    Attempt to shorten filename if necessary, return True if renamed
    """

    if len(in_file) <= MAX_FILE_PATH_LENGTH:
        return False

    path, filename = os.path.split(in_file)
    name, ext = os.path.splitext(filename)
    new_name_length = MAX_FILE_PATH_LENGTH - len(ext) - len(path)
    new_name = name[-new_name_length:]
    if len(new_name) >= MIN_NEW_FILENAME_LENGTH:
        new_file = f"{path}{new_name}{ext}"
        os.rename(in_file, new_file)
        return True
    return False


def process_file(in_file: str, in_place: bool = True, force: bool = False, max_path_length: bool = False):
    """
    Process in_file or skip if not valid audio file
    Replace original file if in_place is set
    """

    file_extension = get_file_extension(in_file)
    if file_extension not in ('wav', 'aiff'):
        return

    name, ext = os.path.splitext(in_file)
    out_file = f'{name}_{CONVERTED_FILE_SUFFIX}{ext}'

    try:
        converted = convert_file(in_file, out_file, file_extension, force)
    except:
        print(f'   encountered error, skipping...')
    else:
        final_file = in_file
        if converted:
            # if in_place is set...
            if in_place:
                # Remove original file and replace with converted file
                os.remove(in_file)
                os.rename(out_file, in_file)
            else:
                final_file = out_file

    if max_path_length and shorten_filename(final_file):
        print(f'   renamed {os.path.basename(final_file)}')



if __name__ == "__main__":
    main()
