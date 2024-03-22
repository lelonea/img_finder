import os
import logging
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
prompt = ("Please provide keywords that describe the symbols or elements depicted in the image. Take a moment to "
          "examine the icons closely and identify any recognizable objects, concepts, or actions they represent. For "
          "example, if the image contains icons representing communication, you might include keywords like "
          "'message', 'chat', 'phone', 'email', etc. Aim to provide descriptive words that capture the essence of "
          "the icon, use one word only. The more keywords, the better. The more specific and relevant your keywords,"
          " the better. Provide answer in the form of a list.")


def generate_image_search_keywords(image_url):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text",
                     "text": f"access image by url {image_url}. {prompt}"},
                ],
            }
        ],
        max_tokens=300,
    )
    logging.info(f"Response from OpenAI: {response}")
    keywords = response.choices[0].message.content.split('\n')
    logging.info(f"Generated keywords for image: {image_url} - {keywords}")
    return keywords
