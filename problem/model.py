from dataclasses import dataclass


@dataclass
class Solution:
    t_w: int  # время пробуждения
    x: int    # 0 или 1


@dataclass
class Schedule:
    t_w: int
    t_sleep: int
    T_sleep: int

    t_work_start: int
    t_work_end: int

    t_study_start: int
    t_study_end: int

    t_relax: int