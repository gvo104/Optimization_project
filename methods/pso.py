import random
import math
from .base import BaseOptimizer

class PSOOptimizer(BaseOptimizer):
    def optimize(self):
        cfg = self.config.pso
        problem = self.config
        from problem.objective import objective

        # particle: [t_w_float, x_float]
        # bounds: t_w in [0,1439], x in [0,1]
        lower = [0.0, 0.0]
        upper = [1439.0, 1.0]

        num_p = cfg.num_particles
        pos = [[random.uniform(lower[0], upper[0]), random.uniform(0,1)] for _ in range(num_p)]
        vel = [[0.0, 0.0] for _ in range(num_p)]

        # evaluate discrete
        def discretize(part):
            t_w = int(round(part[0]))
            x = 1 if part[1] > 0.5 else 0
            return t_w, x

        p_best_pos = [p.copy() for p in pos]
        p_best_obj = [float('inf')]*num_p
        g_best_pos = None
        g_best_obj = float('inf')

        self.history = []

        for it in range(cfg.iterations):
            for i, p in enumerate(pos):
                t_w, x = discretize(p)
                obj = objective(problem, t_w, x)
                if obj < p_best_obj[i]:
                    p_best_obj[i] = obj
                    p_best_pos[i] = p.copy()
                if obj < g_best_obj:
                    g_best_obj = obj
                    g_best_pos = p.copy()
            self.history.append(g_best_obj)

            # update velocity and position
            for i in range(num_p):
                r1, r2 = random.random(), random.random()
                for d in range(2):
                    v = cfg.w * vel[i][d] \
                        + cfg.c1 * r1 * (p_best_pos[i][d] - pos[i][d]) \
                        + cfg.c2 * r2 * (g_best_pos[d] - pos[i][d])
                    # velocity clamping
                    if d == 0:
                        v = max(-cfg.v_max_t, min(cfg.v_max_t, v))
                    vel[i][d] = v
                    pos[i][d] += v
                # clamp position
                pos[i][0] = max(lower[0], min(upper[0], pos[i][0]))
                pos[i][1] = max(0.0, min(1.0, pos[i][1]))

        t_w_best, x_best = discretize(g_best_pos)
        return (t_w_best, x_best), g_best_obj