import os
import discord
from discord import Client, Game, Streaming
from discord.ext import commands

from config import Config

intents = discord.Intents.default()
intents.presences = True
intents.members = True
bot = commands.Bot(command_prefix='!', case_insensitive = True, intents = intents, help_command=None)


bot_id = Config["bot-id"]
ticket_role = Config["ticket-reader-role-name"]
player_role_name = Config["role-to-assign-on-welcome"]
log_channel_id = Config["log-channel-id"]


@bot.command(name="welcome_msg")
async def welcome_msg(ctx):
    embed = discord.Embed(title="Welcome {0}".format("Anatomic"),
     description="""***English***
     Welcome to the Discord server of *Divictus Gaming*.\nPlease take a minute to read the rules in #rules.\nCheers!
     
     ***Български***
     Добре дошли в Discord сървъра на **Divictus Gaming**.\nМоля прочетете правилата в #rules.\nПриятен ден!""",
     color=discord.Colour(484085))
    embed.set_author(name="Divictus Team", icon_url="https://scontent.fsof9-1.fna.fbcdn.net/v/t31.18172-8/23213128_1964267133795574_4927101994895641797_o.png?_nc_cat=110&ccb=1-3&_nc_sid=09cbfe&_nc_ohc=m3HyENvqOckAX_81w8N&_nc_ht=scontent.fsof9-1.fna&oh=43d2e58890d777e6e08669c6c3fa7c0a&oe=61278C28")
    await welcome_channel.send(embed=embed, content="<@!215144135357759488>")



@bot.event
async def on_ready():
    global welcome_channel
    global log_channel
    await bot.wait_until_ready() # necessary for some idiotic reason 
    await bot.change_presence(activity=Game(name="The Official Divictus Bot."))
    welcome_channel = bot.get_channel(Config["welcome-channel-id"])
    log_channel = bot.get_channel(log_channel_id)
    print('Logged on as {0}!'.format(bot.user))
    print('Welcome channel is {0}'.format(welcome_channel))
    await logit("Bot started")



@bot.event
async def on_member_join(member):
    embed = discord.Embed(title="Welcome {0}".format(member.name),
     description="""***English***
     Welcome to the Discord server of **Divictus Gaming**.\nPlease take a minute to read the rules in #rules.\nCheers!
     
     ***Български***
     Добре дошли в Discord сървъра на **Divictus Gaming**.\nМоля прочетете правилата в #rules.\nПриятен ден!""",
     color=discord.Colour(484085))
    embed.set_author(name="Divictus Team", icon_url="https://scontent.fsof9-1.fna.fbcdn.net/v/t31.18172-8/23213128_1964267133795574_4927101994895641797_o.png?_nc_cat=110&ccb=1-3&_nc_sid=09cbfe&_nc_ohc=m3HyENvqOckAX_81w8N&_nc_ht=scontent.fsof9-1.fna&oh=43d2e58890d777e6e08669c6c3fa7c0a&oe=61278C28")
    await welcome_channel.send(embed=embed, content="<@!{0}>".format(member.id))
    player_role = discord.utils.get(member.guild.roles, name=player_role_name)
    await member.add_roles(player_role)

async def logit(message):
    print("here")
    await log_channel.send(message)

@bot.command(name="kick")
@discord.ext.commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *args):
    print("Reason {}".format(" ".join(args)))
    reason = " ".join(args)
    await member.kick(reason=" ".join(args))
    await logit("{0} kicked {1} for Reason: {2}".format(ctx.message.author.name, member.name, reason))

@bot.command(name="ban")
@discord.ext.commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *args):
    print("Reason {}".format(" ".join(args)))
    reason = " ".join(args)
    await member.ban(reason=reason, delete_message_days ="7")
    await logit("{0} banned {1} for Reason: {2}".format(ctx.message.author.name, member.name, reason))
    


