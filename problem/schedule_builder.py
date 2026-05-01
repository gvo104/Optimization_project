def build_schedule(config, t_w: int, x: int, free_time: int = 0):
    """
    Строит расписание с учётом свободного времени перед сном.
    free_time – минуты между окончанием вечернего отдыха и началом сна.
    """
    M, C = config.M, config.C
    W_study = config.W_study

    # Утренние процедуры
    if x == 1:  # учёба утром
        t_leave = t_w + M
        t_study_start = t_leave
        t_study_end = t_study_start + W_study
        t_work_start = t_study_end + C
    else:        # учёба вечером
        t_work_start = t_w + M + C
        t_study_start = None
        t_study_end = None

    t_work_end = t_work_start + config.W_work + config.L
    t_home = t_work_end + config.D_back

    if x == 0:  # вечерняя учёба
        t_study_start = t_home
        t_study_end = t_study_start + W_study
        t_relax = t_study_end
    else:
        t_relax = t_home

    # Свободное время и сон
    t_sleep = t_relax + config.E + free_time
    # Длительность сна: от засыпания до пробуждения следующего дня
    T_sleep = (1440 - t_sleep) + t_w

    return {
        "t_w": t_w,
        "t_sleep": t_sleep,
        "T_sleep": T_sleep,
        "t_work_start": t_work_start,
        "t_work_end": t_work_end,
        "t_study_start": t_study_start,
        "t_study_end": t_study_end,
        "t_relax": t_relax,
        "free_time": free_time
    }