import os
import re
import shutil
import speech_recognition as sr
import moviepy.editor as mp

from datetime import datetime
from googletrans import Translator
from pydub import AudioSegment
from pydub.silence import split_on_silence


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def check_yt_dlp():
    if not shutil.which('yt-dlp'):
        print('> Downloading yt-dlp...\n')

        if not os.path.exists('C:\\Softwares\\yt-dlp'):
            os.makedirs('C:\\Softwares\\yt-dlp')

        os.system(
            'curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -o C:\\Softwares\\yt-dlp\\yt-dlp.exe'
        )

        print('\n> yt-dlp downloaded successfully. Adding to the path....')

        os.system(
            """
            for /f "skip=2 tokens=3*" %a in ('reg query HKCU\Environment /v PATH') do @if [%b]==[] ( @setx PATH "%~a;C:\\Softwares\\yt-dlp" ) else ( @setx PATH "%~a %~b;C:\\Softwares\\yt-dlp" )
            """
        )

        input('\n> Path updated successfully. Please rerun the script.')
        quit()


def get_video(url: str) -> 'tuple[list[str], str]':
    spacing = lambda x, y=20: y - len(x)

    video_properties = [['code', 'ext', 'type', 'quality', 'size']]
    codes = []

    result = os.popen(f'yt-dlp -F "{url}" --compat-options list-formats').readlines()[
        4:
    ]

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

        if not re.match('https://(www.)?youtube.com/watch\?v=.+', url.strip()):
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

        print(result)
        if msg:
            print(msg)
            msg = ''

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
    r = sr.Recognizer()

    sound = AudioSegment.from_wav(path)
    chunks = split_on_silence(
        sound,
        min_silence_len=500,
        silence_thresh=sound.dBFS - 14,
        keep_silence=500,
    )

    chunks_folder = "temp_chunks"

    if not os.path.isdir(chunks_folder):
        os.mkdir(chunks_folder)

    full_text = ''

    for i, audio_chunk in enumerate(chunks, 1):
        chunk_filename = os.path.join(chunks_folder, f"chunk_{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")

        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError:
                print(f"Could not understand audio. Skipping {chunk_filename}")
            else:
                text = f"{text.capitalize()}. "
                print(f'{chunk_filename}: {text}')
                full_text += text

    shutil.rmtree(chunks_folder)
    os.remove('audio.wav')

    return full_text


def normalize_transcript(
    current: str = 'english_transcript.txt',
    paragraph_break: int = 5,
    line_break: int = 15,
) -> None:
    all_words = []

    paragraph = 1
    counter = 1

    with open(current, 'r+') as f:
        for line in f:
            line = line.split(' ')
            all_words.extend(line)

        f.seek(0)
        f.truncate()

        for word in all_words:
            if counter == line_break:
                f.write(word.strip('\n') + "\n")
                paragraph += 1
                counter = 0
            else:
                f.write(word.strip('\n') + " ")

            if paragraph == paragraph_break + 1:
                f.write("\n")
                paragraph = 1

            counter += 1


def translate_transcript():
    translator = Translator()

    normalize_transcript()

    with open('english_transcript.txt', 'r') as f, open(
        'indonesian_transcript.txt', 'w'
    ) as j:
        raw = f.read()

        if len(raw) > 5000:
            for i in range(0, len(raw), 5000):
                text = raw[i : i + 5000]
                translation = translator.translate(text, src='en', dest='id')
                j.write(translation.text)
        else:
            translation = translator.translate(raw, src='en', dest='id')
            j.write(translation.text)


def main():
    check_yt_dlp()

    os.chdir(os.path.join(os.path.expanduser('~'), 'Downloads'))

    unique = datetime.now().strftime('%H%M%S')

    url = get_url()
    choice = get_code(url)

    print('> Downloading the video...\n')

    os.system(
        f'yt-dlp {f"-f {choice}" if choice else ""} -o "{unique} - %(title)s.%(ext)s" {url}'
    )

    old_filename = [file for file in os.listdir() if file.startswith(f'{unique}')][0]
    new_filename, ext = re.findall(r'\d+\s-\s(.+)(\..+)', old_filename)[0]

    video_name = f'video{ext}'

    if os.path.exists(new_filename):
        shutil.rmtree(new_filename)

    os.makedirs(new_filename)
    shutil.move(old_filename, os.path.join(new_filename, video_name))

    os.chdir(new_filename)

    print('\n> Converting the video to audio...\n')

    audio_clip = mp.VideoFileClip(video_name)
    audio_clip.audio.write_audiofile(f'audio.wav')

    print(
        '\n> Transcribing the audio... This might take a while depending on how long the video!\n'
    )

    text = get_large_audio_transcription('audio.wav')

    with open('english_transcript.txt', 'w') as f:
        f.write(text)

    translate_transcript()

    print(f'\n> ✅ Finished! Saved to {os.path.abspath(os.getcwd())}')

    os.system('explorer .')

    input('\n> Press enter to exit...')


if __name__ == '__main__':
    main()
