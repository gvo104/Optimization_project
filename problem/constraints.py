def is_valid(config, schedule):
    if not (config.Work_start_early <= schedule["t_work_start"] <= config.Work_start_late):
        return False

    if schedule["T_sleep"] < config.T_min_sleep:
        return False

    return True