# TkWin11

Windows 11 Fluent-style themes and widgets for Python's `tkinter` / `ttk`.
纯 Tkinter / ttk 实现的 Windows 11 Fluent 风格主题与控件库。

## Installation / 安装

```bash
python -m pip install tkwin11
```

Requires Python 3.8+ with Tkinter available. Developed and tested on Windows 11
with Python 3.11. Windows-specific title bars, Snap and per-monitor DPI features
are enabled only on Windows; other platforms use the ordinary system title bar
and have not been fully tested. On Linux, install your distribution's Tkinter
package (often `python3-tk`) if needed. Tkinter is not installed by pip.

Core widgets require no third-party packages. `ImageViewer` can optionally use
Pillow for JPEG, WebP and additional image formats.

## Quick start / 快速开始

For an existing program, call `install()` before creating its first Tk root:

```python
import tkinter as tk
from tkinter import ttk
import tkwin11

tkwin11.install()
root = tk.Tk()
root.title("TkWin11 example")
ttk.Entry(root).pack(padx=24, pady=12)
ttk.Button(root, text="Save").pack(padx=24, pady=12)
root.mainloop()
```

New programs may instead call `enable_dpi_awareness()` before `tk.Tk()` and
`apply_theme(root)` before creating widgets.

The library includes Fluent buttons, switches, navigation, custom title bars,
menus, dialogs, tooltips, tables, spreadsheets, charts and form controls.

## Window transitions / 窗口过渡

`install()` defaults to `window_flicker_workaround=True`. This experimental
workaround only affects windows using the library's custom title bars; it does
not add a title bar to ordinary Tk windows. To disable it:

```python
tkwin11.install(window_flicker_workaround=False)
```

`WindowChrome`, `FluentWindowChrome` and `FluentTitleBar` also accept this option
per window. Applications using manual theme initialization do not enable it
unless requested. The workaround is timing-based, not a root-cause rendering
fix; occluded windows fall back to native restore behavior.

## Demo and documentation

Download the [GitHub source](https://github.com/bvb6417/tkwin11) or source
distribution, then run `python main.py` to open the Gallery. The wheel installs
the library; the Gallery stays in the source distribution.

- [Full documentation and examples](https://github.com/bvb6417/tkwin11#readme)
- [Changelog](https://github.com/bvb6417/tkwin11/blob/main/CHANGELOG.md)
- [Issue tracker](https://github.com/bvb6417/tkwin11/issues)
- [TkWebUI comparison](https://github.com/bvb6417/tkwin11#如何选择tkwin11-还是-tkwebui)

MIT license. Derived from TkWebUI; see the included LICENSE for attribution.
