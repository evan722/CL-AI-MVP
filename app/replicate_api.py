import replicate
from .config import REPLICATE_API_TOKEN

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

def generate_avatar(text, audio_url):
    output = replicate_client.run(
        "bytedance/latentsync:ccad5eab238c11ee878f7a936fd3d84c9f6d063869ea113306d3b2efb13a570c",
        input={
            "target": "https://replicate.delivery/pbxt/defaults/avatar_example.jpg",
            "source": audio_url,
            "text": text
        }
    )
    return output["video"]
