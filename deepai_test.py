from config import config
import requests
from PIL import Image
import io

query_response = requests.post(
    "https://api.deepai.org/api/steampunk-generator",
    data={
        'text': 'Green Cloud Technology. This is just the first step but looks very promising.',
        'grid_size': "1"
    },
    headers={'api-key': config.DEEP_AI_API_KEY}
).json()
print(query_response['output_url'])
download_response = requests.get(query_response['output_url'], allow_redirects=True)
img = Image.open(io.BytesIO(download_response.content))
img.show()

# print(download_response.json())

