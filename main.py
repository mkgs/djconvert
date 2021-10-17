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
    print(f'      loading...')

    sound = AudioSegment.from_file(in_file)
    processed = False
    sample_rate = str(min(MAX_FRAME_RATE, sound.frame_rate))
    if sound.frame_rate > MAX_FRAME_RATE:
        print(f'      {sound.frame_rate}Hz -> {MAX_FRAME_RATE}Hz')
        processed = True
    bit_depth = min(MAX_SAMPLE_WIDTH, sound.sample_width) * 8
    if bit_depth == 8:
        bit_depth = '-sample_fmt u8'
    elif bit_depth in (16, 32):
        bit_depth = f'-sample_fmt s{bit_depth}'
    elif bit_depth == 24:
        #bit_depth = '-c:a pcm_s24le'
        bit_depth = '-sample_fmt s16'
    else:
        raise NotImplemented()
    if sound.sample_width > MAX_SAMPLE_WIDTH:
        print(f'      {sound.sample_width * 8}bit -> {MAX_SAMPLE_WIDTH * 8}bit')
        processed = True
    if processed:
        print(f'      saving...')
        if file_ext in ['.aiff', '.AIFF']:
            sound.export(out_file, format='aiff', parameters=['-ar', sample_rate, '-sample_fmt', 's16'])
            newdata = music_tag.load_file(out_file)
            for k in metadata.tag_map.keys():
                if k.startswith('#') or k == 'artwork':
                    continue
                newdata[k] = metadata[k].value
            for filename in ('cover.jpg', 'cover.jpeg', 'cover.png'):
                filename = os.path.join(os.path.dirname(in_file), filename)
                if os.path.exists(filename):
                    try:
                        with open(filename, 'rb') as img_in:
                            newdata['artwork'] = img_in.read()
                            break
                    except Exception as e:
                        pass
            newdata.save()
        elif file_ext in ['.wav', '.WAV']:
            sound.export(out_file, format='wav', parameters=['-ar', sample_rate, '-sample_fmt', 's16'])
        else:
            raise NotImplemented()
    return processed
