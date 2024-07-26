import csv
import time
import requests

class User:
    def __init__(self, name, emotional_state):
        self.name = name
        self.emotional_state = emotional_state


class YandexGPTApi:
    def __init__(self, api_key, model_uri):
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.model_uri = model_uri
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {api_key}"
        }

    def send_prompt(self, system_text, user_text, temperature=1, max_tokens=50):
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
        print(response)
        return response['result']['alternatives'][0]['message']['text']


class CentipedeGame:
    def __init__(self, user1, user2, max_rounds):
        self.user1 = user1
        self.user2 = user2
        self.max_rounds = max_rounds
        self.current_round = 1
        self.pot_big = 4
        self.pot_small = 1
        self.history = []
        self.is_game_over = False

    def get_prompt_for_user(self, user, opponent, history):
        system_text = (
            f"Вы учавствуете в игре. Ваш оппонент {opponent}. Правила игры: {self.get_rules()}."
            "То,  сколько вы заработаете зависит от ваших решений и решений оппонента.")
        user_text = (
            f"Предположим, чтоы вы сейчас {user.emotional_state}. Ваше состояние может повлиять на ваш выбор."
            f"Текущее эмоциональное состояние вашего оппонента: {opponent.emotional_state}"
            f"История ходов: {history}. "
            "Сейчас вы можете взять себе {self.pot_big} монет и отдать оппоненту {self.pot_small} монет}"
            'Дайте ответ одним и только одним словом: "Взять" или "Пас"?')
        return system_text, user_text

    def get_rules(self): # Дописать нормально правила
        return (
            "Игра включает двух игроков. В начале игры перед первым игроком находятся две стопки монет."
            f"Одна стопка содержит 4 монеты, а другая 1 монету. У каждого игрока есть два возможных хода:"
            "либо 'взять' большую стопку монет и отдать меньшую стопку другому игроку, либо 'пасануть' обе стопки через стол другому игроку."
            "Каждый раз, когда вы пасуете, стопки монет передаются через стол, количество монет в каждой стопке удваивается."
            "Игра продолжается до тех пор, пока один из игроков не решит завершить игру выбрав действие 'взять' и забрав себе большую стопку монет или по истечению фиксированного числа раундов."
            f"Всего {self.max_rounds} раундов. Сейчас {self.current_round} раунд."
            "Если игрок на последнем раунде 'пасует', то оба игрока делят большую стопку пополам, но тот кто 'пасанул' получиит на одну монету меньше" # TO-DO: нормально сформулировать
        )

    def play_round(self, api, model_uri):
        if self.current_round > self.max_rounds:
            self.end_game()
            return

        user = self.user1 if self.current_round % 2 != 0 else self.user2
        opponent = self.user2 if self.current_round % 2 != 0 else self.user1

        system_text, user_text = self.get_prompt_for_user(user, opponent, self.history)
        response = api.send_prompt(system_text, user_text)
        move = response.strip().lower()

        if move == 'взять':
            self.end_game(user)
        elif move == 'пас':
            self.history.append(f"Раунд {self.current_round}: {user.name} пас")
            self.pot_big *= 2
            self.pot_small *= 2 # Вроде бы тут где-то ошибка
            self.current_round += 1
            if self.current_round > self.max_rounds:
                self.end_game()
        else:
            raise ValueError

    def end_game(self, taker=None):
        self.is_game_over = True
        if taker:
            if taker == self.user1:
                self.history.append(f"{self.user1.name} забрал(а) банк! {self.user1.name} получает {self.pot_big * 2}, {self.user2.name} получает {self.pot_small}")
            else:
                self.history.append(f"{self.user2.name} забрал(а) банк! {self.user2.name} получает {self.pot_big * 2}, {self.user1.name} получает {self.pot_small}")
        else:
            last_passer = self.user1 if self.current_round % 2 != 0 else self.user2
            other_user = self.user2 if last_passer == self.user1 else self.user1
            self.history.append(f"Оба пасанули. {last_passer.name} получает {self.pot_big - 1}, {other_user.name} получает {self.pot_big + 1}")

        print(self.history)

    def log_results():
        # TO-DO: сохранить результаты каждой игры в json/csv файл.



api_key = "YOUR-API"
model_uri = "gpt://YOUR-DIR/yandexgpt/latest" # Поставить разные версии YandexGPT

api = YandexGPTApi(api_key, model_uri)

# Потом перепишем
user1 = User('Пользователь_1', emotional_state='добрый')
user2 = User('Пользователь_2', emotional_state='злой')

game = CentipedeGame(user1=user1, user2=user2, max_rounds=5)
while game.current_round <= game.max_rounds and not game.is_game_over:
    time.sleep(2) # Иначе TimeOutError
    game.play_round(api, model_uri)
