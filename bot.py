import random
from keras.models import load_model
import keras
import numpy as np
import pickle
import discord
import os
import requests
import json
import nltk
from nltk.stem import WordNetLemmatizer
from dotenv import load_dotenv
import wikipedia
import wolframalpha
import webbrowser
from googlesearch import search
import datetime
import pyowm


load_dotenv()
print("Imported")
lemmatizer = WordNetLemmatizer()
model = load_model('chatbot_model.h5')
TOKEN = os.getenv("DISCORD_TOKEN")
APIid = os.getenv("APIid")
owmkey = os.getenv("owmkey")
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
client = discord.Client()
clientWA = wolframalpha.Client(APIid)
owm = pyowm.OWM(owmkey)


jsontimetable = open('timetable.json')
timetabledict = json.load(jsontimetable)


sub2prof = {"Engineering Graphics": "Ravindra Pawarkar", "Effective Communication": "Madhumita Banerjee", "Biology": "Tejaswini Pachpor", "Basics Mechanical Engineering": "Heramb Phadake", "HDPC": "Sheetal Vij", "Basic Civil Engineering": "Vrunda Agarkar", "Physics": "Dr. Prasanta Ghosh",
            "Workshop Practices (LAB)": "Prashant Patane", "Integral Calculus": "Kundan Nagare", "Integral Calculus (Tutorial)": "Kundan Nagare", "Physics (Tutorial)": "Dr. Prasanta Ghosh", "Engineering Graphics (LAB)": "Ravindra Pawarkar", "Effective Communication (LAB)": "Anshul Haldar", "Basics Mechanical Engineering (LAB)": "Heramb Phadake", "Physics (LAB)": "Dr. Prasanta Ghosh", "Basic Civil Engineering (LAB)": "Vrunda Agarkar"}


def checktimetable():
    day_today = datetime.datetime.today().strftime('%A')
    reply = ''
    slotfound = False

    now = datetime.datetime.now()

    now = now.strftime("%H:%M:%S")
    now = datetime.time(int(now.split(':')[0]), int(
        now.split(':')[1]), int(now.split(':')[2]))

    if(day_today == 'Sunday'):
        reply = "NO lectures on sunday"

    for day in timetabledict:
        if day == day_today:
            for slot in timetabledict[day]:
                start = datetime.time(
                    int(slot.split(' - ')[0].split(':')[0]), int(slot.split(' - ')[0].split(':')[1]))
                end = datetime.time(
                    int(slot.split(' - ')[1].split(':')[0]), int(slot.split(' - ')[1].split(':')[1]))

                if(start <= now <= end):
                    slotfound = True
                    print("--------")
                    print("this is the current slot")
                    print("--------")
                    print(start)
                    print("\n")
                    print(timetabledict[day][slot])
                    print("\n")
                    print(end)
                    print("--------")
                    reply = f"Current lecture is {timetabledict[day][slot]} by {sub2prof[timetabledict[day][slot]]} which started at {start} and will end at {end}"

    if slotfound == False:
        reply = "Lectures haven't started yet or are over for the day."

        start = datetime.time(int(list(timetabledict[day_today])[0].split(
            ' - ')[0].split(':')[0]), int(list(timetabledict[day_today])[0].split(' - ')[0].split(':')[1]))
        end = datetime.time(int(list(timetabledict[day_today])[-1].split(' - ')[1].split(
            ':')[0]), int(list(timetabledict[day_today])[-1].split(' - ')[1].split(':')[1]))

        if start > now:
            reply = "Lectures haven't started yet today."

        elif now > end:
            reply = "Lectures have ended for the day."

    return(reply)


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [
        lemmatizer.lemmatize(word.lower()) for word in sentence_words
    ]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence


def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return (np.array(bag))


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if (i['tag'] == tag):
            result = random.choice(i['responses'])
            break
    return result


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " \t\t\t\n-" + json_data[0]['a']
    return (quote)


unlocked = False


class MyClient(discord.Client):
    async def on_message(self, message):
        msg = message.content
        global unlocked
        if message.content == 'unlock':
            print(";__;")
            unlocked = True
            await message.reply("saypls command is now unlocked")

        if message.content == 'lock':
            unlocked = False
            await message.reply("saypls command is now locked")

        if message.author.id == self.user.id:
            return

        if (unlocked):
            if message.content.startswith('inspire'):
                await message.channel.send(get_quote())
            elif message.content.startswith('wiki'):
                t = message.content.split()
                string = ' '.join(t[1:])
                await message.channel.send(wikipedia.summary(string, sentences=2))
            elif message.content.startswith('google') or message.content.startswith('search'):
                t = message.content.split()
                query = ' '.join(t[1:])
                for j in search(query, tld="co.in", num=2, stop=2, pause=2):
                    await message.reply(j)
            elif (message.content == 'quit'):
                exit()
            elif (message.content.startswith("")):
                ints = predict_class(msg, model)
                tag = ints[0]['intent']
                res = getResponse(ints, intents)
                await message.channel.send(res.format(message))
                if tag == "news":
                    for j in search("Top Headlines for today", tld="co.in", num=1, stop=1, pause=2):
                        await message.reply(j)

                if ints[0]['intent'] == 'Timetable':
                    reply = checktimetable()
                    await message.reply(reply)
                elif ints[0]['intent'] == 'weather':
                    weather = owm.weather_at_place('Pune')
                    w = weather.get_weather()
                    tempdict = w.get_temperature('celsius')
                    reply = f"Temperature right now is {tempdict['temp']}°C, today's maximum will be {tempdict['temp_max']}°C and minimum will be {tempdict['temp_min']}°C ."
                    await message.reply(reply)

                if (message.content.startswith('solve')):
                    question = message.content[6:]
                    res = clientWA.query(question)
                    answer = next(res.results).text
                    await message.reply("Here is the result to your query: ")
                    await message.channel.send(answer)
                    res.clear()


client = MyClient()
client.run(TOKEN)
