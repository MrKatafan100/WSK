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

cursor.execute('''CREATE TABLE img (
	server integer,
	img text
)''')

cursor.execute('''CREATE TABLE white (
	server integer,
	bot_id_list text
)''')

cursor.execute('''CREATE TABLE _url_ (
	server integer,
	channel_id integer
)''')
"""
message_count = {}
anti_raid = {}
time_raid = {}


bot = commands.Bot(command_prefix="!", help_command=None, intents=disnake.Intents.all())

@bot.event
async def on_message(message):
	author_id = message.author.id
	channel = message.channel
	message_author_id = message.author.id
	author = message.author
	server_id_bidlo = 1207225250438316052
	ping = author.mention
	reason = "spam"
	time2 = datetime.datetime.now() + datetime.timedelta(minutes=int(5))
	time1 = time.time()
	if message.author.id == bot.user.id:
		return

	server_id = message.guild.id

	automod_status = await automod_check_message(message)

	channel_id = await check_channel_ad(server_id)

	cursor.execute("SELECT * FROM naturali WHERE author_id = ?", (author_id,))
	result = cursor.fetchone()

	if message.channel.id == channel_id:
		return

	if automod_status == True:
		if "https://discord.gg" in message.content:
			if message.author.bot:
				message.author.ban(reason=reason)
			await message.delete()
			return
# bidlovsk only

		if server_id == server_id_bidlo:
			message_count.setdefault(message_author_id, 0)
			message_count[message_author_id] += 1

			if result:
				time_message = result[1]
				resultat = time1 - time_message
				cursor.execute("UPDATE naturali SET time_message = ?  WHERE author_id = ?", (time1, author_id))
				if resultat > 5.5:
					message_count[message_author_id] = 0
					return
				else:
					if message_count[message_author_id] >= 5:
						await author.timeout(reason=reason, until=time2)
						message_count[message_author_id] = 0
						if language == False:
							await channel.send(f"{ping} был замучен за спам на 5 минут.")
						else:
							await channel.send(f"{ping} muted for spamming for 5 minutes.")
						return
					else:
						return	
			else:
				time_message = time.time()	
				cursor.execute("INSERT INTO naturali VALUES (?, ?)", (author_id, time_message))	
		else:
			return

# bidlovsk only
	await bot.process_commands(message)


@bot.event
async def on_guild_channel_delete(channel):
	global anti_raid
	global time_raid
	guild = channel.guild
	server_id = guild.id 
	audit_logs = await guild.audit_logs(limit=1).flatten()
	logs = audit_logs[0]
	reason = "Рейд бот"
	user = logs.user
	owner = channel.guild.owner
	time1 = time.time()
	guild_name = guild.name
	try:
		guild_avatar = guild.icon.url
	except:
		guild_avatar = None	
	raid_reason_r = "Удаление каналов"
	raid_reason_e = "Channel Deletion"

	cursor.execute("SELECT * FROM white WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		white_list = json.loads(result[1])
	else:
		white_list = []

	if bot.user.id == user.id:
		return

	automod_status = await automod_check_channel(channel)
	
	if automod_status == True:
		if logs.user.bot:
			for bot_id in white_list:
				if bot_id == user.id:
					try:
						value = anti_raid[server_id][user.id]
						value += 1
						anti_raid[server_id][user.id] = value
					except:
						value = 1
						anti_raid = {
						server_id: {
						user.id: value
						}
						}

					try:
						value_time = time_raid[server_id][user.id]
					except:#если нету еще записей в словаре
						value_time = time1
						time_raid = {
						server_id: {
						user.id: time1
						}
						}
					raznica = time1-value_time
					if raznica > 5.5:
						anti_raid[server_id][user.id] = 1
						value = 1
						time_raid[server_id][user.id] = time1
					if value > 4:
						try:
							await user.ban(reason=reason)
							embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
							await owner.send(embed=embed)
							white_list.remove(user.id)
							cursor.execute("UPDATE white SET bot_id_list = ? WHERE server = ?", (json.dumps(white_list), server_id))
							time_raid[server_id][user.id] = time1	
						except:
							return	
					time_raid[server_id][user.id] = time1
					return
				time_raid[server_id][user.id] = time1
			try:
				await user.ban(reason=reason)
			except disnake.errors.Forbidden:
				return

			embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
			await owner.send(embed=embed)

@bot.event
async def on_guild_role_delete(role):
	global anti_raid
	global time_raid
	guild = role.guild
	server_id = guild.id
	role_name = role.name
	audit_logs = await guild.audit_logs(limit=1).flatten()
	logs = audit_logs[0]
	reason = "Рейд бот"
	user = logs.user
	time1 = time.time()
	owner = role.guild.owner
	guild_name = guild.name
	try:
		guild_avatar = guild.icon.url
	except:
		guild_avatar = None	
	raid_reason_r = "Удаление ролей"
	raid_reason_e = "Role Deletion"

	cursor.execute("SELECT * FROM white WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if bot.user.id == user.id:
		return

	automod_status = await automod_check_role(role)

	if result:
		white_list = json.loads(result[1])
	else:
		white_list = []

	if automod_status == True:
		if logs.user.bot:
			for bot_id in white_list:
				if bot_id == user.id:
					try:
						value = anti_raid[server_id][user.id]
						value += 1
						anti_raid[server_id][user.id] = value
					except:
						value = 1
						anti_raid = {
						server_id: {
						user.id: value
						}
						}

					try:
						value_time = time_raid[server_id][user.id]
					except:#если нету еще записей в словаре
						value_time = time1
						time_raid = {
						server_id: {
						user.id: time1
						}
						}
					raznica = time1-value_time
					if raznica > 5.5:
						anti_raid[server_id][user.id] = 1
						value = 1
						time_raid[server_id][user.id] = time1
					if value > 4:
						try:
							await user.ban(reason=reason)
							embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
							await owner.send(embed=embed)
							white_list.remove(user.id)
							cursor.execute("UPDATE white SET bot_id_list = ? WHERE server = ?", (json.dumps(white_list), server_id))
							time_raid[server_id][user.id] = time1	
						except:
							return	
					time_raid[server_id][user.id] = time1
					return
				time_raid[server_id][user.id] = time1
			try:
				await user.ban(reason=reason)
			except disnake.errors.Forbidden:
				return

			embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
			await owner.send(embed=embed)

@bot.event
async def on_guild_channel_update(before, after):
	global anti_raid
	global time_raid
	guild = after.guild
	server_id = guild.id
	audit_logs = await guild.audit_logs(limit=1).flatten()
	logs = audit_logs[0]
	user = logs.user
	name = before.name
	reason = "Рейд бот"
	owner = before.guild.owner
	time1 = time.time()
	guild_name = guild.name
	try:
		guild_avatar = guild.icon.url
	except:
		guild_avatar = None	
	raid_reason_r = "Редактирование каналов(массовое переименование, изменение позиции каналов)"
	raid_reason_e = "Editing channels (mass renaming, changing channel position)"

	cursor.execute("SELECT * FROM white WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		white_list = json.loads(result[1])
	else:
		white_list = []

	automod_status = await automod_check_channel(before)

	if bot.user.id == user.id:
		return

	if automod_status == True:
		if logs.user.bot:
			for bot_id in white_list:
				if bot_id == user.id:
					try:
						value = anti_raid[server_id][user.id]
						value += 1
						anti_raid[server_id][user.id] = value
					except:
						value = 1
						anti_raid = {
						server_id: {
						user.id: value
						}
						}

					try:
						value_time = time_raid[server_id][user.id]
					except:#если нету еще записей в словаре
						value_time = time1
						time_raid = {
						server_id: {
						user.id: time1
						}
						}
					raznica = time1-value_time
					if raznica > 5.5:
						anti_raid[server_id][user.id] = 1
						value = 1
						time_raid[server_id][user.id] = time1
					if value > 4:
						try:
							await user.ban(reason=reason)
							embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
							await owner.send(embed=embed)
							white_list.remove(user.id)
							cursor.execute("UPDATE white SET bot_id_list = ? WHERE server = ?", (json.dumps(white_list), server_id))
							time_raid[server_id][user.id] = time1	
						except:
							return	
					time_raid[server_id][user.id] = time1
					return
				time_raid[server_id][user.id] = time1

			try:
				await user.ban(reason=reason)	
			except disnake.errors.Forbidden:
				return
			
			embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
			await owner.send(embed=embed)			

@bot.event
async def on_guild_role_update(before, after):
	global anti_raid
	global time_raid
	guild = after.guild
	server_id = guild.id
	audit_logs = await guild.audit_logs(limit=1).flatten()
	logs = audit_logs[0]
	user = logs.user
	target = logs.target
	name = before.name
	reason = "Рейд бот"
	owner = guild.owner
	time1 = time.time()
	guild_name = guild.name
	try:
		guild_avatar = guild.icon.url
	except:
		guild_avatar = None	
	raid_reason_r = "Редактирование ролей(массовое переименование, изменение позиции ролей)"
	raid_reason_e = "Editing roles (mass renaming, changing the position of roles)"

	cursor.execute("SELECT * FROM white WHERE server = ?", (server_id,))
	result = cursor.fetchone()
	automod_status = await automod_check_role(after)

	if bot.user.id == user.id:
		return

	if result:
		white_list = json.loads(result[1])
	else:
		white_list = []

	if automod_status == True: # переименование ролей
		if logs.user.bot:
			for bot_id in white_list:
				if bot_id == user.id:
					try:
						value = anti_raid[server_id][user.id]
						value += 1
						anti_raid[server_id][user.id] = value
					except:
						value = 1
						anti_raid = {
						server_id: {
						user.id: value
						}
						}

					try:
						value_time = time_raid[server_id][user.id]
					except:#если нету еще записей в словаре
						value_time = time1
						time_raid = {
						server_id: {
						user.id: time1
						}
						}
					raznica = time1-value_time
					if raznica > 5.5:
						anti_raid[server_id][user.id] = 1
						value = 1
						time_raid[server_id][user.id] = time1
					if value > 4:
						try:
							await user.ban(reason=reason)
							embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
							await owner.send(embed=embed)
							white_list.remove(user.id)
							cursor.execute("UPDATE white SET bot_id_list = ? WHERE server = ?", (json.dumps(white_list), server_id))
							time_raid[server_id][user.id] = time1	
						except:
							return	
					time_raid[server_id][user.id] = time1
					return
			try:
				await user.ban(reason=reason)	
			except:
				return
			embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
			await owner.send(embed=embed)			
			return

	if before.is_bot_managed():# если на роль бота дали права
		if automod_status == True:
			if after.permissions.administrator or after.permissions.ban_members or after.permissions.manage_roles or after.permissions.manage_channels or after.permissions.kick_members or after.permissions.manage_messages or after.permissions.manage_guild or after.permissions.mute_members or after.permissions.moderate_members:			
				for bot_member in after.members:
					for bot_id in white_list:
						if bot_id == bot_member.id:
							return
				try:
					await after.edit(permissions=before.permissions)
				except:
					return

	if automod_status == True:# если боту дали обычную роль а потом отредактили ее
		if after.permissions.administrator or after.permissions.ban_members or after.permissions.manage_roles or after.permissions.manage_channels or after.permissions.kick_members or after.permissions.manage_messages or after.permissions.manage_guild or after.permissions.mute_members or after.permissions.moderate_members:
			for member in after.members:
				if member.bot:
					for bot_id in white_list:
						if bot_id == member.id:
							return
					try:
						await member.remove_roles(after)
					except:
						return

@bot.event
async def on_guild_channel_create(channel):
	global time_raid
	global anti_raid
	guild = channel.guild
	server_id = guild.id
	audit_logs = await guild.audit_logs(limit=1).flatten()
	logs = audit_logs[0]
	user = logs.user
	time1 = time.time()
	reason = "Рейд бот"
	raid_reason_r = "Создание множества каналов"
	raid_reason_e = "Creating multiple channels"
	owner = guild.owner
	guild_name = guild.name
	try:
		guild_avatar = guild.icon.url
	except:
		guild_avatar = None	

	cursor.execute("SELECT * FROM white WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if bot.user.id == user.id:
		return

	if result:
		white_list = json.loads(result[1])
	else:
		white_list = []

	automod_status = await automod_check_channel(channel)

	try:
		value = anti_raid[server_id][user.id]
		value += 1
		anti_raid[server_id][user.id] = value
	except:
		value = 1
		anti_raid = {
		server_id: {
		user.id: value
		}
		}

	try:
		value_time = time_raid[server_id][user.id]
	except:#если нету еще записей в словаре
		value_time = time1
		time_raid = {
		server_id: {
		user.id: time1
		}
		}

	if bot.user.id == user.id:
		return

	if automod_status == True:
		if user.bot:
			raznica = time1-value_time
			if raznica > 5.5:
				anti_raid[server_id][user.id] = 1
				value = 1
				time_raid[server_id][user.id] = time1
			if value > 4:
				await user.ban(reason=reason)
				embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
				await owner.send(embed=embed)
				time_raid[server_id][user.id] = time1
				try:
					white_list.remove(user.id)
					cursor.execute("UPDATE white SET bot_id_list = ? WHERE server = ?", (json.dumps(white_list), server_id))
				except:
					return
		else:
			return


	time_raid[server_id][user.id] = time1

@bot.event
async def on_guild_role_create(role):
	global time_raid
	global anti_raid
	guild = role.guild
	server_id = guild.id
	audit_logs = await guild.audit_logs(limit=1).flatten()
	logs = audit_logs[0]
	user = logs.user
	time1 = time.time()
	reason = "Рейд бот"
	raid_reason_r = "Создание множества ролей"
	raid_reason_e = "Creating multiple roles"
	owner = guild.owner
	guild_name = guild.name
	try:
		guild_avatar = guild.icon.url
	except:
		guild_avatar = None	

	cursor.execute("SELECT * FROM white WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	automod_status = await automod_check_role(role)

	try:
		value = anti_raid[server_id][user.id]
		value += 1
		anti_raid[server_id][user.id] = value
	except:
		value = 1
		anti_raid = {
		server_id: {
		user.id: value
		}
		}

	try:
		value_time = time_raid[server_id][user.id]
	except:#если нету еще записей в словаре
		value_time = time1
		time_raid = {
		server_id: {
		user.id: time1
		}
		}

	if bot.user.id == user.id:
		return

	if automod_status == True:
		if user.bot:
			raznica = time1-value_time
			if raznica > 5.5:
				anti_raid[server_id][user.id] = 1
				value = 1
			if value > 4:
				await user.ban(reason=reason)
				embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
				await owner.send(embed=embed)
				try:
					white_list.remove(user.id)
					cursor.execute("UPDATE white SET bot_id_list = ? WHERE server = ?", (json.dumps(white_list), server_id))
				except:
					return
		else:
			return


	time_raid[server_id][user.id] = time1

@bot.event
async def on_member_update(before, after):
	server_id = before.guild.id

	automod_status = await automod_check_member(before)

	cursor.execute("SELECT * FROM white WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		white_list = json.loads(result[1])
	else:
		white_list = []

	for bot_id in white_list:
		if bot_id == after.id:
			return

	if before.bot:
		if automod_status == True:
			if after.guild_permissions.administrator or after.guild_permissions.ban_members or after.guild_permissions.manage_roles or after.guild_permissions.manage_channels or after.guild_permissions.kick_members or after.guild_permissions.manage_messages or after.guild_permissions.manage_guild or after.guild_permissions.mute_members or after.guild_permissions.moderate_members:
				for role in after.roles:
					if role.is_bot_managed():
						continue
					role_perm = role.permissions
					if role_perm.administrator or role_perm.ban_members or role_perm.manage_roles or role_perm.manage_channels or role_perm.kick_members or role_perm.manage_messages or role_perm.manage_guild or role_perm.mute_members or role_perm.moderate_members:
						await after.remove_roles(role)

@bot.event
async def on_member_remove(member):
	global time_raid
	global anti_raid
	guild = member.guild
	server_id = guild.id
	audit_logs = await guild.audit_logs(limit=1).flatten()
	logs = audit_logs[0]
	raid_bot = logs.user
	time1 = time.time()
	reason = "Рейд бот"
	raid_reason_r = "Кик/Бан участника/ов"
	raid_reason_e = "Kick/Ban participant/s"
	owner = guild.owner
	guild_name = guild.name
	try:
		guild_avatar = guild.icon.url
	except:
		guild_avatar = None	
	automod_status = await automod_check_member(member)

	cursor.execute("SELECT * FROM white WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if bot.user.id == raid_bot.id:
		return

	if result:
		white_list = json.loads(result[1])
	else:
		white_list = []

	if raid_bot.bot:
		for bot_id in white_list:
			if bot_id == raid_bot.id:
				try:
					value = anti_raid[server_id][raid_bot.id]
					value += 1
					anti_raid[server_id][raid_bot.id] = value
				except:
					value = 1
					anti_raid = {
					server_id: {
					raid_bot.id: value
					}
					}

				try:
					value_time = time_raid[server_id][raid_bot.id]
				except:#если нету еще записей в словаре
					value_time = time1
					time_raid = {
					server_id: {
					raid_bot.id: time1
					}
					}
				raznica = time1-value_time
				if raznica > 5.5:
					anti_raid[server_id][raid_bot.id] = 1
					value = 1
					time_raid[server_id][raid_bot.id] = time1
				if value > 3:
					try:
						await raid_bot.ban(reason=reason)
					except:
						g = "g"
					embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
					await owner.send(embed=embed)
					time_raid[server_id][raid_bot.id] = time1
					try:
						white_list.remove(raid_bot.id)
						cursor.execute("UPDATE white SET bot_id_list = ? WHERE server = ?", (json.dumps(white_list), server_id))
					except:
						return
				time_raid[server_id][raid_bot.id] = time1
				return

		await raid_bot.ban(reason=reason)
		embed = await embed_return(guild.id, guild_name, guild_avatar, raid_reason_r, raid_reason_e)
		await owner.send(embed=embed)

@bot.event
async def on_ready():
	print(f"{bot.user} готов сжигать евреев.")
	await bot.change_presence(activity=disnake.Game(name="HOI4"))

@has_permissions(administrator=True)
@bot.slash_command(
	name="set_channel_ad",
	description="канал для рекламы",
	options=[
		disnake.Option("channel", "channel", type=disnake.OptionType.channel, required=True)
	]
)
async def channel_ad(ctx, channel):
	server_id = ctx.guild.id
	language = await vibor_yazika(ctx)

	channel_id = channel.id

	cursor.execute("SELECT * FROM _url_ WHERE server = ?", (server_id,))
	result = cursor.fetchone()	

	if result:
		cursor.execute("UPDATE _url_ SET channel_id = ?  WHERE server = ?", (channel_id, server_id))
		if language == False:
			await ctx.send("Канал успешно выбран!")
		else:
			await ctx.send("Channel successfully selected!")	
	else:
		cursor.execute("INSERT INTO _url_ VALUES (?, ?)", (server_id, channel_id))
		if language == False:
			await ctx.send("Канал успешно выбран!")
		else:
			await ctx.send("Channel successfully selected!")

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
	name="set_img_add_on_join",
	description="закрепляет картинку",
	options=[
		disnake.Option("url", "img url", type=disnake.OptionType.string, required=True)
	]
)
async def img(ctx, url: str):
	server_id = ctx.guild.id
	language = await vibor_yazika(ctx)

	cursor.execute("SELECT * FROM img WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		cursor.execute("UPDATE img SET img = ?  WHERE server = ?", (url, server_id))
	else:
		cursor.execute("INSERT INTO img VALUES (?, ?)", (server_id, url))	

	if language == False:
		await ctx.send("Картинка установлена.")
	else:
		await ctx.send("The picture is set.")

async def check_img(member):
	server_id = member.guild.id

	cursor.execute("SELECT * FROM img WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		img = result[1]
	else:
		img = None

	return img

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
	server_id = member.guild.id

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
	img = await check_img(member)

	cursor.execute("SELECT * FROM automod WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		automod_status = result[1]
	else:
		automod_status = False

	if member.bot:
		if automod_status == True:
			bot_roles = member.roles
			for role in bot_roles:
				permissions = role.permissions
				if permissions.administrator or permissions.ban_members or permissions.manage_roles or permissions.manage_channels or permissions.kick_members or permissions.manage_messages or permissions.manage_guild or permissions.mute_members or permissions.moderate_members:
					permissions.update(administrator=False)
					await role.edit(permissions=permissions)

	if title is None or text_mess is None:
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
	
	embedr.set_thumbnail(url=img)

	try:
		await chanel.send(embed=embedr)
	except:
		return
	try:
		await member.add_roles(role1)
	except:
		d = "ошибка"

	try:
		await member.add_roles(role2)
	except:
		d = "ошибка"

	try:
		await member.add_roles(role3)
	except:
		d = "ошибка"


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

@has_permissions(administrator=True)
@bot.slash_command(
	name="anti_raid_system",
	description="anti raid system"
)
async def automod(ctx):
	server_id = ctx.guild.id

	language = await vibor_yazika(ctx)

	cursor.execute("SELECT * FROM automod WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		automod_status = result[1]
		if automod_status == True:
			message_r = "выкл"
			message_e = "off"
		else:
			message_r = "вкл"
			message_e = "on"
	else:
		message_r = "вкл"
		message_e = "on"

	if result:
		if ctx.guild.owner.id == ctx.author.id:
			cursor.execute("UPDATE automod SET automod = NOT automod WHERE server = ?", (server_id,))
			if language == False:
				await ctx.send(f"Статус автомода {message_r}.")
			else:
				await ctx.send(f"Automod status {message_e}.")
		else:
			if language == False:
				await ctx.send("Ты не создатель сервера.")	
			else:
				await ctx.send("You are not the server creator.")
			return
	else:
		cursor.execute("INSERT INTO automod VALUES(?, True)", (server_id,))
		if language == False:
			await ctx.send(f"Статус автомода {message_r}.")	
		else:
			await ctx.send(f"Automod status {message_e}.")

@has_permissions(administrator=True)
@bot.slash_command(
	name="white_bot_list",
	description="white bot list",
	options=[
	disnake.Option("bot_user","bot user", type=disnake.OptionType.user, required=True)
	]
)
async def white_list(ctx, bot_user):
	server_id = ctx.guild.id
	language = await vibor_yazika(ctx)

	cursor.execute("SELECT * FROM white WHERE server = ?", (server_id,))
	result = cursor.fetchone()	

	bot_user_id = bot_user.id

	if result:
		if ctx.guild.owner.id == ctx.author.id:
			white_list = json.loads(result[1])
			if bot_user.bot:
				for bot_id in white_list:
					if bot_id == bot_user_id:
						if language == False:
							await ctx.send("Такой бот уже есть")
						else:
							await ctx.send("There is already such a bot")
						return
				white_list.append(bot_user_id)
				cursor.execute("UPDATE white SET bot_id_list = ? WHERE server = ?", (json.dumps(white_list), server_id))
				if language == False:
					await ctx.send("Бот добавлен в белый список!")
				else:
					await ctx.send("Bot added to white list!")				
			else:
				if language == False:
					await ctx.send("Это не бот")
				else:
					await ctx.send("This not bot user")
				return
		else:
			if language == False:
				await ctx.send("Ты не создатель сервера.")	
			else:
				await ctx.send("You are not the server creator.")
			return	
	else:
		if ctx.guild.owner.id == ctx.author.id:
			if bot_user.bot:
				white_list = []
				white_list.append(bot_user_id)
				json_list = json.dumps(white_list)
				cursor.execute("INSERT INTO white VALUES(?, ?)", (server_id, json_list))
				if language == False:
					await ctx.send("Бот добавлен в белый список!")
				else:
					await ctx.send("Bot added to white list!")
			else:
				if language == False:
					await ctx.send("Это не бот")
				else:
					await ctx.send("This not bot user")
				return	
		else:
			if language == False:
				await ctx.send("Ты не создатель сервера.")	
			else:
				await ctx.send("You are not the server creator.")
			return		

@has_permissions(administrator=True)
@bot.slash_command(
	name="white_bot_delete_list",
	description="white bot delete list",
	options=[
	disnake.Option("bot_user","bot user", type=disnake.OptionType.user, required=True)
	]
)
async def white_list_delete(ctx, bot_user):
	server_id = ctx.guild.id
	language = await vibor_yazika(ctx)

	cursor.execute("SELECT * FROM white WHERE server = ?", (server_id,))
	result = cursor.fetchone()	

	bot_user_id = bot_user.id

	if result:
		if ctx.guild.owner.id == ctx.author.id:
			bot_list = json.loads(result[1])
			try:
				bot_list.remove(bot_user_id)
			except:
				if language == False:
					await ctx.send("Такого бота в списке нету.")
				else:
					await ctx.send("There is no such bot on the list.")
				return

			cursor.execute("UPDATE white SET bot_id_list = ? WHERE server = ?", (json.dumps(bot_list), server_id))

			if language == False:
				await ctx.send("Успешно удалено!")
			else:
				await ctx.send("Successfully deleted!")
		else:
			if language == False:
				await ctx.send("Ты не создатель сервера.")	
			else:
				await ctx.send("You are not the server creator.")
			return
	else:
		if language == False:
			await ctx.send("Ботов в списке нету!")
		else:
			await ctx.send("No bots in the list!")


@has_permissions(administrator=True)
@bot.slash_command(
	name="save",
	description="save data server",
)				
async def save(ctx):
	name = ctx.author.id
	cursor.execute("SELECT * FROM saved_server WHERE saved_name = ?", (name,))
	result = cursor.fetchone()
	saved_data = {}

	saved_data[name] = {
	"categorys": [],
	"roles": []
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

	for roles in ctx.guild.roles:
		if roles.id == ctx.guild.default_role.id:
			continue
		if roles.is_bot_managed():
			print("роль бота")
			continue	
		roles_list = {
		"name": roles.name,
		"color": roles.color.value,
		"permissions": roles.permissions.value
		}
		saved_data[name]["roles"].append(roles_list)
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
)		
async def create(ctx):
	name = ctx.author.id
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

		for roles_data in saved_data["roles"]	:
			permissions = disnake.Permissions(roles_data["permissions"])
			await ctx.guild.create_role(name=roles_data["name"], color=roles_data["color"], permissions=permissions)

@has_permissions(administrator=True)
@bot.slash_command(
	name="gaid",
	description="bot gaid"
)
async def gaid(ctx):
	language = await vibor_yazika(ctx)

	embedr = disnake.Embed(
    	title="Это краткий гайд на бота",
    	description="Все что вам надо знать о анти рейд системе приведено ниже",
    	color=00000,
    	timestamp=datetime.datetime.now(),
)
	embedr.set_author(
		name = "by: v_stoilo",
		url = "https://github.com/MrKatafan100",
		icon_url = "https://cdn.discordapp.com/attachments/1207240200758108181/1228634187385278525/PCpXdqvUWfCW1mXhH1Y_98yBpgsWxuTSTofy3NGMo9yBTATDyzVkqU580bfSln50bFU.png?ex=662cc1c1&is=661a4cc1&hm=855c4eb3755fa480f4dd2dac41d40d77d632b421cdd83a884d9f1eab185c1987&"
	)
	embedr.set_image(url="https://cdn.discordapp.com/attachments/1234459045344182363/1234511599713259630/8_1.gif?ex=66310005&is=662fae85&hm=d5d5bdedfaf49de278ace25081bed549386d62cabf8a09c705b37b2a3a5752ce&")

	embedr.set_footer(
    	text="ВСК",
    	icon_url="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExOG16NTYzbXM1a3E1dDY3ZnpqNTU4bGowd2ZwMmxyMmE5cDl6bzFvOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ouVl8qK2Nk6OxrE0zv/giphy.gif",
	)

	embedr.add_field(name="anti_raid_system", value="Система не защитит сервер полностью.", inline=True)
	embedr.add_field(name="Белый список", value="Если бот занесен в белый список его всеровно ВСК сможет забанить но требований для этого будет больше.", inline=False)
	embedr.add_field(name="Как она работает?", value="1 что сделает система не позволит боту получить любые права необходимые для рейда при входе на сервер и когда либо(исключение: бот находится в белом списке).", inline=False)
	embedr.add_field(name="Как она работает?-2", value="2 что сделает анти рейд система попытается выявить признаки рейда если таковы найдены бот будет автоматически забанен.", inline=False)
	embedr.add_field(name="Рекомендации и предупреждения", value="Бот вас не защитит от рейдов если в них не участвуют боты для этого вам придется использывать другие приложения, бот не сможет полностью сам сдержать рейд рано или поздно ВСК сдаст позиции.", inline=False)

	embede = disnake.Embed(
    	title="This is a brief guide on the bot",
    	description="All you need to know about the anti-raid system is provided below",
    	color=00000,
    	timestamp=datetime.datetime.now(),
)
	embede.set_author(
    	name="by: v_stoilo",
    	url="https://github.com/MrKatafan100",
    	icon_url="https://cdn.discordapp.com/attachments/1207240200758108181/1228634187385278525/PCpXdqvUWfCW1mXhH1Y_98yBpgsWxuTSTofy3NGMo9yBTATDyzVkqU580bfSln50bFU.png?ex=662cc1c1&is=661a4cc1&hm=855c4eb3755fa480f4dd2dac41d40d77d632b421cdd83a884d9f1eab185c1987&"
)
	embede.set_image(url="https://cdn.discordapp.com/attachments/1234459045344182363/1234511599713259630/8_1.gif?ex=66310005&is=662fae85&hm=d5d5bdedfaf49de278ace25081bed549386d62cabf8a09c705b37b2a3a5752ce&")

	embede.set_footer(
    	text="ВСК",
    	icon_url="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExOG16NTYzbXM1a3E1dDY3ZnpqNTU4bGowd2ZwMmxyMmE5cDl6bzFvOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ouVl8qK2Nk6OxrE0zv/giphy.gif",
)

	embede.add_field(name="anti_raid_system", value="The system will not fully protect the server.", inline=True)
	embede.add_field(name="White list", value="If the bot is listed in the white list, VSK will still be able to ban it, but more requirements will be needed for this.", inline=False)
	embede.add_field(name="How does it work?", value="1. The system will prevent the bot from obtaining any permissions necessary for a raid upon entering the server and at any time (exception: the bot is listed in the white list).", inline=False)
	embede.add_field(name="How does it work? -2", value="2. The anti-raid system will attempt to detect raid signs, and if found, the bot will be automatically banned.", inline=False)
	embede.add_field(name="Recommendations and warnings", value="The bot will not protect you from raids if bots are not involved in them; for this, you will need to use other applications. The bot will not be able to fully withstand the raid; sooner or later VSK will give up.", inline=False)

	if language == False:
		await ctx.send(embed=embedr)
	else:
		await ctx.send(embed=embede)

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

async def automod_check_role(role):
	server_id = role.guild.id

	cursor.execute("SELECT * FROM automod WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		automod_status = result[1]
	else:
		automod_status = None

	return automod_status

async def automod_check_member(member):
	server_id = member.guild.id

	cursor.execute("SELECT * FROM automod WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		automod_status = result[1]
	else:
		automod_status = None

	return automod_status

async def embed_return(id_server, guild_name, guild_avatar, raid_reason_r, raid_reason_e):
	cursor.execute("SELECT * FROM local WHERE server = ?", (id_server,))
	result = cursor.fetchone()

	if result:
		language = result[1]
	else:
		language = None

	embed1 = disnake.Embed(
    	title="Информация о рейде",
    	description=f"Ваш сервер пытались зарейдить путем <{raid_reason_r}>. ",
    	color=000000,
    	timestamp=datetime.datetime.now()
	)
	embed1.set_footer(
    	text=guild_name,
    	icon_url=guild_avatar,
	)

	embed2 = disnake.Embed(
    	title="Raid Information",
    	description=f"Your server was attempted to be raided by <{raid_reason_e}>.",
    	color=000000,
    	timestamp=datetime.datetime.now()
	)
	embed2.set_footer(
    	text=guild_name,
    	icon_url=guild_avatar,
	)

	if language == False:
		return embed1
	else:
		return embed2

async def check_channel_ad(server_id):
	cursor.execute("SELECT * FROM _url_ WHERE server = ?", (server_id,))
	result = cursor.fetchone()

	if result:
		channel_id = result[1]
	else:
		channel_id = None

	return channel_id

bot.run("you_tocen")
db.commit()
db.close()
