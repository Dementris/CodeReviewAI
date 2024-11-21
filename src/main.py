from typing import Annotated

from dotenv import load_dotenv


from fastapi import FastAPI
from fastapi.params import Depends

load_dotenv()

from src.schemas import ReviewRequest, ReviewResponse  # noqa E402
from src.service import CodeReviewAIService  # noqa E402


Service = Annotated[CodeReviewAIService, Depends()]
app = FastAPI()


@app.post('/review', response_model=ReviewResponse)
async def read_root(req: ReviewRequest, service: Service):
    return await service.review_repository(req)
