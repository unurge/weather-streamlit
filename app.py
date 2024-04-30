import streamlit as st
import requests
from openai import OpenAI
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

import json

wKEY= os.getenv('OPENWEATHER_API_KEY')

st.title("Weather Check App")


cityName = st.text_input("Which City's temperature you want to check?")


if cityName:
    try:

        def getWeather(city):
            baseURL = f'https://api.openweathermap.org/data/2.5/weather?APPID={wKEY}&units=metric&q='
            fullURL = baseURL + city
            response = requests.get(fullURL)
            wOutput = response.json()
            return json.dumps({'City':city,
                            'Current Weather':wOutput['main']['temp'],
                            'Feels Like':wOutput['main']['feels_like']})


        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        client_groq = Groq(api_key=os.getenv('GROQ_API_KEY'))


        tools=[
                {
                "type": "function",
                "function": {
                    "name": "getWeather",
                    "description": "Get the current weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA"
                            }
                        },
                        "required": ["city"],
                    },
                }
            }
        ]


        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content':f'what is the temperature in {cityName}?'}],
            max_tokens=200,
            tools=tools,
            tool_choice='auto'
        )

        args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)


        currentWeather = getWeather(**args)

        groqOutput = client_groq.chat.completions.create(
            model='llama3-8b-8192',
            messages=[
                {'role':'system', 'content': '''You are a helpful AI assistant. Use this input to tell the user about the current weather and what it feels like. 
                Also, give a suggestion based on the temperature. Note that the temperature is in Celcius. Keep your response short. 
                Here's a sample output: The current temprature in New York is 43°C, and it feels like 48°C. 
                Consider taking a refreshing break in an air-conditioned space or enjoying a cool beverage in a shaded area. Stay hydrated!'''},
                {'role':'user', 'content':currentWeather}
            ],
            max_tokens=500)

        st.write(groqOutput.choices[0].message.content)

    except:
        st.write("There's an error loading the weather data")

else:
    st.write("Please enter a city name, such as 'Delhi, IN'")
