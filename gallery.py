"""TkWin11 Gallery: every control, organised like the WinUI 3 Gallery.

Run:  python gallery.py [--page KEY]   (or double-click main.py)
Standard library only. Pages are built on first visit; demo data stays in memory.
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import textwrap
import time
import tkinter as tk
import traceback
from datetime import date
from pathlib import Path
from tkinter import font as tkfont
from tkinter import ttk

sys.dont_write_bytecode = True
BASE = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

import tkwin11 as ui
from tkwin11 import PALETTE
from tkwin11.fluent import WORKSPACE

# key, title, icon, short description, keywords. Group rows have key None.
NAVIGATION = [
    ('home', '主页', 'home', '', ''),
    ('all', '全部控件', 'controls', '', ''),
    (None, '基础输入', 'edit', 'basic', ''),
    ('button', '按钮', 'play', '主要、次要、轻量、语义色与图标按钮。', 'Button FluentButton Primary Quiet'),
    ('toggle', '切换按钮', 'check', '保持选中状态的按钮、工具按钮与分段选择。', 'ToggleButton ToolButton SegmentedControl'),
    ('check', '复选框与单选', 'check', '复选、三态复选与单选按钮组。', 'Checkbutton Radiobutton CheckBox RadioButton'),
    ('switch', '开关', 'controls', '立即生效的开 / 关切换。', 'ToggleSwitch FluentSwitch Switch'),
    ('slider', '滑块', 'speed', '连续或步进数值、垂直滑块与数值框联动。', 'Slider Scale FluentSlider ValueSlider ProgressSlider'),
    ('combo', '下拉选择', 'chevrondown', '只读、可编辑下拉框与按钮式选择。', 'ComboBox Combobox Dropdown OptionMenu MenuButton'),
    (None, '文本', 'text', 'text', ''),
    ('entry', '文本框', 'edit', '单行输入、输入提示、密码、数字框与输入校验。', 'TextBox Entry PasswordBox NumberBox Spinbox ValidatedEntry PlaceholderEntry PlaceholderText set_placeholder 占位 输入提示 灰字'),
    ('richtext', '多行文本', 'text', '多行编辑、只读模式与快捷键块。', 'RichEditBox Text RoundedText KeyChord'),
    (None, '集合', 'list', 'collections', ''),
    ('listview', '列表', 'list', '单选、多选列表与原生 Listbox。', 'ListView Listbox RoundedListbox'),
    ('treeview', '树形与多列列表', 'layers', '层级节点、多列排序列表。', 'TreeView Treeview SortableTreeview'),
    ('datagrid', '数据表格', 'library', '搜索、筛选、排序、分页与导出。', 'DataGrid DataTable'),
    ('spreadsheet', '电子表格', 'library', '单元格选择、编辑、复制粘贴与撤销。', 'Spreadsheet Excel'),
    ('cardlist', '卡片列表', 'layers', '大数据量卡片列表，单一画布绘制。', 'CardList ItemsView'),
    (None, '日期与时间', 'calendar', 'datetime', ''),
    ('date', '日期选择', 'calendar', '输入或在日历中选择日期，支持范围限制。', 'CalendarDatePicker DateEntry Calendar'),
    (None, '对话框与浮层', 'dialog', 'dialogs', ''),
    ('dialog', '对话框', 'dialog', '模态对话框、确认与输入。', 'ContentDialog Modal Dialogs MessageBox'),
    ('flyout', '浮层', 'window', '附着在控件旁的表单浮层。', 'Flyout FormFlyout'),
    ('menu', '菜单', 'more', '菜单浮层、右键菜单与级联子菜单。', 'MenuFlyout Menu ThemedMenu ContextMenu'),
    ('tooltip', '工具提示', 'info', '悬停或聚焦时显示的说明。', 'ToolTip Tooltip'),
    ('toast', '通知', 'bell', '不阻塞操作、自动消失的通知。', 'InfoBar Toast notify'),
    (None, '布局', 'layers', 'layout', ''),
    ('settings_card', '设置卡片与展开', 'settings', '设置行、展开卡片与折叠区。', 'SettingsCard Expander ExpanderCard Accordion SettingRow'),
    ('tabs', '标签页', 'window', '带禁用状态的标签页。', 'TabView Notebook Tabs'),
    ('split', '分割面板', 'expandview', '可拖动调整的分割区域。', 'SplitView Panedwindow'),
    ('card', '卡片与分组', 'layers', '卡片、分组框、分隔线与尺寸手柄。', 'Card SectionCard LabelFrame Separator Sizegrip'),
    (None, '导航', 'navigation', 'navigation', ''),
    ('navview', '导航视图', 'navigation', '层级导航、指示条与键盘操作。', 'NavigationView'),
    ('sidebar', '侧栏与分段', 'navigation', '紧凑侧栏与分段选择。', 'Sidebar SegmentedControl Pivot'),
    (None, '状态与信息', 'info', 'status', ''),
    ('progress', '进度', 'timer', '确定与不确定进度、带文字进度。', 'ProgressBar ProgressRing TextProgress'),
    ('meter', '仪表与徽章', 'speed', '圆环 / 半圆仪表与状态徽章。', 'Meter Badge InfoBadge'),
    (None, '图表', 'chart', 'charts', ''),
    ('line', '折线与散点图', 'chart', '多系列、缩放平移与悬停数值。', 'LineChart ScatterChart Chart'),
    ('bar', '柱状与饼图', 'chart', '分组柱状、饼图 / 环形图。', 'ColumnChart DonutChart PieChart BarChart'),
    (None, '媒体与外观', 'image', 'media', ''),
    ('image', '图片查看', 'image', '缩放、平移与适应窗口。', 'Image ImageViewer'),
    ('color', '颜色选择', 'palette', '色板、十六进制与 RGB 输入。', 'ColorPicker ColorDialog'),
    ('font', '字体选择', 'text', '字体、字号与样式实时预览。', 'FontPicker FontDialog Typography'),
    (None, '窗口与系统', 'window', 'window', ''),
    ('titlebar', '标题栏', 'window', '一体化标题栏，原生拖动、贴靠与缩放。', 'TitleBar FluentTitleBar WindowChrome'),
    ('dpi', '多显示器与性能', 'maximize', '每显示器 DPI、动画开关与弹窗性能自测。', 'DPI Monitor Performance Animation'),
    ('legacy', '旧程序一键替换', 'refresh', '一行代码让现有 tkinter 程序换上 Win11 外观。', 'install legacy classic theme_classic'),
]
BOTTOM = [('settings', '设置', 'settings', '动画、关于与版本信息。', 'Settings About')]
GROUP_TITLES = {item[3]: item[1] for item in NAVIGATION if item[0] is None}


class Example(ttk.Frame):
    """WinUI Gallery style sample: title, demo surface, options pane, source code."""

    def __init__(self, parent, app, title, *, description='', code='', options=False):
        super().__init__(parent, style='Workspace.TFrame')
        self.app = app
        px = app.px
        ttk.Label(self, text=title, style='Demo.Example.TLabel').pack(anchor='w', pady=(0, px(8)))
        if description:
            app.wrap(ttk.Label(self, text=description, style='Workspace.Muted.TLabel', justify='left')).pack(anchor='w', fill='x', pady=(0, px(8)))
        self.card = ttk.Frame(self, style='Fluent.Card.TFrame', padding=px(2))
        self.card.pack(fill='x')
        top = ttk.Frame(self.card)
        top.pack(fill='x')
        top.columnconfigure(0, weight=1)
        self.demo = ttk.Frame(top, padding=px(20))
        self.demo.grid(row=0, column=0, sticky='nsew')
        self.options = None
        if options:
            ttk.Separator(top, orient='vertical').grid(row=0, column=1, sticky='ns', pady=px(8))
            top.columnconfigure(2, minsize=px(230))
            self.options = ttk.Frame(top, padding=(px(18), px(16)))
            self.options.grid(row=0, column=2, sticky='nsew')
            ttk.Label(self.options, text='选项', style='Muted.TLabel').pack(anchor='w', pady=(0, px(6)))
        self.code = textwrap.dedent(code).strip('\n')
        self.code_view = None
        if self.code:
            ttk.Separator(self.card).pack(fill='x', padx=px(8))
            self.code_button = ttk.Button(self.card, text='  源代码', style='Popup.Quiet.TButton', compound='left',
                                          image=app.chevron(False), command=self.toggle_code)
            self.code_button.pack(fill='x', padx=px(6), pady=px(4))
        self.pack(fill='x', pady=(0, px(26)))

    def toggle_code(self):
        if self.code_view is None:
            px = self.app.px
            lines = self.code.count('\n') + 1
            self.code_view = ui.RoundedText(self.card, height=min(lines, 18), wrap='none', font=self.app.mono,
                                            padding=(px(12), px(10)))
            self.code_view.insert('1.0', self.code)
            ui.set_readonly(self.code_view)
            self.code_view.pack(fill='x', padx=px(10), pady=(0, px(10)))
            self.code_button.configure(image=self.app.chevron(True))
        elif self.code_view.container.winfo_manager():
            self.code_view.pack_forget()
            self.code_button.configure(image=self.app.chevron(False))
        else:
            self.code_view.pack(fill='x', padx=self.app.px(10), pady=(0, self.app.px(10)))
            self.code_button.configure(image=self.app.chevron(True))

    def option(self, widget, pady=4):
        widget.pack(anchor='w', fill='x', pady=self.app.px(pady))
        return widget

    def disable_option(self, controls, text='禁用控件'):
        """Options-pane checkbox that disables the listed controls."""
        variable = tk.BooleanVar(self, value=False)
        def apply():
            disabled = variable.get()
            for control in controls:
                set_disabled(control, disabled)
            self.app.status.set(('已禁用：' if disabled else '已启用：') + self.master_title())
        return self.option(ttk.Checkbutton(self.options, text=text, variable=variable, command=apply))

    def master_title(self):
        return str(self.winfo_children()[0].cget('text'))


def set_disabled(control, disabled):
    if isinstance(control, (ui.FluentSlider, ui.ProgressSlider)):
        control.configure(state='disabled' if disabled else 'normal')
    elif isinstance(control, (tk.Text, tk.Listbox, tk.Scale, tk.Button)):
        control.configure(state='disabled' if disabled else 'normal')
    else:
        control.state(['disabled' if disabled else '!disabled'])


class Demo(tk.Tk):
    def __init__(self, page='home'):
        super().__init__()
        self.withdraw()
        self.errors = []
        self.variables = []     # demo variables must outlive the page builders
        self.title('TkWin11 Gallery')
        ui.apply_theme(self)
        ui.configure_fluent(self)
        ui.theme_classic(self)
        self.scale = self.winfo_fpixels('1i') / 96
        self.px = lambda v: max(1, round(v * self.scale))
        self.info = {item[0]: item for item in NAVIGATION + BOTTOM if item[0]}
        self.group_of = {}
        group = None
        for item in NAVIGATION:
            if item[0] is None:
                group = item[3]
            elif group:
                self.group_of[item[0]] = group
        self.pages = {}
        self.active = None
        self.history = []
        self.jobs = set()
        self.status = tk.StringVar(self, value='就绪')
        self.motion = tk.BooleanVar(self, value=True)
        self.motion.trace_add('write', lambda *_: setattr(self, 'motion_enabled', self.motion.get()))
        mono = 'Cascadia Mono' if tkfont.Font(self, family='Cascadia Mono').actual('family') == 'Cascadia Mono' else 'Consolas'
        self.mono = tkfont.Font(self, family=mono, size=10)
        self.styles()
        self.build()
        self.position()
        self.reveal(page if page in self.info else 'home')

    def reveal(self, page):
        """Show the window only after Tk has applied its size and laid it out.

        Once the native window exists, Tk applies wm geometry at the first map,
        so a withdrawn window is laid out at 200x200 and the first visible
        frames would show the title bar, sidebar and page still resizing. On
        Windows the window is mapped DWM-cloaked (laid out, not composed).
        """
        cloak = None
        if sys.platform == 'win32':
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            def cloak(on):
                value = ctypes.c_int(on)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 13, ctypes.byref(value), 4)  # DWMWA_CLOAK
            cloak(1)
        self.deiconify()
        self.update()       # real size, then the title bar chrome attaches
        self.update()
        self.open(page)
        self.update_idletasks()
        if cloak is not None:
            cloak(0)

    # ---------------------------------------------------------------- shell
    def styles(self):
        style = ttk.Style(self)
        family = 'Microsoft YaHei UI'
        style.configure('Demo.Hero.TLabel', background=WORKSPACE, font=(family, 24, 'bold'))
        style.configure('Demo.Title.TLabel', background=WORKSPACE, font=(family, 20, 'bold'))
        style.configure('Demo.Example.TLabel', background=WORKSPACE, font=(family, 11, 'bold'))
        style.configure('Demo.Group.TLabel', background=WORKSPACE, foreground=PALETTE['muted'], font=(family, 10, 'bold'))
        style.configure('Demo.Api.TLabel', background='#EEF2F6', foreground='#3A4350', font=(self.mono.actual('family'), 9),
                        padding=(self.px(8), self.px(3)))
        style.configure('Demo.Value.TLabel', foreground=PALETTE['accent'], font=(family, 10, 'bold'))
        style.configure('Demo.Big.TLabel', font=(family, 16, 'bold'))

    def report_callback_exception(self, exc, value, tb):
        detail = ''.join(traceback.format_exception(exc, value, tb))
        self.errors.append(detail)
        sys.stderr.write(detail)
        self.status.set('出现错误：' + str(value))

    def position(self):
        left, top, right, bottom = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
        if sys.platform == 'win32':
            import ctypes
            from ctypes import wintypes
            rect = wintypes.RECT()
            if ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0):
                left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
        width = min(right - left - self.px(20), self.px(1320))
        height = min(bottom - top - self.px(60), self.px(860))
        self.geometry(f'{width}x{height}{left + (right - left - width) // 2:+d}{top + self.px(16):+d}')
        self.minsize(self.px(1000), self.px(600))

    def build(self):
        sidebar = ttk.Frame(self, style='Sidebar.TFrame', width=self.px(300))
        self.titlebar = ui.FluentTitleBar(
            self, title='TkWin11 Gallery', sidebar_width=300, sidebar=sidebar,
            on_close=self.close, window_flicker_workaround=True,
        )
        self.titlebar.pack(fill='x')
        self.build_search()
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        self.nav = ui.NavigationView(sidebar, self.open, width=300)
        self.nav.pack(fill='both', expand=True)
        for key, title, symbol, group, _ in NAVIGATION:
            if key is None:
                self.nav.add_group(group, title, symbol, opened=group == 'basic')
            else:
                self.nav.add(key, title, symbol, parent=self.group_of.get(key))
        for key, title, symbol, _, _ in BOTTOM:
            self.nav.add(key, title, symbol, bottom=True)
        shell = ttk.Frame(self, style='Workspace.TFrame')
        shell.pack(fill='both', expand=True)
        footer = ttk.Frame(shell, style='Workspace.TFrame', padding=(self.px(28), self.px(8)))
        footer.pack(side='bottom', fill='x')
        ttk.Label(footer, textvariable=self.status, style='Workspace.Muted.TLabel').pack(side='left')
        self.dpi_label = ttk.Label(footer, style='Workspace.Muted.TLabel')
        self.dpi_label.pack(side='right')
        self.deck = ttk.Frame(shell, style='Workspace.TFrame')
        self.deck.pack(fill='both', expand=True)
        self.bind('<Control-Prior>', lambda e: self.step(-1))
        self.bind('<Control-Next>', lambda e: self.step(1))
        self.bind('<Control-f>', lambda e: (self.search.focus_set(), self.search.select_range(0, 'end'), 'break')[-1])
        self.bind('<Alt-Left>', lambda e: self.back())
        self.refresh_dpi_label()

    def build_search(self):
        """Title-bar search box, like the WinUI Gallery's AutoSuggestBox."""
        holder = ttk.Frame(self.titlebar, style='Workspace.TFrame')
        holder.place(relx=.5, rely=.5, anchor='center', width=self.px(380))
        self.titlebar.chrome.extra_exclusions.append(holder)
        self.query = tk.StringVar(self)
        self.search = ui.PlaceholderEntry(holder, textvariable=self.query, placeholder='搜索控件   Enter 跳转 · ↓ 列表')
        self.search.pack(fill='x')
        self.search.bind('<Return>', lambda e: self.search_go())
        self.search.bind('<Down>', lambda e: self.search_list())
        self.search.bind('<Escape>', lambda e: (self.query.set(''), self.focus_set()))

    def matches(self):
        text = self.query.get().strip().casefold()
        if not text:
            return []
        scored = []
        for key, (k, title, _, desc, words) in self.info.items():
            haystack = ' '.join((title, desc, words, GROUP_TITLES.get(self.group_of.get(key), ''))).casefold()
            if text in haystack:
                scored.append((0 if title.casefold().startswith(text) else 1 if text in title.casefold() else 2, key))
        return [key for _, key in sorted(scored)]

    def search_go(self):
        found = self.matches()
        if found:
            self.open(found[0])
            self.status.set(f'搜索“{self.query.get()}”：{len(found)} 个结果，已打开 {self.info[found[0]][1]}')
        else:
            self.status.set(f'没有找到“{self.query.get()}”')
        return 'break'

    def search_list(self):
        found = self.matches() or [key for key in self.info if key not in ('home', 'all')]
        items = [dict(label=f'{self.info[key][1]}    {GROUP_TITLES.get(self.group_of.get(key), "")}',
                      command=lambda k=key: self.open(k)) for key in found]
        ui.ChoicePopup(self.search, items, self.search.winfo_rootx(), self.search.winfo_rooty() + self.search.winfo_height() + self.px(4),
                       width=self.search.winfo_width(), selected=0)
        return 'break'

    def open(self, key):
        if key not in self.info:
            return
        if key == self.active:
            return
        previous = self.pages.get(self.active)
        if key not in self.pages:
            page = ui.FluentPage(self.deck)
            page.body.configure(padding=(self.px(40), self.px(28), self.px(40), self.px(36)))
            self.pages[key] = page
            started = time.perf_counter()
            getattr(self, 'page_' + key)(page.body)
            built = (time.perf_counter() - started) * 1000
        else:
            built = None
        page = self.pages[key]
        page.prepare(max(1, self.deck.winfo_width()), max(1, self.deck.winfo_height()))
        page.present()
        if previous is not None:
            previous.place_forget()
        if self.active is not None and not getattr(self, '_going_back', False):
            self.history = (self.history + [self.active])[-30:]
        self.active = key
        self.nav.select(key, notify=False)
        self.status.set(self.info[key][1] + (f' · 首次构建 {built:.0f} ms' if built is not None else ''))

    def back(self):
        if self.history:
            self._going_back = True
            try:
                self.open(self.history.pop())
            finally:
                self._going_back = False
        return 'break'

    def step(self, delta):
        keys = [item[0] for item in NAVIGATION + BOTTOM if item[0]]
        index = keys.index(self.active) if self.active in keys else 0
        self.open(keys[(index + delta) % len(keys)])
        return 'break'

    def var(self, cls, value=None, master=None):
        """A Tk variable that stays alive. An unreferenced tk.BooleanVar is
        garbage-collected, which unsets the Tcl variable and silently drops
        the initial value (a menu check mark, a checkbox, a slider position)."""
        variable = cls(master or self) if value is None else cls(master or self, value=value)
        self.variables.append(variable)
        return variable

    def after_job(self, delay, callback):
        job = None
        def run():
            self.jobs.discard(job)
            callback()
        job = self.after(delay, run)
        self.jobs.add(job)
        return job

    def refresh_dpi_label(self):
        if not self.winfo_exists():
            return
        resources = self._dpi_resources
        dpi = resources.window_dpi(self)
        self.dpi_label.configure(text=f'窗口 DPI {dpi} · 缩放 {dpi / 96:.0%} · 程序基准 {resources.base_dpi}')
        self.after_job(1000, self.refresh_dpi_label)

    def close(self):
        for job in list(self.jobs):
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        self.jobs.clear()
        for child in self.winfo_children():
            chrome = getattr(child, '_window_chrome', None)
            if isinstance(child, tk.Toplevel) and chrome is not None:
                chrome.detach()
        self.titlebar.chrome.detach()
        self.destroy()

    # -------------------------------------------------------------- helpers
    def chevron(self, opened):
        return ui.icon(self, 'chevrondown' if opened else 'chevronright', self.px(14))

    def wrap(self, label, minimum=120):
        label.bind('<Configure>', lambda e: label.configure(wraplength=max(minimum, e.width)), add='+')
        return label

    def header(self, body, key, apis=()):
        _, title, symbol, desc, _ = self.info[key]
        group = GROUP_TITLES.get(self.group_of.get(key))
        if group:
            ttk.Label(body, text=group, style='Demo.Group.TLabel').pack(anchor='w')
        ttk.Label(body, text=title, style='Demo.Title.TLabel').pack(anchor='w', pady=(self.px(2), self.px(6)))
        if desc:
            self.wrap(ttk.Label(body, text=desc, style='Workspace.Muted.TLabel', justify='left')).pack(anchor='w', fill='x')
        if apis:
            row = ttk.Frame(body, style='Workspace.TFrame')
            row.pack(anchor='w', pady=(self.px(12), 0))
            for name in apis:
                ttk.Label(row, text=name, style='Demo.Api.TLabel').pack(side='left', padx=(0, self.px(6)))
        ttk.Frame(body, style='Workspace.TFrame', height=self.px(24)).pack(fill='x')

    def example(self, body, title, **kwargs):
        return Example(body, self, title, **kwargs)

    def row(self, parent, pady=6):
        frame = ttk.Frame(parent)
        frame.pack(anchor='w', fill='x', pady=self.px(pady))
        return frame

    def value_label(self, parent, variable=None, text=''):
        label = ttk.Label(parent, textvariable=variable, text=text, style='Demo.Value.TLabel')
        return label

    def say(self, text):
        return lambda *_: self.status.set(text)

    def tile(self, parent, key, row, column, columns_weight=True):
        _, title, symbol, desc, _ = self.info[key]
        card = ui.Card(parent, padding=self.px(16), command=lambda: self.open(key))
        card.grid(row=row, column=column, sticky='nsew', padx=self.px(5), pady=self.px(5))
        ttk.Label(card, image=ui.icon(self, symbol, self.px(26), color=PALETTE['accent'])).pack(anchor='w')
        ttk.Label(card, text=title, style='Strong.TLabel').pack(anchor='w', pady=(self.px(10), self.px(3)))
        self.wrap(ttk.Label(card, text=desc or ' ', style='Muted.TLabel', justify='left'), 80).pack(anchor='w', fill='x')
        return card

    # ---------------------------------------------------------------- pages
    def page_home(self, body):
        ttk.Label(body, text='TkWin11 Gallery', style='Demo.Hero.TLabel').pack(anchor='w')
        self.wrap(ttk.Label(body, text='纯 tkinter / ttk 实现的 Windows 11 Fluent 控件。只需 Python 标准库；'
                                       '现有程序加一行 tkwin11.install() 即可换上同样的外观。',
                            style='Workspace.Muted.TLabel', justify='left')).pack(anchor='w', fill='x', pady=(self.px(6), self.px(24)))
        ex = self.example(body, '快速开始', code='''
            # 现有程序：在创建 Tk() 之前加一行
            import tkwin11; tkwin11.install()

            # 新程序：完整控件库
            import tkinter as tk
            import tkwin11 as ui
            ui.enable_dpi_awareness()          # 必须在 Tk() 之前
            root = tk.Tk()
            ui.apply_theme(root)
            ui.FluentButton(root, text='开始', style='Primary.TButton').pack()
            root.mainloop()
        ''')
        row = self.row(ex.demo, 0)
        for text, key, primary in [('浏览全部控件', 'all', True), ('旧程序一键替换', 'legacy', False), ('多显示器与性能', 'dpi', False)]:
            ui.FluentButton(row, text=text, style='Primary.TButton' if primary else 'TButton',
                            command=lambda k=key: self.open(k)).pack(side='left', padx=(0, self.px(8)))
        ttk.Label(body, text='按类别浏览', style='Demo.Example.TLabel').pack(anchor='w', pady=(0, self.px(8)))
        grid = ttk.Frame(body, style='Workspace.TFrame')
        grid.pack(fill='x', pady=(0, self.px(26)))
        firsts = []
        group = None
        for key, title, symbol, gkey, _ in NAVIGATION:
            if key is None:
                group = (title, symbol, gkey)
            elif group is not None:
                firsts.append((group, key))
                group = None
        for column in range(4):
            grid.columnconfigure(column, weight=1, uniform='group')
        for index, ((title, symbol, gkey), key) in enumerate(firsts):
            count = sum(1 for k in self.group_of if self.group_of[k] == gkey)
            card = ui.Card(grid, padding=self.px(16), command=lambda k=key: self.open(k))
            card.grid(row=index // 4, column=index % 4, sticky='nsew', padx=self.px(5), pady=self.px(5))
            ttk.Label(card, image=ui.icon(self, symbol, self.px(26), color=PALETTE['accent'])).pack(anchor='w')
            ttk.Label(card, text=title, style='Strong.TLabel').pack(anchor='w', pady=(self.px(10), self.px(2)))
            ttk.Label(card, text=f'{count} 个页面', style='Muted.TLabel').pack(anchor='w')
        ex = self.example(body, '本版改进')
        for text in ['副屏弹窗 / 菜单卡顿：消除运行期 ttk 样式写入引起的全局 <<ThemeChanged>> 重排，'
                     '隐藏页面在 DPI 变化后不再被重新映射与重绘。',
                     '修复 Python 3.13 以前 unbind(seq, id) 会删除同一事件全部绑定的问题（关闭菜单后窗口缩放缓存、提示框失效）。',
                     '控件命令代理只转发需要处理的子命令；instate / identify / coords / font measure 等直接走原生。',
                     '新增 tkwin11.install()：旧程序一行代码换肤，经典 tk 控件同样适配。']:
            line = self.row(ex.demo, 3)
            ttk.Label(line, text='•', style='Demo.Value.TLabel').pack(side='left', anchor='n', padx=(0, self.px(8)))
            self.wrap(ttk.Label(line, text=text, justify='left')).pack(side='left', fill='x', expand=True)

    def page_all(self, body):
        ttk.Label(body, text='全部控件', style='Demo.Title.TLabel').pack(anchor='w', pady=(0, self.px(20)))
        group = None
        grid = None
        index = 0
        for key, title, symbol, gkey, _ in NAVIGATION:
            if key in ('home', 'all'):
                continue
            if key is None:
                ttk.Label(body, text=title, style='Demo.Example.TLabel').pack(anchor='w', pady=(self.px(6), self.px(6)))
                grid = ttk.Frame(body, style='Workspace.TFrame')
                grid.pack(fill='x', pady=(0, self.px(14)))
                for column in range(4):
                    grid.columnconfigure(column, weight=1, uniform='tile')
                index = 0
                continue
            self.tile(grid, key, index // 4, index % 4)
            index += 1

    # basic input ------------------------------------------------------------
    def page_button(self, body):
        self.header(body, 'button', ('ttk.Button', 'FluentButton', 'Primary.TButton', 'Quiet.TButton'))
        ex = self.example(body, '标准按钮', options=True, code='''
            import tkinter.ttk as ttk
            ttk.Button(parent, text='标准按钮', command=on_click).pack()   # 原生写法自动获得动效
        ''')
        b = ttk.Button(ex.demo, text='标准按钮', command=self.say('点击了标准按钮'))
        b.pack(anchor='w')
        ex.disable_option([b])
        ex = self.example(body, '强调按钮', description='每个视图中通常只有一个主要操作。', options=True, code='''
            ui.FluentButton(parent, text='保存', style='Primary.TButton', command=save)
        ''')
        b = ui.FluentButton(ex.demo, text='保存更改', style='Primary.TButton', command=self.say('点击了强调按钮'))
        b.pack(anchor='w')
        ex.disable_option([b])
        ex = self.example(body, '轻量按钮与图标按钮', code='''
            icon = ui.icon(root, 'edit', 16)
            button = ttk.Button(parent, image=icon, style='Quiet.TButton', command=edit)
            ui.Tooltip(button, '编辑')
        ''')
        row = self.row(ex.demo, 0)
        ttk.Button(row, text='轻量操作', style='Quiet.TButton', command=self.say('轻量操作')).pack(side='left', padx=(0, self.px(12)))
        for symbol, tip in [('edit', '编辑'), ('search', '搜索'), ('download', '下载'), ('more', '更多')]:
            button = ttk.Button(row, image=ui.icon(self, symbol, self.px(16)), style='Quiet.TButton', command=self.say(tip))
            button.pack(side='left', padx=self.px(2))
            ui.Tooltip(button, tip)
        ex = self.example(body, '语义色按钮', description='实心、描边、链接三种变体，用于成功、警告、危险等语义。', code='''
            ttk.Button(parent, text='删除', style='Danger.TButton')
            ttk.Button(parent, text='重试', style='Warning.Outline.TButton')
            ttk.Button(parent, text='了解更多', style='Info.Link.TButton')
        ''')
        for kind, text in [('Success', '成功'), ('Warning', '警告'), ('Danger', '危险'), ('Info', '信息'), ('Neutral', '次要')]:
            row = self.row(ex.demo, 3)
            for variant, label in [('', '实心'), ('Outline.', '描边'), ('Link.', '链接')]:
                ttk.Button(row, text=f'{text} · {label}', style=f'{kind}.{variant}TButton',
                           command=self.say(f'{text}{label}按钮')).pack(side='left', padx=(0, self.px(8)))
        ex = self.example(body, '状态对照', description='固定显示各状态的外观，便于检查主题；鼠标经过会改变悬停状态。键盘焦点框只在用 Tab 键移动焦点时出现，可在本页其他按钮上按 Tab 查看。', code='''
            button.state(['active'])      # 悬停
            button.state(['pressed'])     # 按下
            button.state(['disabled'])    # 禁用
        ''')
        grid = ttk.Frame(ex.demo)
        grid.pack(fill='x')
        self._state_previews = []
        for column, (name, state) in enumerate([('正常', []), ('悬停', ['active']), ('按下', ['pressed']), ('禁用', ['disabled'])]):
            grid.columnconfigure(column, weight=1, uniform='state')
            ttk.Label(grid, text=name, style='Muted.TLabel').grid(row=0, column=column, pady=(0, self.px(8)))
            for row, style in [(1, 'TButton'), (2, 'Primary.TButton')]:
                button = ttk.Button(grid, text='普通按钮' if row == 1 else '强调按钮', style=style, takefocus=False)
                button.grid(row=row, column=column, padx=self.px(5), pady=self.px(4), sticky='ew')
                button.state(state)
                self._state_previews.append(button)

    def page_toggle(self, body):
        self.header(body, 'toggle', ('ToggleButton', 'ToolButton', 'SegmentedControl'))
        ex = self.example(body, '切换按钮', options=True, code='''
            pinned = tk.BooleanVar(value=True)
            ui.ToggleButton(parent, text='置顶', variable=pinned)
        ''')
        row = self.row(ex.demo, 0)
        controls = []
        for name, on in [('收藏', True), ('置顶', False), ('标记', False)]:
            v = self.var(tk.BooleanVar, on)
            t = ui.ToggleButton(row, text=name, variable=v, command=lambda n=name, var=v: self.status.set(f'{n}：{"开" if var.get() else "关"}'))
            t.pack(side='left', padx=(0, self.px(8)))
            controls.append(t)
        ex.disable_option(controls)
        ex = self.example(body, '工具按钮', description='常用于格式工具栏，可同时选中多个。', code='''
            ui.ToolButton(toolbar, text='B', variable=bold)
        ''')
        row = self.row(ex.demo, 0)
        for name in ('B', 'I', 'U', 'S'):
            ui.ToolButton(row, text=name, variable=self.var(tk.BooleanVar, name == 'B')).pack(side='left', padx=(0, self.px(4)))
        ex = self.example(body, '分段选择', description='在少量互斥选项之间切换视图；方向键可移动选择。', code='''
            period = tk.StringVar(value='week')
            ui.SegmentedControl(parent, [('day', '日'), ('week', '周'), ('month', '月')], period)
        ''')
        value = self.var(tk.StringVar, 'week')
        ui.SegmentedControl(ex.demo, [('day', '日'), ('week', '周'), ('month', '月'), ('year', '年')], value,
                            command=lambda v: self.status.set('分段选择：' + v)).pack(anchor='w')

    def page_check(self, body):
        self.header(body, 'check', ('ttk.Checkbutton', 'ttk.Radiobutton'))
        ex = self.example(body, '复选框', options=True, code='''
            agree = tk.BooleanVar()
            ttk.Checkbutton(parent, text='我已阅读并同意', variable=agree)
        ''')
        controls = []
        for text, on in [('自动保存', True), ('显示详细信息', False), ('启动时检查更新', True)]:
            c = ttk.Checkbutton(ex.demo, text=text, variable=self.var(tk.BooleanVar, on))
            c.pack(anchor='w', pady=self.px(4))
            controls.append(c)
        ex.disable_option(controls)
        ex = self.example(body, '三态复选框', description='父级根据子项显示全选、未选或部分选中（alternate 状态）。', code='''
            def sync_parent(*_):
                values = [v.get() for v in children]
                parent.state(['!alternate'])
                select_all.set(all(values))
                if any(values) and not all(values):
                    parent.state(['alternate'])
        ''')
        select_all = self.var(tk.BooleanVar, False)
        children = [self.var(tk.BooleanVar, v) for v in (True, False, True)]
        parent = ttk.Checkbutton(ex.demo, text='全选', variable=select_all)
        parent.pack(anchor='w')
        def sync_parent(*_):
            values = [v.get() for v in children]
            parent.state(['!alternate'])
            select_all.set(all(values))
            if any(values) and not all(values):
                parent.state(['alternate'])
        def toggle_all():
            target = select_all.get()
            for v in children:
                v.set(target)
        parent.configure(command=toggle_all)
        for text, v in zip(['选项 1', '选项 2', '选项 3'], children):
            ttk.Checkbutton(ex.demo, text=text, variable=v).pack(anchor='w', padx=(self.px(28), 0), pady=self.px(3))
            v.trace_add('write', sync_parent)
        sync_parent()
        ex = self.example(body, '单选按钮组', options=True, code='''
            choice = tk.StringVar(value='标准')
            for value in ('紧凑', '标准', '宽松'):
                ttk.Radiobutton(parent, text=value, value=value, variable=choice).pack(anchor='w')
        ''')
        choice = self.var(tk.StringVar, '标准')
        radios = []
        for text in ('紧凑', '标准', '宽松'):
            r = ttk.Radiobutton(ex.demo, text=text, value=text, variable=choice, command=lambda: self.status.set('选择：' + choice.get()))
            r.pack(anchor='w', pady=self.px(4))
            radios.append(r)
        ex.disable_option(radios)
        horizontal = self.var(tk.BooleanVar, False)
        def orient():
            for r in radios:
                r.pack_configure(side='left' if horizontal.get() else 'top', anchor='w', padx=(0, self.px(18)) if horizontal.get() else 0)
        ex.option(ttk.Checkbutton(ex.options, text='水平排列', variable=horizontal, command=orient))

    def page_switch(self, body):
        self.header(body, 'switch', ('FluentSwitch', "ttk.Checkbutton(style='Switch.TCheckbutton')"))
        ex = self.example(body, '带状态文字的开关', options=True, code='''
            wifi = tk.BooleanVar(value=True)
            ui.FluentSwitch(parent, variable=wifi, command=lambda: print(wifi.get()))
        ''')
        v = self.var(tk.BooleanVar, True)
        row = self.row(ex.demo, 0)
        s = ui.FluentSwitch(row, variable=v, command=lambda: self.status.set('WLAN ' + ('已开启' if v.get() else '已关闭')))
        s.pack(side='left')
        ttk.Label(row, text='WLAN').pack(side='left', padx=self.px(16))
        ex.disable_option([s])
        ex = self.example(body, '原生 ttk 写法', description='旧代码使用 Switch.TCheckbutton 样式即可获得同样的滑动动画。', code='''
            ttk.Checkbutton(parent, text='后台同步', style='Switch.TCheckbutton', variable=sync)
        ''')
        for text, on, disabled in [('开启通知', True, False), ('后台同步', False, False), ('禁用 · 开', True, True), ('禁用 · 关', False, True)]:
            ttk.Checkbutton(ex.demo, text=text, style='Switch.TCheckbutton', variable=self.var(tk.BooleanVar, on),
                            state='disabled' if disabled else 'normal').pack(anchor='w', pady=self.px(6))

    def page_slider(self, body):
        self.header(body, 'slider', ('FluentSlider', 'ttk.Scale', 'ValueSlider', 'ProgressSlider'))
        ex = self.example(body, '基本滑块', description='拖动直接跟手；方向键、Home / End 调整时平滑过渡。', options=True, code='''
            volume = tk.DoubleVar(value=35)
            ui.FluentSlider(parent, variable=volume, from_=0, to=100, width=260)
        ''')
        volume = self.var(tk.DoubleVar, 35)
        row = self.row(ex.demo, 0)
        slider = ui.FluentSlider(row, variable=volume, from_=0, to=100, width=self.px(280))
        slider.pack(side='left')
        label = ttk.Label(row, style='Demo.Value.TLabel', width=5)
        label.pack(side='left', padx=self.px(14))
        volume.trace_add('write', lambda *_: label.configure(text=f'{volume.get():.0f}'))
        label.configure(text='35')
        ex.disable_option([slider])
        step = self.var(tk.StringVar, '1')
        ex.option(ttk.Label(ex.options, text='步长'))
        combo = ex.option(ui.ThemedCombobox(ex.options, values=['1', '5', '10', '25'], textvariable=step, state='readonly', width=8))
        combo.bind('<<ComboboxSelected>>', lambda e: setattr(slider, 'step', float(step.get())))
        ex = self.example(body, '原生 ttk.Scale（水平与垂直）', code='''
            ttk.Scale(parent, from_=0, to=100, variable=value)
            ttk.Scale(parent, orient='vertical', from_=100, to=0, length=120)
        ''')
        row = self.row(ex.demo, 0)
        ttk.Scale(row, orient='vertical', from_=100, to=0, length=self.px(120), variable=self.var(tk.DoubleVar, 60)).pack(side='left', padx=(0, self.px(30)))
        right = ttk.Frame(row)
        right.pack(side='left', fill='x', expand=True)
        ttk.Scale(right, from_=0, to=100, variable=self.var(tk.DoubleVar, 40)).pack(fill='x', pady=self.px(10))
        ttk.Scale(right, from_=0, to=100, variable=self.var(tk.DoubleVar, 75), state='disabled').pack(fill='x', pady=self.px(10))
        ex = self.example(body, '滑块与数值框联动', code='''
            ui.ValueSlider(parent, variable=opacity, from_=0, to=100, step=1, unit='%')
        ''')
        ui.ValueSlider(ex.demo, variable=self.var(tk.DoubleVar, 80), from_=0, to=100, step=1, unit='%').pack(fill='x', pady=self.px(4))
        ui.ValueSlider(ex.demo, variable=self.var(tk.DoubleVar, 1.5), from_=0, to=5, step=.1, unit='秒').pack(fill='x', pady=self.px(8))

    def page_combo(self, body):
        self.header(body, 'combo', ('ThemedCombobox', 'ttk.Combobox', 'Dropdown', 'OptionMenu', 'MenuButton'))
        ex = self.example(body, '只读下拉框', description='当前选中项在原位置展开；方向键定位，输入首字母跳转，Enter 确认。', options=True, code='''
            combo = ui.ThemedCombobox(parent, values=fonts, state='readonly')
            combo.current(0)
            combo.bind('<<ComboboxSelected>>', lambda e: print(combo.get()))
        ''')
        combo = ui.ThemedCombobox(ex.demo, values=['Arial', 'Calibri', 'Consolas', 'Segoe UI', 'Microsoft YaHei UI', 'Times New Roman'],
                                  state='readonly', width=26)
        combo.current(3)
        combo.pack(anchor='w')
        combo.bind('<<ComboboxSelected>>', lambda e: self.status.set('字体：' + combo.get()))
        ex.disable_option([combo])
        ex = self.example(body, '可编辑下拉框', description='既可输入也可从列表选择；原生 ttk.Combobox 写法获得相同浮层。', code='''
            ttk.Combobox(parent, values=['8', '9', '10', '11', '12', '14'])   # 原生写法
        ''')
        row = self.row(ex.demo, 0)
        editable = ttk.Combobox(row, values=['8', '9', '10', '11', '12', '14', '16', '20', '24'], width=10)
        editable.set('11')
        editable.pack(side='left', padx=(0, self.px(14)))
        native = ttk.Combobox(row, values=['普通', '重要', '稍后处理'], state='readonly', width=16)
        native.current(1)
        native.pack(side='left')
        ex = self.example(body, '按钮式选择与菜单按钮', code='''
            ui.Dropdown(parent, ['最近一天', '最近一周', '最近一月'], variable=period)
            ui.OptionMenu(parent, level, '普通', '普通', '重要', '紧急')
        ''')
        row = self.row(ex.demo, 0)
        ui.Dropdown(row, ['最近一天', '最近一周', '最近一月', '全部时间'], variable=self.var(tk.StringVar, '最近一周'),
                    command=lambda v: self.status.set('范围：' + v)).pack(side='left', padx=(0, self.px(12)))
        ui.OptionMenu(row, self.var(tk.StringVar), '普通', '普通', '重要', '紧急',
                      command=lambda v: self.status.set('级别：' + v)).pack(side='left', padx=(0, self.px(12)))
        more = ui.MenuButton(row, text='更多操作')
        more['menu'] = self.make_menu(more)
        more.pack(side='left')

    # text ------------------------------------------------------------------
    def page_entry(self, body):
        self.header(body, 'entry', ('ttk.Entry', 'PlaceholderEntry', 'set_placeholder', 'ttk.Spinbox', 'ValidatedEntry'))
        ex = self.example(body, '单行文本框', options=True, code='''
            name = tk.StringVar(value='项目资料')
            ttk.Entry(parent, textvariable=name)
            ttk.Entry(parent, show='●')            # 密码
            entry.state(['invalid'])                # 错误状态
        ''')
        fields = []
        for label, text, kwargs, state in [('普通输入', '项目资料 / Project notes', {}, None), ('密码', 'tkwin11', {'show': '●'}, None),
                                          ('错误状态', 'name@', {}, 'invalid'), ('只读（可选择复制）', '只读内容', {}, 'readonly')]:
            ttk.Label(ex.demo, text=label).pack(anchor='w', pady=(self.px(6), self.px(4)))
            e = ttk.Entry(ex.demo, width=36, **kwargs)
            e.insert(0, text)
            if state:
                e.state([state])
            e.pack(anchor='w')
            fields.append(e)
        ex.disable_option(fields[:2])
        ex = self.example(body, '输入提示（占位文字）', options=True,
                          description='框内为空时显示灰色提示，开始输入即消失；聚焦后仍显示到第一次输入为止。提示不是内容：get() 与 textvariable 始终是真实文字。', code='''
            ui.PlaceholderEntry(parent, placeholder='请输入用户名')

            # 已有控件（包括旧代码里的 ttk.Entry / Combobox / Spinbox / tk.Entry）加一行即可
            ui.set_placeholder(entry, '搜索')
            ui.set_placeholder(combo, '请选择…')        # 只读下拉框未选择时
        ''')
        user = self.var(tk.StringVar)
        hinted = [ui.PlaceholderEntry(ex.demo, placeholder='请输入用户名', textvariable=user, width=36),
                  ui.PlaceholderEntry(ex.demo, placeholder='密码（至少 8 位）', show='●', width=36)]
        level = ui.ThemedCombobox(ex.demo, values=['普通', '重要', '紧急'], state='readonly', width=34)
        ui.set_placeholder(level, '请选择优先级…')
        size = ttk.Combobox(ex.demo, values=['8', '10', '12', '14'], width=34)
        ui.set_placeholder(size, '输入或选择字号')
        for widget in (*hinted, level, size):
            widget.pack(anchor='w', pady=self.px(5))
        ex.disable_option([*hinted, level, size])
        ex.option(ttk.Button(ex.options, text='读取 get()',
                             command=lambda: self.status.set(f'用户名 get() = {hinted[0].get()!r} · textvariable = {user.get()!r} · 优先级 = {level.get()!r}')))
        ex = self.example(body, '数字框', description='超出范围或非数字时，失去焦点自动恢复为最近的有效值。', code='''
            ttk.Spinbox(parent, from_=1, to=100, textvariable=count)
        ''')
        row = self.row(ex.demo, 0)
        ttk.Spinbox(row, from_=1, to=100, textvariable=self.var(tk.IntVar, 12), width=10).pack(side='left', padx=(0, self.px(14)))
        ttk.Spinbox(row, from_=0, to=1, increment=.05, format='%.2f', width=10).pack(side='left')
        ex = self.example(body, '输入校验', description='必填、整数范围与邮箱格式；失去焦点或回车时显示提示。', code='''
            field = ui.ValidatedEntry(parent, label='处理数量', kind='integer', minimum=1, maximum=100)
            if field.validate():
                print(field.get_value())
        ''')
        fields = []
        for label, kind, initial, options in [('任务名称', 'text', '', {'required': True}), ('处理数量', 'integer', '10', {'minimum': 1, 'maximum': 100}),
                                              ('联系邮箱', 'email', 'demo@example.com', {})]:
            f = ui.ValidatedEntry(ex.demo, label=label, kind=kind, **options)
            f.set(initial)
            f.pack(fill='x', pady=self.px(4))
            fields.append(f)
        ttk.Button(ex.demo, text='校验全部', style='Primary.TButton',
                   command=lambda: ui.notify(self, '校验通过' if all([f.validate() for f in fields]) else '请检查标红的输入项',
                                             kind='success' if all(f.validate() for f in fields) else 'warning')).pack(anchor='w', pady=(self.px(6), 0))

    def page_richtext(self, body):
        self.header(body, 'richtext', ('RoundedText', 'set_readonly', 'tk.Text', 'KeyChord'))
        ex = self.example(body, '多行文本', description='保留 tk.Text 全部接口：标签、撤销、选择与滚动。', options=True, code='''
            editor = ui.RoundedText(parent, height=8, wrap='word', undo=True)
            ui.set_readonly(editor, True)      # 只读但可选择、复制
        ''')
        editor = ui.RoundedText(ex.demo, height=7, wrap='word', undo=True)
        editor.pack(fill='x')
        editor.insert('1.0', '这是一段可编辑的多行文本。\n\n观察圆角边框、内边距、焦点下划线以及文字选择。可直接输入，按 Ctrl+Z 撤销。')
        mode = self.var(tk.StringVar, '编辑')
        def apply_mode():
            editor.configure(state='normal')
            ui.set_readonly(editor, mode.get() == '只读')
            if mode.get() == '禁用':
                editor.configure(state='disabled')
            self.status.set('文本模式：' + mode.get())
        for text in ('编辑', '只读', '禁用'):
            ex.option(ttk.Radiobutton(ex.options, text=text, value=text, variable=mode, command=apply_mode))
        ex = self.example(body, '原生 tk.Text 自动适配', description='旧代码中的 tk.Text / tk.Entry 会自动获得圆角外框和焦点反馈。', code='''
            tk.Text(parent, height=4)     # 无需修改
        ''')
        t = tk.Text(ex.demo, height=3, wrap='word')
        t.insert('1.0', '这是原生 tk.Text。')
        t.pack(fill='x')
        ex = self.example(body, '快捷键块', code='''
            ui.KeyChord(parent, 'Ctrl+Shift+S', command=lambda value: print(value))
        ''')
        ui.KeyChord(ex.demo, 'Ctrl+Shift+S', command=lambda value: self.status.set('快捷键：' + value)).pack(anchor='w')

    # collections -----------------------------------------------------------
    def page_listview(self, body):
        self.header(body, 'listview', ('RoundedListbox', 'tk.Listbox'))
        ex = self.example(body, '列表', description='悬停高亮、Ctrl / Shift 多选，保留原生 Listbox 接口。', options=True, code='''
            lst = ui.RoundedListbox(parent, height=7, selectmode='extended')
            for name in items:
                lst.insert('end', name)
        ''')
        lst = ui.RoundedListbox(ex.demo, height=7, selectmode='extended')
        lst.pack(fill='x')
        for label in ['全部项目', '最近使用', '已收藏', '待处理', '已完成', '已归档', '回收站', '共享给我', '离线可用']:
            lst.insert('end', label)
        lst.selection_set(2)
        lst.bind('<<ListboxSelect>>', lambda e: self.status.set('选中：' + '、'.join(lst.get(i) for i in lst.curselection())))
        ex.disable_option([lst])
        ex = self.example(body, '原生 tk.Listbox', code='''
            tk.Listbox(parent, height=4)    # 无需修改
        ''')
        native = tk.Listbox(ex.demo, height=4)
        for label in ['北京', '上海', '广州', '深圳', '杭州']:
            native.insert('end', label)
        native.pack(fill='x')

    def page_treeview(self, body):
        self.header(body, 'treeview', ('ttk.Treeview', 'SortableTreeview', 'configure_table', 'AutoScrollbar'))
        ex = self.example(body, '树形列表', code='''
            tree = ttk.Treeview(parent, show='tree')
            node = tree.insert('', 'end', text='工作空间', open=True)
            tree.insert(node, 'end', text='文档')
        ''')
        area = ttk.Frame(ex.demo)
        area.pack(fill='x')
        area.columnconfigure(0, weight=1)
        tree = ttk.Treeview(area, height=8, show='tree', selectmode='browse')
        tree.grid(row=0, column=0, sticky='nsew')
        bar = ui.AutoScrollbar(area, command=tree.yview)
        bar.grid(row=0, column=1, sticky='ns')
        tree.configure(yscrollcommand=bar.set)
        for title in ['工作空间', '个人收藏', '共享']:
            item = tree.insert('', 'end', text=title, open=title == '工作空间')
            for name in ['文档', '图片', '归档']:
                child = tree.insert(item, 'end', text=name)
                for i in range(2):
                    tree.insert(child, 'end', text=f'示例文件 {i + 1}')
        ex = self.example(body, '多列列表', description='点击表头排序，Ctrl / Shift 多选；列对齐分别由 column 与 heading 的 anchor 指定。', code='''
            tree = ui.SortableTreeview(parent, columns=('name', 'count'), show='headings')
            tree.heading('name', text='名称', anchor='w')
            ui.configure_table(tree)
        ''')
        area = ttk.Frame(ex.demo)
        area.pack(fill='x')
        area.columnconfigure(0, weight=1)
        table = ui.SortableTreeview(area, columns=('name', 'count', 'state', 'date'), show='headings', height=7, selectmode='extended')
        for key, title, width, anchor in [('name', '名称', 300, 'w'), ('count', '数量', 100, 'e'), ('state', '状态', 110, 'center'), ('date', '更新日期', 140, 'center')]:
            table.heading(key, text=title, anchor=anchor)
            table.column(key, width=self.px(width), minwidth=self.px(70), anchor=anchor)
        for i in range(24):
            table.insert('', 'end', values=(f'{i + 1:02d}  项目资料 / 示例条目', [2, 10, 3, 27][i % 4], ['已完成', '待处理', '进行中'][i % 3], f'2026-10-{i % 28 + 1:02d}'))
        table.grid(row=0, column=0, sticky='nsew')
        vbar = ttk.Scrollbar(area, command=table.yview)
        vbar.grid(row=0, column=1, sticky='ns')
        table.configure(yscrollcommand=vbar.set)
        ui.configure_table(table)

    def page_datagrid(self, body):
        self.header(body, 'datagrid', ('DataTable',))
        ex = self.example(body, '数据表格', description='排序作用于全部筛选结果再分页；右键表头可排序、移动或隐藏列；翻页保留选择。', code='''
            table = ui.DataTable(parent, columns=[{'key': 'name', 'text': '文件名称', 'width': 260}, ...],
                                 rows=rows, page_size=10)
            table.export_csv(scope='filtered')
        ''')
        table = ui.DataTable(ex.demo, columns=[{'key': 'name', 'text': '文件名称', 'width': 260}, {'key': 'count', 'text': '数量', 'width': 90},
                                               {'key': 'state', 'text': '状态', 'width': 120}, {'key': 'group', 'text': '分组', 'width': 140}],
                             rows=[[f'资料_{i + 1:03d}.csv', [2, 10, 30, 5][i % 4], ['待处理', '已完成', '处理中'][i % 3], ['工作', '个人'][i % 2]] for i in range(87)],
                             page_size=10, height=10)
        table.pack(fill='x')
        row = self.row(ex.demo, 8)
        ui.FluentButton(row, text='导出筛选结果', style='Primary.TButton', command=lambda: table.export_csv(scope='filtered')).pack(side='left', padx=(0, self.px(8)))
        ui.FluentButton(row, text='恢复列布局', command=table.reset_layout).pack(side='left')

    def page_spreadsheet(self, body):
        self.header(body, 'spreadsheet', ('Spreadsheet',))
        ex = self.example(body, '可编辑表格', description='单击选择、拖动或 Shift 框选、Ctrl 追加；双击 / F2 编辑；可与 Excel 互相复制粘贴。', code='''
            sheet = ui.Spreadsheet(parent, data=[['项目', '数量'], ['资料整理', '12']], rows=24, columns=8)
            sheet.undo(); sheet.redo()
        ''')
        data = [['项目', '数量', '单价', '备注'], ['资料整理', '12', '25.50', '双击编辑'], ['图片归档', '8', '10.00', 'Ctrl+C / Ctrl+V'],
                ['数据校对', '20', '8.50', 'Shift 选择矩形区域'], ['文献检索', '6', '18.00', 'Ctrl+单击追加']]
        actions = self.row(ex.demo, 0)
        sheet = ui.Spreadsheet(ex.demo, data=data, rows=24, columns=8, height=self.px(380))
        sheet.pack(fill='x', pady=(self.px(10), 0))
        sheet.pack_propagate(False)
        for text, command, primary in [('复制', lambda: sheet._shortcut(sheet.copy), False), ('粘贴', lambda: sheet._shortcut(sheet.paste), True),
                                       ('撤销', sheet.undo, False), ('重做', sheet.redo, False), ('清空选区', sheet.clear_selection, False)]:
            ui.FluentButton(actions, text=text, command=command, style='Primary.TButton' if primary else 'TButton').pack(side='left', padx=(0, self.px(8)))

    def page_cardlist(self, body):
        self.header(body, 'cardlist', ('CardList',))
        ex = self.example(body, '卡片列表', description='单一 Canvas 绘制全部行；上下键切换行，左右键选择操作，Enter 执行。', options=True, code='''
            cards = ui.CardList(parent, on_action=lambda key, action, x, y: print(key, action))
            cards.set_rows(rows, active_id='0', density='标准')
        ''')
        rows = [dict(id=str(i), name=name, detail='本地演示数据 · 点击右侧图标执行操作', tag=tag, mark=name[0], color=color)
                for i, (name, tag, color) in enumerate([('项目资料', '工作', '#0067C0'), ('个人收藏', '个人', '#159576'), ('图片归档', '归档', '#B77717'),
                                                        ('数据校对', '工作', '#D54B58'), ('文献检索', '研究', '#197FA8'), ('会议纪要', '工作', '#657080')])]
        cards = ui.CardList(ex.demo, lambda key, action, x, y: (cards.set_active(key) if action == 'use' else None, self.status.set(f'卡片 {key}：{action}')),
                            height=self.px(300))
        cards.pack(fill='x')
        cards.pack_propagate(False)
        cards.set_rows(rows, '0')
        density = self.var(tk.StringVar, '标准')
        ex.option(ttk.Label(ex.options, text='行密度'))
        for text in ('紧凑', '标准', '宽松'):
            ex.option(ttk.Radiobutton(ex.options, text=text, value=text, variable=density,
                                      command=lambda: cards.set_rows(rows, cards.active_id, density=density.get())))

    # date & time -----------------------------------------------------------
    def page_date(self, body):
        self.header(body, 'date', ('DateEntry', 'CalendarPopup'))
        ex = self.example(body, '日期选择', description='可直接输入 2026-10-18，或点击日历按钮；日历支持月 / 年 / 十年三级视图。', options=True, code='''
            entry = ui.DateEntry(parent, value=date.today(), command=lambda value: print(value))
            entry.get_date()
        ''')
        entry = ui.DateEntry(ex.demo, value=date.today(), command=lambda value: self.status.set(f'日期：{value}'))
        entry.pack(anchor='w', fill='x')
        ex.disable_option([entry.entry, entry.button])
        ex = self.example(body, '日期范围与可空', code='''
            ui.DateEntry(parent, minimum=date(2026, 1, 1), maximum=date(2026, 12, 31))   # 默认为空
        ''')
        ttk.Label(ex.demo, text='仅限 2026 年，可留空').pack(anchor='w', pady=(0, self.px(6)))
        ui.DateEntry(ex.demo, minimum=date(2026, 1, 1), maximum=date(2026, 12, 31)).pack(anchor='w', fill='x')

    # dialogs & flyouts -----------------------------------------------------
    def page_dialog(self, body):
        self.header(body, 'dialog', ('Modal', 'Dialogs.info', 'Dialogs.confirm', 'Dialogs.ask_string'))
        ex = self.example(body, '自定义对话框', description='遮罩淡入；Esc 关闭；Tab 在对话框内循环。', code='''
            dialog = ui.Modal(root, '编辑项目', width=480, height=380)
            ttk.Entry(dialog.body).pack(fill='x')
            dialog.primary.configure(text='保存', command=dialog.close)
            dialog.secondary.pack(side='right', padx=8)
        ''')
        ui.FluentButton(ex.demo, text='打开对话框', style='Primary.TButton', command=self.open_modal).pack(anchor='w')
        ex = self.example(body, '常用对话框', description='阻塞式调用，直接返回结果。', code='''
            if ui.Dialogs.confirm(root, '确认删除这 3 个文件吗？', danger=True):
                ...
            name = ui.Dialogs.ask_string(root, '请输入名称', initial='我的项目')
            count = ui.Dialogs.ask_integer(root, '输入 1–100 的整数', minimum=1, maximum=100)
        ''')
        row = self.row(ex.demo, 0)
        result = self.var(tk.StringVar, '结果会显示在这里')
        D = ui.Dialogs
        for text, command in [('提示', lambda: D.info(self, '这是一条提示信息。')),
                              ('确认', lambda: D.confirm(self, '确认执行这项演示操作吗？')),
                              ('危险确认', lambda: D.confirm(self, '确认删除这 3 个文件吗？此操作无法撤销。', danger=True)),
                              ('输入文本', lambda: D.ask_string(self, '请输入名称', initial='我的项目', title='重命名')),
                              ('输入整数', lambda: D.ask_integer(self, '输入 1–100 的整数', initial=10, minimum=1, maximum=100)),
                              ('错误', lambda: D.error(self, '这是一个演示错误提示。'))]:
            ttk.Button(row, text=text, command=lambda c=command, t=text: result.set(f'{t} → {c()!r}')).pack(side='left', padx=(0, self.px(8)))
        ttk.Label(ex.demo, textvariable=result, style='Muted.TLabel').pack(anchor='w', pady=(self.px(12), 0))

    def open_modal(self):
        existing = getattr(self, 'dialog', None)
        if existing is not None and existing.winfo_exists():
            existing.lift()
            return
        dialog = self.dialog = ui.Modal(self, '编辑项目', width=480, height=390)
        dialog.secondary.pack(side='right', padx=self.px(8))
        ttk.Label(dialog.body, text='项目名称').pack(anchor='w', pady=(0, self.px(5)))
        ttk.Entry(dialog.body, textvariable=self.var(tk.StringVar, '示例项目', master=dialog)).pack(fill='x')
        ttk.Label(dialog.body, text='优先级').pack(anchor='w', pady=(self.px(12), self.px(5)))
        combo = ui.ThemedCombobox(dialog.body, values=['普通', '重要', '紧急'], state='readonly')
        combo.current(1)
        combo.pack(fill='x')
        ttk.Checkbutton(dialog.body, text='保存后保留当前窗口设置', variable=self.var(tk.BooleanVar, True, master=dialog)).pack(anchor='w', pady=self.px(14))
        dialog.primary.configure(text='保存', command=lambda: (self.status.set('表单已保存（演示）'), dialog.close()))

    def page_flyout(self, body):
        self.header(body, 'flyout', ('FormFlyout',))
        ex = self.example(body, '表单浮层', description='附着在触发按钮旁，点击外侧或按 Esc 关闭；内部下拉框与浮层协同。', code='''
            flyout = ui.FormFlyout(button)
            ttk.Entry(flyout.body).pack(fill='x')
            flyout.show()
        ''')
        anchor = ttk.Button(ex.demo, text='新建配置')
        anchor.configure(command=lambda: self.open_flyout(anchor))
        anchor.pack(anchor='w')

    def open_flyout(self, anchor):
        flyout = ui.FormFlyout(anchor)
        ttk.Label(flyout.body, text='新建配置', style='Strong.TLabel').pack(anchor='w', pady=(0, self.px(14)))
        name = tk.StringVar(flyout)
        ttk.Label(flyout.body, text='名称').pack(anchor='w', pady=(0, self.px(5)))
        ttk.Entry(flyout.body, textvariable=name).pack(fill='x')
        ttk.Label(flyout.body, text='复制自').pack(anchor='w', pady=(self.px(12), self.px(5)))
        source = ui.ThemedCombobox(flyout.body, values=['标准', '紧凑', '宽松'], state='readonly')
        source.current(0)
        source.pack(fill='x')
        def confirm():
            self.status.set(f'已创建配置：{name.get().strip()}（复制自 {source.get()}）')
            flyout.close()
        button = ttk.Button(flyout.body, text='确定', style='Primary.TButton', command=confirm)
        button.pack(anchor='e', pady=(self.px(16), 0))
        button.state(['disabled'])
        name.trace_add('write', lambda *_: button.state(['!disabled'] if name.get().strip() else ['disabled']))
        flyout.show()

    def make_menu(self, parent):
        menu = ui.ThemedMenu(parent, tearoff=False)
        menu.add_command(label='新建项目', image=ui.icon(self, 'edit', self.px(15)), compound='left', accelerator='Ctrl+N', command=self.say('新建项目'))
        menu.add_command(label='复制名称', accelerator='Ctrl+C', command=self.say('复制名称'))
        menu.add_separator()
        menu.add_checkbutton(label='显示已完成', variable=self.var(tk.BooleanVar, True))
        order = self.var(tk.StringVar, '名称')
        for value in ('名称', '日期', '大小'):
            menu.add_radiobutton(label='按' + value + '排序', variable=order, value=value)
        menu.add_separator()
        sub = ui.ThemedMenu(menu, tearoff=False)
        sub.add_command(label='导出 CSV', command=self.say('导出 CSV（演示）'))
        sub.add_command(label='导出 JSON', command=self.say('导出 JSON（演示）'))
        menu.add_cascade(label='导出为', menu=sub)
        menu.add_command(label='暂不可用', state='disabled')
        return menu

    def page_menu(self, body):
        self.header(body, 'menu', ('ThemedMenu', 'tk.Menu', 'bind_context_menu', 'MenuButton'))
        ex = self.example(body, '菜单浮层', description='图标、快捷键文字、勾选 / 单选项、分隔线、禁用项与级联子菜单；←/→ 展开返回，Esc 关闭。', code='''
            menu = ui.ThemedMenu(root, tearoff=False)
            menu.add_command(label='新建', accelerator='Ctrl+N', command=new)
            menu.add_cascade(label='导出为', menu=submenu)
            menu.tk_popup(x, y)
        ''')
        menu = self.make_menu(self)
        button = ttk.Button(ex.demo, text='打开菜单')
        button.configure(command=lambda: menu.tk_popup(button.winfo_rootx(), button.winfo_rooty() + button.winfo_height() + self.px(4)))
        button.pack(anchor='w')
        ex = self.example(body, '右键菜单', code='''
            ui.bind_context_menu(widget, menu)    # 右键、Shift+F10、菜单键
        ''')
        area = ttk.Label(ex.demo, text='在此处右键，或聚焦后按 Shift+F10', takefocus=True, anchor='center',
                         padding=self.px(28), style='Muted.TLabel')
        area.pack(fill='x')
        ui.bind_context_menu(area, menu)
        ex = self.example(body, '原生 tk.Menu 自动适配', description='旧代码中的 tk.Menu.tk_popup / post 自动使用同一浮层。', code='''
            m = tk.Menu(root, tearoff=False)
            m.add_command(label='刷新')
            m.tk_popup(event.x_root, event.y_root)
        ''')
        legacy = tk.Menu(self, tearoff=False)
        for label in ('刷新', '属性'):
            legacy.add_command(label=label, command=self.say('原生菜单：' + label))
        b2 = ttk.Button(ex.demo, text='原生 tk.Menu')
        b2.configure(command=lambda: legacy.tk_popup(b2.winfo_rootx(), b2.winfo_rooty() + b2.winfo_height() + self.px(4)))
        b2.pack(anchor='w')

    def page_tooltip(self, body):
        self.header(body, 'tooltip', ('Tooltip',))
        ex = self.example(body, '工具提示', description='悬停 0.45 秒或键盘聚焦时出现；不抢焦点，不影响窗口激活。', code='''
            ui.Tooltip(widget, '保存当前文件 (Ctrl+S)')
            ui.Tooltip(widget, lambda: f'当前值：{value.get()}')   # 动态文本
        ''')
        row = self.row(ex.demo, 0)
        save = ttk.Button(row, text='保存', style='Primary.TButton')
        save.pack(side='left', padx=(0, self.px(10)))
        ui.Tooltip(save, '保存当前文件 (Ctrl+S)')
        long = ttk.Button(row, text='长文本提示')
        long.pack(side='left', padx=(0, self.px(10)))
        ui.Tooltip(long, '工具提示会自动换行。较长的说明文字不会超出屏幕，并在靠近屏幕边缘时自动调整位置。')
        counter = [0]
        dynamic = ttk.Button(row, text='动态提示', command=lambda: counter.__setitem__(0, counter[0] + 1))
        dynamic.pack(side='left')
        ui.Tooltip(dynamic, lambda: f'已点击 {counter[0]} 次')

    def page_toast(self, body):
        self.header(body, 'toast', ('notify', 'ToastNotification'))
        ex = self.example(body, '通知', description='不阻塞操作；多条按角落堆叠；悬停时暂停计时。', options=True, code='''
            ui.notify(root, '文件已保存', kind='success')
            ui.notify(root, '网络不稳定', kind='warning', title='请注意', position='top-right', duration=5000)
        ''')
        position = self.var(tk.StringVar, 'bottom-right')
        row = self.row(ex.demo, 0)
        for kind, text in [('success', '成功'), ('info', '信息'), ('warning', '警告'), ('danger', '失败')]:
            ttk.Button(row, text=text, style=kind.title() + '.Outline.TButton',
                       command=lambda k=kind, t=text: ui.notify(self, f'{t}：这是自动消失的通知。', kind=k, position=position.get())).pack(side='left', padx=(0, self.px(8)))
        ex.option(ttk.Label(ex.options, text='位置'))
        for value, text in [('bottom-right', '右下角'), ('top-right', '右上角')]:
            ex.option(ttk.Radiobutton(ex.options, text=text, value=value, variable=position))

    # layout ----------------------------------------------------------------
    def page_settings_card(self, body):
        self.header(body, 'settings_card', ('SettingsCard', 'ExpanderCard', 'Accordion', 'SettingRow'))
        ex = self.example(body, '设置卡片', description='图标、标题、说明与右侧操作区；窄窗口时操作区自动换到下方。', code='''
            card = ui.SettingsCard(parent, '自动保存', '退出时保存当前设置。', symbol='folder')
            ui.FluentSwitch(card.actions, variable=enabled).pack()
        ''')
        card = ui.SettingsCard(ex.demo, '自动保存', '退出时保存工作区名称、显示密度和此开关。', symbol='folder')
        card.pack(fill='x', pady=(0, self.px(4)))
        ui.FluentSwitch(card.actions, variable=self.var(tk.BooleanVar, True)).pack()
        card = ui.SettingsCard(ex.demo, '显示密度', '调整列表的行间距。', symbol='controls')
        card.pack(fill='x', pady=(0, self.px(4)))
        density = ui.ThemedCombobox(card.actions, values=['紧凑', '标准', '宽松'], state='readonly', width=12)
        density.current(1)
        density.pack()
        card = ui.SettingsCard(ex.demo, '关于本程序', '可点击的设置卡片（command）。', symbol='info', command=lambda: self.open('settings'))
        card.pack(fill='x')
        ttk.Label(card.actions, image=self.chevron(False)).pack()
        ex = self.example(body, '展开卡片', description='高度过渡可中断与反向；展开区可放入任意控件。', code='''
            card = ui.ExpanderCard(parent, '帧率限制', symbol='window', opened=True)
            ttk.Spinbox(card.body, from_=1, to=240).pack(side='right')
        ''')
        for index, (title, desc) in enumerate([('帧率限制', '限制最大刷新率以降低功耗'), ('自定义区域', '只处理窗口中的一部分')]):
            card = ui.ExpanderCard(ex.demo, title, desc, symbol='window', opened=index == 0)
            card.pack(fill='x', pady=(0, self.px(4)))
            ui.FluentSwitch(card.actions, variable=self.var(tk.BooleanVar, index == 0)).pack(side='left')
            ttk.Label(card.body, text='最大帧率' if index == 0 else '宽度 × 高度').pack(side='left')
            ttk.Spinbox(card.body, from_=1, to=240 if index == 0 else 9999, width=10).pack(side='right')
        ex = self.example(body, '折叠区与设置行', code='''
            acc = ui.Accordion(parent, '高级选项', opened=True)
            row = ui.SettingRow(acc.body, '自动保存', help_text='每次编辑后自动保存。')
        ''')
        accordion = ui.Accordion(ex.demo, '高级选项', opened=True, padding=self.px(12))
        accordion.pack(fill='x')
        setting = ui.SettingRow(accordion.body, '自动保存', '每次编辑后保存到本地。', help_text='悬停图标查看说明。')
        setting.pack(fill='x')
        ttk.Checkbutton(setting.action, style='Switch.TCheckbutton', variable=self.var(tk.BooleanVar, True)).pack()

    def page_tabs(self, body):
        self.header(body, 'tabs', ('ttk.Notebook',))
        ex = self.example(body, '标签页', description='Ctrl+Tab 切换，Home / End 跳到首尾；禁用的标签不可选。', options=True, code='''
            notebook = ttk.Notebook(parent)
            notebook.add(frame, text='基本')
            notebook.add(other, text='禁用', state='disabled')
        ''')
        notebook = ttk.Notebook(ex.demo)
        notebook.pack(fill='x')
        for text in ['基本', '高级', '网络', '禁用']:
            frame = ttk.Frame(notebook, padding=self.px(16))
            notebook.add(frame, text=text, state='disabled' if text == '禁用' else 'normal')
            ttk.Label(frame, text=f'{text}设置').pack(anchor='w', pady=(0, self.px(8)))
            ttk.Entry(frame).pack(fill='x', pady=self.px(4))
            ttk.Checkbutton(frame, text='启用当前选项', variable=self.var(tk.BooleanVar)).pack(anchor='w', pady=self.px(4))
        count = [4]
        def add_tab():
            count[0] += 1
            frame = ttk.Frame(notebook, padding=self.px(16))
            ttk.Label(frame, text=f'新标签 {count[0]} 的内容').pack(anchor='w')
            notebook.add(frame, text=f'标签 {count[0]}')
            notebook.select(frame)
        def close_tab():
            current = notebook.select()
            if current and len(notebook.tabs()) > 1:
                notebook.forget(current)
        ex.option(ttk.Button(ex.options, text='添加标签', command=add_tab))
        ex.option(ttk.Button(ex.options, text='关闭当前标签', command=close_tab))

    def page_split(self, body):
        self.header(body, 'split', ('ttk.Panedwindow',))
        ex = self.example(body, '水平分割', description='拖动中间分隔条，或聚焦后用方向键调整（Shift 精细）。', code='''
            paned = ttk.Panedwindow(parent, orient='horizontal')
            paned.add(left, weight=1); paned.add(right, weight=3)
        ''')
        paned = ttk.Panedwindow(ex.demo, orient='horizontal', height=self.px(180))
        paned.pack(fill='x')
        for text, weight in [('资源区域', 1), ('内容工作区', 3)]:
            frame = ttk.Frame(paned, padding=self.px(14))
            paned.add(frame, weight=weight)
            ttk.Label(frame, text=text, style='Strong.TLabel').pack(anchor='w')
            ttk.Label(frame, text='拖动分隔条调整宽度', style='Muted.TLabel').pack(anchor='w', pady=self.px(6))
        ex = self.example(body, '垂直分割', code='''
            ttk.Panedwindow(parent, orient='vertical')
        ''')
        vertical = ttk.Panedwindow(ex.demo, orient='vertical', height=self.px(180))
        vertical.pack(fill='x')
        for title in ['上方区域', '下方区域']:
            pane = ttk.Frame(vertical, padding=self.px(10))
            vertical.add(pane, weight=1)
            ttk.Label(pane, text=title).pack(anchor='w')

    def page_card(self, body):
        self.header(body, 'card', ('Card', 'SectionCard', 'ttk.LabelFrame', 'ttk.Separator', 'ttk.Sizegrip'))
        ex = self.example(body, '卡片', description='普通、选中与可点击卡片。', code='''
            ui.Card(parent, padding=16)
            ui.Card(parent, selected=True)
            ui.Card(parent, command=on_click)       # 悬停 / 按下反馈，Enter 与空格触发
        ''')
        row = self.row(ex.demo, 0)
        for column in range(3):
            row.columnconfigure(column, weight=1, uniform='card')
        for column, (title, kwargs) in enumerate([('普通卡片', {}), ('选中卡片', {'selected': True}), ('可点击卡片', {'command': self.say('点击了卡片')})]):
            card = ui.Card(row, padding=self.px(16), **kwargs)
            card.grid(row=0, column=column, sticky='nsew', padx=self.px(4))
            ttk.Label(card, text=title, style='Selected.Strong.TLabel' if kwargs.get('selected') else 'Strong.TLabel').pack(anchor='w')
            ttk.Label(card, text='卡片内容', style='Selected.Muted.TLabel' if kwargs.get('selected') else 'Muted.TLabel').pack(anchor='w', pady=(self.px(6), 0))
        ex = self.example(body, '分组框', code='''
            group = ui.SectionCard(parent, text='连接设置')
            ttk.LabelFrame(parent, text='原生写法')     # 自动统一为小圆角分组
        ''')
        group = ui.SectionCard(ex.demo, text='连接设置')
        group.pack(fill='x')
        ttk.Entry(group, textvariable=self.var(tk.StringVar, 'https://example.org')).pack(fill='x', pady=(0, self.px(8)))
        ttk.Checkbutton(group, text='启动时自动连接', variable=self.var(tk.BooleanVar, True)).pack(anchor='w')
        native = ttk.LabelFrame(ex.demo, text='原生 ttk.LabelFrame', padding=self.px(12))
        native.pack(fill='x', pady=(self.px(12), 0))
        ttk.Label(native, text='旧代码里的 LabelFrame 无需修改即可获得主题样式。').pack(anchor='w')
        ex = self.example(body, '分隔线与尺寸手柄', code='''
            ttk.Separator(parent).pack(fill='x')
            ttk.Separator(parent, orient='vertical').pack(side='left', fill='y')
            ttk.Sizegrip(parent).pack(side='right')
        ''')
        row = self.row(ex.demo, 0)
        ttk.Label(row, text='左侧').pack(side='left')
        ttk.Separator(row, orient='vertical').pack(side='left', fill='y', padx=self.px(16))
        ttk.Label(row, text='右侧').pack(side='left')
        ttk.Sizegrip(row).pack(side='right')
        ttk.Separator(ex.demo).pack(fill='x', pady=(self.px(12), 0))

    # navigation ------------------------------------------------------------
    def page_navview(self, body):
        self.header(body, 'navview', ('NavigationView',))
        ex = self.example(body, '层级导航', description='本程序的侧栏就是 NavigationView。分组可展开收起，指示条伸展过渡，方向键与 Home / End 导航。', code='''
            nav = ui.NavigationView(parent, command=show_page, width=260)
            nav.add('home', '主页', 'home')
            nav.add_group('docs', '文档', 'folder')
            nav.add('recent', '最近', 'timer', parent='docs')
            nav.add('settings', '设置', 'settings', bottom=True)
        ''')
        row = ttk.Frame(ex.demo, height=self.px(330))
        row.pack(fill='x')
        row.pack_propagate(False)
        content = self.var(tk.StringVar, '选择左侧项目')
        nav = ui.NavigationView(row, lambda key: content.set(f'当前页面：{key}'), width=240)
        nav.pack(side='left', fill='y')
        nav.add('home', '主页', 'home')
        nav.add_group('docs', '文档', 'folder')
        nav.add('recent', '最近', 'timer', parent='docs')
        nav.add('shared', '共享', 'layers', parent='docs')
        nav.section('工具')
        nav.add('search', '搜索', 'search')
        nav.add('settings', '设置', 'settings', bottom=True)
        nav.select('home', notify=True)
        ttk.Label(row, textvariable=content, style='Demo.Big.TLabel', padding=self.px(24)).pack(side='left', anchor='n')

    def page_sidebar(self, body):
        self.header(body, 'sidebar', ('Sidebar', 'SegmentedControl'))
        ex = self.example(body, '紧凑侧栏', options=True, code='''
            sidebar = ui.Sidebar(parent, [('all', '全部项目', 'library'), ('star', '我的收藏', 'star')], on_select)
            sidebar.set_collapsed(True)
        ''')
        row = ttk.Frame(ex.demo, height=self.px(190))
        row.pack(fill='x')
        row.pack_propagate(False)
        view = self.var(tk.StringVar, '全部项目')
        sidebar = ui.Sidebar(row, [('all', '全部项目', 'library'), ('star', '我的收藏', 'star'), ('settings', '设置', 'settings')],
                             lambda key: view.set({'all': '全部项目', 'star': '我的收藏', 'settings': '设置'}[key]), width=self.px(180))
        sidebar.pack(side='left', fill='y')
        sidebar.select('all', notify=False)
        ttk.Label(row, textvariable=view, style='Demo.Big.TLabel', padding=self.px(20)).pack(side='left', anchor='n')
        collapsed = self.var(tk.BooleanVar, False)
        def collapse():
            sidebar.set_collapsed(collapsed.get())
            sidebar.configure(width=self.px(64 if collapsed.get() else 180))
        ex.option(ttk.Checkbutton(ex.options, text='收起为图标', variable=collapsed, command=collapse))

    # status ----------------------------------------------------------------
    def page_progress(self, body):
        self.header(body, 'progress', ('ttk.Progressbar', 'TextProgress'))
        ex = self.example(body, '确定进度', options=True, code='''
            ttk.Progressbar(parent, variable=value, maximum=100)
        ''')
        value = self.var(tk.DoubleVar, 62)
        ttk.Progressbar(ex.demo, variable=value, maximum=100).pack(fill='x', pady=self.px(8))
        ui.TextProgress(ex.demo, variable=value, mask='已完成 {value:.0f} / {maximum}', maximum=100).pack(fill='x', pady=self.px(8))
        ex.option(ttk.Label(ex.options, text='进度值'))
        ex.option(ui.FluentSlider(ex.options, variable=value, from_=0, to=100, width=self.px(190)))
        ex = self.example(body, '不确定进度', code='''
            bar = ttk.Progressbar(parent, mode='indeterminate'); bar.start()
            ui.TextProgress(parent, mode='indeterminate', text='正在处理…').start()
        ''')
        loading = ttk.Progressbar(ex.demo, mode='indeterminate')
        loading.pack(fill='x', pady=self.px(8))
        text_loading = ui.TextProgress(ex.demo, mode='indeterminate', text='正在处理…', kind='primary')
        text_loading.pack(fill='x', pady=self.px(8))
        row = self.row(ex.demo, 4)
        ui.FluentButton(row, text='开始', style='Primary.TButton', command=lambda: (loading.start(), text_loading.start())).pack(side='left', padx=(0, self.px(8)))
        ui.FluentButton(row, text='停止', command=lambda: (loading.stop(), text_loading.stop())).pack(side='left')
        ex = self.example(body, '模拟任务', code='''
            def tick():
                bar['value'] += 5
                if bar['value'] < 100:
                    root.after(120, tick)
        ''')
        task = ttk.Progressbar(ex.demo, maximum=100)
        task.pack(fill='x', pady=self.px(8))
        button = ui.FluentButton(ex.demo, text='开始 3 秒任务', style='Primary.TButton')
        def run():
            button.state(['disabled'])
            task['value'] = 0
            def tick():
                task['value'] = float(task['value']) + 5
                self.status.set(f'任务进行中 · {int(task["value"])}%')
                if task['value'] < 100:
                    self.after_job(120, tick)
                else:
                    button.state(['!disabled'])
                    ui.notify(self, '演示任务已完成', kind='success')
            tick()
        button.configure(command=run)
        button.pack(anchor='w')

    def page_meter(self, body):
        self.header(body, 'meter', ('Meter', 'Badge'))
        ex = self.example(body, '仪表', description='圆环可拖动或用方向键调整；阈值决定颜色。', code='''
            ui.Meter(parent, variable=value, interactive=True, subtext='完成率',
                     thresholds=[(60, 'success'), (85, 'warning'), (100, 'danger')])
        ''')
        value = self.var(tk.DoubleVar, 65)
        thresholds = [(60, 'success'), (85, 'warning'), (100, 'danger')]
        row = self.row(ex.demo, 0)
        ui.Meter(row, variable=value, interactive=True, subtext='完成率', size=170, thresholds=thresholds).pack(side='left', padx=(0, self.px(30)))
        ui.Meter(row, variable=value, meter_type='semi', subtext='资源使用', size=170, thresholds=thresholds).pack(side='left')
        ui.ValueSlider(ex.demo, variable=value, unit='%').pack(fill='x', pady=(self.px(10), 0))
        ex = self.example(body, '状态徽章', code='''
            ui.Badge(parent, text='已完成', kind='success')
        ''')
        row = self.row(ex.demo, 0)
        for kind, text in [('success', '已完成'), ('warning', '待审核'), ('danger', '失败'), ('info', '进行中'), ('neutral', '草稿')]:
            ui.Badge(row, text=text, kind=kind).pack(side='left', padx=(0, self.px(8)))

    # charts ----------------------------------------------------------------
    def chart_clicked(self, data):
        name = data.get('series', data.get('name', ''))
        value = data.get('y', data.get('value', ''))
        self.status.set(f'图表点击：{name} · {data.get("label", "")} · {value}')

    def page_line(self, body):
        self.header(body, 'line', ('LineChart', 'ScatterChart'))
        ex = self.example(body, '折线图', description='悬停查看数值；滚轮缩放，拖动平移，双击重置；点击图例隐藏系列。', options=True, code='''
            chart = ui.LineChart(parent, series=[{'name': '本周', 'values': [12, 18, 14]}],
                                 labels=['周一', '周二', '周三'], on_click=print)
            chart.set_data([{'name': '本周', 'values': new_values}])
        ''')
        labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        line = ui.LineChart(ex.demo, series=[{'name': '本周', 'values': [12, 18, 14, 26, 23, 34, 29]},
                                             {'name': '上周', 'values': [8, 11, 15, 17, 19, 20, 24]}],
                            labels=labels, height=220, on_click=self.chart_clicked)
        line.pack(fill='x')
        counter = [0]
        def refresh():
            counter[0] += 1
            rng = random.Random(counter[0])
            line.set_data([{'name': '本周', 'values': [rng.randint(10, 36) for _ in labels]}, {'name': '上周', 'values': [8, 11, 15, 17, 19, 20, 24]}])
        ex.option(ttk.Button(ex.options, text='随机数据', style='Primary.TButton', command=refresh))
        ex.option(ttk.Button(ex.options, text='重置缩放', command=line.reset_view))
        ex = self.example(body, '散点图', code='''
            ui.ScatterChart(parent, series=[{'name': '观测 A', 'points': [(x, y), ...]}])
        ''')
        rng = random.Random(7)
        ui.ScatterChart(ex.demo, series=[{'name': '观测 A', 'points': [(round(rng.uniform(8, 80), 1), round(rng.gauss(45, 12), 1)) for _ in range(60)]},
                                         {'name': '观测 B', 'points': [(round(rng.uniform(25, 95), 1), round(rng.gauss(65, 10), 1)) for _ in range(60)]}],
                        height=220, on_click=self.chart_clicked).pack(fill='x')

    def page_bar(self, body):
        self.header(body, 'bar', ('ColumnChart', 'DonutChart', 'PieChart', 'BarChart'))
        ex = self.example(body, '分组柱状图', description='支持正负值；点击柱形触发回调。', code='''
            ui.ColumnChart(parent, series=[{'name': '流入', 'values': [12, 18]}, {'name': '流出', 'values': [-6, -9]}],
                           labels=['一月', '二月'])
        ''')
        ui.ColumnChart(ex.demo, series=[{'name': '流入', 'values': [12, 18, 15, 21, 24, 19]}, {'name': '流出', 'values': [-6, -9, -5, -8, -10, -7]}],
                       labels=['一月', '二月', '三月', '四月', '五月', '六月'], height=220, on_click=self.chart_clicked).pack(fill='x')
        ex = self.example(body, '饼图 / 环形图', options=True, code='''
            donut = ui.DonutChart(parent, data=[('已完成', 42), ('处理中', 18)])
            donut.set_hole(0)     # 变为饼图
        ''')
        donut = ui.DonutChart(ex.demo, data=[('已完成', 42), ('处理中', 18), ('待处理', 12), ('已取消', 5)], height=220, on_click=self.chart_clicked)
        donut.pack(fill='x')
        ex.option(ttk.Button(ex.options, text='切换饼图 / 环形', command=lambda: donut.set_hole(0 if donut.hole else .62)))
        ex = self.example(body, '简易柱状图', code='''
            ui.BarChart(parent, [12, 20, 16], ['周一', '周二', '周三'])
        ''')
        chart = ui.BarChart(ex.demo, [12, 20, 16, 28, 22], ['周一', '周二', '周三', '周四', '周五'])
        chart.canvas.configure(height=self.px(150))
        chart.pack(fill='x')

    # media -----------------------------------------------------------------
    def page_image(self, body):
        self.header(body, 'image', ('ImageViewer',))
        ex = self.example(body, '图片查看', description='滚轮缩放，拖动平移，双击适应窗口；“打开”可载入本地 PNG / GIF。', code='''
            viewer = ui.ImageViewer(parent, height=260)
            viewer.set_image(tk.PhotoImage(file='photo.png'))
        ''')
        viewer = ui.ImageViewer(ex.demo, height=260)
        viewer.pack(fill='x')
        image = tk.PhotoImage(master=self, width=720, height=260)
        image.put('#EAF3FF', to=(0, 0, 720, 260))
        for i, (color, box) in enumerate([('#0067C0', (40, 40, 210, 220)), ('#19A58B', (240, 90, 440, 220)), ('#E9A13B', (470, 130, 680, 220))]):
            image.put(color, to=box)
        image.put('#FFFFFF', to=(60, 60, 190, 80))
        viewer.set_image(image)

    def page_color(self, body):
        self.header(body, 'color', ('ColorPicker', 'ColorDialog'))
        ex = self.example(body, '颜色选择', code='''
            picker = ui.ColorPicker(parent, color='#0067C0', command=print)
            value = ui.ColorDialog(root, color=picker.get_color()).show_result()
        ''')
        swatch = tk.Frame(ex.demo, height=self.px(10), background='#0067C0')
        picker = ui.ColorPicker(ex.demo, command=lambda color: (swatch.configure(background=color), self.status.set('颜色：' + color)))
        picker.pack(fill='x')
        swatch.pack(fill='x', pady=self.px(8))
        def dialog():
            value = ui.ColorDialog(self, color=picker.get_color()).show_result()
            if value:
                picker.set_color(value)
        ttk.Button(ex.demo, text='以对话框选择颜色', command=dialog).pack(anchor='w')

    def page_font(self, body):
        self.header(body, 'font', ('FontPicker', 'FontDialog'))
        ex = self.example(body, '字体选择', code='''
            picker = ui.FontPicker(parent)
            font = ui.FontDialog(root).show_result()     # tkinter.font.Font 或 None
        ''')
        ui.FontPicker(ex.demo).pack(fill='x')
        def dialog():
            result = ui.FontDialog(self).show_result()
            if result:
                self._picked_font = result
                self.status.set('已选择字体：' + str(result.actual()))
        ttk.Button(ex.demo, text='以对话框选择字体', command=dialog).pack(anchor='w', pady=(self.px(10), 0))

    # window & system -------------------------------------------------------
    def page_titlebar(self, body):
        self.header(body, 'titlebar', ('FluentTitleBar', 'FluentWindowChrome'))
        ex = self.example(body, '一体化标题栏', description='保留真实任务栏窗口、系统菜单、边缘缩放、Win11 贴靠布局与最大化动画；本窗口顶部即为示例。', code='''
            window = tk.Toplevel(root)
            ui.FluentTitleBar(window, title='窗口操作示例').pack(fill='x')
        ''')
        ui.FluentButton(ex.demo, text='打开示例窗口', style='Primary.TButton', command=self.open_window).pack(anchor='w')

    def open_window(self):
        window = tk.Toplevel(self)
        window.title('窗口操作示例')
        window.geometry(f'{self.px(520)}x{self.px(320)}+{self.winfo_rootx() + self.px(80)}+{self.winfo_rooty() + self.px(90)}')
        bar = ui.FluentTitleBar(window, title='窗口操作示例')
        bar.pack(fill='x')
        area = ttk.Frame(window, padding=self.px(20))
        area.pack(fill='both', expand=True)
        ttk.Label(area, text='拖动标题栏移动；双击最大化；拖到屏幕顶部可贴靠。').pack(anchor='w')
        ttk.Entry(area).pack(fill='x', pady=self.px(12))
        ui.FluentButton(area, text='关闭', command=bar.request_close).pack(anchor='e')

    def page_dpi(self, body):
        self.header(body, 'dpi', ('enable_dpi_awareness', 'per-monitor DPI', 'motion_enabled'))
        ex = self.example(body, '当前显示器', description='把窗口拖到另一块不同缩放比例的显示器，字体、图片与尺寸会按该显示器重新适配。')
        info = self.var(tk.StringVar)
        ttk.Label(ex.demo, textvariable=info, justify='left').pack(anchor='w')
        def update_info():
            if not ex.winfo_exists():
                return
            if ex.winfo_viewable():
                resources = self._dpi_resources
                dpi = resources.window_dpi(self)
                lines = [f'窗口 DPI：{dpi}（{dpi / 96:.0%}）', f'程序基准 DPI：{resources.base_dpi}（启动所在显示器）',
                         f'已适配控件：{len(resources.widgets)}　样式副本：{len(resources.styles)}']
                monitor = monitor_info(self)
                if monitor:
                    lines.append(monitor)
                info.set('\n'.join(lines))
            self.after_job(800, update_info)
        update_info()
        ex = self.example(body, '弹窗性能自测', description='连续打开并关闭下拉浮层与菜单各 5 次，报告平均构建耗时（不含 83 ms 淡入）。在副屏上运行可验证修复效果。', code='''
            started = time.perf_counter()
            combo.controller.open()
            root.update_idletasks()
            elapsed = time.perf_counter() - started
        ''')
        row = self.row(ex.demo, 0)
        combo = ui.ThemedCombobox(row, values=[f'选项 {i}' for i in range(1, 9)], state='readonly', width=16)
        combo.current(0)
        combo.pack(side='left', padx=(0, self.px(12)))
        result = self.var(tk.StringVar, '尚未测试')
        def benchmark():
            timings = {'下拉浮层': [], '菜单': []}
            menu = self.make_menu(self)
            for _ in range(5):
                started = time.perf_counter()
                combo.controller.open()
                self.update_idletasks()
                timings['下拉浮层'].append(time.perf_counter() - started)
                combo.controller.popup.close(restore_focus=False)
                self.update()
                started = time.perf_counter()
                menu.tk_popup(combo.winfo_rootx(), combo.winfo_rooty() + combo.winfo_height())
                self.update_idletasks()
                timings['菜单'].append(time.perf_counter() - started)
                menu.popup.close(restore_focus=False)
                self.update()
            menu.destroy()
            dpi = self._dpi_resources.window_dpi(self)
            result.set('　'.join(f'{name} {statistics.median(values) * 1000:.0f} ms' for name, values in timings.items()) + f'　（DPI {dpi}）')
            self.status.set('性能自测完成：' + result.get())
        ui.FluentButton(row, text='运行自测', style='Primary.TButton', command=benchmark).pack(side='left')
        ttk.Label(ex.demo, textvariable=result, style='Demo.Value.TLabel').pack(anchor='w', pady=(self.px(12), 0))
        ex = self.example(body, '界面动画', description='开关、折叠、滑块与浮层过渡；同时遵循 Windows“动画效果”设置。', code='''
            root.motion_enabled = False      # 立即切换，不播放过渡
        ''')
        card = ui.SettingsCard(ex.demo, '启用界面动画', '关闭后所有过渡立即完成。', symbol='play')
        card.pack(fill='x')
        ui.FluentSwitch(card.actions, variable=self.motion).pack()

    def page_legacy(self, body):
        self.header(body, 'legacy', ('tkwin11.install', 'theme_classic', 'apply_theme'))
        ex = self.example(body, '一行代码替换旧程序外观', description='在旧程序创建 tk.Tk() 之前加一行。ttk 控件、tk.Entry / Text / Listbox、tk.Menu 浮层与经典 Button / Label / Frame 等都会换上 Win11 外观；'
                                                         '代码里显式设置的颜色（如 bg="red"）保持不变；之后调用 theme_use("clam") 也不会覆盖主题。', code='''
            import tkwin11; tkwin11.install()     # ← 唯一新增的一行

            import tkinter as tk
            from tkinter import ttk

            root = tk.Tk()
            tk.Label(root, text='经典 Label').pack()
            tk.Button(root, text='经典 Button').pack()
            ttk.Combobox(root, values=['A', 'B'], state='readonly').pack()
            root.mainloop()

            # 硬编码像素尺寸、依赖系统位图缩放的旧程序可用：tkwin11.install(dpi=False)
        ''')
        ui.FluentButton(ex.demo, text='打开“旧程序”示例窗口', style='Primary.TButton', command=self.open_legacy).pack(anchor='w')
        self.wrap(ttk.Label(ex.demo, text='示例窗口中全部使用未经修改的 tkinter / ttk 写法创建，没有任何 tkwin11 类。', style='Muted.TLabel',
                            justify='left')).pack(anchor='w', fill='x', pady=(self.px(10), 0))
        ex = self.example(body, '已有窗口直接换肤', description='程序已经创建了 Tk 窗口时，调用 apply_theme 与 theme_classic 即可。', code='''
            ui.enable_dpi_awareness()            # 可选，需在 Tk() 之前
            root = tk.Tk()
            ...                                  # 原有界面代码
            ui.apply_theme(root)
            ui.theme_classic(root)               # 经典 tk 控件
        ''')
        ttk.Label(ex.demo, text='已有 ttk 控件在下一次映射时自动接入；经典控件只修改仍为默认值的颜色选项。').pack(anchor='w')

    def open_legacy(self):
        window = tk.Toplevel(self)
        window.title('旧程序示例（未修改的 tkinter 代码）')
        window.geometry(f'+{self.winfo_rootx() + self.px(120)}+{self.winfo_rooty() + self.px(80)}')
        pad = dict(padx=self.px(14), pady=self.px(4))
        tk.Label(window, text='经典 tk.Label').pack(anchor='w', **pad)
        tk.Label(window, text='显式 bg="#FFF4CE" 保持不变', bg='#FFF4CE').pack(anchor='w', **pad)
        tk.Button(window, text='经典 tk.Button', command=self.say('经典按钮')).pack(anchor='w', **pad)
        tk.Checkbutton(window, text='经典 tk.Checkbutton').pack(anchor='w', **pad)
        tk.Radiobutton(window, text='经典 tk.Radiobutton', value=1).pack(anchor='w', **pad)
        tk.Scale(window, orient='horizontal', length=self.px(260)).pack(anchor='w', **pad)
        tk.Entry(window).pack(fill='x', **pad)
        group = tk.LabelFrame(window, text='tk.LabelFrame')
        group.pack(fill='x', **pad)
        ttk.Button(group, text='ttk.Button').pack(anchor='w', padx=self.px(10), pady=self.px(6))
        ttk.Combobox(group, values=['A', 'B', 'C'], state='readonly').pack(anchor='w', padx=self.px(10), pady=self.px(6))
        menu = tk.Menu(window, tearoff=False)
        for label in ('打开', '另存为', '退出'):
            menu.add_command(label=label, command=self.say('旧菜单：' + label))
        button = tk.Button(window, text='tk.Menu.tk_popup')
        button.configure(command=lambda: menu.tk_popup(button.winfo_rootx(), button.winfo_rooty() + button.winfo_height()))
        button.pack(anchor='w', **pad)
        tk.Label(window, text='').pack(pady=self.px(4))

    def page_settings(self, body):
        self.header(body, 'settings')
        ex = self.example(body, '外观与行为')
        card = ui.SettingsCard(ex.demo, '界面动画', '开关、折叠、滑块与浮层过渡；同时遵循系统设置。', symbol='play')
        card.pack(fill='x', pady=(0, self.px(4)))
        ui.FluentSwitch(card.actions, variable=self.motion).pack()
        card = ui.SettingsCard(ex.demo, '源代码视图字体', self.mono.actual('family'), symbol='code')
        card.pack(fill='x')
        ex = self.example(body, '关于')
        for title, text in [(f'TkWin11 {ui.__version__}', '基于 TkWebUI 的 Windows 11 / Fluent 风格分支，MIT 许可。'),
                            ('运行要求', f'Python {sys.version.split()[0]} · Tk {self.tk.call("info", "patchlevel")} · 仅需标准库'),
                            ('设计参考', 'WinUI 3 Gallery 的页面组织；并非 WinUI 3，Tk 无法提供 Mica / Acrylic 材质。')]:
            row = self.row(ex.demo, 4)
            ttk.Label(row, text=title, style='Strong.TLabel', width=14).pack(side='left', anchor='n')
            self.wrap(ttk.Label(row, text=text, style='Muted.TLabel', justify='left')).pack(side='left', fill='x', expand=True)


def monitor_info(window):
    if sys.platform != 'win32':
        return ''
    import ctypes
    from ctypes import wintypes as w
    class MonitorInfo(ctypes.Structure):
        _fields_ = [('cbSize', w.DWORD), ('rcMonitor', w.RECT), ('rcWork', w.RECT), ('dwFlags', w.DWORD)]
    user = ctypes.WinDLL('user32')     # private prototypes, never ctypes.windll
    user.MonitorFromWindow.argtypes = [w.HWND, w.DWORD]
    user.MonitorFromWindow.restype = w.HANDLE
    user.GetParent.argtypes = [w.HWND]
    user.GetParent.restype = w.HWND
    hwnd = user.GetParent(window.winfo_id()) or window.winfo_id()
    monitor = user.MonitorFromWindow(hwnd, 2)
    info = MonitorInfo()
    info.cbSize = ctypes.sizeof(info)
    if not user.GetMonitorInfoW(monitor, ctypes.byref(info)):
        return ''
    r = info.rcMonitor
    return f'显示器：{r.right - r.left}×{r.bottom - r.top}，位置 ({r.left}, {r.top})' + ('，主显示器' if info.dwFlags & 1 else '')


def main():
    parser = argparse.ArgumentParser(description='TkWin11 Gallery')
    parser.add_argument('--page', default='home', help='page key, e.g. button, menu, dpi')
    args = parser.parse_args()
    ui.enable_dpi_awareness()
    Demo(page=args.page).mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        (BASE / 'startup_error.log').write_text(traceback.format_exc(), encoding='utf-8')
        raise
