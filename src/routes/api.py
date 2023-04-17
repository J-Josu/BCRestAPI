import asyncio
import os
import json
from typing import Any, Callable, Coroutine, Literal, cast as cast_type
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, status,  Request
from EdgeGPT import Chatbot, ConversationStyle
from pydantic import BaseModel


# https://github.com/acheong08/EdgeGPT for more info on EdgeGPT


load_dotenv()
try:
    cookies_1 = json.loads(cast_type(str, os.getenv("BING_COOKIES_1")))
    cookies_2 = json.loads(cast_type(str, os.getenv("BING_COOKIES_2")))
except:
    raise Exception(
        'Error: COOKIES is not a valid JSON string. Please check your .env file.'
    )


bot1 = Chatbot(cookies=cookies_1)
bot2 = Chatbot(cookies=cookies_2)
# bot3 = Chatbot(cookies=cookies_3)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # First ask for ws handshake
    await bot1.ask(prompt="Hello world", conversation_style=ConversationStyle.creative)
    await bot2.ask(prompt="Hello world", conversation_style=ConversationStyle.creative)

    yield

    # Clean up
    await bot1.close()
    await bot2.close()


async def auth_dependancy(request: Request):
    if request.headers.get('Access-Token') != os.getenv('ACCESS_TOKEN'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')


MAX_SIMULTANEOUS_REQUESTS = 4
current_requests = 0


app = FastAPI(
    lifespan=lifespan,
    tags=['api'],
)
lock1 = asyncio.Lock()
lock2 = asyncio.Lock()


@app.middleware("http")
async def limit_simultaneous_requests(request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]):
    if request.headers.get('Access-Token') != os.getenv('ACCESS_TOKEN'):
        return Response("Invalid access token", status_code=status.HTTP_401_UNAUTHORIZED)

    global current_requests
    if current_requests >= MAX_SIMULTANEOUS_REQUESTS:
        return Response("Too many requests", status_code=429)

    current_requests += 1
    response = await call_next(request)
    current_requests -= 1
    return response


class Question(BaseModel):
    prompt: str
    style: Literal['creative', 'balanced', 'precise']


@app.post("/_ask/{id}")
async def ask_id(question: Question, id: int):
    if id == 1:
        lock = lock1
        bot = bot1
    elif id == 2:
        lock = lock2
        bot = bot2
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Invalid bot id')

    async with lock:
        response = await bot.ask(prompt=question.prompt, conversation_style=ConversationStyle[question.style])
        await bot.reset()
        if response is None or response['item']['result']['value'] != 'Success':
            return {'success': False}

        return {
            'success': True,
            'messages': response['item']['messages']
        }


def id_generator():
    id = 0
    while True:
        id += 1
        yield id
        if id == 2:
            id = 0


next_id = id_generator()


@app.post("/ask")
async def ask(question: Question, status_code: int = status.HTTP_200_OK):
    return await ask_id(question, next(next_id))
