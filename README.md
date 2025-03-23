# Activity Planner Assistant

This project is a simple demo for using the OpenAI Agents SDK to create an Activity Planner Assistant. The assistant helps users plan activities based on their location, date, and weather conditions.

## Features

- **Activity Planner Agent**: Asks for date and location information and routes the conversation to the Weather Agent.
- **Weather Agent**: Uses the OpenWeatherMap API to get weather information and routes the conversation to the Activities Agent.
- **Activities Agent**: Searches for activities based on location and weather, providing a summary of possible activities.
- **Calendar Agent**: Creates events in `.ics` format based on user input.

## Project Structure

- `agents_config.py`: Configuration for the agents and their interactions.
- `server.py`: FastAPI server to handle chat requests.
- `main.py`: Gradio interface for interacting with the assistant.
- `calendar/`: Directory containing `.ics` files for calendar events.
- `.env.example`: Example environment variables file.

## Setup

1. Clone the repository.
2. Create a virtual environment and activate it.
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Create a `.env` file in the root directory and add your API keys:
    ```env
    OPEN_WEATHER_API_KEY=your_open_weather_api_key
    OPEN_AI_API_KEY=your_open_ai_api_key
    ```
5. Run the FastAPI server:
    ```bash
    uvicorn server:app --reload
    ```
6. Launch the Gradio interface:
    ```bash
    python main.py
    ```

## Usage

- Access the Gradio interface to interact with the Activity Planner Assistant.
- Provide the necessary information such as date and location to get activity recommendations.
- Save activities to your calendar in `.ics` format.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [OpenAI](https://www.openai.com/) for the GPT-4 model.
- [OpenWeatherMap](https://openweathermap.org/) for the weather API.
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework.
- [Gradio](https://gradio.app/) for the user interface.
