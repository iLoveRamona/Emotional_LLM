import time

from fastapi import APIRouter, Request, UploadFile, Form, File, Depends, Response, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from src.view.agent import CentipedeGame, Player, api
from src.view.config import model_uri

emts = {'Joy':'радостный', 'Fear': 'испуганный', 'Anger': 'гневный', 'Disgust': 'брезгливый', 'Sadness':'грустный'}

import random
router = APIRouter(prefix="",
                   tags=["upload"])

templates = Jinja2Templates(directory="templates")
emotes = ['радостный', 'грустный', 'брезгливый', 'гневный', 'испуганный']

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
async def start_dialog(action: dict):
    print(action)
    usr1 = "Иннокентий"
    usr2 = "Василиск"
    if not (action['emotion_state_1'] in emts):
        emotion_1 = ['радостный', 'грустный', 'брезгливый', 'гневный', 'испуганный'][random.randint(0, 4)]
    else:
        emotion_1 = emts[action['emotion_state_1']]
    if not (action['emotion_state_2'] in emts):
        emotion_2 = ['радостный', 'грустный', 'брезгливый', 'гневный', 'испуганный'][random.randint(0, 4)]
    else:
        emotion_2 = emts[action['emotion_state_2']]

    users = {usr1: Player(usr1, emotion_1), usr2: Player(usr2, emotion_2)}
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
            message=game.explanation[i][0].upper() + game.explanation[i][1:].replace('васелиск', 'Васелиск').replace('иннокентий', 'Иннокентий'),
            emotion=(users[usr1] if usr else users[usr2]).emotional_state,
            money=f"big pot: {4* 2**(i)} coins \n small pot: {1 * 2 ** (i)} coins "
        )
        print(game.history[i])
        response_messages.append(response_message)

    return response_messages


@router.post("/send-messages", response_model=List[Message])
async def send_messages(action: dict):
    history = []
    action = action['messages']

    usr2 = "Иннокентий"
    usr1 = "Василиск"

    if not (action[-1][0]['emotion_state'] in emts):
        emotion = ['радостный', 'грустный', 'брезгливый', 'гневный', 'испуганный'][random.randint(0, 4)]
    else:
        emotion = emts[action[-1][0]['emotion_state']]
    print(emotion, action[-1][0]['emotion_state'])
    users = {usr1: Player(usr1, emotion),
             usr2: Player(usr2, emotion)}
    game = CentipedeGame(users[usr1], users[usr2], 10)
    for x in action:
        if x:
            if x[0]['action'] == 'Take':
                x = x[0]
                response_message = [Message(
                    id=0,
                    role=['user', 'bot'][x['role'] == usr2],
                    username='Server',
                    message=f'Игра окончена',
                    money=f"bit pot :{x['big_pot']}, small pot {x['small_pot']} ",
                    action='Take',
                    big_pot=x['big_pot'],
                    small_pot=x['small_pot'],

                )]
                break
        else:
            break

    else:
        history = []
        for x in range(len(action)):

            if x % 2 == 0:

                history.append(f'Раунд {x + 1}: Иннокентий пас')
            else:
                history.append(f'Раунд {x + 1}: Василиск пас')


        if action[-1][0]['action'] == 'Take':
            act = 'взять'
        else:
            act = 'пас'


        data = {'action': act, 'history': history}
        pot_big = game.pot_big
        pot_small = game.pot_small
        game.play_round_online(api, model_uri, data)
        usr = False
        if usr2 + ' пас' in game.history[-1] or usr2 + ' забрал' in game.history[-1]:
            usr = True

        print(game.history)
        print(game.explanation)
        if game.history[-1].split()[-1] == 'пас':
            acted = 'Pass'
        else:
            acted = 'Take'
        response_message = [Message(
            id=0,
            role=['user', 'bot'][int(usr)],
            username=usr2 if usr else usr1,
            message=game.explanation[0][0].upper() + game.explanation[0][1:].replace('васелиск', 'Васелиск'),
            emotion=(users[usr2] if usr else users[usr1]).emotional_state,
            money=f"big pot: {pot_big * 2**(len(history) - 1)} coins \n small pot: {pot_small * 2**(len(history) - 1)} coins ",
            action=acted,
            big_pot=game.pot_big * 2**(len(history) - 1),
            small_pot=game.pot_small * 2**(len(history) - 1)
        )]

    return response_message
