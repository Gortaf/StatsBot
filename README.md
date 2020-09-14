# StatsBot for discord
A bot that provides statisical tools for managing your discord server. The bot's command prefix is >


## Adding this bot to your server
Simply click this link: https://discord.com/oauth2/authorize?client_id=729973342035247167&scope=bot&permissions=101440. Then select your server. 


## Features
StatsBot is a work in progress. It was made to give you tools to visualise stats from your discord server. Here's the current list of working features:

#### 1. \>poll

the \>poll command allows you to organise a poll accross your server. Simply follow this syntax:

>\>poll option0,option1,option2 time

where you can add up to 10 options, and time is the time before the poll is closed in seconds. When the poll is closed, the bot will process the data and post a pie chart like so:

![poll pie chart](https://i.gyazo.com/b01ae62d4a17b3e3144c87b0cea2c8b0.png "poll pie chart")

#### 2. \>userstats

the \>userstats command will be a multipurpose command to retrieve data about a certain user. Currently the only implemented features of this command are "help" and "messages"

#####   \>userstats help

This will send you a help message on how to use \>userstats.

#####   \>userstats messages

This command will retrieve the messaging data in the last 30 days from a specified user (if no user is specified, defaults to the one who used the command) and display stats for it. Simply follow this syntax:

>\>userstats messages @user

This will send stats from the user's messages in this format:

![userstats messages chart](https://i.gyazo.com/b3cba4ad4cf01fe73b008bae0a5fdd3e.png "userstats messages stats")

NOTE: you can add the keyword "private" at the end of this command to receive the results in your DMs


## Upcoming features
Any feature in that list isn't yet implemented. It only serves as a preview of what the next features of this bot will be

#### \>userstats (add more features)    [low priority]
\>userstats is already partially implemented with \>userstats messages, however this is supposed to be a multipurpose command, and as such more options will be implemented for this command. 

#### \>serverstats    [medium priority]
Much like \>userstats, serverstats will be a multipurpose command. However serverstats will provide server-wide stats, such as the repartition of messages between your channels, so you can see which channels are the most/least used. The repartition of roles in your server, etc...

#### \>opensuggest & \>suggest   [medium priority]
These command will work as a pair. Whenever the \>opensuggest command is used (with a title and time after which it closes) users will be able to suggest features in relation to your title with \>suggest. The bot will add a :+1: and :-1: reaction to the suggestion, allowing others to vote for or against it. When the suggestions are closed, the bot will compile stats from the suggestions and their votes to display a pie chart of the most voted suggestions.

Please note that these are just features that are already planned and in the work. Many more features not listed here will most likely be added.
