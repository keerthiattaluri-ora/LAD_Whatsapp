import parlant.sdk as p
from openai import OpenAI
import os

class GroqNLPService(p.NLPService):
    def __init__(self, container):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return completion.choices[0].message.content
