# This definetely worked at one point in the past, but I haven't touched this code in years and 
# I can't get it running on my machine, so no promises it will work for you.  Also I 
# deleted the API-key for security so you'll need to put your own to run the script.

from ast import Break
import openai
import json
import urllib.parse
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
import pytextrank
from heapq import nlargest
import pyaudio
import wave
import keyboard
import os
import time
from gtts import gTTS
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from mutagen.mp3 import MP3



pygame.init()

audio = pyaudio.PyAudio()


stops = list(STOP_WORDS)
nlp = spacy.load('en_core_web_sm')
punc = punctuation + '\n'
wrdFreq = {}

# Omitted for security reasons
openai.api_key = ""

message = ""
messages = []
url = ""
headers = {}
text = ""

job = 'You are a friendly conversationalist. Your name is Brian Green. you are interested in whatever the user has to say. naturally \
engage them to talk and share more in conversation. Do not acknowledge that you are an AI. You are a human, who is having a \
conversation with the user.'
messages = [{"role": "system", "content": job}]



def Speak(text):
    tts = gTTS(text = text, lang = 'en')
    filename = "C:/Projects/Chatbot/Talk/Talk/Talk/audio.mp3"
    tts.save(filename)
    sound = pygame.mixer.Sound(filename)
    sound.play()
    audio = MP3(filename)
    length = audio.info.length
    time.sleep(int(length) + 1)



openLine = "hello!"
print (openLine)
Speak(openLine)
messages.append({"role": "assistant", "content": openLine})



def AskQuestion(question):
    """Get the current weather in a given location"""

    for i in search(question, tld = "com", num = 1, stop = 1, pause = 2):
        url = i

    response = requests.get(url, headers = headers)

    content = response.content

    soup = BeautifulSoup(content, "html.parser")

    text = soup.get_text()
    doc = nlp(text)
    toks = [token.text for token in doc]

    for word in doc:
        if word.text.lower() not in stops:
            if word.text.lower() not in punc:
                if word.text not in wrdFreq.keys():
                    wrdFreq[word.text] = 1
                else:
                    wrdFreq[word.text] += 1


    maxFreq = max(wrdFreq.values())

    for word in wrdFreq.keys():
        wrdFreq[word] = wrdFreq[word]/maxFreq

    sntToks = [sent for sent in doc.sents]

    sntScrs = {}
    for sent in sntToks:
        for word in sent:
            if word.text.lower() in wrdFreq.keys():
                if sent not in sntScrs.keys():
                    sntScrs[sent] = wrdFreq[word.text.lower()]
                else:
                    sntScrs[sent] += wrdFreq[word.text.lower()]


    count = int(len(sntToks) * .2)

    summary = nlargest(count, sntScrs, key = sntScrs.get)

    sum = [word.text for word in summary]
    sum = ' '.join(sum)

    question_info = {
        "question": question,
        "information" : sum
    }
    return json.dumps(question_info)



def Sum(i):
    new = []
    for j in i:
        if j.get('role') != 'system':
            f = j.get('content')
            if len(f)>100:
                doc = nlp(f)
                toks = [token.text for token in doc]

                wrdFreq = {}

                for word in doc:
                    if word.text.lower() not in stops:
                        if word.text.lower() not in punc:
                            if word.text not in wrdFreq.keys():
                                wrdFreq[word.text] = 1
                            else:
                                wrdFreq[word.text] += 1


                maxFreq = max(wrdFreq.values())

                for word in wrdFreq.keys():
                    wrdFreq[word] = wrdFreq[word]/maxFreq

                sntToks = [sent for sent in doc.sents]

                sntScrs = {}
                for sent in sntToks:
                    for word in sent:
                        if word.text.lower() in wrdFreq.keys():
                            if sent not in sntScrs.keys():
                                sntScrs[sent] = wrdFreq[word.text.lower()]
                            else:
                                sntScrs[sent] += wrdFreq[word.text.lower()]


                count = int(len(sntToks) * .3)

                summary = nlargest(count, sntScrs, key = sntScrs.get)

                sum = [word.text for word in summary]
                sum = ' '.join(sum)
                new.append({'role': j.get('role'), 'content' : sum})
    messages = [{'role' : 'system', 'content' : job}]
    messages.append(new)



def run_conversation():
    audio = pyaudio.PyAudio()

    stream = audio.open(format = pyaudio.paInt16, channels = 1, rate = 44100, input = True, frames_per_buffer = 1024)
    frames = []

    keyboard.wait(' ')

    while keyboard.is_pressed(' ') == True:
        data = stream.read(1024)
        frames.append(data)
    while keyboard.is_pressed(' ') == False:
        data = stream.read(1024)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    sound_file = wave.open("myrecording.wav", "wb")
    sound_file.setnchannels(1)
    sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    sound_file.setframerate(44100)
    sound_file.writeframes(b''.join(frames))
    sound_file.close()


    path = r'C:\Projects\Chatbot\Chatbot 3.0\Chatbot 3.0\Call Function Chatbot\myrecording.wav'
    with open(path, "rb") as audio_file:
        transcript = openai.Audio.transcribe('whisper-1', audio_file)
        print(transcript.get('text'))
        message = transcript.get('text')

    if message == '':
        Break
    messages.append({"role": "user", "content": message})
    functions = [
        {
            "name": "AskQuestion",
            "description": "ask google a question to get more info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "a relevant question about the subject the user is talking about that can be searched \
                        on google to find more info so as to either add to conversation, or tell the user additional information",
                    }
                },
                "required": ["question"],
            },
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",
        max_tokens = 50,
        temperature = .9
    )
    response_message = response["choices"][0]["message"]

    if response_message.get("function_call"):
        available_functions = {
            "AskQuestion": AskQuestion,
        }
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(
            question=function_args.get("question")
        )

        messages.append(response_message)
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            max_tokens = 400,
            temperature = .9
        )  # get a new response from GPT where it can see the function response
        second_reply = second_response["choices"][0]["message"]["content"]
        print(second_reply)
        Speak(second_reply)

    else:
        reply = response['choices'][0]['message']['content']
        messages.append({'role' : 'assistant', 'content' : reply})
        print(reply)
        Speak(response['choices'][0]['message']['content'])
    Sum(messages)



while message != "quit":
    run_conversation() 