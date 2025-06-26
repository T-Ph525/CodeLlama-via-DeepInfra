import streamlit as st
from openai import OpenAI
import os

# Initialize OpenAI client with RunPod endpoint
client = OpenAI(
    api_key=os.getenv('RUNPOD_API_KEY'),  # Ensure you have this in your environment variables
    base_url='https://api.runpod.ai/v2/78o7kdng19e9mo/openai/v1'  # Replace with your RunPod endpoint
)

async def fetch_models():
    try:
        # Fetch the list of models
        models_response = await client.models.list()
        # Extract model IDs
        list_of_models = [model.id for model in models_response.data]
        return list_of_models
    except Exception as error:
        print(f'Error fetching models: {error}')
        return []

def main():
    st.title('RunPod Models List')
    # Fetch and display the list of models
    models = fetch_models()
    st.subheader('Available Models')
    if models:
        for model in models:
            st.write(model)
    else:
        st.write('No models found or there was an error fetching models.')

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
