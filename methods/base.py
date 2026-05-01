from abc import ABC, abstractmethod

class BaseOptimizer(ABC):
    def __init__(self, config):
        self.config = config
        self.history = []   # best objective per iteration

    @abstractmethod
    def optimize(self):
        """Return best_solution (t_w, x) and best_objective."""
        pass