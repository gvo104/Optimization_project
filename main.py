#!/usr/bin/env python3
"""
Главный скрипт. Выводит входные параметры, строит визуализации,
находит глобальный минимум перебором, запускает алгоритмы оптимизации
и печатает сводную таблицу с расписаниями.
"""

from config import ScheduleProblemConfig
from experiments.runner import run_all, print_unique_schedules
from utils.visualization import (
    plot_heatmap_free,
    plot_optimal_free_slice,
    plot_3d_surface,
    plot_3d_both_surfaces,
    # plot_2d,
    # plot_2d_log,
    # plot_heatmap,
    # plot_with_minimum,
    find_global_minimum
)


def print_config(config: ScheduleProblemConfig):
    """Выводит в консоль основные параметры задачи и веса."""
    print("=" * 60)
    print("ВХОДНЫЕ ПАРАМЕТРЫ ЗАДАЧИ")
    print("-" * 60)
    print("Длительности блоков (мин):")
    print(f"  Утренние сборы (M):                  {config.M}")
    print(f"  Дорога на работу (C):                 {config.C}")
    print(f"  Обед (L):                             {config.L}")
    print(f"  Чистое рабочее время (W_work):        {config.W_work}")
    print(f"  Длительность учёбы (W_study):          {config.W_study}")
    print(f"  Дорога домой (D_back):                {config.D_back}")
    print(f"  Вечерний отдых (E):                   {config.E}")

    print("\nПараметры сна:")
    print(f"  Минимальная длительность сна (T_min): {config.T_min_sleep} мин "
          f"({config.T_min_sleep // 60} ч {config.T_min_sleep % 60} мин)")
    print(f"  Желаемая длительность сна (T_best):   {config.T_best_sleep} мин "
          f"({config.T_best_sleep // 60} ч {config.T_best_sleep % 60} мин)")
    print(f"  Длительность цикла сна (Cycle):       {config.Cycle} мин")

    print("\nОграничения на работу:")
    print(f"  Самое раннее начало: {config.Work_start_early} мин "
          f"({config.Work_start_early // 60:02d}:{config.Work_start_early % 60:02d})")
    print(f"  Самое позднее начало: {config.Work_start_late} мин "
          f"({config.Work_start_late // 60:02d}:{config.Work_start_late % 60:02d})")
    print(f"  Идеальное начало:     {config.Ideal_start} мин "
          f"({config.Ideal_start // 60:02d}:{config.Ideal_start % 60:02d})")

    print("\nУчёба:")
    print(f"  Порог неэффективности: {config.Study_ineffective_after} мин "
          f"({config.Study_ineffective_after // 60:02d}:{config.Study_ineffective_after % 60:02d})")
    print(f"  Коэффициент падения эффективности: {config.Study_eff_drop}")

    print("\nСвободное время:")
    print(f"  Максимальное свободное время: {config.max_free_time} мин")

    print("\nВеса и вознаграждения:")
    print(f"  Фаза сна (w_phase):                 {config.w_phase}")
    print(f"  Недосып (w_debt):                   {config.w_debt}")
    print(f"  Вознаграждение за лишний сон:       {config.reward_extra_sleep}")
    print(f"  Раннее начало работы (w_work_early):{config.w_work_early}")
    print(f"  Позднее начало работы (w_work_late):{config.w_work_late}")
    print(f"  Поздняя учёба (w_study):            {config.w_study}")
    print(f"  Вознаграждение за свободное время:  {config.reward_free_time}")

    print("\nПараметры алгоритмов (кратко):")
    print(f"  GA:   популяция={config.ga.pop_size}, поколений={config.ga.generations}")
    print(f"  PSO:  частиц={config.pso.num_particles}, итераций={config.pso.iterations}")
    print(f"  ACO:  муравьёв={config.aco.num_ants}, итераций={config.aco.iterations}")
    print(f"  SA:   начальная темп.={config.annealing.initial_temp}, "
          f"охлаждение={config.annealing.cooling_rate}")

    print(f"\nВыходная папка: {config.output_dir}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # 1. Конфигурация задачи
    config = ScheduleProblemConfig()
    print_config(config)                     # <-- вывод всех вводных

    # 2. Визуализации (сохраняются в output_dir)
    plot_heatmap_free(config, x=0, log_scale=False)
    plot_heatmap_free(config, x=1, log_scale=False)

    # Срез: для каждого t_w оптимальное free_time и значение objective
    plot_optimal_free_slice(config)
    plot_3d_surface(config, x=0)
    plot_3d_surface(config, x=1)
    plot_3d_both_surfaces(config)

    # 3. Глобальный минимум перебором
    best, val = find_global_minimum(config, t_step=5, free_step=1)
    global_min_info = (best[0], best[1], best[2], val)

    # 4. Запуск алгоритмов
    results = run_all(config)

    # 5. Сводная таблица и расписания
    print_unique_schedules(results, config, global_min=global_min_info)