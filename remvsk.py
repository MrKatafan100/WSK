import disnake
import json
import datetime
import sqlite3
import time
from disnake import audit_logs
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from disnake import Embed

db = sqlite3.connect("D:/newvsk/huina.db")
cursor = db.cursor()
"""
cursor.execute('''CREATE TABLE local (
	server integer,
	language boolean
)''')

cursor.execute('''CREATE TABLE roles (
	server integer,
	role1 integer,
	role2 integer,
	role3 integer
)''')

cursor.execute('''CREATE TABLE text_message (
	server integer,
	title text,
	text_mess text
)''')

cursor.execute('''CREATE TABLE chnl (
	server integer,
	chnannel integer
)''')

cursor.execute('''CREATE TABLE automod (
	server integer,
	automod boolean
)''')

cursor.execute('''CREATE TABLE naturali (
	author_id integer,
	time_message integer
)''')

cursor.execute('''CREATE TABLE saved_server (
	saved_name text,
	save_category_channel text
)''')
"""
message_count = {}

bot = commands.Bot(command_prefix="!", help_command=None, intents=disnake.Intents.all())

@bot.event
async def on_message(message):
	#bidlovsk only
	guild = message.guild
	role3 = disnake.utils.get(guild.roles, name="Анти ІДІ Нахуй (114 робуксов)")
	author = message.author
	#bidlovsk only
	author_id = message.author.id
	server_id = message.guild.id
	channel = message.channel
	message_author_id = message.author.id
	author = message.author
	ping = author.mention
	reason = "spam"
	time2 = datetime.datetime.now() + datetime.timedelta(minutes=int(5))
	time1 = time.time()

	cursor.execute("SELECT * FROM naturali WHERE author_id = ?", (author_id,))
	result = cursor.fetchone()

	language = await vibor_yazika_message(message)

	automod_status = await automod_check_message(message)

	if automod_status == True:
		if role3 in author.roles: #bidlovsk only
			return #bidlovsk only
		message_count.setdefault(message_author_id, 0)
		message_count[message_author_id] += 1

		if result:
			time_message = result[1]
			resultat = time1 - time_message
			cursor.execute("UPDATE naturali SET time_message = ?  WHERE author_id = ?", (time1, author_id))
			if resultat > 5.5:
				message_count[message_author_id] = 0
				print("нахрюк ебаный")
				return
			else:
				if message_count[message_author_id] >= 5:
					await author.timeout(reason=reason, until=time2)
					message_count[message_author_id] = 0
					if language == False:
						await channel.send(f"{ping} был замучен за спам на 5 минут.")
						print(resultat)
					else:
						await channel.send(f"{ping} muted for spamming for 5 minutes.")
						print(resultat)	
					return
				else:
					return	
		else:
			time_message = time.time()	
			cursor.execute("INSERT INTO naturali VALUES (?, ?)", (author_id, time_message))
			print("на карандашике")			
	else:
		return

	await bot.process_commands(message)	

@bot.event
async def on_guild_channel_delete(channel):
	guild = channel.guild
	channel_name = channel.name
	channel_position = channel.position
	channel_category = channel.category
	server_roles = channel.guild.roles 
	permissions = {}
	audit_logs = await guild.audit_logs(limit=1).flatten()
	logs = audit_logs[0]
	reason = "Рейд бот"
	user = logs.user


	for role in server_roles:
		permissions[role] = channel.overwrites_for(role)

	automod_status = await automod_check_channel(channel)
	

	if automod_status == True:
		if channel.type == disnake.ChannelType.voice:
			if logs.user.bot:
				try:
					await user.ban(reason=reason)
					print("Бот был забанен")
				except disnake.errors.Forbidden:
					print("Бот не может быть забанен из-за недостатка прав")
			await channel.guild.create_voice_channel(name=channel_name, position=channel_position, category=channel_category, overwrites=permissions)
		if channel.type == disnake.ChannelType.text:	
			if logs.user.bot:
				try:
					await user.ban(reason=reason)
					print("Бот был забанен")
				except disnake.errors.Forbidden:
					print("Бот не может быть забанен из-за недостатка прав")
			await channel.guild.create_text_channel(name=channel_name, position=channel_position, category=channel_category, overwrites=permissions)
		if channel.type == disnake.ChannelType.category:
			if logs.user.bot:
				try:
					await user.ban(reason=reason)
					print("Бот был забанен")
				except disnake.errors.Forbidden:
					print("Бот не может быть забанен из-за недостатка прав")
			await channel.guild.create_category(name=channel_name, position=channel_position,overwrites=permissions)			

@bot.event
async def on_ready():
	print(f"{bot.user} готов сжигать евреев.")
	await bot.change_presence(activity=disnake.Game(name="HOI4"))

