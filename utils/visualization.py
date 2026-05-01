import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from problem.objective import objective

def plot_3d_interactive(config, step=10, save_html=True):
    t_w_values = np.arange(0, 1440, step)

    Z_evening = []
    Z_morning = []

    for t_w in t_w_values:
        Z_evening.append(objective(config, int(t_w), 0))
        Z_morning.append(objective(config, int(t_w), 1))

    Z_evening = np.array(Z_evening)
    Z_morning = np.array(Z_morning)

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=t_w_values,
        y=np.zeros_like(t_w_values),
        z=Z_evening,
        mode='lines',
        name='x=0 (evening)'
    ))

    fig.add_trace(go.Scatter3d(
        x=t_w_values,
        y=np.ones_like(t_w_values),
        z=Z_morning,
        mode='lines',
        name='x=1 (morning)'
    ))

    fig.update_layout(
        title="Objective Function Landscape",
        scene=dict(
            xaxis_title="t_w",
            yaxis_title="mode",
            zaxis_title="objective"
        )
    )

    if save_html:
        fig.write_html("objective_3d.html")
    else:
        fig.show()
  
      
def plot_2d(config, step=5):
    t_w_values = np.arange(0, 1440, step)

    Z_evening = [objective(config, int(t), 0) for t in t_w_values]
    Z_morning = [objective(config, int(t), 1) for t in t_w_values]

    plt.figure()
    plt.plot(t_w_values, Z_evening, label="x=0 (evening)")
    plt.plot(t_w_values, Z_morning, label="x=1 (morning)")

    plt.xlabel("t_w")
    plt.ylabel("objective")
    plt.legend()
    plt.title("Objective function (2D view)")

    plt.show()

  
def plot_2d_log(config, step=5):
    t_w_values = np.arange(0, 1440, step)

    Z_evening = [objective(config, int(t), 0) for t in t_w_values]
    Z_morning = [objective(config, int(t), 1) for t in t_w_values]

    Z_evening = np.log(np.array(Z_evening) + 1)
    Z_morning = np.log(np.array(Z_morning) + 1)

    plt.figure()
    plt.plot(t_w_values, Z_evening, label="x=0 (evening)")
    plt.plot(t_w_values, Z_morning, label="x=1 (morning)")

    plt.xlabel("t_w")
    plt.ylabel("log(objective)")
    plt.legend()
    plt.title("Objective (log scale)")

    plt.show()
    
def plot_heatmap(config, step=10):
    t_w_values = np.arange(0, 1440, step)
    x_values = [0, 1]

    Z = np.zeros((2, len(t_w_values)))

    for i, x in enumerate(x_values):
        for j, t in enumerate(t_w_values):
            Z[i, j] = objective(config, int(t), x)

    plt.figure()
    plt.imshow(Z, aspect='auto')

    plt.yticks([0, 1], ["evening", "morning"])
    plt.xlabel("t_w index")
    plt.ylabel("mode")
    plt.title("Objective heatmap")

    plt.colorbar()
    plt.show()
    
def find_global_minimum(config, step=1):
    best_val = float("inf")
    best = None

    for t_w in range(0, 1440, step):
        for x in [0, 1]:
            val = objective(config, t_w, x)

            if val < best_val:
                best_val = val
                best = (t_w, x)

    return best, best_val


def plot_with_minimum(config, step=5):
    t_w_values = np.arange(0, 1440, step)

    Z_evening = [objective(config, int(t), 0) for t in t_w_values]
    Z_morning = [objective(config, int(t), 1) for t in t_w_values]

    (t_best, x_best), val_best = find_global_minimum(config)

    plt.figure()
    plt.plot(t_w_values, Z_evening, label="x=0")
    plt.plot(t_w_values, Z_morning, label="x=1")

    plt.scatter([t_best], [val_best], label="minimum")

    plt.legend()
    plt.title("Minimum point")

    plt.show()