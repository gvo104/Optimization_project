"""
Функции для преобразования времени из минут в строки и форматирования расписания.
"""

def minutes_to_time(minutes: int) -> str:
    """Переводит минуты от полуночи (0..1439) в строку ЧЧ:ММ."""
    if minutes is None:
        return "—"
    hours = (minutes // 60) % 24
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def format_schedule(solution, config):
    """
    Принимает пару (t_w, x) и конфиг, возвращает подробное описание расписания.
    """
    from problem.schedule_builder import build_schedule

    t_w, x = solution
    s = build_schedule(config, t_w, x)

    wake_time   = minutes_to_time(s["t_w"])
    leave_time  = minutes_to_time(s["t_w"] + config.M)
    study_start = minutes_to_time(s["t_study_start"])
    study_end   = minutes_to_time(s["t_study_end"])
    work_start  = minutes_to_time(s["t_work_start"])
    work_end    = minutes_to_time(s["t_work_end"])
    home_time   = minutes_to_time(s["t_work_end"] + config.D_back)
    relax_start = minutes_to_time(s["t_relax"])
    sleep_time  = minutes_to_time(s["t_sleep"])

    lines = []
    lines.append(f"Расписание при пробуждении в {wake_time} и порядке учёбы "
                 f"{'утром' if x == 1 else 'вечером'}:")
    lines.append(f"  Утренние сборы:          {wake_time} – {leave_time}")
    if x == 1:
        lines.append(f"  Учёба:                   {study_start} – {study_end}")
        lines.append(f"  Дорога на работу:        {study_end} – {work_start}")
    else:
        lines.append(f"  Дорога на работу:        {leave_time} – {work_start}")

    lines.append(f"  Работа:                  {work_start} – {minutes_to_time(s['t_work_end'] - config.L)}")
    lines.append(f"  Обед:                    {minutes_to_time(s['t_work_end'] - config.L)} – {work_end}")
    lines.append(f"  Дорога домой:            {work_end} – {home_time}")

    if x == 0:
        lines.append(f"  Учёба (вечер):           {study_start} – {study_end}")
        lines.append(f"  Отдых:                   {study_end} – {minutes_to_time(s['t_relax'] + config.E)}")
    else:
        lines.append(f"  Отдых:                   {relax_start} – {minutes_to_time(s['t_relax'] + config.E)}")

    lines.append(f"  Сон:                     {sleep_time} – {wake_time} (длительность: {s['T_sleep']} мин)")

    return "\n".join(lines)