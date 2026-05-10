"""
Модуль запуска всех методов оптимизации и вывода результатов.
График сходимости сохраняется в папку config.output_dir.
"""
import os
import time
import matplotlib
matplotlib.use('Agg')          # неинтерактивный бэкенд (сохранение файлов)
import matplotlib.pyplot as plt
from collections import defaultdict

from config import ScheduleProblemConfig
from methods.genetic import GeneticOptimizer
from methods.pso import PSOOptimizer
from methods.aco import AntColonyOptimizer
from methods.annealing import SimulatedAnnealingOptimizer
from utils.display_schedule import format_schedule


def run_all(config=None):
    """Запускает GA, PSO, ACO, SA и возвращает словарь результатов с историей."""
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
        solution, obj = opt.optimize()          # (t_w, x, free_time), objective
        elapsed = time.time() - start
        results[name] = {
            "t_w": solution[0],
            "x": solution[1],
            "free_time": solution[2],
            "objective": obj,
            "time_sec": elapsed
        }
        histories[name] = opt.history

    # Сохраняем график сходимости в output_dir
    os.makedirs(config.output_dir, exist_ok=True)
    plt.figure(figsize=(10, 5))
    for name, hist in histories.items():
        plt.plot(range(1, len(hist) + 1), hist, label=name)
    plt.yscale('log')
    plt.xlabel('Iteration')
    plt.ylabel('Best objective (log)')
    plt.legend()
    plt.title('Convergence curves')
    plt.grid(True)
    plt.savefig(os.path.join(config.output_dir, 'convergence.png'), dpi=150)
    plt.close()

    return results


def print_unique_schedules(results, config, global_min=None):
    """
    Группирует результаты по уникальным (t_w, x, free_time) и выводит:
    - сводную таблицу (методы, время, штраф);
    - текстовые расписания для каждого уникального варианта.
    Если передан global_min = (t_w, x, free_time, obj), добавляет его в таблицу.
    """
    groups = defaultdict(list)
    for method_name, res in results.items():
        key = (res["t_w"], res["x"], res["free_time"])
        groups[key].append(method_name)

    # --- Сводная таблица ---
    print("\n" + "=" * 60)
    print("Сводная таблица результатов")
    print(f"{'Метод/Глоб. мин':<20} {'t_w':<6} {'x':<4} {'Free':<6} {'Objective':<12} {'Time, s':<10}")
    for (tw, x, ft), methods in groups.items():
        method_list = ", ".join(sorted(methods))
        obj = results[methods[0]]["objective"]   # все в группе дают одно значение
        time_str = ", ".join([f"{results[m]['time_sec']:.3f}" for m in methods])
        print(f"{method_list:<20} {tw:<6} {x:<4} {ft:<6} {obj:<12.2f} {time_str:<10}")

    if global_min:
        tw_g, x_g, ft_g, obj_g = global_min
        print(f"{'ГЛОБАЛЬНЫЙ МИНИМУМ':<20} {tw_g:<6} {x_g:<4} {ft_g:<6} {obj_g:<12.2f} {'—':<10}")

    # --- Расписания ---
    print("\n" + "=" * 60)
    print("Итоговые варианты расписаний:\n")
    for (tw, x, ft), methods in groups.items():
        method_list = ", ".join(sorted(methods))
        print(f"Методы: {method_list}")
        print(format_schedule((tw, x, ft), config))
        print("-" * 60)