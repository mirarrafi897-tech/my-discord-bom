import os
import json
import time
import discord
from discord.ext import commands, tasks
from itertools import cycle
from typing import Union

intents = discord.Intents.all()
idk = ["-", ""]

def is_owner(ctx):
    return ctx.author.id in [1181514638106574941, 1103331364503289856, 1086567184920227900]

def get_prefix(client, message):
    if not os.path.exists("info.json"):
        with open("info.json", "w") as f:
            json.dump({"np": []}, f)
            
    with open("info.json", "r") as ok:
        try:
            kk = json.load(ok)
            ded = [str(i) for i in kk.get("np", [])]
            if str(message.author.id) in ded:
                return idk
            else:
                return "-"
        except (json.decoder.JSONDecodeError, KeyError):
            return "-"

client = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    owner_ids={1181514638106574941, 1103331364503289856, 1086567184920227900},
    case_insensitive=True,
    strip_after_prefix=True
)

lundlele = cycle(["Nukers Territory™ <$", "Ping: {:.2f} ms"])  

@tasks.loop(seconds=7)
async def loda():
    status_message = next(lundlele)
    if "{:.2f}" in status_message:
        status_message = status_message.format(client.latency * 100)  
    await client.change_presence(activity=discord.Game(name=status_message), status=discord.Status.dnd)

@client.event
async def on_ready():
    print("Success: Bot Is Connected To Discord")
    print("Loaded & Online!")
    print(f"Connected to: {len(client.users)} users")
    
    # Slash Commands Cync
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

    loda.start()

    # Voice channel connect
    try:
        tci = 1213768911313575957
        tc = client.get_channel(tci)
        if tc:
            voice_channel = await tc.connect()
            await voice_channel.guild.change_voice_state(channel=tc, self_deaf=True)
    except Exception as e:
        print(f"Voice join error: {e}")

def is_permitted(ctx):
    if not os.path.exists('perms.txt'):
        return False
    with open('perms.txt', 'r') as file:
        permitted_users = [line.strip() for line in file.readlines()]
    return str(ctx.author.id) in permitted_users

tick = "<:stolen_emoji:1188884329238106193>"
cross = "<:stolen_emoji:1188884392404340737>"
clr = discord.Colour.default()

client.remove_command("help")

# --- COMMANDS ---

@client.command()
async def help(ctx):
    embed = discord.Embed(
        title="Nukers Territory",
        description=f"Hy {ctx.author.mention}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Fun", value="`wizz`", inline=False)
    embed.add_field(name="Moderation", value="`ban`,`kick`,`unban`,`lock`,`unlock`,`hide`,`unhide`", inline=False)
    embed.add_field(name="Role", value="`staff`,`rstaff`,`buddy`,`rbuddy`,`qt`,`rqt`", inline=False)
    embed.set_footer(text="discord.gg/ntop")
    await ctx.send(embed=embed)

@client.command()
async def wizz(ctx):
    x = await ctx.send(f"`Wizzing {ctx.guild.name}, will take 69 seconds to complete`")
    z = await ctx.send(f"`successfully pruned {ctx.guild.name}`")
    e = await ctx.send("`Deleting Channels...`")
    r = await ctx.send("`Deleting roles...`")
    t = await ctx.send("`Installing Ban Wave..`")
    await x.delete()
    await z.delete()
    await e.delete()
    await r.delete()
    await t.delete()
    await ctx.send(f"**{tick} `successfully wizzed {ctx.guild.name}`**")

@client.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: Union[discord.Member, int] = None, *, reason=None):
    if not (ctx.author.top_role.position) > int(ctx.guild.me.top_role.position):
        embed = discord.Embed(title=f"{ctx.author.name}", description=f"{cross} | Your top role should be above my top role", color=clr)
        await ctx.send(embed=embed)
    elif member is None:
        embed = discord.Embed(title=f"{ctx.author.name}", description=f"{cross} | Please provide a valid member or user ID to ban", color=clr)
        await ctx.send(embed=embed)
    else:
        guild = ctx.guild
        member_id = member.id if isinstance(member, discord.Member) else member
        member_to_ban = guild.get_member(member_id)

        if member_to_ban:
            await guild.ban(member_to_ban, reason=f"Banned by {ctx.author.name} | {reason}")
            try:
                await member_to_ban.send(f"❗You have been banned from **`{guild.name}`**.\nReason: **`{reason}`**")
            except discord.errors.Forbidden:
                pass  
            embed = discord.Embed(title=f"{ctx.author.name}", description=f"{tick} | Successfully banned {member_to_ban.name}", color=clr)
            embed.set_footer(text=f"Reason: {reason} | Nukers Territory™")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"{ctx.author.name}", description=f"{cross} | Member not found", color=clr)
            await ctx.send(embed=embed)

@client.event
async def on_webhooks_update(channel):
    guild = channel.guild
    if guild.id != 1099703918298136718:
        return

    mohit = client.get_channel(1213746355319734313)
    entry = None

    async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.webhook_create):
        entry = log
        break

    if entry:
        user_id = entry.user.id
        wl = []
        if os.path.exists('wl.txt'):
            with open('wl.txt', 'r') as file:
                wl = [int(line.strip()) for line in file.readlines() if line.strip().isdigit()]

        if user_id not in wl:
            try:
                await guild.ban(entry.user, reason="ANTIWEBHOOK CREATE | AIZER")
            except discord.Forbidden:
                pass

        webhooks = await guild.webhooks()
        for webhook in webhooks:
            try:
                await webhook.delete()
            except Exception:
                pass

        if mohit:
            embed = discord.Embed(title="Webhook Creation", description="Someone attempted to create a webhook.", color=clr)
            embed.add_field(name="Guild", value=guild.name)
            embed.add_field(name="Channel", value=channel.name)
            embed.add_field(name="User", value=entry.user.mention)
            embed.set_footer(text=f"User ID: {user_id}")
            await mohit.send(embed=embed)

# Bot Run via Railway Environment Variable
token = os.getenv("DISCORD_TOKEN")
if token:
    client.run(token)
else:
    print("Error: DISCORD_TOKEN Environment Variable is missing!")