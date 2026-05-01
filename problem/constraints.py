def is_valid(config, schedule):
    """Проверка ограничений, включая свободное время."""
    if not (config.Work_start_early <= schedule["t_work_start"] <= config.Work_start_late):
        return False
    if schedule["T_sleep"] < config.T_min_sleep:
        return False
    # Свободное время не может превышать заданный максимум
    if schedule["free_time"] > config.max_free_time:
        return False
    # t_sleep должно быть в пределах суток (до 1440)
    if schedule["t_sleep"] >= 1440:
        return False
    # Минимальное свободное время – 0
    if schedule["free_time"] < 0:
        return False
    return True