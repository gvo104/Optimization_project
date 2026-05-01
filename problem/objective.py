import math
from .schedule_builder import build_schedule
from .constraints import is_valid


def objective(config, t_w: int, x: int):
    schedule = build_schedule(config, t_w, x)

    if not is_valid(config, schedule):
        return 1e12  # большой штраф

    T_sleep = schedule["T_sleep"]

    # --- 1. фаза сна ---
    k = round(T_sleep / config.Cycle)
    T_ideal = k * config.Cycle
    P_phase = (T_sleep - T_ideal) ** 2

    # --- 2. недосып ---
    if T_sleep < config.T_best_sleep:
        P_debt = (config.T_best_sleep - T_sleep) ** 2
    else:
        P_debt = 0

    # --- 3. работа ---
    t_work_start = schedule["t_work_start"]
    P_work = (t_work_start - config.Ideal_start) ** 2

    # --- 4. учеба ---
    t_study_start = schedule["t_study_start"]

    if t_study_start <= config.Study_ineffective_after:
        eff = 1
    else:
        eff = config.Study_eff_drop

    P_study = config.W_study * (1 - eff)

    # --- итог ---
    total = (
        config.w_phase * P_phase
        + config.w_debt * P_debt
        + config.w_work * P_work
        + config.w_study * P_study
    )

    return total