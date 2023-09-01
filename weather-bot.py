"""
Subject: COMP1112 Assignment 3
Student Name: Magg Lui
Student ID: 200543030
Last Modified: 2023-08-09
"""

import discord
from discord.ext import commands
import requests
import json

# discord bot token
TOKEN = "ENTER_YOUR_TOKEN"

# discord server name
server = "ENTER_YOUR_SERVER_NAME"

# weather API key
API_KEY = "ENTER_YOUR_API_KEY"

# specify the necessary intents
intents = discord.Intents.default()
# enable member intent to send message on member joins
intents.members = True
# enable intent to check message content
intents.message_content = True

# create instance of discord bot
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """
    Send message on the general channel when the bot comes online
    :return: None
    """
    # print the client and guild info
    guild = discord.utils.get(bot.guilds, name=server)
    print(f"{bot.user} is online on {guild.name}!")

    # send message on the general channel
    general = discord.utils.get(guild.channels, name="general")
    await general.send(f"This bot will give the current weather info of different cities.\nTry now with the '!weather "
                       f"(city)' command.\nYou can pass city name, US Zipcode, UK Postcode, Canada Postalcode, "
                       f"IP address, or Latitude/Longitude (decimal degree).")


@bot.event
async def on_member_join(member):
    """
    Send welcome message on the general channel
    :param member: class discord.Member, represents the member who joins the guild
    :return: None
    """
    guild = discord.utils.get(bot.guilds, name=server)
    welcome_message = (f"Hello {member.name}, welcome to {guild.name}!\nAsk me about the current weather in any cities "
                       f"using the '!weather (city)' command.")
    # Print the member name in console
    print(f"{member.name} just joined {guild.name}.")

    # Send a channel message
    general = discord.utils.get(guild.channels, name="general")
    await general.send(welcome_message)


# The * means everything will be passed as one argument, see https://stackoverflow.com/a/52155247
@bot.command()
async def weather(ctx, *, location_query: str):
    """
    Fetch the current weather conditions in a specific location and send the results in an embedded msg
    :param ctx: Context in which a command is being invoked under
    :param location_query: String, can be city name, US Zipcode, UK Postcode,
        Canada Postalcode, IP address, or Latitude/Longitude (decimal degree)
    :return: None
    """
    response = requests.get(f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={location_query}")
    data = json.loads(response.text)

    # show error message if client provides a wrong location reference
    if "error" in data:
        # Create embedded message
        error = discord.Embed(
            title="Not Found",
            description=data["error"]["message"],
            color=discord.Color.red(),
        )
        # Send error message
        await ctx.send(embed=error)
        # print to console for debugging purpose
        print("Location not found\n")

    # otherwise fetch the current weather conditions of the specified location
    else:
        # location details
        city_name = data["location"]["name"]
        country = data["location"]["country"]
        local_time = data["location"]["localtime"]

        # current weather conditions
        current_weather = data["current"]
        condition = current_weather["condition"]["text"]
        icon_url = "https:" + current_weather["condition"]["icon"]
        actual_temperature = current_weather["temp_c"]
        perceived_temperature = current_weather["feelslike_c"]
        humidity = current_weather["humidity"]
        wind_kph = current_weather["wind_kph"]
        wind_dir = current_weather["wind_dir"]
        uv = current_weather["uv"]

        # Create embedded message
        result = discord.Embed(
            title=f"{city_name}, {country}\n{local_time}",
            description=condition,
            color=discord.Color.blue(),
        )

        # Set the weather icon as the message thumbnail
        result.set_thumbnail(url=icon_url)

        # Add weather details as fields
        result.add_field(name="Temperature", value=f"{actual_temperature} ℃", inline=True)
        result.add_field(name="Feels Like", value=f"{perceived_temperature} ℃", inline=True)
        result.add_field(name="Wind Speed & Direction", value=f"{wind_kph}km/h, {wind_dir}", inline=False)
        result.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        result.add_field(name="UV Index", value=uv, inline=True)

        # Set footer
        result.set_footer(text="Powered by WeatherAPI.com")

        # Send the results message
        await ctx.send(embed=result)

        # print to console for debugging purpose
        print("Weather results fetched\n")

# Run the bot
bot.run(TOKEN)
