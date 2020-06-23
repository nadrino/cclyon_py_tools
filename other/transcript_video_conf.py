#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.utils import make_chunks
import os
import speech_recognition as sr
import time
from threading import Thread
import cclyon_toolbox_lib as toolbox
from tqdm import tqdm
import threading

# file_path = "/Users/ablanche/Movies/OBS/2020-06-02 09-07-47.mkv"
file_path = "\"/Users/ablanche/Movies/Franck_Lepage_Incultures_1.mp4\""
# file_path = "/Users/ablanche/Movies/OBS/2020-05-15 14-17-03.mkv"
# file_path = "/Users/ablanche/Movies/OBS/2020-05-19 15-33-33.mkv"
# file_path = "/Users/ablanche/Movies/OBS/2020-05-19 16-34-04.mkv"
audio_chanel = "0:1"
speech_language = "fr-FR"
# speech_language= "en-US"

# split_by_option = "silences"
split_by_option = "duration"
chunk_length_ms = 15000  # pydub calculates in millisec
# chunk_length_ms = 20000  # pydub calculates in millisec

sr_algo = "google"
# sr_algo = "sphinx"

toolbox.nb_threads = 8

# Define a function to normalize a chunk to a target amplitude.
def match_target_amplitude(aChunk, target_dBFS):
    """ Normalize given audio chunk """
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)


file_name = file_path.split("/")[-1].split(".")[0]
file_name = "_".join(file_name.split(" "))

# Export all of the individual chunks as wav files
output_folder = os.getenv("TEMP_DIR") + "/transcript/" + file_name + "_" + speech_language + "_" + split_by_option + "/"
chunks_subfolder = output_folder + "chunks/"
toolbox.mkdir(chunks_subfolder)
os.system("rm " + chunks_subfolder + "/*")

audio_file_path = output_folder + file_name + ".wav"

# ffmpeg -i "2020-05-15 14-17-03.mkv"
# to find audio chanel

if not os.path.isfile(audio_file_path + ".mp3"):
    os.system("rm " + audio_file_path)
    os.system("ffmpeg -i \"" + file_path + "\" -map " + audio_chanel + " -acodec pcm_s16le -ac 2 " + audio_file_path)

    full_length_audio_file = AudioSegment.from_file(audio_file_path, "wav")
    print(toolbox.info, "Converting to mp3...")
    full_length_audio_file.export(audio_file_path + ".mp3",bitrate="192k",format="mp3")
    os.system("rm " + audio_file_path)

full_length_audio_file = AudioSegment.from_file(audio_file_path + ".mp3", "mp3")



if split_by_option == "silences":
    # Split track where the silence is 2 seconds or more and get chunks using
    # the imported function.
    print(toolbox.info, "Splitting audio file by silence moments...")
    chunks = split_on_silence (
        # Use the loaded audio.
        full_length_audio_file

        # Specify that a silent chunk must be at least 2 seconds or 2000 ms long.
        # , min_silence_len = 2000
        , min_silence_len = 3000

        # Consider a chunk silent if it's quieter than -16 dBFS.
        # (You may want to adjust this parameter.)
        # , silence_thresh = -16
        , silence_thresh = -24
        , keep_silence = 1000
    )
elif split_by_option == "duration":
    # chunks = make_chunks(full_length_audio_file, chunk_length_ms)  # Make chunks of one sec
    chunks = list()
    offset=0
    break_loop = False
    while not break_loop:
        end_index = offset+chunk_length_ms+3000
        if end_index > len(chunks):
            end_index = len(chunks)
            break_loop = True

        chunks.append(
            full_length_audio_file[offset:end_index]
        )  # add extra 2s for speech recognition

        offset += chunk_length_ms


    chunks = make_chunks(full_length_audio_file, chunk_length_ms)  # Make chunks of one sec

html_file_path = output_folder + "transcript_output.html"
def write_html_file(content_):
    with open(html_file_path, 'w') as out_file:
        out_file.write(content_)


