import gradio as gr
import requests

def get_response(message, history):
    try:
        api_response = requests.post("http://localhost:8000/chat", json={"message": message, "history": history})
        response = api_response.json()["response"]
        return response
    except requests.exceptions.RequestException as e:
        print(str(e))
        return "Error: Could not connect to server"
    
demo = gr.ChatInterface(get_response, type="messages", autofocus=True, title="Activity Planner")

if __name__ == "__main__":
    demo.launch()