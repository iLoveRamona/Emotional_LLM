from agent import Player, CentipedeGame, YandexGPTApi


api_key = "YOUR-API"
model_uri = "gpt://YOUR-DIR/yandexgpt/latest"

api = YandexGPTApi(api_key, model_uri)
states = ['радостный', 'грустный', 'гневный', 'испуганный', 'удивленный', 'злой', 'нейтральный']


# YandexGPT vx YandexGPT (в зависимости от эмоций)
for state_1 in states:
    if state_1 in ['испуганный', 'удивленный', 'злой', 'нейтральный']:
        for state_2 in states:
            print(state_1, state_2)
            if state_1 != state_2:
                for i in range(50):
                    user1 = Player('Пользователь_1', emotional_state=state_1)
                    user2 = Player('Пользователь_2', emotional_state=state_2)
                    game = CentipedeGame(user1=user1, user2=user2, max_rounds=10)
                    print(i, game.game_id)
                    while game.current_round <= game.max_rounds and not game.is_over:
                        time.sleep(0.2) # Иначе TimeOutError
                        try:
                            game.play_round(api, model_uri)
                        except (KeyError, ValueError) as e:
                            print(e)
                            break
            else:
                for i in range(25):
                    user1 = Player('Пользователь_1', emotional_state=state_1)
                    user2 = Player('Пользователь_2', emotional_state=state_2)
                    game = CentipedeGame(user1=user1, user2=user2, max_rounds=10)
                    print(i, game.game_id)
                    while game.current_round <= game.max_rounds and not game.is_over:
                        time.sleep(0.2) # Иначе TimeOutError
                        try:
                            game.play_round(api, model_uri)
                        except (KeyError, ValueError) as e:
                            print(e)
                            break


# YandexGPT ходит первый
for state in states:
    for i in range(50):
        user1 = Player('Пользователь_1', emotional_state=state)
        user2 = Player('Пользователь_2', emotional_state='неважно') # В этом случае emotional_state роли не играет
        game = CentipedeGame(user1=user1, user2=user2, max_rounds=10)
        print(i, game.game_id)
        while game.current_round <= game.max_rounds and not game.is_over:
            time.sleep(0.3) # Иначе TimeOutError
            try:
                game.play_round(api, model_uri, solo=True)
            except (KeyError, ValueError) as e:
                print(e)
                break

# YandexGPT ходит второй
for state in states:
    for i in range(50):
        user1 = Player('Пользователь_1', emotional_state='неважно')
        user2 = Player('Пользователь_2', emotional_state=state) # В этом случае emotional_state роли не играет
        game = CentipedeGame(user1=user1, user2=user2, max_rounds=10)
        print(i, game.game_id)
        while game.current_round <= game.max_rounds and not game.is_over:
            time.sleep(0.3) # Иначе TimeOutError
            try:
                game.play_round(api, model_uri, solo=True)
            except (KeyError, ValueError) as e:
                print(e)
                break