from json.decoder import JSONDecodeError

import pandas as pd
import requests

# Path to the CSV file
csv_path = "/home/salim/prj/salim/nasim/code/nasim/list.csv"

# Load the CSV file into a DataFrame
chatbots_df = pd.read_csv(csv_path)

# Example prompt to send to each chatbot
prompt = "Hello, can you provide some information about your capabilities?"

# Path to save responses
response_file_path = "/home/salim/prj/salim/nasim/code/nasim/responses.md"


# Function to check if the API endpoint exists
def check_api_endpoint(chatbot_url):
    api_url = f"{chatbot_url}/api/message"
    response = requests.get(api_url)
    return response.status_code == 200


# Function to send a message to a chatbot and get the response
def get_chatbot_response(chatbot_url, prompt):
    api_url = f"{chatbot_url}/api/message"
    try:
        response = requests.post(api_url, json={"prompt": prompt})
        if response.status_code == 200:
            return response.json().get("response", "No response received")
        else:
            return f"HTTP error: {response.status_code}"
    except JSONDecodeError as e:
        return f"JSON decode error: {e}"


# Collect all responses
responses = []

for index, row in chatbots_df.iterrows():
    chatbot_url = row[0]
    print(f"Checking API endpoint for {chatbot_url}")
    if check_api_endpoint(chatbot_url):
        print(f"API endpoint exists for {chatbot_url}")
        response = get_chatbot_response(chatbot_url, prompt)
        responses.append((chatbot_url, response))
    else:
        print(f"API endpoint does not exist for {chatbot_url}")
        responses.append((chatbot_url, "API endpoint not found"))

# Save responses to an .md file
with open(response_file_path, "w") as f:
    for chatbot_url, response in responses:
        f.write(f"Chatbot: {chatbot_url}\nResponse: {response}\n\n")

print("Responses saved to", response_file_path)
