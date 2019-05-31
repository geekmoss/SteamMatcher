import click
import discord
from discord import Embed, Colour, Message
import shlex
import config
from BotModules.SteamMatch import SteamMatch, SteamMatchException

client = discord.Client()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.change_presence(activity=discord.Activity(name="?sm-help", type=discord.ActivityType.listening))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('?sm-help'):
        await message.channel.send(
            embed=Embed(title="Steam Matcher Help", type="rich", color=Colour.from_rgb(66, 244, 125),
                        description="Displays the intersection of games from Steam libraries"
                                    " of selected Steam profiles. \n\n" +
                                    "Usage: `?sm SteamID VanityURL`\n" +
                                    "Example: `?sm 123456 SomeGamerBoi`\n\n" +
                                    message.author.mention))
        pass
    elif message.content.lower().startswith('?sm'):
        try:
            m: Message = await message.channel.send('Wait a moment...')
            sm = SteamMatch(*shlex.split(message.content[4:]))
            data = sm.compare()

            libs = ', '.join(map(lambda x: f'**{x}** *({data["users"][x]} games)*', data['users']))

            def build_item(game):
                pt = sum(game["info"]["u"].values())
                is_mins = pt < 60
                t = pt if is_mins else pt / 60
                return f'- **[{game["info"]["name"]}]({game["url"]})**, *playtime of everyone ' \
                    f'`{t:.1f} {"min" if is_mins else "hour"}{"" if t < 2.0 else "s"}`*;'
                pass

            body = "" + \
                   f"There are {len(data['games'])} matches from {libs} players libraries.\n\n" + \
                   '\n'.join(map(build_item, data['games']))

            if len(body) > 2048:
                buff = ""
                msgs = []
                for l in body.splitlines():
                    if len(buff + l + "\n") <= 2048:
                        buff += l + "\n"
                        pass
                    else:
                        msgs.append(buff)
                        buff = l + "\n"
                        pass
                    pass

                if buff:
                    msgs.append(buff)

                await m.delete()
                for i, n in enumerate(msgs):
                    await message.channel.send(content=None, embed=Embed(
                        title=f"Steam Matcher Result - Part {i + 1}",
                        color=Colour.from_rgb(66, 244, 125),
                        description=n
                    ))
                pass
            else:
                await m.edit(content=None, embed=Embed(
                    title="Steam Matcher Result",
                    color=Colour.from_rgb(66, 244, 125),
                    description=body
                ))
                pass
            pass
        except SteamMatchException as e:
            await message.channel.send(embed=Embed(
                title="Steam Matcher Error",
                type="rich",
                color=Colour.from_rgb(216, 34, 34),
                description=e.args[0] + "\n\n" + message.author.mention
            ))
        pass
    return


@click.command()
@click.option('--steam-key', default=config.STEAM_KEY)
@click.option('--discord-token', default=config.DISCORD_TOKEN)
def cli(steam_key, discord_token):
    config.STEAM_KEY = steam_key
    config.DISCORD_TOKEN = discord_token
    client.run(config.DISCORD_TOKEN)
    pass


if __name__ == "__main__":
    cli()
    pass
