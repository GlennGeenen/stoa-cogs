import copy
import discord

from redbot.core import Config, commands, checks
from redbot.core.utils.chat_formatting import pagify

class StoaReact(commands.Cog):
    """Create automatic reactions when trigger words are typed in chat"""

    default_guild_settings = {
        "reactions": {},
        "channels": []
    }

    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier=685743681, force_registration=True)
        self.conf.register_guild(
            **self.default_guild_settings
        )

    @checks.mod_or_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(name="addstoareact")
    async def addstoareact(self, ctx, word, response):
        """Add an auto reaction to a word"""
        guild = ctx.message.guild
        message = ctx.message
        await self.create_smart_reaction(guild, word, response, message)

    @checks.mod_or_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(name="delstoareact")
    async def delstoareact(self, ctx, word, response):
        """Delete an auto reaction to a word"""
        guild = ctx.message.guild
        message = ctx.message
        await self.remove_smart_reaction(guild, word, response, message)

    @checks.mod_or_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(name="liststoareact")
    async def liststoareact(self, ctx):
        """List reactions for this server"""
        reactions = await self.conf.guild(ctx.guild).reactions()
        msg = f"Smart Reactions for {ctx.guild.name}:\n"
        for response in reactions:
            for command in reactions[response]:
                msg += f"{response}: {command}\n"
        for page in pagify(msg, delims=["\n"]):
            await ctx.send(page)

    async def create_smart_reaction(self, guild, word, response, message):
        try:
            await message.channel.send("Add reaction **{}** for trigger **{}**.".format(
                response, word
            ))
            reactions = await self.conf.guild(guild).reactions()
            if response in reactions:
                if word.lower() in reactions[response]:
                    await message.channel.send("This smart reaction already exists.")
                    return
                reactions[response].append(word.lower())
            else:
                reactions[response] = [word.lower()]
            await self.conf.guild(guild).reactions.set(reactions)
            await message.channel.send("Successfully added this reaction.")

        except (discord.errors.HTTPException, discord.errors.InvalidArgument):
            await message.channel.send("Oops, I failed to add this reaction.")

    async def remove_smart_reaction(self, guild, word, response, message):
        try:
            await message.channel.send("Remove reaction **{}** for trigger **{}**.".format(
                response, word
            ))
            reactions = await self.conf.guild(guild).reactions()
            if response in reactions:
                if word.lower() in reactions[response]:
                    reactions[response].remove(word.lower())
                    await self.conf.guild(guild).reactions.set(reactions)
                    await message.channel.send("Removed this smart reaction.")
                else:
                    await message.channel.send("That response is not used as a reaction for that word.")
            else:
                await message.channel.send("There are no smart reactions which use this response.")

        except (discord.errors.HTTPException, discord.errors.InvalidArgument):
            await message.channel.send("Oops, I failed to remove this reaction.")

    # Thanks irdumb#1229 for the help making this "more Pythonic"
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        if message.author == self.bot.user:
            return
        guild = message.guild
        reacts = copy.deepcopy(await self.conf.guild(guild).reactions())
        if reacts is None:
            return
        sentence = message.content.lower()
        for response in reacts:
            for reaction in reacts[response]:
                word = reaction.lower()
                if word in sentence:
                    try:
                        await message.channel.send(response)
                    except (discord.errors.Forbidden, discord.errors.InvalidArgument, discord.errors.NotFound):
                        pass
