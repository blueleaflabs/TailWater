"""Shared matplotlib style for every TailWater figure (one place to change).

Font: the journal asks for Times New Roman inside figures. That font is not redistributable, so it
is not in the repository. Put a copy of 'Times New Roman.ttf' (and 'Times New Roman Bold.ttf') in
fonts/ at the repository root — on macOS they are in /System/Library/Fonts/Supplemental/ — and
this module registers them. Without them it falls back to Liberation Serif, which has identical
metrics, so layouts do not shift.
"""
import pathlib, glob
import matplotlib
from matplotlib import font_manager

ROOT = pathlib.Path(__file__).resolve().parents[1]
for f in glob.glob(str(ROOT / 'fonts' / '*.[to]tf')):
    font_manager.fontManager.addfont(f)
_names = {f.name for f in font_manager.fontManager.ttflist}
FONT = 'Times New Roman' if 'Times New Roman' in _names else 'Liberation Serif'

INK = '#0b0b0b'; MUTED = '#898781'; GRID = '#e1e0d9'; SURF = '#fcfcfb'
COLORS = {'above': '#2a78d6', 'below': '#eb6834', 'bell': '#1baf7a', 'dunn': '#eda100', 'trib': '#898781'}

def apply(size=9):
    matplotlib.rcParams.update({
        'font.family': 'serif', 'font.serif': [FONT, 'Liberation Serif', 'Nimbus Roman'], 'font.size': size,
        'axes.edgecolor': '#c3c2b7', 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
        'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': SURF, 'axes.facecolor': SURF,
        'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6})
    return FONT
