import time
import matplotlib.pyplot as plt
from config import ScheduleProblemConfig
from methods.genetic import GeneticOptimizer
from methods.pso import PSOOptimizer
from methods.aco import AntColonyOptimizer
from methods.annealing import SimulatedAnnealingOptimizer
from utils.display_schedule import format_schedule


def run_all(config=None):
    """Запускает все четыре метода оптимизации и возвращает словарь результатов."""
    if config is None:
        config = ScheduleProblemConfig()

    methods = {
        "GA": GeneticOptimizer(config),
        "PSO": PSOOptimizer(config),
        "ACO": AntColonyOptimizer(config),
        "SA": SimulatedAnnealingOptimizer(config)
    }

    results = {}
    histories = {}

    for name, opt in methods.items():
        start = time.time()
        (tw, x), obj = opt.optimize()
        elapsed = time.time() - start
        results[name] = {
            "t_w": tw,
            "x": x,
            "objective": obj,
            "time_sec": elapsed
        }
        histories[name] = opt.history
        print(f"{name}: t_w={tw}, x={x}, obj={obj:.2f}, time={elapsed:.3f}s")

    # Таблица сравнения
    print("\n--- Comparison ---")
    print(f"{'Method':<6} {'t_w':<6} {'x':<4} {'Objective':<12} {'Time, s':<10}")
    for name, r in results.items():
        print(f"{name:<6} {r['t_w']:<6} {r['x']:<4} {r['objective']:<12.2f} {r['time_sec']:<10.3f}")

    # График сходимости
    plt.figure(figsize=(10, 5))
    for name, hist in histories.items():
        plt.plot(range(1, len(hist)+1), hist, label=name)
    plt.yscale('log')
    plt.xlabel('Iteration')
    plt.ylabel('Best objective (log)')
    plt.legend()
    plt.title('Convergence curves')
    plt.grid(True)
    plt.show()

    return results


def print_unique_schedules(results, config):
    """
    Группирует решения по уникальным (t_w, x) и выводит расписание для каждого.
    Перед расписанием перечисляются методы, которые к нему пришли.
    """
    from collections import defaultdict

    # Группируем методы по решению (t_w, x)
    groups = defaultdict(list)
    for method_name, res in results.items():
        key = (res["t_w"], res["x"])
        groups[key].append(method_name)

    print("\n" + "="*60)
    print("Итоговые варианты расписаний (найдены алгоритмами):\n")
    for (tw, x), methods in groups.items():
        method_list = ", ".join(sorted(methods))
        print(f"Методы: {method_list}")
        print(format_schedule((tw, x), config))
        print("-"*60)