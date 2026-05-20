"""
Модуль запуска всех методов оптимизации и вывода результатов.
График сходимости сохраняется в папку config.output_dir.
"""
import os
import time
import numpy as np
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

    # Сохраняем график сходимости с нормированной осью X
    os.makedirs(config.output_dir, exist_ok=True)
    plt.figure(figsize=(10, 5))
    for name, hist in histories.items():
        n = len(hist)
        x = [i / (n - 1) for i in range(n)] if n > 1 else [0.0]  # нормировка на [0,1]
        plt.plot(x, hist, label=f"{name} ({n} iter)")
    plt.yscale('log')
    plt.xlabel('Доля выполненных итераций')
    plt.ylabel('Лучшее значение objective (log)')
    plt.legend()
    plt.title('Сходимость алгоритмов (нормированная шкала)')
    plt.grid(True)
    plt.savefig(os.path.join(config.output_dir, 'convergence.png'), dpi=150)
    plt.close()

    return results


def run_statistical_comparison(config=None, n_runs=30):
    """
    Запускает каждый метод n_runs раз и собирает финальные значения objective.
    Возвращает dict: name -> list[float].
    """
    if config is None:
        config = ScheduleProblemConfig()

    method_classes = {
        "GA":  GeneticOptimizer,
        "PSO": PSOOptimizer,
        "ACO": AntColonyOptimizer,
        "SA":  SimulatedAnnealingOptimizer,
    }

    scores = {name: [] for name in method_classes}
    print(f"\nСтатистическое сравнение: {n_runs} запусков каждого метода...")
    for name, cls in method_classes.items():
        for _ in range(n_runs):
            _, obj = cls(config).optimize()
            scores[name].append(obj)
        vals = np.array(scores[name])
        print(f"  {name}: mean={vals.mean():.2f}  std={vals.std():.2f}  "
              f"best={vals.min():.2f}  worst={vals.max():.2f}")
    return scores


def print_statistical_report(scores, config):
    """
    Описательная статистика + попарный тест Манна–Уитни (с поправкой Бонферрони)
    + вывод о лучшем методе. Сохраняет boxplot в config.output_dir.
    """
    try:
        from scipy.stats import mannwhitneyu
        has_scipy = True
    except ImportError:
        has_scipy = False

    methods = list(scores.keys())
    n_runs = len(next(iter(scores.values())))
    n_pairs = len(methods) * (len(methods) - 1) // 2
    alpha_raw = 0.05
    alpha_bonf = alpha_raw / n_pairs  # поправка Бонферрони

    # --- 1. Описательная статистика ---
    print("\n" + "=" * 70)
    print(f"СТАТИСТИЧЕСКОЕ СРАВНЕНИЕ  ({n_runs} запусков на метод)")
    print("-" * 70)
    row_fmt = "{:<6} {:>10} {:>10} {:>10} {:>10} {:>10}"
    print(row_fmt.format("Метод", "Mean", "Std", "Best", "Worst", "Median"))
    print("-" * 70)

    stats = {}
    for name in methods:
        v = np.array(scores[name])
        stats[name] = dict(mean=v.mean(), std=v.std(),
                           best=v.min(), worst=v.max(), median=np.median(v))
        s = stats[name]
        print(row_fmt.format(
            name,
            f"{s['mean']:.2f}", f"{s['std']:.2f}",
            f"{s['best']:.2f}", f"{s['worst']:.2f}", f"{s['median']:.2f}",
        ))

    # --- 2. Попарные тесты Манна–Уитни ---
    pval = {m: {} for m in methods}   # pval[m1][m2] = P(m1 < m2)

    if has_scipy:
        print(f"\nПопарный тест Манна–Уитни  "
              f"(α={alpha_raw}, поправка Бонферрони α'={alpha_bonf:.4f})")
        print("p-value: строка значимо лучше столбца?  * = p < α'")
        header_fmt = "{:<6}" + "{:>10}" * len(methods)
        print(header_fmt.format("", *methods))
        for m1 in methods:
            row = f"{m1:<6}"
            for m2 in methods:
                if m1 == m2:
                    pval[m1][m2] = None
                    row += f"{'—':>10}"
                else:
                    _, p = mannwhitneyu(scores[m1], scores[m2], alternative='less')
                    pval[m1][m2] = p
                    marker = "*" if p < alpha_bonf else " "
                    row += f"{p:>9.4f}{marker}"
            print(row)
        print(f"  * p < {alpha_bonf:.4f}")
    else:
        print("\n[!] scipy не найден — попарные тесты пропущены.")
        print("    Установите: conda install scipy  или  pip install scipy")

    # --- 3. Вывод о победителе ---
    sorted_methods = sorted(methods, key=lambda m: (stats[m]["median"], stats[m]["mean"], stats[m]["std"]))
    best = sorted_methods[0]

    print("\n" + "=" * 70)
    print("ВЫВОД")
    print("-" * 70)
    print(f"Наилучшая медиана: {best}  ({stats[best]['median']:.2f})")

    if has_scipy:
        wins_against = [
            m2 for m2 in methods
            if m2 != best and pval[best][m2] is not None and pval[best][m2] < alpha_bonf
        ]
        ties_with = [
            m2 for m2 in methods
            if m2 != best and (pval[best][m2] is None or pval[best][m2] >= alpha_bonf)
        ]

        if len(wins_against) == len(methods) - 1:
            print(f"=> ПОБЕДИТЕЛЬ: {best} статистически значимо лучше всех остальных.")
        elif wins_against:
            print(f"=> {best} значимо лучше: {', '.join(wins_against)}")
            print(f"   Статистически неотличим от: {', '.join(ties_with)}")
        else:
            # Нет явного победителя — проверяем, есть ли группа эквивалентных лидеров
            top_group = [best] + ties_with
            print(f"=> Явного победителя нет. Методы статистически эквивалентны: "
                  f"{', '.join(top_group)}")
            print(f"   Среди них лучшая медиана у {best}.")
    else:
        print(f"=> По медиане лидирует {best} (статистические тесты недоступны).")

    # --- 4. Boxplot ---
    os.makedirs(config.output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    data = [scores[m] for m in methods]
    bp = ax.boxplot(data, labels=methods, patch_artist=True, notch=False)
    colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_ylabel('Objective (лучшее за запуск)')
    ax.set_title(f'Распределение результатов ({n_runs} запусков)')
    ax.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    path = os.path.join(config.output_dir, 'statistical_comparison.png')
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\nBoxplot сохранён: {path}")
    print("=" * 70)


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