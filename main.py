import os
import shutil
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

from auth_db import get_user_token, set_user_token
from utils import check_dm_author, url_name
from vector_db import load_to_db
from models import openai_embeddings
from chain import response_chain
from constants import TOKEN_PROMPTS

load_dotenv()

discord_token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)

git_repo_link = "https://github.com/pavanvnk/HealthXoxo"
repo_path = os.path.join(os.getcwd(), "cloned_repo")
chat_history = []

@bot.command()
async def set_token(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        user_id = ctx.author.id
        user_tokens = {}

        for token_name, prompt in TOKEN_PROMPTS.items():
            await ctx.send(prompt)

            try:
                msg = await bot.wait_for(
                    'message',
                    check=check_dm_author(ctx),
                    timeout=60
                )
                token = msg.content.strip()
                user_tokens[token_name] = token
            except asyncio.TimeoutError:
                await ctx.send("Token setup timed out. Please try again.")
                return
        
        set_user_token(user_id, user_tokens)

        await ctx.send("Tokens have been set successfully!")
    else:
        await ctx.send("Please use the !settokens command in a direct message (DM) with the bot.")

@bot.command()
async def git_link(ctx, repo_link):
    global git_repo_link
    git_repo_link = repo_link
    await ctx.send(f"Repository link has been set to: {repo_link}")

    user_id = ctx.author.id
    tokens = get_user_token(user_id)

    al_token = tokens.get('activeloop')
    al_org = tokens.get('activeloop_org')
    openai_api = tokens.get('openai')

    dataset_name = url_name(repo_link)

    db_path = f"hub://{al_org}/{dataset_name}"

    await load_to_db(
            repo_link,
            db_path,
            al_token,
            openai_embeddings(openai_api)
        )
    
    await ctx.send(f"{dataset_name} repository sucessfully loaded.")

@bot.command()
async def delete_git(ctx):
    try:
        shutil.rmtree(repo_path)
        await ctx.send("Repository deleted successfully.")
        global git_repo_link
        git_repo_link = None
    except Exception as e:
        await ctx.send(f"Error deleting repository: {e}")

@bot.command()
async def query(ctx, *, question):
    user_id = ctx.author.id
    tokens = get_user_token(user_id)
    al_token = tokens.get('activeloop')
    al_org = tokens.get('activeloop_org')
    openai_api = tokens.get('openai')
    ai21_api = tokens.get('ai21')

    dataset_name = url_name(git_repo_link)
    db_path = f"hub://{al_org}/{dataset_name}"

    qa = response_chain(
        db_path=db_path,
        embeddings=openai_embeddings(openai_api),
        ai21_token=ai21_api,
        al_token=al_token
    )

    result = qa({"question": question, "chat_history": chat_history})
    chat_history.append((question, result["answer"]))

    await ctx.send(f"{result['answer']}")

bot.run(discord_token)