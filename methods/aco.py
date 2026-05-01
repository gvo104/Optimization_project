import random
from .base import BaseOptimizer

class AntColonyOptimizer(BaseOptimizer):
    def optimize(self):
        cfg = self.config.aco
        problem = self.config
        from problem.objective import objective

        step = cfg.step_minutes
        tw_nodes = list(range(0, 1440, step))
        free_nodes = list(range(0, problem.max_free_time + 1, step))
        x_nodes = [0, 1]

        # феромон для каждого измерения
        tau_tw = [1.0] * len(tw_nodes)
        tau_free = [1.0] * len(free_nodes)
        tau_x = [1.0, 1.0]

        best_sol = None
        best_obj = float('inf')
        self.history = []

        def heuristic(tw_idx, free_idx, x):
            return 1.0 / (objective(problem, tw_nodes[tw_idx], x, free_nodes[free_idx]) + 1e-6)

        for it in range(cfg.iterations):
            iter_best_obj = float('inf')
            iter_best_sol = None
            for _ in range(cfg.num_ants):
                # выбор t_w
                if random.random() < cfg.q0:
                    scores = [ (tau_tw[i]**cfg.alpha) * ( (heuristic(i, 0, 0) + heuristic(i, 0, 1))/2 )**cfg.beta for i in range(len(tw_nodes)) ]
                    tw_idx = max(range(len(tw_nodes)), key=lambda i: scores[i])
                else:
                    scores = [ (tau_tw[i]**cfg.alpha) * ( (heuristic(i, 0, 0) + heuristic(i, 0, 1))/2 )**cfg.beta for i in range(len(tw_nodes)) ]
                    sum_s = sum(scores)
                    r = random.random() * sum_s
                    cum = 0
                    tw_idx = 0
                    for i, s in enumerate(scores):
                        cum += s
                        if cum >= r:
                            tw_idx = i
                            break
                # выбор free
                if random.random() < cfg.q0:
                    scores_f = [ (tau_free[i]**cfg.alpha) * ( (heuristic(tw_idx, i, 0) + heuristic(tw_idx, i, 1))/2 )**cfg.beta for i in range(len(free_nodes)) ]
                    free_idx = max(range(len(free_nodes)), key=lambda i: scores_f[i])
                else:
                    scores_f = [ (tau_free[i]**cfg.alpha) * ( (heuristic(tw_idx, i, 0) + heuristic(tw_idx, i, 1))/2 )**cfg.beta for i in range(len(free_nodes)) ]
                    sum_s = sum(scores_f)
                    r = random.random() * sum_s
                    cum = 0
                    free_idx = 0
                    for i, s in enumerate(scores_f):
                        cum += s
                        if cum >= r:
                            free_idx = i
                            break
                # выбор x
                if random.random() < cfg.q0:
                    x = 0 if (tau_x[0]**cfg.alpha)*(heuristic(tw_idx, free_idx, 0)**cfg.beta) > (tau_x[1]**cfg.alpha)*(heuristic(tw_idx, free_idx, 1)**cfg.beta) else 1
                else:
                    scores_x = [ (tau_x[m]**cfg.alpha) * (heuristic(tw_idx, free_idx, m)**cfg.beta) for m in [0,1] ]
                    sum_sx = sum(scores_x)
                    r = random.random() * sum_sx
                    x = 0 if r <= scores_x[0] else 1

                obj_val = objective(problem, tw_nodes[tw_idx], x, free_nodes[free_idx])
                if obj_val < iter_best_obj:
                    iter_best_obj = obj_val
                    iter_best_sol = (tw_nodes[tw_idx], x, free_nodes[free_idx])

            if iter_best_obj < best_obj:
                best_obj = iter_best_obj
                best_sol = iter_best_sol
            self.history.append(best_obj)

            # испарение и отложение феромона
            tau_tw = [(1-cfg.evaporation)*t for t in tau_tw]
            tau_free = [(1-cfg.evaporation)*f for f in tau_free]
            tau_x = [(1-cfg.evaporation)*x for x in tau_x]

            tw_b, x_b, free_b = iter_best_sol
            idx_tw = tw_nodes.index(tw_b)
            idx_free = free_nodes.index(free_b)
            deposit = 1.0 / (iter_best_obj + 1e-6)
            tau_tw[idx_tw] += deposit
            tau_free[idx_free] += deposit
            tau_x[x_b] += deposit

        return best_sol, best_obj