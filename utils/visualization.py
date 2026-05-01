import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from problem.objective import objective


# ---------------------------------------------------------------------------
#  Вспомогательные функции
# ---------------------------------------------------------------------------

def _min_to_time(t):
    """Преобразует минуты в строку ЧЧ:ММ для оси."""
    h = (t // 60) % 24
    m = t % 60
    return f"{h:02d}:{m:02d}"


def _find_best_free_for_tw_x(config, t_w, x, free_step=2):
    """Для заданных t_w и x находит лучшее значение free_time перебором."""
    best_obj = float('inf')
    best_free = 0
    for ft in range(0, config.max_free_time + 1, free_step):
        obj = objective(config, t_w, x, ft)
        if obj < best_obj:
            best_obj = obj
            best_free = ft
    return best_free, best_obj


# ---------------------------------------------------------------------------
#  Глобальный минимум с учётом free_time
# ---------------------------------------------------------------------------

def find_global_minimum(config, t_step=5, free_step=2):
    """Полный перебор по t_w, x, free_time. Возвращает (t_w, x, free_time), значение."""
    best_val = float('inf')
    best = None
    for t_w in range(0, 1440, t_step):
        for x in [0, 1]:
            best_free, val = _find_best_free_for_tw_x(config, t_w, x, free_step)
            if val < best_val:
                best_val = val
                best = (t_w, x, best_free)
    return best, best_val


# ---------------------------------------------------------------------------
#  Тепловая карта на плоскости (t_w, free_time) для выбранного x
# ---------------------------------------------------------------------------

def plot_heatmap_free(config, x=0, t_step=5, free_step=2, log_scale=False):
    """
    Тепловая карта: ось X – время пробуждения, ось Y – свободное время,
    цвет – значение целевой функции. Ограничения отсекаются.
    """
    t_w_vals = np.arange(0, 1440, t_step)
    free_vals = np.arange(0, config.max_free_time + 1, free_step)

    Z = np.zeros((len(free_vals), len(t_w_vals)))
    for i, ft in enumerate(free_vals):
        for j, tw in enumerate(t_w_vals):
            val = objective(config, int(tw), x, int(ft))
            if val >= 1e11:          # недопустимое решение – замена на NaN для белого
                val = np.nan
            Z[i, j] = val

    if log_scale:
        Z = np.log10(np.maximum(Z, 1e-6))

    plt.figure(figsize=(10, 6))
    plt.imshow(Z, aspect='auto', origin='lower',
               extent=[t_w_vals[0], t_w_vals[-1], free_vals[0], free_vals[-1]])
    plt.colorbar(label='log10(objective)' if log_scale else 'objective')
    plt.xlabel('Время пробуждения (мин от полуночи)')
    plt.ylabel('Свободное время (мин)')
    mode = 'утром' if x == 1 else 'вечером'
    plt.title(f'Ландшафт целевой функции (учёба {mode})')

    # отметим лучшую точку
    best_ft, best_tw = np.unravel_index(np.nanargmin(Z), Z.shape)
    plt.scatter(t_w_vals[best_tw], free_vals[best_ft], c='red', marker='o', label='Глобальный минимум (срез)')
    plt.legend()
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
#  Тепловая карта с оптимальным free_time для каждого t_w (по одному графику на x)
# ---------------------------------------------------------------------------

def plot_optimal_free_slice(config, t_step=5, free_step=2):
    """
    Для каждого t_w и x находим лучшее free_time и строим график objective(t_w)
    с цветовой индикацией этого выбранного free_time.
    """
    tw_vals = np.arange(0, 1440, t_step)
    modes = [0, 1]
    _, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, x in zip(axes, modes):
        obj_arr = []
        best_free_arr = []
        for tw in tw_vals:
            bf, bo = _find_best_free_for_tw_x(config, int(tw), x, free_step)
            obj_arr.append(bo)
            best_free_arr.append(bf)
        sc = ax.scatter(tw_vals, obj_arr, c=best_free_arr, cmap='viridis', s=10)
        ax.set_xlabel('Время пробуждения (мин)')
        ax.set_ylabel('Целевая функция')
        ax.set_title(f"x = {x} ({'утро' if x==1 else 'вечер'})")
        plt.colorbar(sc, ax=ax, label='Лучшее free_time (мин)')
    plt.suptitle('Минимальное значение objective при оптимальном free_time для каждого t_w')
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
#  3D-поверхность (plotly) для x=0 и x=1 с осями t_w и free_time
# ---------------------------------------------------------------------------

def plot_3d_surface(config, x=0, t_step=10, free_step=5, save_html=False):
    """Интерактивная поверхность objective(t_w, free_time) для заданного режима учёбы."""
    tw_vals = np.arange(0, 1440, t_step)
    free_vals = np.arange(0, config.max_free_time + 1, free_step)
    T, F = np.meshgrid(tw_vals, free_vals)
    Z = np.zeros_like(T, dtype=float)
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            val = objective(config, int(T[i, j]), x, int(F[i, j]))
            Z[i, j] = val if val < 1e11 else None  # убираем запрещённые области

    fig = go.Figure(data=[go.Surface(
        x=tw_vals, y=free_vals, z=Z,
        colorscale='Viridis',
        colorbar=dict(title='Objective'),
        name=f'Режим {x}'
    )])
    mode = 'утром' if x == 1 else 'вечером'
    fig.update_layout(
        title=f'Поверхность целевой функции (учёба {mode})',
        scene=dict(
            xaxis_title='Пробуждение (мин)',
            yaxis_title='Свободное время (мин)',
            zaxis_title='Objective'
        )
    )
    if save_html:
        fig.write_html(f'objective_3d_mode_{x}.html')
    else:
        fig.show()


def plot_3d_both_surfaces(config, t_step=10, free_step=5, save_html=False):
    """Обе поверхности на одном графике с разными цветами."""
    tw_vals = np.arange(0, 1440, t_step)
    free_vals = np.arange(0, config.max_free_time + 1, free_step)
    T, F = np.meshgrid(tw_vals, free_vals)
    
    Z_evening = np.zeros_like(T, dtype=float)
    Z_morning = np.zeros_like(T, dtype=float)
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            val_e = objective(config, int(T[i, j]), 0, int(F[i, j]))
            val_m = objective(config, int(T[i, j]), 1, int(F[i, j]))
            Z_evening[i, j] = val_e if val_e < 1e11 else None
            Z_morning[i, j] = val_m if val_m < 1e11 else None

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=tw_vals, y=free_vals, z=Z_evening,
        colorscale='Reds', showscale=True, colorbar=dict(title='Вечер'),
        name='Вечерняя учёба'
    ))
    fig.add_trace(go.Surface(
        x=tw_vals, y=free_vals, z=Z_morning,
        colorscale='Blues', showscale=True, colorbar=dict(title='Утро'),
        name='Утренняя учёба'
    ))
    fig.update_layout(
        title='Сравнение режимов учёбы (красный – вечер, синий – утро)',
        scene=dict(
            xaxis_title='Пробуждение (мин)',
            yaxis_title='Свободное время (мин)',
            zaxis_title='Objective'
        )
    )
    if save_html:
        fig.write_html('objective_3d_both.html')
    else:
        fig.show()


