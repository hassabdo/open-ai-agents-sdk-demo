import os
from agents import (
    Agent,
    WebSearchTool,
    function_tool,
    set_default_openai_key,
)
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
def get_weather(request: WeatherRequest):
    lat, lon = get_lat_lon(request.city, request.country)
    api_response = requests.get(
        f"https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}&date={request.date}&appid={OPEN_WEATHER_API_KEY}"
    )
    response = api_response.json()
    print(response)
    return response


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
    instructions="""You are activities search assistant. You should provide activities based on location and weather.
        - Search in web for activities in a the user's specific location and date
        - Based on the weather given, respond in a way that provides a summary of possible activities so that for example if it's raining privilege indoor activities. 
        - Format the activities to provide an explicit link if exists, full address and any other contact informations. 
        - Ask the user if he wants to save an activity.
        """,
    tools=[WebSearchTool()],
    handoff_description="Activities Agent will provide activities information.",
)

weather_agent = Agent(
    model="gpt-4o",
    name="Weather Agent",
    instructions="""You are a weather assistant. You use the OpenWeatherMap API to get weather information.
        - Format the input as json {"city": "city name", "country": "country code", "date": "yyyy-mm-dd"}.
        - Format the output as text providing a weather summary with location and date informations.
        - Route the conversation to Activities Agent if you have a weather summary.
        """,
    tools=[get_weather],
    handoffs=[activities_agent],
    handoff_description="Weather Agent will provide weather information and route the conversation to Activities Agent.",
)

planner_agent = Agent(
    model="gpt-4o",
    name="Activity Planner agent",
    instructions="""You are an activity planning assistant.
        When a user asks for an activity recommendation you should :
        - Ask for the exact date if the user didn't say anything about it.
        - Ask for date confirmation if the user provides a date.
        - Ask for the user's location informations.
        If you have the date and location informations, route the conversation to Weather Agent.
        """,
    handoffs=[weather_agent],
    handoff_description="Activity Planner agent will ask for date and location informations and route the conversation to Weather Agent.",
)

triage_agent = Agent(
    model="gpt-4o",
    name="Triage Agent",
    instructions="""Route the conversation as follow :
    - To Calendar Agent there is a list of activities and the user wants to save an activity.
    - To Activity Planner agent otherwise.
    """,
    handoffs=[planner_agent, calendar_agent],
)

starting_agent = triage_agent
