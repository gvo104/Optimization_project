def minutes_to_time(minutes: int) -> str:
    if minutes is None:
        return "—"
    hours = (minutes // 60) % 24
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def format_schedule(solution, config):
    t_w, x, free_time = solution
    from problem.schedule_builder import build_schedule
    s = build_schedule(config, t_w, x, free_time)

    wake   = minutes_to_time(s["t_w"])
    leave  = minutes_to_time(s["t_w"] + config.M)
    study_start = minutes_to_time(s["t_study_start"])
    study_end   = minutes_to_time(s["t_study_end"])
    work_start  = minutes_to_time(s["t_work_start"])
    work_end    = minutes_to_time(s["t_work_end"])
    home   = minutes_to_time(s["t_work_end"] + config.D_back)
    relax  = minutes_to_time(s["t_relax"])
    sleep  = minutes_to_time(s["t_sleep"])
    free   = s["free_time"]

    lines = []
    lines.append(f"Пробуждение в {wake}, учёба {'утром' if x==1 else 'вечером'}, свободное время {free} мин")
    lines.append(f"  Сборы:            {wake} – {leave}")
    if x == 1:
        lines.append(f"  Учёба:            {study_start} – {study_end}")
        lines.append(f"  Дорога на работу: {study_end} – {work_start}")
    else:
        lines.append(f"  Дорога на работу: {leave} – {work_start}")
    lines.append(f"  Работа:           {work_start} – {minutes_to_time(s['t_work_end'] - config.L)}")
    lines.append(f"  Обед:             {minutes_to_time(s['t_work_end'] - config.L)} – {work_end}")
    lines.append(f"  Дорога домой:     {work_end} – {home}")
    if x == 0:
        lines.append(f"  Учёба (вечер):    {study_start} – {study_end}")
        lines.append(f"  Отдых:            {study_end} – {minutes_to_time(s['t_relax'] + config.E)}")
    else:
        lines.append(f"  Отдых:            {relax} – {minutes_to_time(s['t_relax'] + config.E)}")
    lines.append(f"  Свободное время:  {minutes_to_time(s['t_relax'] + config.E)} – {sleep} ({free} мин)")
    lines.append(f"  Сон:              {sleep} – {wake} ({s['T_sleep']} мин)")
    return "\n".join(lines)