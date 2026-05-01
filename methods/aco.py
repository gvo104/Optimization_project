import random
import math
from .base import BaseOptimizer

class AntColonyOptimizer(BaseOptimizer):
    def optimize(self):
        cfg = self.config.aco
        problem = self.config
        from problem.objective import objective

        step = cfg.step_minutes
        tw_nodes = list(range(0, 1440, step))   # discrete t_w values
        x_nodes = [0, 1]                        # study placement
        num_tw = len(tw_nodes)

        # pheromone matrices: τ_tw[i], τ_x[mode]
        tau_tw = [1.0] * num_tw
        tau_x = [1.0, 1.0]

        best_sol = None
        best_obj = float('inf')
        self.history = []

        # heuristic: inverse of objective (with small epsilon)
        def heuristic(tw_idx, x):
            val = objective(problem, tw_nodes[tw_idx], x)
            # handle huge penalty
            return 1.0 / (val + 1e-6)

        for it in range(cfg.iterations):
            iter_best_obj = float('inf')
            iter_best_sol = None
            # each ant constructs a solution
            for _ in range(cfg.num_ants):
                # choose t_w probabilistically
                if random.random() < cfg.q0:
                    # exploitation
                    probs_tw = [ (tau_tw[i]**cfg.alpha) * (heuristic(i,0)**cfg.beta) for i in range(num_tw) ]
                    # sum over x? better use average heuristic or choose x after
                    # Simplified: choose tw based on average heuristic
                    avg_heur = [ (heuristic(i,0)+heuristic(i,1))/2 for i in range(num_tw) ]
                    scores = [ (tau_tw[i]**cfg.alpha) * (avg_heur[i]**cfg.beta) for i in range(num_tw) ]
                    tw_idx = max(range(num_tw), key=lambda i: scores[i])
                else:
                    # probabilistic
                    scores = []
                    for i in range(num_tw):
                        avg_heur = (heuristic(i,0)+heuristic(i,1))/2
                        scores.append((tau_tw[i]**cfg.alpha) * (avg_heur**cfg.beta))
                    sum_scores = sum(scores)
                    r = random.random() * sum_scores
                    cum = 0
                    tw_idx = 0
                    for i, s in enumerate(scores):
                        cum += s
                        if cum >= r:
                            tw_idx = i
                            break
                # choose x
                if random.random() < cfg.q0:
                    x = 0 if (tau_x[0]**cfg.alpha)*(heuristic(tw_idx,0)**cfg.beta) > (tau_x[1]**cfg.alpha)*(heuristic(tw_idx,1)**cfg.beta) else 1
                else:
                    scores_x = [ (tau_x[m]**cfg.alpha) * (heuristic(tw_idx,m)**cfg.beta) for m in [0,1] ]
                    sum_sx = sum(scores_x)
                    r = random.random() * sum_sx
                    if r <= scores_x[0]:
                        x = 0
                    else:
                        x = 1

                obj_val = objective(problem, tw_nodes[tw_idx], x)
                if obj_val < iter_best_obj:
                    iter_best_obj = obj_val
                    iter_best_sol = (tw_nodes[tw_idx], x)
                # local pheromone update (optional) – we skip for simplicity

            # update global pheromone based on iteration best
            if iter_best_obj < best_obj:
                best_obj = iter_best_obj
                best_sol = iter_best_sol
            self.history.append(best_obj)

            # evaporation
            tau_tw = [(1-cfg.evaporation)*t for t in tau_tw]
            tau_x = [(1-cfg.evaporation)*t for t in tau_x]
            # deposit
            tw_best, x_best = iter_best_sol
            idx_tw = tw_nodes.index(tw_best)
            deposit = 1.0 / (iter_best_obj + 1e-6)
            tau_tw[idx_tw] += deposit
            tau_x[x_best] += deposit

        return best_sol, best_obj