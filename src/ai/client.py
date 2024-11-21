from abc import ABC, abstractmethod

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from src.ai.config import settings_openai, settings_ollama
from src.schemas import ReviewInAI


class AbstractAIAdapter(ABC):
    client = None
    model = None

    @abstractmethod
    async def chat_completion(self, *args, **kwargs):
        pass


class OllamaAdapter(AbstractAIAdapter):
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings_ollama.OLLAMA_URL,
            api_key='ollama',
        )
        self.model = settings_ollama.OLLAMA_MODEL

    async def chat_completion(self, messages):
        return await self.client.chat.completions.create(
            messages=messages, model=self.model, temperature=0.2
        )


class OpenAIAdapter(AbstractAIAdapter):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings_openai.OPENAI_TOKEN.get_secret_value()
        )
        self.model = settings_ollama.MODEL_VERSION

    async def chat_completion(self, messages):
        return await self.client.chat.completions.create(
            messages=messages, model='gpt-3.5-turbo', temperature=0.2
        )


class AIClient:
    def __init__(self, ai_adapter: AbstractAIAdapter):
        self.ai_adapter = ai_adapter
        self.user_prompt = {
            'role': 'user',
            'content': """
            Step by step identify the problem this code solves. 
            Compare how well it solves the problem given the assignment description and the candidate's level. 
            Provide comments on how to improve the code according to best practices, including clean code structure, 
            consistent formatting, test coverage, and proper error handling, if any, given the candidate's level. 
            Please rate on a scale from 0 to 10 how well this solution matches the task description,according to best practices, 
            including clean code structure, consistent formatting, test coverage, and proper error handling. Return only **Expected Outputs** in json
            
            - **Annotated Inputs**:
              - `assignment_description` (string): Provide a detailed description of the coding assignment.
              - `candidate_level` (enum): Candidate's level (`Junior`, `Middle`, or `Senior`).
              - `text_files`: 
                - `path` (string): The relative path of the file in the repository.
                - `content` (string): The full content of the file, including code, markdown, and comments.
            
            - **Expected Outputs**:
            {
              'found_files' (list of strings): List of file path.
              'comments' (list of strings): Provide constructive feedback on the code quality, including its strengths and areas for improvement.
              'rating' (float): Give an overall rating for the code out of 10.
              'conclusion' (string): Summarize the overall assessment and recommendations for the candidate.
            }
            
            """,
        }

    async def review_repository(self, input: ReviewInAI) -> ChatCompletion:
        input = {
            'role': 'user',
            'content': input.model_dump_json(),
        }
        messages = [self.user_prompt, input]
        return await self.ai_adapter.chat_completion(messages)
