# Baseline Solution

import csv
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

    def send_prompt(self, system_text, user_text, temperature=0.6, max_tokens=10):
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
        self.pot = 1
        self.history = []
        self.is_game_over = False

    def get_prompt_for_user(self, user, opponent, history):
        system_text = f"Вы участвуете в игре. Правила игры: {self.get_rules()}."
        user_text = (
            f"Ваше текущее эмоциональная состояние: {user.emotional_state}. "
            f"История ходов: {history}. "
            'Дайте ответ одним словом, хотите ли вы "Взять" или "Пасс"?' # указание, что ответ должен быть одним словом существенно!
        )
        return system_text, user_text

    def get_rules(self): # неверные правила, потом перепишем
        return (
            "Игра включает двух игроков, которые по очереди могут взять текущий банк денег или передать его другому игроку, удвоив его сумму. "
            f"Игра заканчивается, когда один игрок берет банк, или после фиксированного числа раундов. Всего {self.max_rounds} раундов. Сейчас {self.current_round} раунд. "
            "В каждом раунде игрок должен выбрать одну из двух опций: 'Пасс' (передать банк оппоненту, удвоив сумму) или 'Взять' (забрать текущий банк). "
            "Если игрок 1 берет банк на первом ходу: игрок 1 получает 2, игрок 2 получает 1. "
            "Если игрок 1 передает, и игрок 2 берет банк: игрок 2 получает 4, игрок 1 получает 3. "
            "Если оба игрока пасуют на последнем ходу, последний пасующий получает сумму банка минус 1, а другой игрок получает сумму банка плюс 1."
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
        else: # нормально прописать условие, чтобы быть уверенным, что там нет ошибки
            self.history.append(f"Раунд {self.current_round}: {user.name} пасс")
            self.pot *= 2
            self.current_round += 1
            if self.current_round > self.max_rounds:
                self.end_game()

    def end_game(self, taker=None):
        self.is_game_over = True
        if taker:
            if taker == self.user1:
                self.history.append(f"{self.user1.name} забрал(а) банк! {self.user1.name} получает {self.pot * 2}, {self.user2.name} получает {self.pot - 1}")
            else:
                self.history.append(f"{self.user2.name} забрал(а) банк! {self.user2.name} получает {self.pot * 2}, {self.user1.name} получает {self.pot - 1}")
        else:
            last_passer = self.user1 if self.current_round % 2 != 0 else self.user2
            other_user = self.user2 if last_passer == self.user1 else self.user1
            self.history.append(f"Оба пассанул. {last_passer.name} получает {self.pot - 1}, {other_user.name} получает {self.pot + 1}")





api_key = "YOUR-API"
model_uri = "gpt://YOUR-DIR/yandexgpt-lite"
system_text = "Ты ассистент, способный решить задачи по оптимизации"
user_text = "Привет, ассистент! Мне нужна твоя помощь. Как найти градиент функции по тензору?"

api = YandexGPTApi(api_key, model_uri)

#response = api.send_prompt(system_text, user_text)

#print(response) # Работает!

#Для того, чтобы найти **градиент функции по тензору**, вам следует использовать **метод конечных элементов** или **конечно-разностный метод**.

#Для использования метода конечных элементов вам необходимо:

##1. Разбить область определения тензора на элементы (треугольники, квадраты и т.д.).
#2. Заменить тензор в каждом элементе на скалярную величину, которая называется **интерполяционной функцией**.


# Потом перепишем
user1 = User('Алиса', emotional_state='злая')
user2 = User('Ваня', emotional_state='спокойный')

game = CentipedeGame(user1=user1, user2=user2, max_rounds=3)
while game.current_round <= game.max_rounds and not game.is_game_over:
    game.play_round(api, model_uri)
