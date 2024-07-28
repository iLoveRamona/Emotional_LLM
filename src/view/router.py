
from fastapi import APIRouter, Request, UploadFile, Form, File, Depends, Response, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from src.view.agent import CentipedeGame, Player, api
from src.view.config import model_uri

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
async def start_dialog():
    usr1 = "Иннокентий"
    usr2 = "Василиск"
    users = {usr1: Player(usr1, ['радостный', 'грустный', 'отвращение', 'гнев', 'страх'][random.randint(0, 4)]), usr2: Player(usr2, ['радостный', 'грустный', 'отвращение', 'гнев', 'страх'][random.randint(0, 4)])}
    game = CentipedeGame(users[usr1], users[usr2], 10)

    while not game.is_over:
        game.play_round(api, model_uri)
    print(game.explanation)
    response_messages = []
    for i in range(len(game.history)):
        usr = False
        if usr1 in game.history[i]:
            usr = True
        response_message = Message(
            id=0,
            role=['user', 'bot'][int(usr)],
            username=(users[usr1] if usr else users[usr2]).name,
            message=game.explanation[i],
            emotion=(users[usr1] if usr else users[usr2]).emotional_state,
            money=f"{1} coins"
        )
        response_messages.append(response_message)
        messages.append(response_message)

    return response_messages


@router.post("/send-messages", response_model=List[Message])
async def send_messages(action: dict):
    if action.get('action') != 'start':
        raise HTTPException(status_code=400, detail="Invalid action")
    print(action)
    response_message = [Message(
        id=len(messages) + 1,
        role=['user', 'bot'][random.randint(0, 1)],
        username='ChatBot',
        message=f'Message {1 + 1} from the bot',
        emotion=random.choice(['радость', 'грусть', 'отвращение', 'гнев', 'страх']),
        money=f"{random.randint(1, 10)} coins"
    )]
    return response_message
