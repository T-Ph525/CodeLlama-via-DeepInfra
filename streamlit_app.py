import streamlit as st
import requests

# Set page configuration
st.set_page_config(page_title="RunPod Playground - vLLM", page_icon='🦙')

# Set API configurations
RUNPOD_API_KEY = st.secrets["RUNPOD_API_KEY"]
RUNPOD_ENDPOINT = "https://api.runpod.ai/v2/78o7kdng19e9mo/openai/v1"

# Function to fetch models from the API
def fetch_models(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    try:
        response = requests.get(f"{RUNPOD_ENDPOINT}/models", headers=headers)
        response.raise_for_status()
        models_response = response.json()
        list_of_models = [model['id'] for model in models_response.get('data', [])]
        return list_of_models
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return []

# Fetch models
list_of_models = fetch_models(RUNPOD_API_KEY)

# Model images mapping
MODEL_IMAGES = {
    model: "https://em-content.zobj.net/source/twitter/376/tornado_1f32a-fe0f.png" for model in list_of_models
}

# Format model names for display
def format_model_name(model_key):
    parts = model_key.split('/')
    model_name = parts[-1]
    name_parts = model_name.split('-')
    formatted_name = ' '.join(name_parts).title()
    return formatted_name

formatted_names_to_identifiers = {format_model_name(key): key for key in MODEL_IMAGES.keys()}

# Sidebar for model selection
selected_formatted_name = st.sidebar.radio("Select LLM Model", list(formatted_names_to_identifiers.keys()))
selected_model = formatted_names_to_identifiers[selected_formatted_name]

# Display selected model image
if MODEL_IMAGES[selected_model].startswith("http"):
    st.image(MODEL_IMAGES[selected_model], width=90)
else:
    st.write(f"Model Icon: {MODEL_IMAGES[selected_model]}", unsafe_allow_html=True)

# Function to get completion from the model
def get_completion(api_key, model, prompt, max_tokens, temperature):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    try:
        response = requests.post(f"{RUNPOD_ENDPOINT}/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        return None, str(e)

# Main app interface
st.header(f"`{selected_formatted_name}` Model")

with st.expander("About this app"):
    st.write("""
    This app allows users to interact with various models hosted on RunPod Serverless using vLLM.
    """)

# Sidebar for additional parameters
with st.sidebar:
    max_tokens = st.slider('Max Tokens', 10, 500, 100)
    temperature = st.slider('Temperature', 0.0, 1.0, 0.7, 0.05)

if max_tokens > 100:
    user_provided_api_key = st.text_input("👇 Your RunPod API Key", value=st.session_state.get("RUNPOD_API_KEY", ""), type='password')
    if user_provided_api_key:
        st.session_state.RUNPOD_API_KEY = user_provided_api_key
    if not st.session_state.get("RUNPOD_API_KEY"):
        st.warning("❄️ If you want to try this app with more than `100` tokens, you must provide your own RunPod API key.")

if max_tokens <= 100 or st.session_state.get("RUNPOD_API_KEY"):
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, error = get_completion(st.session_state.get("RUNPOD_API_KEY", ""), selected_model, prompt, max_tokens, temperature)
                if error:
                    st.error(f"Error: {error}")
                else:
                    response_text = response['choices'][0]['text']
                    placeholder = st.empty()
                    placeholder.markdown(response_text)
                    message = {"role": "assistant", "content": response_text}
                    st.session_state.messages.append(message)

# Clear chat history function
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
