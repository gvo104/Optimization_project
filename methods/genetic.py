import random
from .base import BaseOptimizer

class GeneticOptimizer(BaseOptimizer):
    def optimize(self):
        cfg = self.config.ga
        problem = self.config

        # initial population
        pop = []
        for _ in range(cfg.pop_size):
            t_w = random.randint(0, 1439)
            x = random.choice([0, 1])
            pop.append([t_w, x])

        best_sol = None
        best_obj = float('inf')

        from problem.objective import objective

        def evaluate(ind):
            return objective(problem, ind[0], ind[1])

        self.history = []

        for gen in range(cfg.generations):
            # evaluate
            fits = [evaluate(ind) for ind in pop]
            # update global best
            for ind, fit in zip(pop, fits):
                if fit < best_obj:
                    best_obj = fit
                    best_sol = ind.copy()
            self.history.append(best_obj)

            # selection & reproduction
            new_pop = []
            # elitism
            sorted_idx = sorted(range(len(fits)), key=lambda i: fits[i])
            for i in range(cfg.elite_size):
                new_pop.append(pop[sorted_idx[i]])

            while len(new_pop) < cfg.pop_size:
                # tournament selection
                p1 = self._tournament(pop, fits, cfg.tournament_size)
                p2 = self._tournament(pop, fits, cfg.tournament_size)
                if random.random() < cfg.crossover_rate:
                    c1, c2 = self._crossover(p1, p2)
                else:
                    c1, c2 = p1.copy(), p2.copy()
                c1 = self._mutate(c1, cfg.mutation_rate)
                c2 = self._mutate(c2, cfg.mutation_rate)
                new_pop.append(c1)
                if len(new_pop) < cfg.pop_size:
                    new_pop.append(c2)
            pop = new_pop

        return (best_sol[0], best_sol[1]), best_obj

    def _tournament(self, pop, fits, k):
        idx = random.sample(range(len(pop)), k)
        best_i = min(idx, key=lambda i: fits[i])
        return pop[best_i].copy()

    def _crossover(self, p1, p2):
        # blending for t_w, simple one-point for x
        alpha = random.random()
        t1 = int(p1[0] * alpha + p2[0] * (1 - alpha))
        t2 = int(p1[0] * (1 - alpha) + p2[0] * alpha)
        t1 = max(0, min(1439, t1))
        t2 = max(0, min(1439, t2))
        x1, x2 = p1[1], p2[1]
        if random.random() < 0.5:
            x1, x2 = x2, x1
        return [t1, x1], [t2, x2]

    def _mutate(self, ind, rate):
        if random.random() < rate:
            # mutate t_w
            delta = random.randint(-30, 30)
            ind[0] += delta
            ind[0] = max(0, min(1439, ind[0]))
        if random.random() < rate:
            # flip x
            ind[1] = 1 - ind[1]
        return ind