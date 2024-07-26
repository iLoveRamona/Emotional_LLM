from abc import ABC
from copy import deepcopy
from typing import Any, Dict, List, Callable


class ActionSpace:
    """Action space is specific to the selected game and may contain continuous
     (proposed split in Ultimatum proposer) or discrete (decision in Ultimatum 
     Responder).  
    """
    def get_description_prompt(self):
        pass

    def update(self):
        pass


class Role:
    """Dataclass defining roles in the game (like Proposer and Responder in 
    the Ultimatum game) and the default_action_space (continuous or discrete) 
    """
    name: str
    default_action_space: ActionSpace


class Player:
    """Player class defines Role of a player in the game, id (for the cases when we 
    have multiple players with the same role) and the action space which can be updated
    during the game.
    """
    role: Role
    id: int
    action_space: ActionSpace

    def __init__(self, role: Role, id):
        self.role = role
        self.id = id
        self.action_space = deepcopy(role.default_action_space)


class State:
    # Information about agent's decisions in a round
    selected_strategies: Dict[Player, Any]  # Player -> Action


class Game(ABC):
    state2reward: Callable[[State], Dict[Player, float]]
    ordered_players: List[Player]  # role: str
    # role2action_space: Dict[Player, ActionSpace]
    rules: str

    def init_roles(self, **kwargs):
        """Init roles based on a game config.
        """
        # self.player_roles =
        # self.roles_order =
        pass

    def update_simultaneous_info_all(self, player2action):
        
        # пересчет ревордов
        # распространяем инфу за раунд
        pass

    def update_info_sequential(self, player2action):
        pass

    def update_sequential_info_all(self, player2action):
        # пересчет ревордов
        # распространяем инфу за раунд
        pass

    def get_simultaneous_player_step_params(self, role: str):
        pass

    def get_sequential_player_step_params(self, role: str, player2action):
        pass


class GamePlay:
    def run(self, game: Game, player2agent: Dict[str, Agent]):
        pass



