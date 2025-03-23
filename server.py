from agents_config import starting_agent
from agents import Runner
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    history: list


@app.get("/")
def read_root():
    return {
        "message": """sumary_line: This is a simple API for an activity planner assistant. It uses OpenAI's GPT-4 model to generate responses. The API has a single endpoint, /chat, which accepts a POST request with a JSON body containing the user's message and the conversation history. The API then uses the GPT-4 model to generate a response based on the user's message and the conversation history. The response is returned as a JSON object containing the generated text. The API is built using FastAPI, a modern web framework for building APIs with Python."""
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    formatted_history = "\n".join(
        [entry["role"] + " : " + entry["content"] for entry in request.history]
    )
    input_message = f"{formatted_history} {request.message}"
    response = await Runner.run(
        starting_agent=starting_agent,
        input=input_message,
    )
    return {
        "response": response.final_output
        if response
        else "I'm sorry, I don't understand."
    }
