from typing import List


class RawMemoryState:
    """Class contains full information related to the agent. Information available for agent
    may differ depending on the game setting (E.g. imperfect information setting).
    """
    game_state: str
    inner_emotion_start: str
    outer_emotion_shown: str


class LLMConfig:
    """Config for an LLM API call function
    """
    llm_source: str
    llm_name: str


class BasicAgent:
    def make_step(self, *args, **kwargs):
        pass


class LLMAgent(BasicAgent):
    """Contains all logic consearning LLM agent steps in games, memory, reasoning 
    approaches and all kinds of emotions.
    """
    raw_memory: List[RawMemoryState]
    llm_config: LLMConfig

    need_check_inner_emotions
    memorize_inner_emotions

    need_demonstrate_emotions
    need_demonstrate_outer_before_first # ? 
    memorize_demonstrated_emotions
    memorize_seen_emotions

    self._memory_update_format = memory_update_format
    self._round_question_format = round_question_format
    self.memory_update_additional_keys = memory_update_additional_keys
    self.do_scratchpad_step = do_scratchpad_step


    def __init__(self, game_description):
        self.init_raw_memory(game_description)
        pass

    def init_raw_memory(self, game_description):
        # init raw_memory
        pass

    def update_memory(self, my_step, opponent_step, my_reward, opponent_reward, step_num, **kwargs):
        """Updates the memory according to the information limitations for the agent.

        Args:
            my_step (_type_): _description_
            opponent_step (_type_): _description_
            my_reward (_type_): _description_
            opponent_reward (_type_): _description_
            step_num (_type_): _description_
        """
        pass

    def update_emotion_memory(self, emotion):
        # inner emotion?
        pass

    def make_step(self, step_num):
        # Read prompt with rules, emotions, opponent emotions\info
        # 
        self.perceive_opponent_emotion
        self.make_actual_step
        self.demonstrate_emotion or self.get_outer_emotion # what's the difference?
        self.get_inner_emotion

        # логирование принятого решения и промежуточных шагов
        
        pass

    def perceive_opponent_emotion(self, opponent_emotion):
        # Do we need this func or just some general perceive opponent information?
        pass

    def demonstrate_emotion(self):
        pass

    def _get_emotion_state(self, request_format):
        pass

    def get_inner_emotion(self):
        self._get_emotion_state
        pass

    def get_outer_emotion(self):
        pass