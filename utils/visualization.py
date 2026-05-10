import os
import numpy as np
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')          # без GUI, только сохранение
import matplotlib.pyplot as plt
from problem.objective import objective


def _ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


# ------------------------------------------------------------
#  Глобальный минимум перебором
# ------------------------------------------------------------
def _find_best_free_for_tw_x(config, t_w, x, free_step=2):
    best_obj = float('inf')
    best_free = 0
    for ft in range(0, config.max_free_time + 1, free_step):
        obj = objective(config, t_w, x, ft)
        if obj < best_obj:
            best_obj = obj
            best_free = ft
    return best_free, best_obj


def find_global_minimum(config, t_step=5, free_step=2):
    best_val = float('inf')
    best = None
    for t_w in range(0, 1440, t_step):
        for x in [0, 1]:
            best_free, val = _find_best_free_for_tw_x(config, t_w, x, free_step)
            if val < best_val:
                best_val = val
                best = (t_w, x, best_free)
    return best, best_val


# ------------------------------------------------------------
#  Тепловая карта (t_w vs free_time) для выбранного режима
# ------------------------------------------------------------
def plot_heatmap_free(config, x=0, t_step=5, free_step=2, log_scale=False):
    t_w_vals = np.arange(0, 1440, t_step)
    free_vals = np.arange(0, config.max_free_time + 1, free_step)
    Z = np.zeros((len(free_vals), len(t_w_vals)))
    for i, ft in enumerate(free_vals):
        for j, tw in enumerate(t_w_vals):
            val = objective(config, int(tw), x, int(ft))
            if val >= 1e11:
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
    plt.scatter(t_w_vals[best_tw], free_vals[best_ft],
                c='red', marker='o', label='Лучшая точка на сетке')
    plt.legend()
    plt.tight_layout()

    fname = f'heatmap_free_x{x}.png'
    path = os.path.join(config.output_dir, fname)
    _ensure_dir(path)
    plt.savefig(path, dpi=150)
    plt.close()


# ------------------------------------------------------------
#  Срез оптимального free_time для каждого t_w (оба режима)
# ------------------------------------------------------------
def plot_optimal_free_slice(config, t_step=5, free_step=2):
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

    path = os.path.join(config.output_dir, 'optimal_free_slice.png')
    _ensure_dir(path)
    plt.savefig(path, dpi=150)
    plt.close()


# ------------------------------------------------------------
#  3D-поверхности Plotly (сохраняются в HTML)
# ------------------------------------------------------------
def plot_3d_surface(config, x=0, t_step=10, free_step=5):
    tw_vals = np.arange(0, 1440, t_step)
    free_vals = np.arange(0, config.max_free_time + 1, free_step)
    T, F = np.meshgrid(tw_vals, free_vals)
    Z = np.zeros_like(T, dtype=float)
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            val = objective(config, int(T[i, j]), x, int(F[i, j]))
            Z[i, j] = val if val < 1e11 else None

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
    fname = f'3d_surface_x{x}.html'
    path = os.path.join(config.output_dir, fname)
    _ensure_dir(path)
    fig.write_html(path)


def plot_3d_both_surfaces(config, t_step=10, free_step=5):
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
    path = os.path.join(config.output_dir, '3d_both_surfaces.html')
    _ensure_dir(path)
    fig.write_html(path)


# ------------------------------------------------------------
#  Классические двумерные срезы при free_time=0
# ------------------------------------------------------------
def plot_2d(config, step=5):
    t_w_vals = np.arange(0, 1440, step)
    Z_evening = [objective(config, int(t), 0, 0) for t in t_w_vals]
    Z_morning = [objective(config, int(t), 1, 0) for t in t_w_vals]

    plt.figure(figsize=(10,5))
    plt.plot(t_w_vals, Z_evening, label="x=0 (вечер)")
    plt.plot(t_w_vals, Z_morning, label="x=1 (утро)")
    plt.xlabel("Время пробуждения (мин)")
    plt.ylabel("Objective")
    plt.legend()
    plt.title("Целевая функция при free_time=0")
    plt.grid(True)

    path = os.path.join(config.output_dir, '2d_slice.png')
    _ensure_dir(path)
    plt.savefig(path, dpi=150)
    plt.close()


def plot_2d_log(config, step=5):
    t_w_vals = np.arange(0, 1440, step)
    Z_e = np.array([objective(config, int(t), 0, 0) for t in t_w_vals])
    Z_m = np.array([objective(config, int(t), 1, 0) for t in t_w_vals])
    Z_e = np.log(np.maximum(Z_e, 1e-6) + 1)
    Z_m = np.log(np.maximum(Z_m, 1e-6) + 1)

    plt.figure(figsize=(10,5))
    plt.plot(t_w_vals, Z_e, label="x=0 (вечер)")
    plt.plot(t_w_vals, Z_m, label="x=1 (утро)")
    plt.xlabel("Время пробуждения (мин)")
    plt.ylabel("log(objective + 1)")
    plt.legend()
    plt.title("Логарифмический масштаб (free_time=0)")
    plt.grid(True)

    path = os.path.join(config.output_dir, '2d_log_slice.png')
    _ensure_dir(path)
    plt.savefig(path, dpi=150)
    plt.close()


def plot_heatmap(config, step=10):
    t_w_vals = np.arange(0, 1440, step)
    x_vals = [0, 1]
    Z = np.zeros((2, len(t_w_vals)))
    for i, x in enumerate(x_vals):
        for j, t in enumerate(t_w_vals):
            Z[i, j] = objective(config, int(t), x, 0)

    plt.figure(figsize=(10,4))
    plt.imshow(Z, aspect='auto', extent=[t_w_vals[0], t_w_vals[-1], -0.5, 1.5])
    plt.yticks([0, 1], ["вечер", "утро"])
    plt.xlabel("Время пробуждения (мин)")
    plt.ylabel("Режим учёбы")
    plt.colorbar(label='objective')
    plt.title("Тепловая карта при free_time=0")

    path = os.path.join(config.output_dir, 'heatmap_2d.png')
    _ensure_dir(path)
    plt.savefig(path, dpi=150)
    plt.close()


def plot_with_minimum(config, step=5, free_time=0):
    t_w_vals = np.arange(0, 1440, step)
    Z_eve = [objective(config, int(t), 0, free_time) for t in t_w_vals]
    Z_morn = [objective(config, int(t), 1, free_time) for t in t_w_vals]

    best_val = float('inf')
    best_tw, best_x = 0, 0
    for tw in t_w_vals:
        for x in [0, 1]:
            val = objective(config, int(tw), x, free_time)
            if val < best_val:
                best_val = val
                best_tw, best_x = tw, x

    plt.figure(figsize=(10,5))
    plt.plot(t_w_vals, Z_eve, label="x=0 (вечер)")
    plt.plot(t_w_vals, Z_morn, label="x=1 (утро)")
    plt.scatter([best_tw], [best_val], color='red', zorder=5,
                label=f'Мин. при free_time={free_time}')
    plt.xlabel("Время пробуждения (мин)")
    plt.ylabel("Objective")
    plt.legend()
    plt.title("Целевая функция с минимумом")
    plt.grid(True)

    path = os.path.join(config.output_dir, '2d_with_minimum.png')
    _ensure_dir(path)
    plt.savefig(path, dpi=150)
    plt.close()