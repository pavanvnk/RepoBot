import re
import discord

def check_dm_author(ctx):
    def predicate(message):
        return message.author == ctx.author and isinstance(message.channel, discord.DMChannel)

    return predicate

def url_name(url):
    pattern = r"https?://github.com/([^/]+)/([^/]+)"
    match = re.match(pattern, url)
    if match:
        owner = match.group(1)
        repo = match.group(2)
        return f"{owner}_{repo}"