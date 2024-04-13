import disnake
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from disnake import Embed

bot = commands.Bot(command_prefix="!", help_command=None, intents=disnake.Intents.all())

@bot.event
async def on_ready():
	print(f"{bot.user} готов сжигать евреев.")
	await bot.change_presence(activity=disnake.Game(name="HOI4"))

@bot.event
async def on_member_join(member):
	ping = member.mention
	guild = member.guild
	role = disnake.utils.get(guild.roles, name="Гражданский")
	role2 = disnake.utils.get(guild.roles, name="Налог")
	chanel = disnake.utils.get(guild.channels, name="👨👩гражданины")
	embed = Embed(
		title="Этого мобилизируем↓↓↓",
		description=f"Новый Участник! {ping} тобі пізда.",
		colour = 000000
	)
	
	embed.set_author(
		name = "by: v_stoilo",
		url = "https://github.com/MrKatafan100",
		icon_url = "https://cdn.discordapp.com/attachments/1207240200758108181/1228634187385278525/PCpXdqvUWfCW1mXhH1Y_98yBpgsWxuTSTofy3NGMo9yBTATDyzVkqU580bfSln50bFU.png?ex=662cc1c1&is=661a4cc1&hm=855c4eb3755fa480f4dd2dac41d40d77d632b421cdd83a884d9f1eab185c1987&"
	)
	
	embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211575984483078206/1228591262450585631/3.png?ex=662c99c7&is=661a24c7&hm=d4b9580d8a9637fb3e46b6567398d75a57d8eeff14c43e2f51671841c4d10e33&")

	await member.add_roles(role, role2)
	await chanel.send(embed=embed)


@bot.slash_command(
	name="test", 
	description="Тест Эмбэдов"
	)
async def test(ctx):
	embed = Embed(
		title="ГОЙДААААААААААААААААААААА",
		colour = 000000
	)

	embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211575984483078206/1228591262450585631/3.png?ex=662c99c7&is=661a24c7&hm=d4b9580d8a9637fb3e46b6567398d75a57d8eeff14c43e2f51671841c4d10e33&")

	await ctx.send(embed=embed)

@has_permissions(ban_members=True)
@bot.slash_command(
	name="ban",
	description="банит участника",
	options=[
		disnake.Option("user", "пользыватель", type=disnake.OptionType.user, required=True),
		disnake.Option("reason", "причина бана", type=disnake.OptionType.string, required=True)
	]
)

async def ban(ctx, user: disnake.Member, reason: str):
	ping = user.mention

	if ctx.author.top_role.position > user.top_role.position:
		await user.ban(reason=reason)
		await ctx.send(f"{ping} был забанен по причине {reason}.")
	else:
		await ctx.send("Ты хотел забанить админа? ІДІ нахуй.")

@has_permissions(kick_members=True)
@bot.slash_command(
	name="kick",
	description="кикает участника",
	options=[
	disnake.Option("user","пользыватель", type=disnake.OptionType.user, required=True),
	disnake.Option("reason", "причина кика", type=disnake.OptionType.string, required=True)
	]
)
async def kick(ctx, user: disnake.Member, reason: str):
	ping = user.mention

	if ctx.author.top_role.position > user.top_role.position:
		await user.kick(reason=reason)
		await ctx.send(f"{ping} был кикнут по причине {reason}.")
	else:
		await ctx.send("Ты хотел кикнуть админа? ІДІ нахуй.")
		
bot.run("YOU_TOKEN")
