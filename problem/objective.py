from .schedule_builder import build_schedule
from .constraints import is_valid


def objective(config, t_w: int, x: int, free_time: int = 0):
    """
    Возвращает значение целевой функции (штраф + вознаграждения).
    Чем меньше, тем лучше. Отрицательные значения означают преобладание вознаграждений.
    """
    schedule = build_schedule(config, t_w, x, free_time)

    if not is_valid(config, schedule):
        return 1e12  # огромный штраф при нарушении жёстких ограничений

    T_sleep = schedule["T_sleep"]
    t_work_start = schedule["t_work_start"]
    t_study_start = schedule["t_study_start"]
    free = schedule["free_time"]

    # --- 1. Фаза сна (штраф) ---
    k = round(T_sleep / config.Cycle)
    T_ideal = k * config.Cycle
    P_phase = (T_sleep - T_ideal) ** 2

    # --- 2. Недосып / пересып ---
    if T_sleep < config.T_best_sleep:
        P_debt = config.w_debt * ((config.T_best_sleep - T_sleep) ** 2)
    else:
        # вознаграждение за лишний сон (отрицательное значение)
        P_debt = -config.reward_extra_sleep * (T_sleep - config.T_best_sleep)

    # --- 3. Отклонение начала работы (асимметричное) ---
    delta = t_work_start - config.Ideal_start
    if delta >= 0:
        P_work = config.w_work_late * (delta ** 2)
    else:
        P_work = config.w_work_early * ((-delta) ** 2)

    # --- 4. Эффективность учёбы (вечерняя учёба) ---
    if t_study_start is not None and t_study_start > config.Study_ineffective_after:
        P_study = config.w_study * config.W_study * (1 - config.Study_eff_drop)
    else:
        P_study = 0.0

    # --- 5. Свободное время (вознаграждение) ---
    P_free = -config.reward_free_time * free

    # Итого
    total = (
        config.w_phase * P_phase
        + P_debt
        + P_work
        + P_study
        + P_free
    )
    return total