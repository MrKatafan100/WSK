import disnake
import json
import datetime
import sqlite3
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from disnake import Embed

db = sqlite3.connect("huina.db")
cursor = db.cursor()
"""
cursor.execute('''CREATE TABLE local (
	server integer,
	language boolean
)''')
"""
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
	server_id = member.guild.id

	cursor.execute("SELECT * FROM local WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		await print("Не выбран язык")

	embedr = Embed(
		title="Этого мобилизируем↓↓↓",
		description=f"Новый Участник! {ping} тобі пізда.",
		colour = 000000
	)
	
	embedr.set_author(
		name = "by: v_stoilo",
		url = "https://github.com/MrKatafan100",
		icon_url = "https://cdn.discordapp.com/attachments/1207240200758108181/1228634187385278525/PCpXdqvUWfCW1mXhH1Y_98yBpgsWxuTSTofy3NGMo9yBTATDyzVkqU580bfSln50bFU.png?ex=662cc1c1&is=661a4cc1&hm=855c4eb3755fa480f4dd2dac41d40d77d632b421cdd83a884d9f1eab185c1987&"
	)

	embeda = Embed(
		title="Mobilizing this one↓↓↓",
		description=f"New Member! {ping}, you're screwed.",
		colour = 000000
	)
	
	embeda.set_author(
		name = "by: v_stoilo",
		url = "https://github.com/MrKatafan100",
		icon_url = "https://cdn.discordapp.com/attachments/1207240200758108181/1228634187385278525/PCpXdqvUWfCW1mXhH1Y_98yBpgsWxuTSTofy3NGMo9yBTATDyzVkqU580bfSln50bFU.png?ex=662cc1c1&is=661a4cc1&hm=855c4eb3755fa480f4dd2dac41d40d77d632b421cdd83a884d9f1eab185c1987&"
	)
	
	embedr.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211575984483078206/1228591262450585631/3.png?ex=662c99c7&is=661a24c7&hm=d4b9580d8a9637fb3e46b6567398d75a57d8eeff14c43e2f51671841c4d10e33&")
	embeda.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211575984483078206/1228591262450585631/3.png?ex=662c99c7&is=661a24c7&hm=d4b9580d8a9637fb3e46b6567398d75a57d8eeff14c43e2f51671841c4d10e33&")
	
	if language == False:
		await member.add_roles(role, role2)
		await chanel.send(embed=embedr)
	else:
		await member.add_roles(role, role2)
		await chanel.send(embed=embeda)		

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
	server_id = ctx.guild.id

	cursor.execute("SELECT * FROM local WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		await ctx.send("choose a language")

	if language == False:
		if ctx.author.top_role.position > user.top_role.position:
			await user.ban(reason=reason)
			await ctx.send(f"{ping} был забанен по причине {reason}.")
		else:
			await ctx.send("Ты хотел забанить админа? ІДІ нахуй.")

	else:
		if ctx.author.top_role.position > user.top_role.position:
			await user.ban(reason=reason)
			await ctx.send(f"{ping} was banned for {reason}.")
		else:
			await ctx.send("Did you want to ban an admin?.")		

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
	server_id = ctx.guild.id

	cursor.execute("SELECT * FROM local WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		await ctx.send("choose a language")

	if language == False:
		if ctx.author.top_role.position > user.top_role.position:
			await user.kick(reason=reason)
			await ctx.send(f"{ping} был кикнут по причине {reason}.")
		else:
			await ctx.send("Ты хотел кикнуть админа? ІДІ нахуй.")
	else:
		if ctx.author.top_role.position > user.top_role.position:
			await user.kick(reason=reason)
			await ctx.send(f"{ping} was kicked for {reason}.")
		else:
			await ctx.send("Did you want to kick an admin?")

@has_permissions(mute_members=True)
@bot.slash_command(
	name="mute",
	description="мутит участника",
	options=[
	disnake.Option("user", "пользыватель", type=disnake.OptionType.user, required=True),
	disnake.Option("time", "время мута", type=disnake.OptionType.integer, required=True),
	disnake.Option("reason", "причина мута", type=disnake.OptionType.string, required=True)
	]
)
async def mute(ctx, user: disnake.Member, time: int, reason: str):
	ping = user.mention
	time = datetime.datetime.now() + datetime.timedelta(minutes=int(time))
	server_id = ctx.guild.id

	cursor.execute("SELECT * FROM local WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		await ctx.send("choose a language")

	if language == False:
		if ctx.author.top_role.position > user.top_role.position:
			await user.timeout(reason=reason, until=time)
			await ctx.send(f"Пользыватель {ping} был замучен по причине {reason}.")
		else:
			await ctx.send("Ты хотел замутить админа? ІДІ нахуй.")
	else:
		if ctx.author.top_role.position > user.top_role.position:
			await user.timeout(reason=reason, until=time)
			await ctx.send(f"User {ping} has been muted due to {reason}.")
		else:
			await ctx.send("Did you want to mute an admin?")

# только для быдловска
@has_permissions(administrator=True)
@bot.slash_command(
	name="bidlovsk_only_arest",
	description="арестовует участника",
	options=[
	disnake.Option("user","пользыватель", type=disnake.OptionType.user, required=True)
	]
)
async def arest(ctx, user: disnake.Member):
	ping = user.mention
	roles = user.roles
	server_id = ctx.guild.id
	guild = ctx.guild
	role = disnake.utils.get(guild.roles, name="Арестованный")

	cursor.execute("SELECT * FROM local WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		language = None	

	if language == False:
		if ctx.author.top_role.position > user.top_role.position:
			await user.edit(roles=[])
			await user.add_roles(role)
			await ctx.send(f"Пользыватель {ping} был арестован.")
		else:
			await ctx.send("Ты хотел арестовать админа? ІДІ нахуй.")
	else:
		if ctx.author.top_role.position > user.top_role.position:
			await user.edit(roles=[])
			await user.add_roles(role)
			await ctx.send(f"User {ping} has been arrested.")
		else:
			await ctx.send("You wanted to arrest an admin?")
# только для быдловска

@has_permissions(administrator=True)
@bot.slash_command(
	name="language_english",
	description="changes bot language"
)
async def obnova(ctx):
	server_id = ctx.guild.id

	cursor.execute("SELECT * FROM local WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		language = None

	if language is None:
		cursor.execute("INSERT INTO local VALUES(?, False)", (server_id,))
		await ctx.send("language changed")
	else:
		cursor.execute("UPDATE local SET language = NOT language WHERE server = ?", (server_id,))
		await ctx.send("language changed")

@has_permissions(administrator=True)
@bot.slash_command(
	name="language",
	description="bot language"
)
async def test(ctx):
	server_id = ctx.guild.id

	cursor.execute("SELECT * FROM local WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		await ctx.send("choose a language")

	if language == False:
		await ctx.send("язык бота Русский")
	else:
		await ctx.send("bot language English")
		
bot.run("YOU_TOKEN")
db.commit()
db.close()
