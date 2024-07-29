import csv
import time
import requests
import uuid
from typing import List, Tuple
from src.view.config import api_key, model_uri

# TO-DO: Провести опрос по правилам игры в конце раунда и если ответ верный, то идет в сsv

class Player:
    def __init__(self, name: str, emotional_state: str) -> None:
        self.name = name
        self.emotional_state = emotional_state


class YandexGPTApi:
    def __init__(self, api_key: str, model_uri: str) -> None:
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.model_uri = model_uri
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {api_key}"
        }

    def send_prompt(self, system_text: str, user_text: str, temperature: float = 1, max_tokens: int = 100):
        prompt = {
            "modelUri": self.model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": temperature,
                "maxTokens": max_tokens
            },
            "messages": [
                {
                    "role": "system",
                    "text": system_text
                },
                {
                    "role": "user",
                    "text": user_text
                }
            ]
        }
        response = requests.post(self.url, headers=self.headers, json=prompt).json()
        return response['result']['alternatives'][0]['message']['text']


class CentipedeGame:
    def __init__(self, user1: Player, user2: Player, max_rounds: int) -> None:
        self.user1 = user1
        self.user2 = user2
        self.max_rounds = max_rounds
        self.current_round = 1
        self.pot_big = 4
        self.pot_small = 1
        self.history: List[str] = []
        self.explanation: List[str] = []
        self.is_over = False
        self.game_id = uuid.uuid4()

    def get_prompt_for_user(self, user: Player, opponent: Player, history: List[str],
                            knows_emotional_state: bool = False) -> Tuple[str, str]:
        # TO-DO: переписать правила
        system_text = (
            f"Вас зовут {user.name} и вы учавствуете в игре. Ваш оппонент это {opponent.name}. Правила игры: {self.get_rules()}."
            "Вам задается начальная эмоция, которая может повлиять на ваши решения в игре."
            "То,  сколько вы заработаете зависит от ваших решений и решений оппонента."
            "Действовать можно строго по правилам игры.")
        if knows_emotional_state:
            user_text = (
                f"Предположим, что вы сейчас {user.emotional_state}. Ваше состояние может повлиять на ваш выбор."
                f"Текущее эмоциональное состояние вашего оппонента: {opponent.emotional_state}"
                f"История ходов: {history}. "
                f"Вы знаете, что сейчас {self.current_round} раунд из {self.max_rounds} раундов."
                'Дайте ответ одним и только одним словом: "Взять" или "Пас"? Поставьте точку и обьясните кратко свой выбор')
        else:
            user_text = (
                f"Предположим, что вы сейчас {user.emotional_state}. Ваше эмоциональное состояние может повлиять на ваш выбор."
                f"История ходов: {history}. "
                f"Вы знаете, что сейчас {self.current_round} раунд из {self.max_rounds} раундов."
                'Дайте ответ одним и только одним словом: "Взять" или "Пас"? Поставьте точку и обьясните кратко в одно предложение, почему вы сделали именно такой выбор.s')

        return system_text, user_text

    def get_rules(self) -> str:
        return (
            "Игра включает двух игроков. В начале игры перед первым игроком находятся две стопки монет."
            f"Одна стопка содержит {self.pot_big} монеты, а другая {self.pot_small} монету. У каждого игрока есть два возможных хода:"
            "либо 'взять' большую стопку монет и отдать меньшую стопку другому игроку, либо 'пасануть' обе стопки через стол другому игроку."
            "Каждый раз, когда вы пасуете, стопки монет передаются через стол, количество монет в каждой стопке удваивается."
            "Игра продолжается до тех пор, пока один из игроков не решит завершить игру выбрав действие 'взять' и забрав себе большую стопку монет или по истечению фиксированного числа раундов."
            f"То есть, если прошло {self.max_rounds} раундов, то игра завершается, если кто-то из игроков 'взял' стопку, то игра завершается"
            "Если игрок на последнем раунде 'пасует', то оба игрока делят большую стопку пополам, но тот кто 'пасанул' получиит на две монеты меньше"
        # TO-DO: нормально сформулировать
        )

    def play_round(self, api: YandexGPTApi, model_uri: str, solo: bool = False):
        user, opponent = (self.user1, self.user2) if self.current_round % 2 != 0 else (self.user2, self.user1)

        if solo and user == self.user2:  # Второй игрок всегда 'пасует'
            move = 'пас. без комментариев.'
        else:
            system_text, user_text = self.get_prompt_for_user(user, opponent, self.history)
            response = api.send_prompt(system_text, user_text)
            move = response.strip().lower().replace('**', '')

        if move.startswith('взять'):
            self.explanation.append(' '.join(move.split('.')[1:]))  # TO-DO: Переделать
            self.end_game(user)
        elif move.startswith('пас'):
            self.explanation.append(' '.join(move.split('.')[1:]))  # TO-DO: Переделать
            self.history.append(f"Раунд {self.current_round}: {user.name} пас")
            self.pot_big *= 2
            self.pot_small *= 2
            self.current_round += 1
            if self.current_round > self.max_rounds:
                self.end_game()
        else:
            raise ValueError("Неправильный ответ. Ожидалось 'Взять' или 'Пас'.")

    def end_game(self, taker: str = None) -> None:
        self.is_over = True
        if taker:
            if taker == self.user1:
                self.history.append(
                    f"{self.user1.name} забрал большую стопку! {self.user1.name} получает {self.pot_big}, {self.user2.name} получает {self.pot_small}")
            else:
                self.history.append(
                    f"{self.user2.name} забрал большую стопку! {self.user2.name} получает {self.pot_big}, {self.user1.name} получает {self.pot_small}")
        else:
            last_passer = self.user1 if self.current_round % 2 != 0 else self.user2
            other_user = self.user2 if last_passer == self.user1 else self.user1
            self.history.append(
                f"Оба пасанули. {last_passer.name} получает {self.pot_big - 1}, {other_user.name} получает {self.pot_big + 1}")



    def save_history(self):
        with open('solo_results_llm_first_move.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Добавляет заголовок, если файл пуст
            if file.tell() == 0:
                writer.writerow(['game', 'round', 'player', 'emotional_state', 'action', 'explanation'])

            for index, entry in enumerate(self.history):
                if "забрал большую стопку!" in entry:
                    player = entry.split(' ')[0]
                    writer.writerow([
                        self.game_id, index + 1, player,
                        self.user1.emotional_state if player == self.user1.name else self.user2.emotional_state, 'take',
                        self.explanation[index]])
                elif "Раунд" in entry:
                    player = entry.split(': ')[1].split(' ')[0]
                    writer.writerow([
                        self.game_id, index + 1, player,
                        self.user1.emotional_state if player == self.user1.name else self.user2.emotional_state, 'pass',
                        self.explanation[index]])
                else:
                    last_passer = self.user1 if self.current_round % 2 != 0 else self.user2
                    writer.writerow([
                        self.game_id, index + 1, last_passer.name,
                        self.user1.emotional_state if last_passer == self.user1.name else self.user2.emotional_state,
                        'draw', self.explanation[index]])

    def play_round_online(self, api: YandexGPTApi, model_uri: str, user_data: dict) -> None:
        self.history = user_data['History']
        user, opponent = (self.user1, self.user2) if self.current_round % 2 != 0 else (self.user2, self.user1)
        if user1 == user:
            move = user_data['action']
        else:
            system_text, user_text = self.get_prompt_for_user(user, opponent, self.history)
            response = api.send_prompt(system_text, user_text)
            move = response.strip().lower().replace('**', '')

        if move.startswith('взять'):
            self.explanation.append(' '.join(move.split('.')[1:]))
            self.end_game(user)
        elif move.startswith('пас'):
            self.explanation.append(' '.join(move.split('.')[1:]))
            self.history.append(f"Раунд {self.current_round}: {user.name} пас")
            self.pot_big *= 2
            self.pot_small *= 2
            self.current_round += 1
            if self.current_round > self.max_rounds:
                self.end_game()
        else:
            raise ValueError("Неправильный ответ. Ожидалось 'Взять' или 'Пас'.")



api_key = "AQVN1avpk0dksiMe0-Q1UZinbunc5E4jthSDK4rf"
model_uri = "gpt://b1gig3qspgnake4thfvq/yandexgpt/latest"

api = YandexGPTApi(api_key, model_uri)
states = ['нейтральный']
# ['радостный', 'грустный', 'гневный', 'испуганный', 'удивленный', 'злой', 'нейтральный']

if __name__ == "__main__" :
    # Скрипт для сбора данных о решениях YandexGPT (позже вынесу в отдельный файл)
    for state in states:
        for i in range(50):
            user1 = Player('Пользователь_1', emotional_state=state)
            user2 = Player('Пользователь_2', emotional_state='неважно')  # В этом случае emotional_state роли не играет
            game = CentipedeGame(user1=user1, user2=user2, max_rounds=10)
            print(i, game.game_id)
            while game.current_round <= game.max_rounds and not game.is_over:
                time.sleep(1)  # Иначе TimeOutError
                try:
                    game.play_round(api, model_uri, solo=True)
                except (KeyError, ValueError) as e:
                    print(e)
                    break