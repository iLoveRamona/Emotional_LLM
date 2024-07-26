from typing import Dict

from src.base import GamePlay, Game, Agent


class SimultaneousRoundGameplay(GamePlay):
    def run(self, game: Game, player2agent: Dict[str, Agent]):
        player2action = {}
        for player in game.ordered_players:
            cur_agent = player2agent[player]
            agent_step_params = game.get_simultaneous_player_step_params(player)
            selected_action = cur_agent.make_step(**agent_step_params)
            player2action[player] = selected_action
        return player2action
        # game.update_simultaneous_info_all(player2action)


class SequentialRoundGameplay(GamePlay):
    def run(self, game: Game, player2agent: Dict[str, Agent]):
        player2action = {}
        for player in game.ordered_players:
            game.update_info_sequential(player2action)
            cur_agent = player2agent[player]
            agent_step_params = game.get_sequential_player_step_params(player, player2action)
            selected_action = cur_agent.make_step(**agent_step_params)
            player2action[player] = selected_action
        return player2action
        # game.update_sequential_info_all(player2action)



class RepeatedGeneralPipeline():
    game_theory_game_play: GamePlay
    n_rounds: int

    def run_step(self, game: Game, player2agent: Dict[str, Agent]):
        self.exchange_info_before(game, player2agent)
        player2action = self.game_theory_game_play.run(game, player2agent)
        # логирование - общая сводка за раунд
        self.update_info_after(game, player2agent, player2action)

    def run(self, game: Game, player2agent: Dict[str, Agent]):
        for n_round in range(self.n_rounds):
            self.run_step(game, player2agent)