# ---------------------------------------------------------------------------
#  Старые 2D-графики (для совместимости) – теперь строят при фиксированном free_time=0
# ---------------------------------------------------------------------------

def plot_2d(config, step=5):
    """2D-срез при free_time = 0."""
    t_w_values = np.arange(0, 1440, step)
    Z_evening = [objective(config, int(t), 0, 0) for t in t_w_values]
    Z_morning = [objective(config, int(t), 1, 0) for t in t_w_values]

    plt.figure()
    plt.plot(t_w_values, Z_evening, label="x=0 (вечер)")
    plt.plot(t_w_values, Z_morning, label="x=1 (утро)")
    plt.xlabel("Время пробуждения (мин)")
    plt.ylabel("Objective")
    plt.legend()
    plt.title("Целевая функция при free_time=0")
    plt.grid(True)
    plt.show()


def plot_2d_log(config, step=5):
    """2D-срез в логарифмическом масштабе при free_time=0."""
    t_w_values = np.arange(0, 1440, step)
    Z_evening = np.array([objective(config, int(t), 0, 0) for t in t_w_values])
    Z_morning = np.array([objective(config, int(t), 1, 0) for t in t_w_values])
    Z_evening = np.log(np.maximum(Z_evening, 1e-6) + 1)
    Z_morning = np.log(np.maximum(Z_morning, 1e-6) + 1)

    plt.figure()
    plt.plot(t_w_values, Z_evening, label="x=0 (вечер)")
    plt.plot(t_w_values, Z_morning, label="x=1 (утро)")
    plt.xlabel("Время пробуждения (мин)")
    plt.ylabel("log(objective + 1)")
    plt.legend()
    plt.title("Логарифмический масштаб (free_time=0)")
    plt.grid(True)
    plt.show()


def plot_heatmap(config, step=10):
    """Тепловая карта (t_w vs режим) при free_time=0."""
    t_w_values = np.arange(0, 1440, step)
    x_values = [0, 1]
    Z = np.zeros((2, len(t_w_values)))
    for i, x in enumerate(x_values):
        for j, t in enumerate(t_w_values):
            Z[i, j] = objective(config, int(t), x, 0)

    plt.figure()
    plt.imshow(Z, aspect='auto', extent=[t_w_values[0], t_w_values[-1], -0.5, 1.5])
    plt.yticks([0, 1], ["вечер", "утро"])
    plt.xlabel("Время пробуждения (мин)")
    plt.ylabel("Режим учёбы")
    plt.colorbar(label='objective')
    plt.title("Тепловая карта при free_time=0")
    plt.show()


def plot_with_minimum(config, step=5, free_time=0):
    """2D-срез с отмеченным глобальным минимумом для заданного free_time."""
    t_w_values = np.arange(0, 1440, step)
    Z_evening = [objective(config, int(t), 0, free_time) for t in t_w_values]
    Z_morning = [objective(config, int(t), 1, free_time) for t in t_w_values]

    best_val = float('inf')
    best_tw, best_x = 0, 0
    for tw in t_w_values:
        for x in [0, 1]:
            val = objective(config, int(tw), x, free_time)
            if val < best_val:
                best_val = val
                best_tw, best_x = tw, x

    plt.figure()
    plt.plot(t_w_values, Z_evening, label="x=0 (вечер)")
    plt.plot(t_w_values, Z_morning, label="x=1 (утро)")
    plt.scatter([best_tw], [best_val], color='red', zorder=5, label=f'Мин. при free_time={free_time}')
    plt.xlabel("Время пробуждения (мин)")
    plt.ylabel("Objective")
    plt.legend()
    plt.title("Целевая функция с минимумом")
    plt.grid(True)
    plt.show()