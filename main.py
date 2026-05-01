"""
Главный скрипт для решения задачи «Идеальный рабочий день».
Строит визуализации целевой функции, находит глобальный минимум перебором,
запускает четыре алгоритма оптимизации и выводит сводную таблицу и расписания.
"""

from config import ScheduleProblemConfig
from experiments.runner import run_all, print_unique_schedules
from utils.visualization import (
    plot_heatmap_free,
    plot_optimal_free_slice,
    plot_3d_surface,
    plot_3d_both_surfaces,
    plot_2d,
    plot_2d_log,
    plot_heatmap,
    plot_with_minimum,
    find_global_minimum
)


if __name__ == "__main__":
    # ------------------------------------------------------------------
    # 1. Конфигурация задачи (можно подкрутить параметры здесь или в config.py)
    # ------------------------------------------------------------------
    config = ScheduleProblemConfig()

    # ------------------------------------------------------------------
    # 2. Визуализация ландшафта целевой функции
    #    Закомментируйте ненужные графики, чтобы не открывать всё сразу.
    # ------------------------------------------------------------------
    # Тепловые карты на плоскости (t_w, free_time) для каждого режима
    plot_heatmap_free(config, x=0, log_scale=False)
    plot_heatmap_free(config, x=1, log_scale=False)

    # Срез: для каждого t_w оптимальное free_time и значение objective
    plot_optimal_free_slice(config)

    # Интерактивные 3D-поверхности (открываются в браузере)
    # Если не нужны — закомментируйте или поставьте save_html=True
    plot_3d_surface(config, x=0, save_html=False)
    plot_3d_surface(config, x=1, save_html=False)
    plot_3d_both_surfaces(config, save_html=False)

    # Классические двумерные срезы при free_time=0 (для справки)
    plot_2d(config)
    plot_2d_log(config)
    plot_heatmap(config)
    plot_with_minimum(config, free_time=0)

    # ------------------------------------------------------------------
    # 3. Поиск истинного глобального минимума полным перебором
    # ------------------------------------------------------------------
    # Высокая точность: t_step=5 мин, free_step=1 мин
    best, val = find_global_minimum(config, t_step=5, free_step=1)
    global_min_info = (best[0], best[1], best[2], val)

    # ------------------------------------------------------------------
    # 4. Запуск четырёх алгоритмов оптимизации
    # ------------------------------------------------------------------
    results = run_all(config)

    # ------------------------------------------------------------------
    # 5. Вывод сводной таблицы и расписаний
    #    В таблицу автоматически добавляется строка глобального минимума.
    # ------------------------------------------------------------------
    print_unique_schedules(results, config, global_min=global_min_info)