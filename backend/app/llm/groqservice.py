import os
from dotenv import load_dotenv
from groq import Groq, GroqError
load_dotenv()


class GroqService:
    def __init__(self, api_key: str = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured. Please set it in your .env file or pass it to the class."
            )

        self.client = Groq(api_key=self.api_key)
        self.model = model

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.2) -> str:
        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": prompt,
        })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content

        except GroqError as e:
            # You can log this to a file or monitoring system in a real app
            print(f"Groq API Error: {e}")
            return f"Error generating response: {e}"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "An unexpected error occurred."