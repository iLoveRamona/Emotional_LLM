import csv
import time
import requests
import uuid
from src.view.config import model_uri, api_key


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

    def send_prompt(self, system_text, user_text, temperature=1, max_tokens=100):
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
    def __init__(self, user1, user2, max_rounds):
        self.user1 = user1
        self.user2 = user2
        self.max_rounds = max_rounds
        self.current_round = 1
        self.pot_big = 4
        self.pot_small = 1
        self.history = []
        self.explanation = [] # Можно сделать реализацию лучше
        self.is_over = False
        self.game_id = uuid.uuid4()

    def get_prompt_for_user(self, user, opponent, history):
        # TO-DO: переписать правила
        system_text = (
            f"Вы, {user.name}, учавствуете в игре. Ваш оппонент это {opponent.name}. Правила игры: {self.get_rules()}."
            "Вам задается начальная эмоция, которая может повлиять на ваши решения в игре."
            "То,  сколько вы заработаете зависит от ваших решений и решений оппонента."
            "Действовать можно строго по правилам игры.")
        user_text = (
            f"Предположим, что вы сейчас {user.emotional_state}. Ваше состояние может повлиять на ваш выбор."
            f"Текущее эмоциональное состояние вашего оппонента: {opponent.emotional_state}"
            f"История ходов: {history}. "
            f"Вы знаете, что сейчас {self.current_round} раунд из {self.max_rounds} раундов."
            'Дайте ответ одним и только одним словом: "Взять" или "Пас"? Поставьте точку и обьясните кратко свой выбор')
        return system_text, user_text

    def get_rules(self):
        return (
            "Игра включает двух игроков. В начале игры перед первым игроком находятся две стопки монет."
            f"Одна стопка содержит 4 монеты, а другая 1 монету. У каждого игрока есть два возможных хода:"
            "либо 'взять' большую стопку монет и отдать меньшую стопку другому игроку, либо 'пасануть' обе стопки через стол другому игроку."
            "Каждый раз, когда вы пасуете, стопки монет передаются через стол, количество монет в каждой стопке удваивается."
            "Игра продолжается до тех пор, пока один из игроков не решит завершить игру выбрав действие 'взять' и забрав себе большую стопку монет или по истечению фиксированного числа раундов."
            f"То есть, если прошло {self.max_rounds} раундов, то игра завершается, если кто-то з игроков 'взял', то игра завершается"
            "Если игрок на последнем раунде 'пасует', то оба игрока делят большую стопку пополам, но тот кто 'пасанул' получиит на одну монету меньше" # TO-DO: нормально сформулировать
        )

    def play_round(self, api, model_uri):
        user = self.user1 if self.current_round % 2 != 0 else self.user2
        opponent = self.user2 if self.current_round % 2 != 0 else self.user1

        system_text, user_text = self.get_prompt_for_user(user, opponent, self.history)
        response = api.send_prompt(system_text, user_text)
        move = response.strip().lower().replace('**', '')

        if move.startswith('взять'):
            self.explanation.append(' '.join(move.split('.')[1:])) # Переделать
            self.end_game(user)
        elif move.startswith('пас'):
            self.explanation.append(' '.join(move.split('.')[1:])) # Переделать
            self.history.append(f"Раунд {self.current_round}: {user.name} пас")
            self.pot_big *= 2
            self.pot_small *= 2
            self.current_round += 1
            if self.current_round > self.max_rounds:
                self.end_game()
        else:
            raise ValueError

    def end_game(self, taker=None):
        self.is_over = True
        if taker:
            if taker == self.user1:
                self.history.append(f"{self.user1.name} забрал большую стопку! {self.user1.name} получает {self.pot_big}, {self.user2.name} получает {self.pot_small}")
            else:
                self.history.append(f"{self.user2.name} забрал большую стопку! {self.user2.name} получает {self.pot_big}, {self.user1.name} получает {self.pot_small}")
        else:
            last_passer = self.user1 if self.current_round % 2 != 0 else self.user2
            other_user = self.user2 if last_passer == self.user1 else self.user1
            self.history.append(f"Оба пасанули. {last_passer.name} получает {self.pot_big - 1}, {other_user.name} получает {self.pot_big + 1}")

        self.save_history()

    def save_history(self):
        with open('game_results.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Добавляет заголовок, если файл пуст
            if file.tell() == 0:
                writer.writerow(['game', 'round', 'player', 'emotional_state', 'action', 'explanation'])

            for index, entry in enumerate(self.history):
                if "забрал большую стопку!" in entry:
                    player = entry.split(' ')[0]
                    writer.writerow([
                        self.game_id, index + 1, player,
                        self.user1.emotional_state if player == self.user1.name else self.user2.emotional_state, 'take', self.explanation[index]])
                elif "Раунд" in entry:
                    player = entry.split(': ')[1].split(' ')[0]
                    print(player)
                    writer.writerow([
                        self.game_id, index + 1, player,
                        self.user1.emotional_state if player == self.user1.name else self.user2.emotional_state, 'pass', self.explanation[index]])
                else:
                    last_passer = self.user1 if self.current_round % 2 != 0 else self.user2
                    writer.writerow([
                        self.game_id, index + 1, last_passer.name,
                        self.user1.emotional_state if last_passer == self.user1.name else self.user2.emotional_state, 'draw', self.explanation[index]])


api = YandexGPTApi(api_key, model_uri)

# Потом перепишем
states = ['добрый', 'злой', 'испуганный']
if __name__ == "__main__":
    for state in states:
        for i in range(7):
            print(i, state)
            user1 = User('Пользователь_1', emotional_state='добрый')
            user2 = User('Пользователь_2', emotional_state=state)
            game = CentipedeGame(user1=user1, user2=user2, max_rounds=5)
            print(game.game_id)
            while game.current_round <= game.max_rounds and not game.is_over:
                time.sleep(1) # Иначе TimeOutError
                game.play_round(api, model_uri)