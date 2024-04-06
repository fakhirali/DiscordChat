import discord
from discord.ext import commands
from datetime import datetime, timedelta
import pytz
import re
import os
import requests
import pandas as pd
from utils import truncate_message
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
general_prompt = '''Keep your answers short.'''

chatbots = dict()  # name -> system prompt

# loading the chatbot system prompts from the csv file
if os.path.exists('chatbot_system_prompts.csv'):
    df = pd.read_csv('chatbot_system_prompts.csv')
    for index, row in df.iterrows():
        chatbots[row['name']] = row['system_prompt']


def create_chatbot(name, system_prompt):
    chatbots[name] = system_prompt
    # saving the chatbot system prompts to the csv file
    df = pd.DataFrame(list(chatbots.items()), columns=['name', 'system_prompt'])
    df.to_csv('chatbot_system_prompts.csv', index=False)
    if name in chatbots:
        return f"Chatbot '{name}' system prompt updated"
    else:
        return f"Chatbot '{name}' created"


# Dummy function to simulate sending a message to a chatbot
def send_message_to_chatbot(name, last_messages):
    # Here, you'd implement the logic to send a message to the specified chatbot
    # For this example, we'll just return a dummy response
    if name in chatbots:
        chat_messages = [{'role': 'user', 'content': chatbots[name] + '\n' + general_prompt}]
        for messages in last_messages:
            chat_messages.append({'role': 'user', 'content': messages['content']})
        pprint(chat_messages)
        url = 'http://localhost:8000/chat'
        data = chat_messages
        response = requests.post(url, json=data)
        response = truncate_message(response.json()['response'])
        return response
    else:
        return f"Chatbot '{name}' not found."


def remove_text_inside_brackets(text):
    # Remove text inside <>
    cleaned_text = re.sub("<[^>]*>", "", text)
    return cleaned_text


async def fetch_last_messages(channel, limit=20):
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
    return recent_messages[::-1][-1:]


@bot.command(name='sys')
async def create_bot(ctx, bot_name, *, system_prompt):
    response = create_chatbot(bot_name, system_prompt)
    await ctx.send(response)


@bot.command(name='sys_show')
async def sys_show(ctx, bot_name):
    if bot_name not in chatbots:
        response = f"Chatbot '{bot_name}' not found."
    else:
        response = f'The system prompt of {bot_name}:\n' + chatbots[bot_name]
    await ctx.send(response)


@bot.event
async def on_message(message):
    target_channel = 1215008326253813830
    if message.author == bot.user or message.channel.id != target_channel:
        return
    await bot.process_commands(message)
    content = message.content
    if content.startswith('!'):
        parts = content[1:].split(' ', 1)
        if len(parts) == 2:
            bot_name, user_message = parts
            if bot_name in [command.name for command in bot.commands]:
                return
            # last_messages = await fetch_last_messages(message.channel)
            response = send_message_to_chatbot(bot_name, [{'content': user_message}])
            await message.channel.send(response)


bot_token = os.getenv("BOT")

bot.run(bot_token)
