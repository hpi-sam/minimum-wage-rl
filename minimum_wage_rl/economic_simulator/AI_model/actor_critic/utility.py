from collections import namedtuple

class Storage:
    
    def __init__(self) -> None:
        self.actions = list()
        self.log_actions = list()
        self.state_values = list()
        self.advantages = list()
        self.expected_returns = list()
        self.rewards = list()
        self.episode_end_flag = list()

    def extract(self, keys):
        data = [getattr(self, k) for k in keys]
        # data = map(lambda x: torch.cat(x, dim=0), data)
        Entry = namedtuple('Entry', keys)
        return Entry(*list(data))

        # keys = ["actions","log_actions","state_values",
                # "advantages","expected_returns","rewards","episode_end_flag"]