import json
import random

from nextcord.ext import commands
import requests, datetime, asyncio
from PIL import Image, ImageFont, ImageDraw
import textwrap
from nextcord import File, ButtonStyle, Embed, Color, SelectOption, Intents, Interaction, SlashOption, Member
from nextcord.ui import Button, View, Select

helpGuide = json.load(open("help.json"))

intents = Intents.all()
intents.members = True

links = json.load(open("gifs.json"))

client = commands.Bot(command_prefix='botcuk ', intents=intents)
client.remove_command("help")


def createHelpEmbed(pageNum=0, inline=False):
    pageNum = pageNum % len(list(helpGuide))
    pageTitle = list(helpGuide)[pageNum]
    embed = Embed(color=0x0080ff, title=pageTitle)
    for key, val in helpGuide[pageTitle].items():
        embed.add_field(name=client.command_prefix + key, value=val, inline=inline)
        embed.set_footer(text=f"Page {pageNum + 1} of {len(list(helpGuide))}")
    return embed


@client.command(name="help")
async def Help(ctx):
    currentPage = 0

    # functionality for buttons

    async def next_callback(interaction):
        nonlocal currentPage, sent_msg
        currentPage += 1
        await sent_msg.edit(embed=createHelpEmbed(pageNum=currentPage), view=myview)

    async def previous_callback(interaction):
        nonlocal currentPage, sent_msg
        currentPage -= 1
        await sent_msg.edit(embed=createHelpEmbed(pageNum=currentPage), view=myview)

    # add buttons to embed

    previousButton = Button(label="<", style=ButtonStyle.blurple)
    nextButton = Button(label=">", style=ButtonStyle.blurple)
    previousButton.callback = previous_callback
    nextButton.callback = next_callback

    myview = View(timeout=180)
    myview.add_item(previousButton)
    myview.add_item(nextButton)

    sent_msg = await ctx.send(embed=createHelpEmbed(currentPage), view=myview)


@client.command(name="profile")
async def profile(ctx, user: Member = None):
    if user is None:
        user = ctx.message.author
    inline = True
    embed = Embed(title=user.name + "#" + user.discriminator, color=0x0080ff)
    userData = {
        "Mention": user.mention,
        "Nick": user.nick,
        "Created at": user.created_at.strftime("%b, %d, %Y, %T"),
        "Joined at": user.joined_at.strftime("%b, %d, %Y, %T"),
        "Server": user.guild,
        "Top Role": user.top_role
    }
    for [fieldName, fieldVal] in userData.items():
        embed.add_field(name=fieldName + ":", value=fieldVal, inline=inline)
    embed.set_footer(text=f"id: {user.id}")

    embed.set_thumbnail(user.display_avatar)
    await ctx.send(embed=embed)


@client.command(name="server")
async def Server(ctx):
    guild = ctx.message.author.guild
    embed = Embed(title=guild.name, color=0x0080ff)
    serverData = {
        "Owner": guild.owner.mention,
        "Channels": len(guild.channels),
        "Members": guild.member_count,
        "Created at": guild.created_at.strftime("%b, %d, %Y, %T"),
        "Description": guild.description,
    }
    for [fieldName, fieldVal] in serverData.items():
        embed.add_field(name=fieldName + ":", value=fieldVal, inline=True)
    embed.set_footer(text=f"id: {guild.id}")

    embed.set_thumbnail(guild.icon)
    await ctx.send(embed=embed)


@client.command(name="give me a dog photo")
async def SendMessage(ctx):
    async def dropdown_callback(interaction):
        for value in dropdown.values:
            await ctx.send(random.choice(links[value]))

    option1 = SelectOption(label="chill", value="gif", description="doggo is lonely", emoji="😎")
    option2 = SelectOption(label="play", value="play", description="doggo is bored", emoji="🙂")
    option3 = SelectOption(label="feed", value="feed", description="doggo is hungry", emoji="😋")
    dropdown = Select(placeholder="What would you like to do with doggo?", options=[option1, option2, option3],
                      max_values=3)
    dropdown.callback = dropdown_callback
    myview = View(timeout=180)
    myview.add_item(dropdown)

    await ctx.send('Hello! Are you bored?', view=myview)