@bot.command(name="ticket")
@discord.ext.commands.has_permissions(administrator=True)
async def ticket(ctx, *args):
    if len(args) < 3:
        await ctx.send("If you want to create a new ticket use -> !ticket \"title\" \"content\" <emoji to be used>")
    else:
        embed = discord.Embed(
            title=args[0], 
            description=args[1], 
            color=discord.Colour(484085))

        embed.set_author(name="Divictus Team", icon_url="https://scontent.fsof9-1.fna.fbcdn.net/v/t31.18172-8/23213128_1964267133795574_4927101994895641797_o.png?_nc_cat=110&ccb=1-3&_nc_sid=09cbfe&_nc_ohc=m3HyENvqOckAX_81w8N&_nc_ht=scontent.fsof9-1.fna&oh=43d2e58890d777e6e08669c6c3fa7c0a&oe=61278C28")

        await ctx.message.delete()
        def check(reaction, user):
            return str(reaction) == str(args[2]) and user.id != bot_id

        msg = await ctx.send(embed=embed)
        await msg.add_reaction(str(args[2]))

        await logit("Ticket system started by {}".format(ctx.message.author.name))

        while True:
            reaction, user = await bot.wait_for('reaction_add', check=check)
            print(reaction, user, user.id)
            await reaction.remove(user)
            ticket_name = "ticket-{}".format(user.name)
            ticket_channel = await ctx.guild.create_text_channel(ticket_name, category=discord.utils.get(ctx.guild.categories, id=Config["ticket-category"]))
            for role in ctx.guild.roles: # disable for normal users access to tickets
                if role.name != ticket_role:
                    await ticket_channel.set_permissions(ctx.guild.default_role, read_messages=False)
            await ticket_channel.set_permissions(user, read_messages=True) # add the opener of the ticket to the people who can see it
            await ticket_channel.send("**TO CLOSE TICKET USE:** *!ticketclose*")
            await logit("Ticket opened by {}".format(user.name))
        

@bot.command(name="ticketclose")
async def ticket(ctx):
    if ctx.channel.name.startswith("ticket-"):
        await ctx.channel.delete()
        await logit("Ticket {} closed by {}".format(ctx.channel.name, ctx.message.author.name))
    else:
        await ctx.send("**This is not a ticket.**")

@bot.command(name="poll")
@discord.ext.commands.has_permissions(kick_members=True) # a strange permission but one that lower staff will have
async def poll(ctx, *args):
    if len(args) < 4:
        await ctx.send("If you want to start a poll use -> !poll \"title\" \"content\" <Emoji 1> <Emoji 2> ...")
    else:
        embed = discord.Embed(
            title=args[0], 
            description=args[1], 
            color=discord.Colour(484085))

        embed.set_author(name="Divictus Team", icon_url="https://scontent.fsof9-1.fna.fbcdn.net/v/t31.18172-8/23213128_1964267133795574_4927101994895641797_o.png?_nc_cat=110&ccb=1-3&_nc_sid=09cbfe&_nc_ohc=m3HyENvqOckAX_81w8N&_nc_ht=scontent.fsof9-1.fna&oh=43d2e58890d777e6e08669c6c3fa7c0a&oe=61278C28")
        
        msg = await ctx.send(embed=embed)
        args = list(args)
        args.pop(0)
        args.pop(0) 
        for arg in args:
            await msg.add_reaction(str(arg))
        
        await logit("Poll started by {}".format(ctx.message.author.name))

@bot.command(name="help")
async def help(ctx):
    embed = discord.Embed(title="Help Message",
     description="""**The Divictus Bot - Under GPLv3 - Made by *Anatomic* **""",
     color=discord.Colour(484085))
    embed.add_field(name="!help", value="This message", inline=True)
    embed.add_field(name="!ticket", value="Create a ticket system - !ticket \"<title>\" \"<descripion>\" <emoji>", inline=True)
    embed.add_field(name="!ticketclose", value="Close a ticket", inline=True)
    embed.add_field(name="!ban", value="Ban a user - !ban @someone <reason>", inline=True)
    embed.add_field(name="!kick", value="Kick a user - !kick @someone <reason>", inline=True)
    embed.add_field(name="!poll", value="Start a poll - !poll \"<title>\" \"<descripion>\" <emoji 1> <emoji 2> ...", inline=True)
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error): 
    if isinstance(error, discord.ext.commands.MissingPermissions):
        await ctx.send("You don't have permissions to do that!")
    elif isinstance(error, discord.ext.commands.BotMissingPermissions):
        await ctx.send("The Bot doesn't have the permissions to do that!")
    else:
        print(error)



bot.run(os.getenv('BOTTOKEN'))
