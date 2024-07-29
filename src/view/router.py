import time

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
    action: Optional[str] = None
    big_pot: Optional[int] = None
    small_pot: Optional[int] = None


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
        time.sleep(0.2)
        game.play_round(api, model_uri)

    response_messages = []
    for i in range(len(game.history)):
        usr = False
        if usr1 + ' пас' in game.history[i] or usr1 + ' забрал' in game.history[i]:
            usr = True
        response_message = Message(
            id=0,
            role=['user', 'bot'][int(usr)],
            username=usr1 if usr else usr2,
            message=game.explanation[i],
            emotion=(users[usr1] if usr else users[usr2]).emotional_state,
            money=f"big pot: {game.pot_big} coins \n small pot: {game.pot_small} coins "
        )
        print(game.history[i])
        response_messages.append(response_message)
        messages.append(response_message)

    return response_messages


@router.post("/send-messages", response_model=List[Message])
async def send_messages(action: dict):
    history = []
    usr1 = "Иннокентий"
    usr2 = "Василиск"
    users = {usr1: Player(usr1, ['радостный', 'грустный', 'отвращение', 'гнев', 'страх'][random.randint(0, 4)]),
             usr2: Player(usr2, ['радостный', 'грустный', 'отвращение', 'гнев', 'страх'][random.randint(0, 4)])}
    game = CentipedeGame(users[usr1], users[usr2], 10)
    for x in action:
        if x['action'] == 'Take':
            response_message = [Message(
                id=0,
                role=['user', 'bot'][x['username'] == usr1],
                username=x['username'],
                message=f'Message {1 + 1} from the bot',
                emotion=x['emotion'],
                money=f"{random.randint(1, 10)} coins",
                big_pot=
                action='Take'
            )]
            break

    else:
        for x in range(len(action)):

            if x % 2 - 1:
                history.append(f'Раунд окончен: Оба пасанули')
            else:
                history.append(f'Раунд {x // 2 + 1}: Василиск пас')
    game.play_round_online(history)

    return response_message
