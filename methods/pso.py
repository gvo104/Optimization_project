import random
from .base import BaseOptimizer

class PSOOptimizer(BaseOptimizer):
    def optimize(self):
        cfg = self.config.pso
        problem = self.config
        from problem.objective import objective

        lower = [0.0, 0.0, 0.0]
        upper = [1439.0, 1.0, float(problem.max_free_time)]

        num_p = cfg.num_particles
        pos = [[random.uniform(lower[i], upper[i]) for i in range(3)] for _ in range(num_p)]
        vel = [[0.0, 0.0, 0.0] for _ in range(num_p)]

        def discretize(part):
            t_w = int(round(part[0]))
            x = 1 if part[1] > 0.5 else 0
            free = int(round(part[2]))
            free = max(0, min(problem.max_free_time, free))
            return t_w, x, free

        p_best_pos = [p.copy() for p in pos]
        p_best_obj = [float('inf')] * num_p
        g_best_pos = None
        g_best_obj = float('inf')
        self.history = []

        v_max = [cfg.v_max_t, 0.5, cfg.v_max_free]

        for it in range(cfg.iterations):
            for i, p in enumerate(pos):
                t_w, x, free = discretize(p)
                obj = objective(problem, t_w, x, free)
                if obj < p_best_obj[i]:
                    p_best_obj[i] = obj
                    p_best_pos[i] = p.copy()
                if obj < g_best_obj:
                    g_best_obj = obj
                    g_best_pos = p.copy()
            self.history.append(g_best_obj)

            for i in range(num_p):
                r1, r2 = random.random(), random.random()
                for d in range(3):
                    v = cfg.w * vel[i][d] \
                        + cfg.c1 * r1 * (p_best_pos[i][d] - pos[i][d]) \
                        + cfg.c2 * r2 * (g_best_pos[d] - pos[i][d])
                    v = max(-v_max[d], min(v_max[d], v))
                    vel[i][d] = v
                    pos[i][d] += v
                pos[i][0] = max(lower[0], min(upper[0], pos[i][0]))
                pos[i][1] = max(lower[1], min(upper[1], pos[i][1]))
                pos[i][2] = max(lower[2], min(upper[2], pos[i][2]))

        t_w_best, x_best, free_best = discretize(g_best_pos)
        return (t_w_best, x_best, free_best), g_best_obj