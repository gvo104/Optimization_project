"""
Главный модуль: строит визуализации целевой функции, находит глобальный минимум
полным перебором и запускает четыре метода оптимизации.
В конце выводятся расписания, соответствующие найденным решениям.
"""
from config import ScheduleProblemConfig
from experiments.runner import run_all, print_unique_schedules
from utils.visualization import *

if __name__ == "__main__":
    config = ScheduleProblemConfig()   # можно менять параметры

    # Визуализация ландшафта целевой функции
    plot_2d(config)
    plot_2d_log(config)
    plot_heatmap(config)
    plot_3d_interactive(config)

    # Полный перебор для поиска глобального минимума
    best, val = find_global_minimum(config)
    print("Глобальный минимум (перебор):", best, val)

    # Запуск оптимизационных алгоритмов
    results = run_all(config)

    # Вывод расписаний, сгруппированных по уникальным решениям
    print_unique_schedules(results, config)