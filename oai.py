from openai import OpenAI
import os 
from dotenv import load_dotenv

load_dotenv()

nvidia_api = os.environ.get("NVIDIA_API_KEY")
model_name= "meta/llama-3.1-70b-instruct"

#This is a function to call Open AI
def process_data(data): 
    openai = OpenAI(
        organization="nvidia", 
        base_url="https://integrate.api.nvidia.com/v1", 
        api_key=nvidia_api

    )

    prompt = f"""
                You are provided with a CSV dataset containing headers and rows of data. Please analyze the dataset and provide a concise, clear summary that includes:
                1.	An overall overview or theme of the dataset, if identifiable.
                2.	A description of each column, including the type of data it contains (e.g., dates, numerical values, text).
                3.	A brief analysis of the range and distribution of key numerical columns.
                4.	Any notable trends, patterns, or outliers observed.
                5.	Potential insights or questions that the data might help answer.

                    Ensure the summary is understandable for someone without prior context about the dataset.

                This is the data {data}.
        """
    # calling open ai api call
    response = openai.chat.completions.create(
        model=model_name, 
        messages= [{"role": "user", "content": prompt}], 
        temperature=0.5
    )

    explanation=response.choices[0].message.content
    return explanation