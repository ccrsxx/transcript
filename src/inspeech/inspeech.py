import os
import re
import shutil
import speech_recognition as sr
import moviepy.editor as mp

from pydub import AudioSegment
from pydub.silence import split_on_silence


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_video(url):
    spacing = lambda x, y=20: y - len(x)

    video_properties = [['code', 'ext', 'type', 'quality', 'size']]
    codes = []

    result = os.popen(f'yt-dlp -F {url} --compat-options list-formats').readlines()[4:]

    for prop in result:
        if 'mhtml' in prop:
            continue
        video_code = re.findall(r'^\d+', prop)[0]
        video_ext = re.findall(r'^\d+\s+(\w+)\s', prop)[0]
        video_size = re.findall(r'(\d+\.?\d+\w+(\s\(best\))?)\n', prop)
        video_size = video_size[0][0] if video_size else 'Unknown (best)'
        video_quality = re.findall(r'only\s+(low|medium)|\d+x\d+\s+(\d{3,4}p)', prop)[0]
        video_quality = (
            'audio'
            if 'low' in video_quality or 'medium' in video_quality
            else video_quality[1]
        )
        video_type = re.findall('video only|audio only', prop)
        video_type = 'video & audio' if not video_type else video_type[0]
        video_properties.append(
            [video_code, video_ext, video_type, video_quality, video_size]
        )
        codes.append(video_code)

    items = []

    for video_info in video_properties:
        for j, item in enumerate(video_info):
            space = spacing(item) if j > 0 else spacing(item, 10)

            if j == 4:
                item = f'{item}{"":{space}}\n'
            else:
                item = f'{item}{"":{space}}'

            items.append(item)

    return codes, ''.join(items)


def get_url():
    url, msg = '', ''

    while not url:
        cls()

        if msg:
            print(msg)
            msg = ''

        try:
            url = input(
                'Enter Youtube Video URL ex. https://www.youtube.com/watch?v=dQw4w9WgXcQ\n> '
            )
        except KeyboardInterrupt:
            print('\n\nUser intrerupted the program. Exiting...')
            exit()

        if not re.match('https://(www.)?youtube.com/watch\?v=.+', url):
            msg = 'Invalid URL. Please try again.\n'
            url = ''
            continue

    cls()

    return url


def get_code(url: str) -> str:
    codes, result = get_video(url)

    choice, msg = '', ''

    while choice not in codes:
        cls()

        if msg:
            print(msg)
            msg = ''

        print(result)

        try:
            choice = input(
                f'Select video code to download? input "best" to get max quality\n> '
            )
        except KeyboardInterrupt:
            print('\n\nUser intrerupted the program. Exiting...')
            exit()

        if choice == 'best':
            choice = ''
            break
        elif not choice.isdigit():
            msg = 'Invalid input. Please enter a number.\n'
            continue

        msg = 'Invalid code. Please try again.\n'

    cls()

    return choice


def get_large_audio_transcription(path: str) -> str:
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """

    r = sr.Recognizer()

    sound = AudioSegment.from_wav(path)
    chunks = split_on_silence(
        sound,
        min_silence_len=500,
        silence_thresh=sound.dBFS - 14,
        keep_silence=500,
    )

    chunks_folder = "audio-chunks"

    if not os.path.isdir(chunks_folder):
        os.mkdir(chunks_folder)

    full_text = ""

    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(chunks_folder, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")

        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                pass
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                full_text += text
    shutil.rmtree('audio-chunks')

    return full_text


def main():
    # url = get_url()

    # choice = get_code(url)

    # os.system(f'yt-dlp {f"-f {choice}" if choice else ""} -o "dw_video.%(ext)s" {url}')

    filename = [file for file in os.listdir() if file.startswith('dw_video.')][0]

    print(filename)

    clip = mp.VideoFileClip(filename)
    clip.audio.write_audiofile(f'{filename}.wav')

    text = get_large_audio_transcription(f'{filename}.wav')
    text = text.replace('. ', '.\n')

    with open('transcript.txt', 'w') as f:
        f.write(text)


if __name__ == '__main__':
    main()
