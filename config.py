from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
#  Конфигурации алгоритмов оптимизации
# ---------------------------------------------------------------------------

@dataclass
class GAConfig:
    """Параметры генетического алгоритма"""
    pop_size: int = 50
    generations: int = 100
    mutation_rate: float = 0.15
    crossover_rate: float = 0.8
    elite_size: int = 2
    tournament_size: int = 3


@dataclass
class PSOConfig:
    """Параметры метода роя частиц"""
    num_particles: int = 30
    iterations: int = 100
    w: float = 0.7                # инерция
    c1: float = 1.5               # когнитивный коэффициент
    c2: float = 1.5               # социальный коэффициент
    v_max_t: float = 60           # макс. скорость для t_w
    v_max_free: float = 30        # макс. скорость для free_time


@dataclass
class ACOConfig:
    """Параметры муравьиного алгоритма"""
    num_ants: int = 30
    iterations: int = 50
    evaporation: float = 0.1
    alpha: float = 1.0
    beta: float = 2.0
    q0: float = 0.5
    step_minutes: int = 5         # шаг дискретизации t_w и free_time
    max_free_time: int = 120      # максимальное свободное время (мин)


@dataclass
class SimAnnealingConfig:
    """Параметры имитации отжига"""
    initial_temp: float = 1000.0
    cooling_rate: float = 0.995
    iterations_per_temp: int = 10
    min_temp: float = 0.1
    step_std_t: float = 30        # std для t_w
    step_std_free: float = 20     # std для free_time


# ---------------------------------------------------------------------------
#  Конфигурация задачи «Идеальный рабочий день» (расширенная)
# ---------------------------------------------------------------------------

@dataclass
class ScheduleProblemConfig:
    """
    Параметры модели расписания и веса целевой функции.
    Вознаграждения задаются отрицательными весами (уменьшают штраф).
    """

    # ---- Длительности блоков (минуты) ----
    M: int = 60           # утренние сборы
    C: int = 20           # дорога на работу
    L: int = 60           # обед
    W_work: int = 480     # чистая работа
    W_study: int = 120    # учёба
    D_back: int = 30      # дорога домой
    E: int = 45           # обязательный вечерний отдых

    # ---- Сон ----
    T_min_sleep: int = 360          # абсолютный минимум сна (иначе огромный штраф)
    T_best_sleep: int = 540         # желаемая длительность сна
    Cycle: int = 90                 # длительность цикла сна

    # ---- Работа ----
    Work_start_early: int = 540     # самое раннее разрешённое начало работы
    Work_start_late: int = 660      # самое позднее разрешённое начало работы
    Ideal_start: int = 570          # идеальное начало работы (09:30)

    # ---- Учёба ----
    Study_ineffective_after: int = 1145   # после этого времени учёба менее эффективна
    Study_eff_drop: float = 0.5           # коэффициент падения эффективности

    # ---- Веса и вознаграждения ----
    # Штраф за фазу сна (положительный вес)
    w_phase: float = 10

    # Штраф за недосып: если T_sleep < T_best_sleep, начисляется квадрат нехватки,
    # иначе даётся вознаграждение за лишний сон (отрицательный вклад).
    w_debt: float = 5             # коэффициент при недостатке сна
    reward_extra_sleep: float = 2 # вознаграждение за каждую минуту сверх нормы (отрицательный штраф)

    # Штраф за отклонение начала работы от идеала.
    # Отклонение в любую сторону наказывается, но позже идеала – сильнее.
    w_work_early: float = 1       # штраф за минуту раньше идеала
    w_work_late: float = 3        # штраф за минуту позже идеала

    # Штраф за позднюю учёбу (положительный вес)
    w_study: float = 3

    # Свободное время: можно добавить после вечернего отдыха до сна.
    # Максимальное свободное время (мин), чтобы не допустить бесконечного уменьшения сна.
    max_free_time: int = 120
    # Вознаграждение за каждую минуту свободного времени (отрицательный вклад)
    reward_free_time: float = 1

    # ---- Вложенные конфигурации алгоритмов ----
    ga: GAConfig = field(default_factory=GAConfig)
    pso: PSOConfig = field(default_factory=PSOConfig)
    aco: ACOConfig = field(default_factory=ACOConfig)
    annealing: SimAnnealingConfig = field(default_factory=SimAnnealingConfig)
    
    output_dir: str = "output"   # папка для сохранения графиков