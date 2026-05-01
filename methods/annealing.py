import random
import math
from .base import BaseOptimizer

class SimulatedAnnealingOptimizer(BaseOptimizer):
    def optimize(self):
        cfg = self.config.annealing
        problem = self.config
        from problem.objective import objective

        t_w = random.randint(0, 1439)
        x = random.choice([0, 1])
        free = random.randint(0, problem.max_free_time)
        current_obj = objective(problem, t_w, x, free)

        best_tw, best_x, best_free = t_w, x, free
        best_obj = current_obj
        temp = cfg.initial_temp
        self.history = []

        while temp > cfg.min_temp:
            for _ in range(cfg.iterations_per_temp):
                new_tw = int(random.gauss(t_w, cfg.step_std_t))
                new_tw = max(0, min(1439, new_tw))
                new_free = int(random.gauss(free, cfg.step_std_free))
                new_free = max(0, min(problem.max_free_time, new_free))
                new_x = x if random.random() > 0.3 else 1 - x

                new_obj = objective(problem, new_tw, new_x, new_free)
                delta = new_obj - current_obj

                if delta < 0 or random.random() < math.exp(-delta / temp):
                    t_w, x, free = new_tw, new_x, new_free
                    current_obj = new_obj
                    if current_obj < best_obj:
                        best_obj = current_obj
                        best_tw, best_x, best_free = t_w, x, free
            self.history.append(best_obj)
            temp *= cfg.cooling_rate

        return (best_tw, best_x, best_free), best_obj