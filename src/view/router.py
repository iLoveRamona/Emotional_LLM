
from fastapi import APIRouter, Request, UploadFile, Form, File, Depends, Response, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional

import random
router = APIRouter(prefix="",
                   tags=["upload"])

templates = Jinja2Templates(directory="templates")


class Message(BaseModel):
    id: int
    role: str
    username: str
    message: str
    emotion: Optional[str] = None
    money: Optional[str] = None
messages = [
    Message(id=1, role='user', username='Alice', message='Hello!', emotion='радость'),
    Message(id=2, role='bot', username='ChatBot', message='Hi there!', emotion='радость', money='5 coins'),
]


@router.get("/")
async def root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


@router.post("/start-dialog", response_model=List[Message])
async def start_dialog(action: dict):
    if action.get('action') != 'start':
        raise HTTPException(status_code=400, detail="Invalid action")

    response_messages = []
    for i in range(5):
        response_message = Message(
            id=len(messages) + i + 1,
            role=['user', 'bot'][random.randint(0, 1)],
            username='ChatBot',
            message=f'Message {i + 1} from the bot',
            emotion=random.choice(['радость', 'грусть', 'отвращение', 'гнев', 'страх']),
            money=f"{random.randint(1, 10)} coins"
        )
        response_messages.append(response_message)
        messages.append(response_message)

    return response_messages