@has_permissions(administrator=True)
@bot.slash_command(
	name="set_channel_add_on_join",
	description="закрепляет канал",
	options=[
		disnake.Option("channel", "channel", type=disnake.OptionType.channel, required=True)
	]
)
async def chanel_add(ctx, channel: disnake.TextChannel):
	server_id = ctx.guild.id
	language = await vibor_yazika(ctx)

	channel_id = channel.id

	cursor.execute("SELECT * FROM chnl WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		cursor.execute("UPDATE chnl SET chnannel = ?  WHERE server = ?", (channel_id, server_id))
		if language == False:
			await ctx.send("Канал успешно выбран!")
		else:
			await ctx.send("Channel successfully selected!")			
	else:
		cursor.execute("INSERT INTO chnl VALUES (?, ?)", (server_id, channel_id))
		if language == False:
			await ctx.send("Канал успешно выбран!")
		else:
			await ctx.send("Channel successfully selected!")

async def channel_id_func(member):
	server_id = member.guild.id

	cursor.execute("SELECT * FROM chnl WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		channel_id = result[1]
	else:
		channel_id = None

	return channel_id			

@has_permissions(administrator=True)
@bot.slash_command(
	name="set_roles_add_on_join",
	description="закрепляет роль",
	options=[
		disnake.Option("role1", "role", type=disnake.OptionType.role, required=True),
		disnake.Option("role2", "role", type=disnake.OptionType.role, required=False),
		disnake.Option("role3", "role", type=disnake.OptionType.role, required=False)
	]
)

async def get_roles(ctx, role1: disnake.Role, role2: disnake.Role = None, role3: disnake.Role = None):
	server_id = ctx.guild.id

	role_id1 = role1.id	

	if role2 is None:
		role_id2 = None
	else:
		role_id2 = role2.id

	if role3 is None:
		role_id3 = None
	else:
		role_id3 = role3.id 		 

	cursor.execute("SELECT * FROM roles WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	language = await vibor_yazika(ctx)

	if result:
		cursor.execute("UPDATE roles SET role1 = ?, role2 = ?, role3 = ?  WHERE server = ?", (role_id1, role_id2, role_id3, server_id))
		if language == False:
			await ctx.send("Роли успешно выбраны!")
		else:
			await ctx.send("Roles have been successfully selected!")			
	else:
		cursor.execute("INSERT INTO roles VALUES (?, ?, ?, ?)", (server_id, role_id1, role_id2, role_id3))
		if language == False:
			await ctx.send("Роли успешно выбраны!")
		else:
			await ctx.send("Roles have been successfully selected!")

@has_permissions(administrator=True)
@bot.slash_command(
	name="set_message_add_on_join",
	description="Сообщение которое будет отправлятся когда кто то заходит.",
	options=[
		disnake.Option("title", "title", type=disnake.OptionType.string, required=True),
		disnake.Option("text", "text", type=disnake.OptionType.string, required=True)
	]
)

async def get_message(ctx, title: str, text: str):
	server_id = ctx.guild.id
	language = await vibor_yazika(ctx)

	cursor.execute("SELECT * FROM text_message WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if language == False:
		if result:
			cursor.execute("UPDATE text_message SET title = ?, text_mess = ? WHERE server = ?", (title, text, server_id))
			await ctx.send("Текст добавлен.")
		else:
			cursor.execute("INSERT INTO text_message VALUES (?, ?, ?)", (server_id, title, text))	
			await ctx.send("Текст добавлен.")
	else:
		if result:
			cursor.execute("UPDATE text_message SET title = ?, text_mess = ? WHERE server = ?", (title, text, server_id))
			await ctx.send("Text added.")
		else:
			cursor.execute("INSERT INTO text_message VALUES (?, ?, ?)", (server_id, title, text))	
			await ctx.send("Text added.")		

@bot.event
async def vibor_yazika_member(member):
	server_id = member.guild.id

	cursor.execute("SELECT * FROM local WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		language = None

	return language	

@bot.event
async def role_hz(member):
	server_id = member.guild.id

	cursor.execute("SELECT * FROM roles WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:	
		role_id1 = result[1]
	else:
		role_id1 = None

	if result:	
		role_id2 = result[2]
	else:
		role_id2 = None

	if result:	
		role_id3 = result[3]
	else:
		role_id3 = None				

	return role_id1, role_id2, role_id3

async def text_return(member):
	server_id = member.guild.id

	cursor.execute("SELECT * FROM text_message WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		title = result[1]
		text_mess = result[2]
	else:
		title = None
		text_mess = None		

	return title, text_mess

@bot.event
async def on_member_join(member):
	ping = member.mention
	guild = member.guild
	result1 = await text_return(member)
	result2 = await role_hz(member)

	chanel_id = await channel_id_func(member)
	role_id1 = result2[0]
	role_id2 = result2[1]
	role_id3 = result2[2]
	role1 = disnake.utils.get(guild.roles, id=role_id1)
	role2 = disnake.utils.get(guild.roles, id=role_id2)
	role3 = disnake.utils.get(guild.roles, id=role_id3)
	chanel = disnake.utils.get(guild.channels, id=chanel_id)	
	title = result1[0]
	text_mess = result1[1]

	if title is None or text_mess is None:
		print("Не выбран текст")
		return

	embedr = Embed(
		title=title,
		description=f"{text_mess} {ping}.",
		colour = 000000
	)
	
	embedr.set_author(
		name = "by: v_stoilo",
		url = "https://github.com/MrKatafan100",
		icon_url = "https://cdn.discordapp.com/attachments/1207240200758108181/1228634187385278525/PCpXdqvUWfCW1mXhH1Y_98yBpgsWxuTSTofy3NGMo9yBTATDyzVkqU580bfSln50bFU.png?ex=662cc1c1&is=661a4cc1&hm=855c4eb3755fa480f4dd2dac41d40d77d632b421cdd83a884d9f1eab185c1987&"
	)
	
	embedr.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211575984483078206/1228591262450585631/3.png?ex=662c99c7&is=661a24c7&hm=d4b9580d8a9637fb3e46b6567398d75a57d8eeff14c43e2f51671841c4d10e33&")

	await chanel.send(embed=embedr)
	await member.add_roles(role1, role2, role3)

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

# часть для автомода
@has_permissions(administrator=True)
@bot.slash_command(
	name="automod",
	description="set automod"
)
async def automod(ctx):
	server_id = ctx.guild.id

	language = await vibor_yazika(ctx)

	cursor.execute("SELECT * FROM automod WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		cursor.execute("UPDATE automod SET automod = NOT automod WHERE server = ?", (server_id,))
		if language == False:
			await ctx.send("Статус автомода изменен.")
		else:
			await ctx.send("Automod status changed.")
	else:
		cursor.execute("INSERT INTO automod VALUES(?, True)", (server_id,))
		if language == False:
			await ctx.send("Статус автомода изменен.")	
		else:
			await ctx.send("Automod status changed.")	

@has_permissions(administrator=True)
@bot.slash_command(
	name="save",
	description="save data server",
	options=[
	disnake.Option("name", "имя сохранения", type=disnake.OptionType.string, required=True)
	]
)				
async def save(ctx, name: str):
	cursor.execute("SELECT * FROM saved_server WHERE saved_name = ?", (name,))
	result = cursor.fetchone()
	saved_data = {}

	saved_data[name] = {
	"categorys": []
	}

	for category in ctx.guild.categories:
		categorys = {
		"name": category.name,
		"channels": []
		}
		for channel in category.channels:
			channel_type = "voice" if channel.type == disnake.ChannelType.voice else "text"
			channels_data = {
			"name": channel.name,
			"type": channel_type
			}

			categorys["channels"].append(channels_data)
		saved_data[name]["categorys"].append(categorys)

	print(saved_data)

	if result:
		cursor.execute("UPDATE saved_server SET save_category_channel = ?  WHERE saved_name = ?", (json.dumps(saved_data[name]), name))
	else:
		cursor.execute("INSERT INTO saved_server VALUES(?, ?)", (name, json.dumps(saved_data[name])))

	await ctx.send("готово")

@has_permissions(administrator=True)
@bot.slash_command(
	name="create",
	description="creat data server",
	options=[
	disnake.Option("name", "имя сохранения", type=disnake.OptionType.string, required=True)
	]
)		
async def create(ctx, name: str):
	language = await vibor_yazika(ctx)

	cursor.execute("SELECT * FROM saved_server WHERE saved_name = ?", (name,))
	result = cursor.fetchone()

	if language == False:
		await ctx.send("Создано!")	
	else:
		await ctx.send("Created!")		

	if result:
		saved_data = json.loads(result[1])

		for category_data in saved_data["categorys"]:
			print(category_data)
			new_category = await ctx.guild.create_category(name=category_data["name"])

			for channel in category_data["channels"]:
				if channel["type"] == "text":
					await new_category.create_text_channel(name=channel["name"])
				if channel["type"] == "voice":
					await new_category.create_voice_channel(name=channel["name"])		


async def vibor_yazika(ctx):
	server_id = ctx.guild.id

	cursor.execute("SELECT * FROM local WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		language = None

	return language	

async def vibor_yazika_message(message):
	server_id = message.guild.id

	cursor.execute("SELECT * FROM local WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		language = None

	return language	

async def automod_check_message(message):
	server_id = message.guild.id

	cursor.execute("SELECT * FROM automod WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		automod_status = result[1]
	else:
		automod_status = None

	return automod_status

async def automod_check_channel(channel):
	server_id = channel.guild.id

	cursor.execute("SELECT * FROM automod WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		automod_status = result[1]
	else:
		automod_status = None

	return automod_status				
		
bot.run("YOU_TOKEN")
db.commit()
db.close()
