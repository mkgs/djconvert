from pydub import AudioSegment
import music_tag
import mutagen.aiff
import mutagen.wave


MAX_FRAME_RATE = 48000
MAX_SAMPLE_WIDTH = 3
MAX_BITS = 24


def process_file(in_file, out_file):

    if in_file.endswith('.wav') or in_file.endswith('.WAV'):
        metadata = mutagen.wave.Open(in_file)
        id3 = None
    elif in_file.endswith('.aiff') or in_file.endswith('.AIFF'):
        metadata = mutagen.aiff.Open(in_file)
        id3 = music_tag.load_file(in_file)
    else:
        return

    rate_ok = metadata.info.sample_rate <= MAX_FRAME_RATE
    bits_ok = metadata.info.bits_per_sample <= MAX_BITS

    if rate_ok and bits_ok:
        return

    sound = AudioSegment.from_file(in_file)
    processed = False
    if sound.frame_rate > MAX_FRAME_RATE:
        sound.set_frame_rate(MAX_FRAME_RATE)
        processed = True
    if sound.sample_width > MAX_SAMPLE_WIDTH:
        sound.set_sample_width(MAX_SAMPLE_WIDTH)
        processed = True
    if processed:
        sound.export(out_file)
        if id3:
            id3.save(out_file)
