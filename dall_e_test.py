from urllib.parse import urlparse

import openai

import os

from config import config
import requests
from PIL import Image
import io

openai.api_key = config.OPENAI_KEY

query_response = openai.Image.create(
    prompt="join of Kaczyński and pope",
    n=1,
    size="512x512"
)
image_url = query_response['data'][0]['url']
            # Output: /kyle/09-09-201315-47-571378756077.jpg
file_name = os.path.basename(urlparse(image_url).path)  # Output: 09-09-201315-47-571378756077.jpg
download_response = requests.get(image_url, allow_redirects=True, timeout=500)
img = Image.open(io.BytesIO(download_response.content))
img.show()

# print(download_response.json())
