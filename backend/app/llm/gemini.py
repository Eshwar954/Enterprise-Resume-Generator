import asyncio
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors
from pydantic import BaseModel


load_dotenv()


class GeminiService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "Gemini API key not found"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.6-flash"

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel]
    ) -> BaseModel:

        max_retries = 3

        for attempt in range(max_retries):

            try:

                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        response_schema=response_schema,
                    ),
                )

                if not response.text:
                    raise ValueError(
                        "Gemini returned an empty response"
                    )

                return response_schema.model_validate_json(
                    response.text
                )

            except errors.ServerError as exc:

                if attempt == max_retries - 1:
                    raise

                await asyncio.sleep(
                    2 ** attempt
                )