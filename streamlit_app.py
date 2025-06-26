import Streamlit from 'streamlit';
import { OpenAI } from 'openai';


const client = new OpenAI({
  apiKey: process.env.RUNPOD_API_KEY,
  baseURL: 'https://api.runpod.ai/v2/78o7kdng19e9mo/openai/v1',
});

async function fetchModels() {
  try {
    // Fetch the list of models
    const modelsResponse = await client.models.list();
    // Extract model IDs
    const listOfModels = modelsResponse.data.map(model => model.id);
    return listOfModels;
  } catch (error) {
    console.error('Error fetching models:', error);
    return [];
  }
}

async function main() {
  Streamlit.title('RunPod Models List');

  // Fetch and display the list of models
  const models = await fetchModels();

  Streamlit.subheader('Available Models');
  if (models.length > 0) {
    models.forEach(model => {
      Streamlit.write(model);
    });
  } else {
    Streamlit.write('No models found or there was an error fetching models.');
  }
}

main();
