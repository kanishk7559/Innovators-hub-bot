import discord
from discord.ext import commands
import os
import requests
import json



client= discord.Client()

def get_quote():
	response= requests.get("https://zenquotes.io/api/random")
	json_data = json.loads(response.text)
	quote= json_data[0]['q'] + " \t\t\n-" + json_data[0]['a']
	return(quote)

@client.event
async def on_ready():
	print("Working !")

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if msg.startswith('#inspire'):
    quote = get_quote()
    await message.channel.send(quote)
  if msg.startswith('#help'):
    quote = get_quote()
    await message.channel.send("This Bot is under development")
client.run("<< BOT TOKEN >>")
