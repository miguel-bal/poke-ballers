import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class RadarChartWidget(FigureCanvasQTAgg):
    def __init__(self, labels):
        self.labels = labels
        self.num_axes = len(labels)
        self.angles = np.linspace(0, 2 * np.pi, self.num_axes, endpoint=False).tolist()
        self.angles += self.angles[:1]

        fig = Figure(figsize=(4, 4))
        self.ax = fig.add_subplot(111, polar=True)
        super().__init__(fig)

    def plot(self, series):
        """series: list of (name, values, color) where values has one entry per label."""
        self.ax.clear()
        self.ax.set_theta_offset(np.pi / 2)
        self.ax.set_theta_direction(-1)
        self.ax.set_xticks(self.angles[:-1])
        self.ax.set_xticklabels(self.labels)
        self.ax.set_ylim(0, 100)
        self.ax.set_yticks([25, 50, 75, 100])
        self.ax.set_yticklabels(["25", "50", "75", "100"], fontsize=7)

        for name, values, color in series:
            closed_values = list(values) + [values[0]]
            self.ax.plot(self.angles, closed_values, color=color, linewidth=2, label=name)
            self.ax.fill(self.angles, closed_values, color=color, alpha=0.15)

        self.ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)
        self.draw()
