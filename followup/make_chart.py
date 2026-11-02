"""summary.csv로 README의 크기 비교 그림을 만든다. 값은 파일에서만 읽는다.

    uv run --no-project --with matplotlib python followup/make_chart.py
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch

ROOT = Path(__file__).resolve().parent.parent
THEMES = {
    "": {"surface": "#fcfcfb", "ink": "#0b0b0b", "muted": "#52514e", "bar": "#2a78d6"},
    "_dark": {"surface": "#1a1a19", "ink": "#f0efec", "muted": "#c3c2b7", "bar": "#2a78d6"},
}
DPI = 200
BAR_PX = 24 * DPI / 100
RADIUS_PX = 4 * DPI / 100


def rounded_bar(ax, y, value, color):
    """기준선 쪽은 각지게, 값 쪽 끝만 둥글게 그린다."""
    x0, yc = ax.transData.transform((0, y))
    x1, _ = ax.transData.transform((value, y))
    top, bottom = yc + BAR_PX / 2, yc - BAR_PX / 2
    r = min(RADIUS_PX, (x1 - x0) / 2)
    verts = [(x0, bottom), (x1 - r, bottom), (x1, bottom), (x1, bottom + r),
             (x1, top - r), (x1, top), (x1 - r, top), (x0, top), (x0, bottom)]
    codes = [MplPath.MOVETO, MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3,
             MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3, MplPath.LINETO, MplPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=color, edgecolor="none", transform=None))


def panel(ax, rows, title, fmt, theme, limit):
    ax.set_facecolor(theme["surface"])
    ax.set_xlim(0, limit)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_title(title, loc="left", fontsize=12, color=theme["muted"], pad=10)
    ax.set_xticks([])
    ax.set_yticks(range(len(rows)), [name for name, _ in rows], fontsize=12, color=theme["ink"])
    ax.tick_params(length=0, pad=8)
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(theme["muted"])
    for y, (_, value) in enumerate(rows):
        ax.annotate(fmt(value), (value, y), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=12, color=theme["ink"])


def draw(rows, suffix, theme):
    plt.rcParams["font.family"] = ["Apple SD Gothic Neo", "Noto Sans CJK KR", "sans-serif"]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.1), dpi=DPI, facecolor=theme["surface"])
    fig.subplots_adjust(left=0.09, right=0.95, top=0.70, bottom=0.14, wspace=0.34)
    fig.text(0.02, 0.91, "small까지 오류가 크게 줄고, large-v3는 시간이 크게 늘어납니다",
             fontsize=15, fontweight="bold", color=theme["ink"])
    fig.text(0.02, 0.04, "공개 낭독 음성 457문장, Apple M5 CPU에서 측정. GPU 처리 시간이 아닙니다.",
             fontsize=10, color=theme["muted"])
    wer = [(r["모델"], float(r["WER 그대로"])) for r in rows]
    minutes = [(r["모델"], 60 / float(r["실시간 대비 배속"])) for r in rows]
    panel(axes[0], wer, "WER(낮을수록 좋음)", lambda v: f"{v:.3f}", theme, 0.75)
    panel(axes[1], minutes, "음성 1시간 전사 시간(분)", lambda v: f"{v:.1f}분", theme, 88)
    fig.canvas.draw()
    for ax, data in ((axes[0], wer), (axes[1], minutes)):
        for y, (_, value) in enumerate(data):
            rounded_bar(ax, y, value, theme["bar"])
    fig.savefig(ROOT / "assets" / f"whisper_size_comparison{suffix}.png", facecolor=theme["surface"])


if __name__ == "__main__":
    with open(ROOT / "followup" / "summary.csv", encoding="utf-8") as f:
        table = list(csv.DictReader(f))
    for name, colors in THEMES.items():
        draw(table, name, colors)
