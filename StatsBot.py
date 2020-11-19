# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 04:23:30 2020

@author: Nicolas JACQUIN

Matricule: 20148533

Contact: nicolas.jacquin@umontreal.ca

Description: Discord bot that provides stats tool for managing your server
    
Syntaxe: None. Imbeded in a discord app
"""

import os
import discord
import asyncio
from dotenv import load_dotenv
import matplotlib
import matplotlib.pyplot as plt
import random as rn
import string

from discord.ext import commands
from discord.utils import get
import datetime
from datetime import timedelta
from datetime import date
# from discord.voice_client import VoiceClient

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client =commands.Bot(command_prefix = ">", intents = intents)
client.remove_command('help')
client.suggestOpened={}

@client.event
async def on_ready():
    print("Logged in as: " + client.user.name + "\n")
	
@client.command(pass_context=True)
async def poll(ctx,arg,arg2=30):
	
	#Not displaying unvoted option in the pie chart
	def spe_autopct(pct):
		return ('%.2f%%' % pct) if pct != 0 else ''
	
	# Empty list of lists to be filled with the reactions
	reactions = [[] for i in range(0,10)]
	
	arg2 = int(arg2)
	
	#Format the args
	choices = arg.split(",")
		
	#Number emotes. Index corresponds with emote
	emoteRef = ["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]
	
	#Check if there are enough arguments
	if arg == None or len(choices) < 2:
		await ctx.send("You need at least 2 option to start a poll.")
		return
	
	#Check if there aren't too many args
	elif len(choices) > 10:
		await ctx.send("You cannot add more than 10 choices")
		return
	
	#Create the message
	toPrint = "Please choose between: "
	print(choices)
	
	for choice,count in zip(choices, range(len(choices))):
		toPrint += f"{emoteRef[count]}-{choice} // "
	
	
	toPrint = toPrint[0:len(toPrint)-3]
	message = await ctx.send(toPrint)
	
	#Add the reactions
	for choice,count in zip(choices, range(len(choices))):
		await message.add_reaction(emoteRef[count])
	
	#Wait for the poll time to end
	await asyncio.sleep(arg2)
	
	await ctx.send("The poll has expired. Processing results now...")
	
	cache_msg = get(client.cached_messages, id=message.id)
		
	reactions = [get(cache_msg.reactions, emoji=emoteRef[i]) for i in range(0,10)]
	
	#Get the arguments for the pie chart construction
	sizes = []
	for reac in reactions:
		if reac is not None:
			sizes.append(reac.count -1) #-1 needed to not count the bot's reac
		else:
			sizes.append(0)
			
	voteNb = sum(sizes)
	sizes = sizes[:len(choices)]

	#Create the pie chart
	patches, texts, percent = plt.pie(sizes, shadow=True, startangle=140, autopct=spe_autopct)
	plt.legend(patches, choices, loc="best", title=f"{voteNb} votes")
	plt.axis('equal')
	plt.tight_layout()

	#Randomly generated plot ID to prevent mixing up plots between users
	plotID = str(rn.randrange(1,100000))
	plt.savefig(f"Plot_id{plotID}.png", transparent=True)
	
	#Send the pie chart
	await ctx.send(file=discord.File(f'Plot_id{plotID}.png'))
	os.remove(f'Plot_id{plotID}.png')
	
	plt.cla()   # Clear axis
	plt.clf()   # Clear figure
	plt.close()

@client.command(pass_context=True) # TODO: rewrite with *args
async def userstats(ctx, statType = "help",user = None, private = None):
	
	if private == "private":
		private = True
	
	if user == "private":
		private = True
	
	user = ctx.message.author
	print(ctx.message.mentions)
	if len(ctx.message.mentions) > 0:
		print(ctx.message.mentions)
		user = ctx.message.mentions[0]
		
	
		
	async def help(ctx, user, private):
		helpMsg = "Hi there! This message was made to help you use >userstats.\n"
		helpMsg += "Here are the differents types of stats currently implemented:\n"
		helpMsg += '">userstats messages @user" will show stats about user\'s messages.\n'
		helpMsg += '">userstats help" will show this message.\n'
		helpMsg += "You can add the keyword private at the end of your command to receive the results in your DMs\n"
		helpMsg += "_Note: If you don't specify a user, I will assume that you want your own stats._"
		await user.send(helpMsg)
	
	async def messages(ctx, user, private):
		
		await ctx.send("Retrieving the messages from " + user.display_name + "...")
		dayMonthList = []
		dateList = []
		channelList = []
		hasAllAccess = True
		
		if private:
			toSend = ctx.message.author
		else:
			toSend = ctx

		# Goes through every channel to find the user's messages
		for channel in ctx.message.guild.text_channels:
			
			try:
				
				# Goes through the messages of this channel
				async for msg in channel.history(limit=10000):
					msgDate = msg.created_at
					
					now = date.today()
					then = msgDate.date()
					limit = now - timedelta(days = 30)
					
					# If the message is older than 30 days, our job is done here
					if then < limit:
						break
					
					# If the message is from the user, then it's the data we want
					elif msg.author == user:
						dateList.append(then)
						channelList.append(msg.channel.name)
			
			# The bot might not have access to certain channels
			except discord.errors.Forbidden:
				hasAllAccess = False
		
		# Sorting the dateList
		dateList.sort()
		
		# TODO: Maybe set() before to avoid another long loop?
		for dates in dateList:
			day = dates.day
			monthName = dates.strftime("%b")
			dayMonth = str(day) + " - " + monthName
			dayMonthList.append(dayMonth)
		
		
		# Now that we retrieved the data, we prepare graphs out of it
		dayNb = []
		channelNb = []
		
		# A list of unique days that still keeps order
		uniqueDayMonth = list(sorted(set(dayMonthList), key=dayMonthList.index))
		uniqueChannel = list(sorted(set(channelList), key=channelList.index))
		
		# List of messages/month ordered by the unique days list
		for dayMonth in uniqueDayMonth:
			dayNb.append(dayMonthList.count(dayMonth))
		
		# List of nb of messages/channel ordered by the channel list
		for channel in uniqueChannel:
			channelNb.append(channelList.count(channel))

		# Creates the msg/day graph
		matplotlib.rcParams.update({'font.size': 14})
		fig = plt.figure(figsize = [12,7])
		plt.style.use("dark_background")
		
		# Creates the messages/day plot
		ax = fig.add_subplot(211)
		ax.set_facecolor("#36393E")
		ax.bar(uniqueDayMonth,dayNb, color = "#7289DA")
		ax.set_title("messages/day from "+user.display_name+" in the last 30 days")
		
		# Final touches
		plt.xticks(rotation=45)
		plt.tight_layout()
		
		# Creates the messages/channel plot
		ax2 = fig.add_subplot(212)
		ax2.set_facecolor("#36393E")
		ax2.bar(uniqueChannel,channelNb, color = "#7289DA")
		ax2.set_title("messages/channel from "+user.display_name+" in the last 30 days")
		
		# Final touches
		plt.xticks(rotation=35)
		plt.tight_layout()
		
		#Randomly generated plot ID to prevent mixing up plots between users
		plotID = str(rn.randrange(1,10000000))
		plt.savefig(f"Plot_id{plotID}.png", transparent=False, facecolor="#36393E", edgecolor='none')
		
		# Set the font size back to default
		matplotlib.rcParams.update({'font.size': 12})
		
		#Send the plot
		if private:
			await ctx.send("The data has been processed! Check your DMs!   (private stats)")
		
		await toSend.send("Here are the stats for "+ user.mention +" 's messages:   (Click to enhance)")
		await toSend.send(file=discord.File(f'Plot_id{plotID}.png'))
		os.remove(f'Plot_id{plotID}.png')
	
		plt.cla()   # Clear axis
		plt.clf()   # Clear figure
		plt.close()
					
	await eval(f"{statType}(ctx,user,private)")

@client.command(pass_context=True)
async def serverstats(ctx, *args):
	
	if args[len(args)-1] == "private":
		private = True
	else:
		private = False
		
	#Not displaying unvoted option in the pie chart
	def spe_autopct(pct):
		return ('%.2f%%' % pct) if pct != 0 else ''
	
	async def channels(ctx, private):
		pass
		
	async def roles(ctx, private):
		tmp = ctx.guild.roles
		dicRoles = {toAdd:0 for toAdd in tmp if not toAdd.is_default()}
		sizes = []
		
		for toCheck in ctx.guild.members:
			for toAdd in toCheck.roles:
				if not toAdd.is_default():
					dicRoles[toAdd] += 1
					
		sizes = dicRoles.values()
		
		#Create the pie chart
		patches, texts, percent = plt.pie(sizes, shadow=True, startangle=140, autopct=spe_autopct)
		plt.legend(patches, dicRoles.keys(), loc="best", title=f"Role repartition in {ctx.guild.name}")
		plt.axis('equal')
		plt.tight_layout()
	
		#Randomly generated plot ID to prevent mixing up plots between users
		plotID = str(rn.randrange(1,100000))
		plt.savefig(f"Plot_id{plotID}.png", transparent=True)
		
		#Send the pie chart
		if private:
			await ctx.author.send(file=discord.File(f'Plot_id{plotID}.png'))
		else:
			await ctx.send(file=discord.File(f'Plot_id{plotID}.png'))
		os.remove(f'Plot_id{plotID}.png')
		
		plt.cla()   # Clear axis
		plt.clf()   # Clear figure
		plt.close()
		
		print(dicRoles)
		
		
	await eval(f"{args[0]}(ctx, private)")


@client.command(pass_context=True)
async def help(ctx, *args):
	user = ctx.author
	toSend = " ```\nThis is the list of the currently available commands:        ([argument] = required argument, {argument} = optional argument)\n\n>help\nSends this message in the user's DMs.\n\n>poll [options] {time}\nThis command will generate a poll for users to vote. At the of the time, the bot will post a pie chart of the results.\n[options]: All the options the users can vote for. Follow this format: \"option1,option2,option3\" (quotation marks included). You can add up to 10 options.\n{time}: The amount of time users will have to vote in seconds. If no time is specified, defaults to 30.\n# Note: If the bots needs to restart, ongoing polls will be lost. Try to avoid making the poll too long to prevent any kind of loss.\n\n>userstats [type] {@user} {private}\nThis command allows you to obtain various stats on a user. \n[type]: There are several types:\nmessages: this will retrieve the messages from a user, and post graphs of the user's messaging history statistics on this server.\n(more types to come)\n{@user}: The user you wish to collect stats from. You need to mention the user with @user. If no user is specified, defaults to the one who used the command.\n{private}: if the keyword \"private\" is used at the end of the command, the results will be sent in the DMs of the person using the command.\n\n>serverstats [type] {private}\nThis command allows you to obtain various stats on the server.\n[type]: There are several types:\nroles: This will retrieve the repartition of roles in the server and post a pie chart showing it.\n(more types to come)\n{private}: if the keyword \"private\" is used at the end of the command, the results will be sent in the DMs of the person using the command.\n```"
	await user.send(toSend)

client.run(token)
