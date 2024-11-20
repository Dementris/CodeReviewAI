from typing import Annotated

from dotenv import load_dotenv


from fastapi import FastAPI
from fastapi.params import Depends

from src.schemas import ReviewRequest
from src.service import CodeReviewAIService

load_dotenv()

Service = Annotated[CodeReviewAIService, Depends()]
app = FastAPI()


@app.post('/review')
async def read_root(req: ReviewRequest, service: Service):
    return await service.review_repository(req)
