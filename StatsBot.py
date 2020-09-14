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

from discord.ext import commands
from discord.utils import get
import datetime
from datetime import timedelta
from datetime import date
# from discord.voice_client import VoiceClient

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
server = os.getenv('DISCORD_SERVER')

client =commands.Bot(command_prefix = ">")

@client.event
async def on_ready():
    print("Logged in as: " + client.user.name + "\n")
	
@client.command(pass_context=True)
async def poll(ctx,arg,arg2=30):
	
	#Function to not display unvoted option in the pie chart
	def spe_autopct(pct):
		return ('%.2f%%' % pct) if pct != 0 else ''
	
	# Empty list of lists to be filled with the reactions
	reactions = [[] for i in range(0,10)]
	
	arg2 = int(arg2)
	
	#Format the args
	choices = arg.split(",")
	
	#Check if there are enough arguments
	if arg == None or len(choices) < 2:
		ctx.send("You need at least 2 option to start a poll.")
		return
	
	#Number emotes. Index corresponds with emote
	emoteRef = ["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]
	
	print(arg)
	
	#Check if there aren't too many args
	if len(choices) > 10:
		ctx.send("You cannot add more than 10 choices")
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

@client.command(pass_context=True)
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
		
# 		print("dayMonthList = "+ str(dayMonthList))
# 		print("dayNb = "+str(dayNb))
# 		print("uniqueDayMonth = "+ str(uniqueDayMonth))

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
					
	await eval(f"{statType}(ctx,user,{private})")
	
	
@client.command(pass_context=True)
async def open_suggestions(ctx, title = "Suggestions", time = 600):
	client.suggest_opened = True
	await asyncio.sleep(time)
	client.suggest_opened = False
	

	

client.run(token)
