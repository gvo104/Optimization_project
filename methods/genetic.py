import random
from .base import BaseOptimizer

class GeneticOptimizer(BaseOptimizer):
    def optimize(self):
        cfg = self.config.ga
        problem = self.config
        from problem.objective import objective

        def random_gene():
            return [
                random.randint(0, 1439),
                random.choice([0, 1]),
                random.randint(0, problem.max_free_time)
            ]

        pop = [random_gene() for _ in range(cfg.pop_size)]
        best_sol = None
        best_obj = float('inf')
        self.history = []

        for gen in range(cfg.generations):
            fits = [objective(problem, *ind) for ind in pop]
            for ind, fit in zip(pop, fits):
                if fit < best_obj:
                    best_obj = fit
                    best_sol = ind.copy()
            self.history.append(best_obj)

            new_pop = []
            sorted_idx = sorted(range(len(fits)), key=lambda i: fits[i])
            for i in range(cfg.elite_size):
                new_pop.append(pop[sorted_idx[i]])

            while len(new_pop) < cfg.pop_size:
                p1 = self._tournament(pop, fits, cfg.tournament_size)
                p2 = self._tournament(pop, fits, cfg.tournament_size)
                if random.random() < cfg.crossover_rate:
                    c1, c2 = self._crossover(p1, p2)
                else:
                    c1, c2 = p1.copy(), p2.copy()
                new_pop.append(self._mutate(c1, cfg.mutation_rate))
                if len(new_pop) < cfg.pop_size:
                    new_pop.append(self._mutate(c2, cfg.mutation_rate))
            pop = new_pop

        return (best_sol[0], best_sol[1], best_sol[2]), best_obj

    def _tournament(self, pop, fits, k):
        idx = random.sample(range(len(pop)), k)
        best_i = min(idx, key=lambda i: fits[i])
        return pop[best_i].copy()

    def _crossover(self, p1, p2):
        # blend t_w, free_time; swap x with 50% chance
        alpha = random.random()
        t1 = int(p1[0] * alpha + p2[0] * (1 - alpha))
        t2 = int(p1[0] * (1 - alpha) + p2[0] * alpha)
        t1 = max(0, min(1439, t1))
        t2 = max(0, min(1439, t2))
        f1 = int(p1[2] * alpha + p2[2] * (1 - alpha))
        f2 = int(p1[2] * (1 - alpha) + p2[2] * alpha)
        max_f = self.config.max_free_time
        f1 = max(0, min(max_f, f1))
        f2 = max(0, min(max_f, f2))
        x1, x2 = p1[1], p2[1]
        if random.random() < 0.5:
            x1, x2 = x2, x1
        return [t1, x1, f1], [t2, x2, f2]

    def _mutate(self, ind, rate):
        if random.random() < rate:
            ind[0] += random.randint(-30, 30)
            ind[0] = max(0, min(1439, ind[0]))
        if random.random() < rate:
            ind[1] = 1 - ind[1]
        if random.random() < rate:
            ind[2] += random.randint(-15, 15)
            ind[2] = max(0, min(self.config.max_free_time, ind[2]))
        return ind