@client.command(name="dog")
async def sendDog(ctx):
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    image_link = response.json()["message"]
    await ctx.send(image_link)


@client.command(name="daily")
async def daily(ctx, mystr: str, hour: int, minute: int, second: int):
    print(mystr, hour, minute, second)

    if not (0 < hour < 24 and 0 <= minute <= 60 and 0 <= second <= 60):
        raise commands.BadArgument()

    time = datetime.time(hour, minute, second)
    timestr = time.strftime("%I:%M:%S %p")
    await ctx.send(
        f"A daily message will be sent at {timestr} everyday in this channel. \nDaily Message:\"{mystr}\nConfirm by simply saying: 'yes'")
    try:
        msg = await client.wait_for("message", timeout=60, check=lambda message: message.author == ctx.author)
    except asyncio.TimeoutError:
        await ctx.send("Bekleyemem artık. İşimiz gücümüz var arkadaş !!!!")
        return

    if msg.content == "yes":
        await ctx.send("Daily message is now starting!")
        await schedule_daily_message(hour, minute, second, mystr, ctx.channel.id)
    else:
        await ctx.send("Daily Message Cancelled")


@daily.error
async def daily_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("doğru düzgün yaz sikmeyem ananı")


@client.command(name="speak")
async def speakOld(ctx, *args):
    msg = " ".join(args)
    font = ImageFont.truetype("Silkscreen-Bold.ttf", 200)
    img = Image.open("pexels-valeria-boltneva-1805164.jpg")
    cx, cy = (1750, 1000)

    lines = textwrap.wrap(msg, width=16)
    print(lines)
    w, h = font.getsize(msg)
    y_offset = (len(lines) * h) / 2
    y_text = cy - (h / 2) - y_offset

    for line in lines:
        draw = ImageDraw.Draw(img)
        w, h = font.getsize(line)
        draw.text((cx - (w / 2), y_text), line, (0, 0, 0), font=font)
        img.save("editedImg.jpg")
        y_text += h

    with open("editedImg.jpg", "rb") as f:
        img = File(f)
        await ctx.channel.send(file=img)


@client.slash_command(guild_ids=["channel id"])
async def speak(interaction: Interaction, msg: str,
                fontSize: int = SlashOption(name="picker", choices={"150pt": 150, "200pt": 200, "250pt": 250})):
    font = ImageFont.truetype("Silkscreen-Bold.ttf", fontSize)
    img = Image.open("pexels-valeria-boltneva-1805164.jpg")
    cx, cy = (1750, 1000)

    lines = textwrap.wrap(msg, width=16)
    print(lines)
    w, h = font.getsize(msg)
    y_offset = (len(lines) * h) / 2
    y_text = cy - (h / 2) - y_offset

    for line in lines:
        draw = ImageDraw.Draw(img)
        w, h = font.getsize(line)
        draw.text((cx - (w / 2), y_text), line, (0, 0, 0), font=font)
        img.save("editedImg.jpg")
        y_text += h

    with open("editedImg.jpg", "rb") as f:
        img = File(f)
        await interaction.response.send_message("hi", file=img)


async def schedule_daily_message(h, m, s, msg, channel_id, ):
    while True:
        now = datetime.datetime.now()

        # then = now.datetime.timedelta(days=1)
        # then.replace(hour=5, minute=39)

        then = now.replace(hour=h, minute=m, second=s)
        if then < now:
            then += datetime.timedelta(days=1)
        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)

        channel = client.get_channel(channel_id)

        await channel.send(msg)
        await asyncio.sleep(1)


@client.command(name="support")
async def support(ctx):
    subscribe = Button(label="Visit Website", url="https://github.com/MrSolak51")

    myview = View(timeout=180)
    myview.add_item(subscribe)

    await ctx.send("hi", view=myview)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = Embed(title="$low it down bro", description=f"Try it again in {error.retry_after:.2f}s.",
                   color=Color.red())
        await ctx.send(embed=em)


@client.event
async def on_ready():
    print(f"{client.user.name} is now ready for use")
    # await schedule_daily_message()


if __name__ == '__main__':
    client.run('TOKEN')
