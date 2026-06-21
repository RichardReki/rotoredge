"""Generate the RotorEdge BUIDL logo: a 480x480 PNG, brand colors (dark + green),
a 'rotor' pinwheel motif (rotation/rotation-of-momentum) with an RE monogram."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from pathlib import Path

BG = "#0d1117"
C0 = np.array([0.10, 0.40, 0.34])   # dim teal
C1 = np.array([0.20, 0.88, 0.63])   # bright green (#34e0a1-ish)

fig = plt.figure(figsize=(4.8, 4.8), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.axis("off")
fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

# rounded dark background square is implicit; add a subtle outer ring
ax.add_patch(Circle((0, 0), 0.965, fill=False, lw=3, ec="#1c2530", zorder=1))

N = 14
inner_r, outer_r = 0.44, 0.93
w = (np.pi / N) * 0.60      # half angular width of a blade base
skew = 0.42                 # tip lead angle -> pinwheel spin

for i in range(N):
    a = 2 * np.pi * i / N
    t = i / (N - 1)
    color = tuple(C0 + (C1 - C0) * t)
    p1 = inner_r * np.array([np.cos(a - w), np.sin(a - w)])
    p2 = inner_r * np.array([np.cos(a + w), np.sin(a + w)])
    tip = outer_r * np.array([np.cos(a + skew), np.sin(a + skew)])
    ax.add_patch(Polygon([p1, p2, tip], closed=True, facecolor=color,
                         edgecolor=BG, linewidth=1.2, zorder=2))

# center disc + green ring
ax.add_patch(Circle((0, 0), 0.475, facecolor=BG, edgecolor="#34e0a1", lw=4, zorder=3))
ax.text(0, -0.02, "RE", ha="center", va="center", color="#eafff6",
        fontsize=62, fontweight="bold", family="DejaVu Sans", zorder=4)

out = Path(__file__).resolve().parents[1] / "logo.png"
fig.savefig(out, dpi=100, facecolor=fig.get_facecolor())
print(f"saved {out}  ({out.stat().st_size/1024:.0f} KB)")
