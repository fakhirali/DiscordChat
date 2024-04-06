import discord
from discord.ext import commands
from datetime import datetime, timedelta
import pytz
import os
import requests
import pandas as pd
from pprint import pprint
from utils import truncate_message, remove_mentions

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
general_prompt = '''Keep your answers short.'''

chatbots = dict()  # name -> system prompt

# loading the chatbot system prompts from the csv file
if os.path.exists('chatbot_system_prompts.csv'):
    df = pd.read_csv('chatbot_system_prompts.csv')
    for index, row in df.iterrows():
        chatbots[row['name']] = row['system_prompt']

pprint(chatbots['epicac'])


def send_message_to_chatbot(name, last_messages):
    if name in chatbots:
        chat_messages = [{'role': 'user', 'content': chatbots[name]}]
        for messages in last_messages:
            if messages['username'] == 'Epicac':
                chat_messages.append({'role': 'assistant', 'content': messages['content']})
            else:
                chat_messages.append({'role': 'user', 'content': messages['username'] + ':' + messages['content']})

        pprint(chat_messages)
        url = 'http://localhost:8000/chat'
        data = chat_messages
        response = requests.post(url, json=data)
        response = truncate_message(response.json()['response'])
        return response
    else:
        return f"Chatbot '{name}' not found."


async def fetch_last_messages(channel, limit=20):
    messages = []

    async for message in channel.history(limit=limit):
        messages.append(message)

    utc_zone = pytz.utc
    one_hour_ago = datetime.now(utc_zone) - timedelta(hours=1)
    recent_messages = [
        {'username': msg.author.display_name,
         'content': remove_mentions(msg.content)}
        for msg in messages if msg.created_at > one_hour_ago
    ]

    # Return the last 5 messages, or all of them if there are fewer than 5
    return recent_messages[::-1][-3:]


@bot.command(name='sys_show')
async def sys_show(ctx):
    bot_name = 'epicac'
    if bot_name not in chatbots:
        response = f"Chatbot '{bot_name}' not found."
    else:
        response = f'The system prompt of {bot_name}:\n' + chatbots[bot_name]
    await ctx.send(response)


@bot.event
async def on_message(message):
    target_channel = 1216433219524886589
    if message.author == bot.user or message.channel.id != target_channel:
        return
    await bot.process_commands(message)
    bot_name = 'epicac'
    if bot.user in message.mentions:
        last_messages = await fetch_last_messages(message.channel)
        response = send_message_to_chatbot(bot_name, last_messages)
        await message.channel.send(response)


bot_token = os.getenv("EPICAC")

bot.run(bot_token)
