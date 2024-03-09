import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import pytz
from llama_cpp import Llama
from preprompts import epicac_prompt
from pprint import pprint
import re
import time
import os

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

model = Llama(model_path='models/mistral-7b-instruct-v0.2.Q4_K_M.gguf', n_ctx=4096,
              n_gpu_layers=-1,
              verbose=False,
              chat_format='mistral-instruct')

sys_prompt = epicac_prompt
guild = None


def remove_text_inside_brackets(text):
    # Remove text inside <>
    cleaned_text = re.sub("<[^>]*>", "", text)
    return cleaned_text



@bot.event
async def on_ready():
    global guild
    for g in bot.guilds:
        guild = g


async def fetch_last_messages(channel, limit=100):
    # Fetch the last 'limit' messages from the channel
    messages = []

    # Asynchronously iterate through the channel's history and collect messages
    async for message in channel.history(limit=limit):
        messages.append(message)

    utc_zone = pytz.utc
    one_hour_ago = datetime.now(utc_zone) - timedelta(hours=1)
    # recent_messages = [msg.content for msg in messages if msg.created_at > one_hour_ago]
    recent_messages = [
        {'username': msg.author.name,
         'content': remove_text_inside_brackets(msg.content)}
        for msg in messages if msg.created_at > one_hour_ago
    ]

    # Return the last 5 messages, or all of them if there are fewer than 5
    return recent_messages[::-1][-5:]


async def generate_response(messages):
    # Placeholder for your LLM-based response generation logic
    # This should take the messages as input and return a generated response
    chat_messages = [{'role': 'user', 'content': sys_prompt}]
    for messages in messages:
        if messages['username'] == 'Epicac':
            chat_messages.append({'role': 'assistant', 'content': messages['content']})
        else:
            chat_messages.append({'role': 'user', 'content': messages['content']})



    pprint(chat_messages[1:])
    time.sleep(15)
    response = model.create_chat_completion(chat_messages)
    pprint(response)
    return response['choices'][0]['message']['content'][:1500] + f'<@1215015266505855037>'


@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Example command to trigger response generation
    # if 'epicac' in message.content:
    if bot.user in message.mentions:
        last_messages = await fetch_last_messages(message.channel)
        response = await generate_response(last_messages)
        await message.channel.send(response)

    # Process commands
    # await bot.process_commands(message)

#get env var EPICAC
epicac = os.getenv("EPICAC")

bot.run(epicac)

