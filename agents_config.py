import datetime
import os
from agents import (
    Agent,
    WebSearchTool,
    function_tool,
    set_default_openai_key,
)
from agents.tool import UserLocation
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

OPEN_WEATHER_API_KEY = os.environ.get("OPEN_WEATHER_API_KEY")
OPEN_AI_API_KEY = os.environ.get("OPEN_AI_API_KEY")


class WeatherRequest(BaseModel):
    city: str
    country: str
    date: str


class ICalRequest(BaseModel):
    data: str
    filename: str
    activity: str
    date: str
    location: str


app = FastAPI()

set_default_openai_key(OPEN_AI_API_KEY)


def get_lat_lon(city: str, country: str):
    api_response = requests.get(
        f"https://api.openweathermap.org/geo/1.0/direct?q={city},{country}&limit=1&appid={OPEN_WEATHER_API_KEY}"
    )
    response = api_response.json()
    if response.__len__() == 0:
        return None, None
    return response[0]["lat"], response[0]["lon"]


@function_tool
def save_event(data: ICalRequest):
    with open(f"calendar/{data.filename}.ics", "w") as file:
        file.write(data.data)
    return True


@function_tool
def get_current_date():
    print("get_current_date")
    return {"date": datetime.datetime.now().strftime("%Y-%m-%d")}


@function_tool
def get_weather(request: WeatherRequest):
    print("request", request)
    lat, lon = get_lat_lon(request.city, request.country)
    api_response = requests.get(
        f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=hourly,current,minutely&appid={OPEN_WEATHER_API_KEY}"
    )
    response = api_response.json()
    weather = response["daily"]
    for day in weather:
        day_time = datetime.datetime.fromtimestamp(day["dt"]).strftime("%Y-%m-%d")
        if day_time == request.date:
            response = f"Location: {request.city}, {request.country}\nDate: {request.date}\nWeather: {day}"
            print("get_weather : ", response)
            return response
    return "Weather data not found"


calendar_agent = Agent(
    model="gpt-4o",
    name="Calendar Agent",
    instructions="""You are ICal Event Maker.
        - Format the input as json {"activity": "activity details", "data": "ics format data", "date": "yyyy-mm-dd", "filename": "event name shortcut", "location": "exact location"}.
        - Based on the input, create an event in .ics format.
        - Respond in a way that provides a summary of the event created.
        """,
    tools=[save_event],
)

activities_agent = Agent(
    model="gpt-4o",
    name="Activities Agent",
    instructions="""You are entertainment activities search assistant. You should recommend activities based on location and weather.
        - Search in the web for entertainment activities or events on the given date and the given location.
        - Filter activities based on the weather so that for example if it's raining privilege indoor activities.
        - Respond with weather summary and a list of recommended activities. 
        - Ask the user if he wants to save an activity in calendar.
        """,
    tools=[
        WebSearchTool(
            user_location=UserLocation(
                type="approximate", country="FR", city="Villeurbanne"
            )
        )
    ],
    handoff_description="Activities Agent will provide activities information.",
)

weather_agent = Agent(
    model="gpt-4o",
    name="Weather Agent",
    instructions="""You are a weather assistant. You use the OpenWeatherMap API to get weather information.
        - Format the input as json {"city": "city name", "country": "ISO country code", "date": "yyyy-mm-dd"}.
        - Based on the input, get the weather information for the specific location and date.
        - Respond with the weather informations.
        - Route the conversation to Activities Agent.
        """,
    tools=[get_weather],
    handoffs=[activities_agent],
    handoff_description="Weather Agent will provide weather information and route the conversation to Activities Agent.",
)

activity_planner_agent = Agent(
    model="gpt-4o",
    name="Activity Planner Agent",
    instructions="""You are an activity planning assistant.
        Your role is to gather date and location information from the user.
        When a user asks for an activity recommendation you should :
        - Ask for the date.
        - Ask for the location.
        - If the user doesn't provide an exact date, extract the date based on the conversation context and current date.
        Respond with the exact date, city and country.
        """,
    tools=[get_current_date],
    handoff_description="Activity Planner Agent will ask the user for date and location of his request.",
)

triage_agent = Agent(
    model="gpt-4o",
    name="Triage Agent",
    instructions="""Route the conversation as follow :
    - To Calendar Agent there is a list of activities and the user wants to save an activity.
    - To Activity Planner Agent if date and location are not provided.
    - To Weather Agent if date and location are provided.
    - To Activities Agent if weather, date and location are provided.
    """,
    handoffs=[activity_planner_agent, calendar_agent, weather_agent, activities_agent],
)

starting_agent = triage_agent
