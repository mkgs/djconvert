from pydub import AudioSegment
import music_tag
import os


MAX_FRAME_RATE = 48000
MAX_SAMPLE_WIDTH = 3
MAX_BITS = 24


def process_dir(in_dir):

    for root, dirs, files in os.walk(in_dir):
        print(f'reading {root}')
        for name in files:
            full_name = os.path.join(root, name)
            process_file(full_name, full_name)
        for name in dirs:
            process_dir(os.path.join(root, name))


def process_file(in_file, out_file):

    _, file_ext = os.path.splitext(in_file)

    if file_ext in ['.wav', '.WAV']:
        pass
    elif file_ext in ['.aiff', '.AIFF']:
        pass
    else:
        return False

    metadata = music_tag.load_file(in_file)

    rate_ok = metadata['#sample_rate'].value <= MAX_FRAME_RATE
    bits_ok = metadata['#bits_per_sample'].value <= MAX_BITS

    if rate_ok and bits_ok:
        return False

    print(f'   converting {in_file}')

    sound = AudioSegment.from_file(in_file)
    processed = False
    if sound.frame_rate > MAX_FRAME_RATE:
        print(f'      {sound.frame_rate}Hz -> {MAX_FRAME_RATE}Hz')
        sound.set_frame_rate(MAX_FRAME_RATE)
        processed = True
    if sound.sample_width > MAX_SAMPLE_WIDTH:
        print(f'      {sound.sample_width * 8}bit -> {MAX_SAMPLE_WIDTH * 8}bit')
        sound.set_sample_width(MAX_SAMPLE_WIDTH)
        processed = True
    if processed:
        sound.export(out_file)
        if file_ext in ['.aiff', '.AIFF']:
            newdata = music_tag.load_file(out_file)
            for k in metadata.tag_map.keys():
                if k.startswith('#'):
                    continue
                newdata[k] = metadata[k].value
            newdata.save()
    return processed
