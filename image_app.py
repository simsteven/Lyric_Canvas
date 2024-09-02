import gradio as gr
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from openai import OpenAI
import os
import requests
from PIL import Image as PILImage
from io import BytesIO

# Initialize the OpenAI API key
openai_api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client
client = OpenAI(api_key=openai_api_key)

# Initialize the ChatOpenAI model
openai_llm = ChatOpenAI()

# Define the prompt template
prompt_template = PromptTemplate.from_template(
  """Imagine '{genre}' Album Cover and provide the detailed prompt for the Following album/song/lyrics: '{lyrics}' to create the realistic imaginery graphic for the album/music chorus by understanding and mimicing the emotional depth with the emotional tone of '{emotion}' .

Please ensure that the genre of the lyrics matches the provided genre parameter: 'Rock' for powerful guitar riffs, rebellious energy, and raw emotion; 'Pop' for catchy hooks, vibrant colors, and trendy aesthetics; 'Metal' for dark, intense imagery with heavy and aggressive tones; 'Folk' for earthy, acoustic elements with natural and rustic visuals; '80s' for retro-futuristic vibes, neon colors, and nostalgic references; 'Jazz' for smooth, elegant, and sophisticated visuals with a touch of improvisation; 'K-pop' for sleek, modern, and colorful designs with a polished, high-energy look; and 'Country' for rustic, heartfelt, and down-to-earth imagery often set in rural or natural environments.

For emotions, match the tone: 'Heartbreak' for visuals that convey loss, sadness, or longing; 'Fantasy' for dreamy, otherworldly, or surreal visuals; and 'Dark' for ominous, mysterious, or haunting imagery.

Consider the age and gender of the subject(s) in the lyrics to ensure the visuals align with their emotional experience, whether depicting a young woman in the throes of first love, an older man reflecting on past sorrows, or a child lost in a fantasy world.

The visual style should be photo-realistic, 8K resolution, hyper-detailed, and cinematic. Include elements such as high-contrast lighting, intricate detail, and realistic textures. Depending on the emotion, use glamour photography for 'Fantasy', stark contrasts for 'Dark', and soft, muted tones for 'Heartbreak'. The image should also reflect a high-fashion or art-inspired aesthetic, with influences from award-winning photography styles, cinematic lighting, and advanced rendering techniques to create a masterpiece that is both visually stunning and emotionally evocative.

If there is a person,  do not show their faces.
"""

)

# Define the lyrics response chain
lyrics_response_chain = LLMChain(llm=openai_llm, prompt=prompt_template, verbose=True)

# Create a directory for saving images if it doesn't exist
os.makedirs("generated_images", exist_ok=True)

# Function to generate and save image based on lyrics, genre, and emotion
def generate_image(lyrics, genre, emotion):
    try:
        formatted_prompt = prompt_template.format(lyrics=lyrics, genre=genre, emotion=emotion)
        response = lyrics_response_chain.run({'lyrics': lyrics, 'genre': genre, 'emotion': emotion})

        # Generate the image using DALL-E 3
        image_response = client.images.generate(
          model="dall-e-3",
          prompt=response,
          size="1024x1024",
          quality="hd",
          n=1,
        )

        image_url = image_response.data[0].url

        # Save the image locally
        response = requests.get(image_url)
        image = PILImage.open(BytesIO(response.content))
        file_path = os.path.join("generated_images", "album_cover.png")
        image.save(file_path)

        return image_url

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Create Gradio interface
def gradio_interface():
    lyrics_input = gr.Textbox(label="Lyrics", placeholder="Enter the song lyrics here...")
    genre_input = gr.Dropdown(label="Genre", choices=['Rock', 'Pop', 'Metal', 'Folk', '80s', 'Jazz', 'K-pop', 'Country'])
    emotion_input = gr.Dropdown(label="Emotion", choices=['Heartbreak', 'Fantasy', 'Dark'])
    output_image = gr.Image(label="Generated Album Cover")

    gr.Interface(fn=generate_image, 
                 inputs=[lyrics_input, genre_input, emotion_input], 
                 outputs=output_image,
                 title="Album Cover Generator").launch()

# Run the Gradio interface
gradio_interface()
