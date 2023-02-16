from typing import Literal, Optional
import discord
from discord.ext import commands
from discord.ext.commands import Greedy, Context  # or a subclass of yours
import os
import openai

# OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Discord settings
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


# Do something when bot see new messages.
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Send hello message when somebody send hello bot!
    if message.content.lower() == "hello bot!":
        await message.channel.send(f'Hello, dear {message.author.mention}!')

    # Without it, bot will ignore all commands.
    await bot.process_commands(message)


# Taken from here https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
        ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


# This command allows user to ask davinci AI to answer a question as friend.
@bot.hybrid_command()
async def ask(ctx, *, question):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"You are a friend. And your best friend asked you: {question}, answer to him. Start with capitalize letter.",
            temperature=0.5,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["You:"]
        )
        answer = response.choices[0].text
    except discord.ext.commands.errors.HybridCommandError:
        answer = "Sorry, I cant answer your question. :("
    finally:
        await ctx.send(answer)


if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_TOKEN"))