html_header_lines = list()
html_header_lines.append("<!DOCTYPE html>")
html_header_lines.append("<html>")
html_header_lines.append("<head>")
html_header_lines.append("<meta charset=\"utf-8\"/>")
html_header_lines.append("<style>")
html_header_lines.append("table, th, td {")
html_header_lines.append("  border: 1px solid black;")
html_header_lines.append("  border-collapse: collapse;")
html_header_lines.append("}")
html_header_lines.append("tr:nth-child(even) {background-color: #f2f2f2;}")
html_header_lines.append("</style>")
html_header_lines.append("</head>")
html_header_lines.append("<body>")
full_audio_relative_path = audio_file_path.replace("/".join(html_file_path.split("/")[0:-1]), ".")
html_header_lines.append("<h2>Transcript de la vidéo-conf : " + "<a href=\"" + full_audio_relative_path + ".mp3" + "\">" + file_name + "</a></td></h2>")
html_header_lines.append("<table style=\"width:100%\">")
html_header = "\n".join(html_header_lines)

html_footer_lines = list()
html_footer_lines.append("</table>")
html_footer_lines.append("</body>")
html_footer_lines.append("</html>")
html_footer = "\n".join(html_footer_lines)


print(toolbox.info, "Reading chunks...")
html_body_lines = list()
chunk_relative_path_list = list()

lock = threading.Lock()

def process(i_file):

    chunk = chunks[i_file]
    chunk_file_name = chunks_subfolder + "chunk{0}.wav".format(i_file)
    # print("Processing:", chunk_file_name)

    # add silence both sides
    # if split_by_option == "duration":
    silence_chunk = AudioSegment.silent(duration=1000)
    audio_chunk = silence_chunk + chunk + silence_chunk
    # Normalize the entire chunk.
    audio_chunk = match_target_amplitude(chunk, -20.0)

    # uncompressed
    audio_chunk.export(chunk_file_name, format="wav")
    audio_chunk.export(chunk_file_name + ".mp3",bitrate="192k",format="mp3")

    # Speech recognition
    r = sr.Recognizer()
    with sr.AudioFile(chunk_file_name) as source:
        audio = r.record(source)

    line_transcript = ""
    try:
        if sr_algo == "google":
            line_transcript = r.recognize_google(audio, language=speech_language)
        elif sr_algo == "google_cloud": # paywall
            line_transcript = r.recognize_google_cloud(audio, language=speech_language)
        # elif sr_algo == "bing":
        #     line_transcript = r.recognize_bing(audio, language=speech_language)
        # elif sr_algo == "ibm":
        #     line_transcript = r.recognize_ibm(audio, language=speech_language)
        # elif sr_algo == "houndify": # en only
        #     line_transcript = r.recognize_houndify(audio)
        elif sr_algo == "sphinx":
            line_transcript = r.recognize_sphinx(audio, language=speech_language)
        # elif sr_algo == "wit": # en only
        #     line_transcript = r.recognize_wit(audio)
    except sr.UnknownValueError:
        line_transcript = "sr.UnknownValueError"
    except Exception as e:
        line_transcript = "Exception: " + str(e)

    print(toolbox.info + line_transcript)

    chunk_relative_path = chunk_file_name.replace("/".join(html_file_path.split("/")[0:-1]), ".")
    html_table_line = ""
    html_table_line += "  <tr>\n"
    html_table_line += "    <th>" + line_transcript + "</th>\n"
    html_table_line += "    <td><a href=\"" + chunk_relative_path + ".mp3" + "\">" + chunk_file_name.split("/")[
        -1] + "</a></td>\n"
    html_table_line += "  </tr>\n"

    with lock:
        global html_body_lines, chunk_relative_path_list
        html_body_lines = list(html_body_lines)
        chunk_relative_path_list = list(chunk_relative_path_list)

        chunk_relative_path_list.append(i_file)
        html_body_lines.append(html_table_line)

        chunk_relative_path_list, html_body_lines = zip(*sorted(zip(chunk_relative_path_list, html_body_lines)))

        html_file_content = html_header
        html_file_content += "\n"
        html_file_content += "\n".join(html_body_lines)
        html_file_content += "\n"
        html_file_content += html_footer
        html_file_content += "\n"

        # prevent interrupt with CTRL-C while writing
        a = Thread(target=write_html_file, args=[html_file_content])
        a.start()
        a.join()

    os.remove(chunk_file_name)

toolbox.multithread_processing(process, range(len(chunks)))

print(toolbox.info, "html output :", html_file_path)
