# WindowChrome 闪烁问题与窗口状态切换修复记录

更新日期：2026-11-08

## 当前方案

本方案是实验性的时序规避，默认关闭。`install(window_flicker_workaround=True)` 为之后创建的根窗口启用；其 Toplevel 自动继承。它不会给普通 Tk 窗口添加自定义标题栏，也不改变已创建根窗口的设置。

`WindowChrome`、`FluentWindowChrome` 和 `FluentTitleBar` 同样接受 `window_flicker_workaround`：`None`（默认）继承所属 Tk 根窗口设置，`True` / `False` 显式覆盖。不经过 `install()` 的程序可直接在创建这些组件时启用。

关闭时不创建位图控制器、不接管背景擦除，也不使用 1px inset、拖动时缓存/激活延迟；DWM frame、非客户区绘制和最大化路径保持上游 v0.2.2 行为。

正常最大化和最小化还原是两条不同的绘制路径，不共用静态层，也不再对正常最大化强制同步重绘。

### 正常窗口到最大化

保留原生 DWM 动画，在 `toggle_maximize()` 和原生 `SC_MAXIMIZE` 入口开启**全窗口 80ms 擦除保护**。保护只覆盖动画初期新暴露的客户区，随后通过同一个窗口计时器自动撤除，避免长期接管子窗口背景擦除。

当前组合：

- `begin_erase_guard(duration=80)`，范围为全窗口；
- DWM `MARGINS` 为 `(0,0,0,0)`，不保留顶部 1px frame；
- 不再执行 `update_idletasks() + RedrawWindow()` 抢画；
- `WM_NCCALCSIZE` 的最大化工作区处理保持不变。

原 PR 的真实 Gallery 实验报告，全窗口 80ms 保护改善了此前的黑闪；随后分别移除同步重绘和顶部 frame，未观察到效果回退。电池模式下仍可能短暂看到接近背景色的白板，不保证所有硬件上的效果。

长期全窗口擦除保护曾引起右侧频闪和还原回归。80ms 版本有效不代表可以恢复原来的 1000ms 全量接管。

### 最小化到普通或最大化状态

保留原生任务栏、DWM 还原动画和现有 Tk 控件。核心是由父窗口内部的静态子 HWND 提供动画期间的完整画面，等待真实 Tk 控件在窗口重新可见后完成绘制。

流程：

1. `minimize()` 或原生 `SC_MINIMIZE` 入口，使用屏幕 `BitBlt` 保存客户区画面。复制前后检查目标可见、未最小化、在虚拟桌面范围内，且 Z 序上方没有与截图区域相交的可见窗口；被遮挡或检查失败时不创建位图，退回原生还原。透明遮挡也保守地跳过，不猜测其像素内容。
2. 有有效截图、iconic 状态下收到 `SC_RESTORE` 时，窗口过程只设置请求标志，不直接调用 Tk。
3. `poll_native()` 在 Tk 主线程调用精简后的 `prepare_restore()`，只执行 `ShowWindow(SW_RESTORE)` 或 `ShowWindow(SW_MAXIMIZE)`。
4. `Static` 子 HWND 显示保存的位图，跟随父窗口参与 DWM 动画，不是独立置顶覆盖窗口。
5. 还原后保留静态层 350ms；交接时先 `DwmFlush()`，再销毁子 HWND 并释放 DC 和位图。
6. `withdraw()` 不捕获截图；隐藏时立即移除覆盖层，Tk 主线程随后取消定时任务并释放位图。恢复交接不再依赖轮询是否观察到过 iconic 状态。
7. 交接期间再次最小化时放弃旧位图，该次退回原生还原。窗口 wrapper 被替换、主动切换最大化和 `detach()` 同样清理资源；还原客户区尺寸与截图不同时不显示旧图。

这是一种保守回退，不是遮挡窗口的离屏渲染。屏幕截图与窗口移动并非原子操作；复制前后的检查缩小了竞争窗口，但不能保证所有并发桌面变化。没有采用同步 [PrintWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-printwindow)，因为该调用发送绘制消息，而原生回调路径不应重入 Tk/Tcl。

相关文件：

- `tkwin11/window_chrome.py`：原生状态桥接、80ms 擦除保护和还原入口。
- `tkwin11/restore_animation.py`：截图、静态子 HWND、350ms 交接和资源释放。
- `tests/check_window_chrome.py`：普通还原、快速状态和最大化状态回归。

## iconic 预绘制对比结论

以下连续帧数据为原 PR 的历史实验记录，本次修改没有重新测量这些时间。

此前 `prepare_restore()` 还在 `ShowWindow` 前执行 `SetWindowPos + update_idletasks + RedrawWindow`，并将其描述为“预绘制”。真实 Gallery 的三组隔离实验推翻了这一描述：

- 完整版本：保留上述三个调用；
- `no-redraw`：去掉 `RedrawWindow`；
- `show-only`：只执行 `ShowWindow`。

三组均固定使用同一个 350ms 静态层。结果：

- `ShowWindow` 前所有 Tk 控件的 `winfo_ismapped()` 都为 0；
- 对 359 个原生窗口的观察中，三组 iconic 阶段均为 0 次 `WM_PAINT`；
- 三组都在 `ShowWindow` 后出现 188 次绘制事件，真实绘制约在 245–255ms 完成；
- 静态层约 358–363ms 交接，覆盖了真实绘制窗口期；
- 三种版本的交接前截图彼此完全相同，交接后截图也彼此完全相同，SHA-256 一致。

因此，iconic 中的 `RedrawWindow` 没有实际绘制效果；本轮实验中提前设置尺寸和处理 idle 也没有可观察收益。这些冗余调用以及不再使用的 `_restore_work_area` 已删除。静态层不是预绘制的替代品之外的可选优化，而是当前还原方案稳定视觉的主要保障。

实验数据保存在 `perf/results/restore-predraw-full/`、`restore-predraw-no-redraw/`、`restore-predraw-show-only/`。这些结果来自当前 Tk/Windows 环境，不外推为所有 Tk 版本的源码级结论。

## 最大化截图的黑边问题

最大化还原曾出现左侧和顶部黑边，随后跳到正确画面。根因不是目标位置延迟，而是截图把最大化窗口的不可见边框也包含进去了。

同一时刻实测：

- `GetWindowRect`：`(-9,-9,1929,1149)`，包含不可见调整边框；
- DWM extended frame bounds：`(0,0,1920,1140)`，为实际可见工作区；
- 旧截图左侧前 9 列和顶部前 9 行为纯黑，静态层把这些屏幕外像素显示到了窗口内部。

原 PR 在 `IsZoomed(hwnd)` 为真时，改用 `DwmGetWindowAttribute(..., DWMWA_EXTENDED_FRAME_BOUNDS, ...)`。当前版本统一使用 `GetClientRect + ClientToScreen` 定位自定义标题栏窗口的客户区，与原生子覆盖层的 `(0, 0)` 对齐；不再截图不可见窗口边框。多显示器和不同 DPI 下不能假定不可见边框固定为 9px。

## 正常最大化诊断摘要

早期探针记录了 `WM_ERASEBKGND`、`WM_PAINT`、wrapper surface 和屏幕采样：

- 1418 次背景擦除涉及的 HWND，其类背景刷 `hbrBackground` 都为 0，黑块不是默认黑色刷子填出的；
- 修复前 wrapper 采样已出现黑色区域，而内容区、toolbar 和搜索框首绘明显更晚；
- 一轮 `update_idletasks() + RedrawWindow()` 曾将关键控件首绘提前到约 32–50ms，减少黑闪范围和时间，但不能消除顶部细条；
- 第二轮 idle 没有收益；
- 在当时没有全窗口 80ms 保护的组合下，`top=1` 优于 `top=0` 和 `top=2`；加入 80ms 保护后，用户复测移除同步重绘和顶部 frame 均不影响最终效果，因此二者均已删除；
- `WM_NCPAINT` 只在最大化初期到达一次，测试色补画未在最终合成采样中出现；
- `DWMWA_BORDER_COLOR` 调用成功，但测试色未命中顶部采样区域。

连续帧和绘制数据保存在 `perf/results/maximize-diagnostic/`、`maximize-sync/`、`maximize-timeline/`。采样本身有开销，不能把采样时刻当作无扰动的 DWM 每帧时序。

## 保留的拖动兼容性处理

- 手动拖动期间，`WM_NCCALCSIZE` 使用 `rect.bottom -= 1`，规避 DWM 原生子窗口缩放瑕疵。
- 拖动期间推迟 `refresh_cache()`，退出拖动后统一刷新。
- Fluent 标题激活颜色动画在 `_native_moving` 期间暂停，结束后同步。
- `gallery.py` 没有为这些窗口状态修复而修改。

## 不要重复的失败方案

以下方案已经实测失败或引入回归，不能因编译、自动测试通过就重新保留：

- `WVR_REDRAW`、`WVR_VALIDRECTS`、`SWP_NOCOPYBITS`。
- `WS_CLIPCHILDREN`，包括后补样式并调用 `SWP_FRAMECHANGED`。
- DWM 垂直刷新时序同步和 `DCompositionWaitForCompositorClock` 类计时补丁。
- `ShowWindow` 与过渡计数挂起。
- 临时切换原生标题栏，动画结束后再切回。
- 禁用 DWM 动画、冻结文字或整个子窗口树。
- 长期全窗口擦除保护、第二轮 idle、正常最大化后的强制同步重绘。
- 最大化前 cloak、目标尺寸预布局后缩回；同步 Tk 原生重入曾触发 GIL fatal error。
- 独立置顶 BitBlt 覆盖窗口；当前有效的是父窗口内部静态子 HWND。
- DirectComposition 原型：具体实现未通过 Gallery 黑闪目测。
- 在还原期间忽略左侧子菜单高度回写：未通过并已撤回。
- 依靠 iconic 中的 `RedrawWindow` 代替静态层：实测没有发生预绘制。

## 验证与维护边界

标准检查：

```bash
python -m compileall -q tkwin11 gallery.py tests/check_window_chrome.py
python -m unittest discover -s tests -p "test_*.py"
python tests/check_window_chrome.py
git diff --check
```

WindowChrome 与 FluentWindowChrome 的 normal、destroy、single、override、before_attach 在开关关闭/开启两种状态下共 20 组测试必须全部通过。`test_window_flicker_workaround.py` 另覆盖默认关闭、install 继承与覆盖、隐藏/还原、遮挡回退、快速最小化、原生系统命令和交接资源清理。自动状态回归不能替代真实 Gallery 的连续帧和目测验证。

后续修改时：

- 正常最大化的 80ms 保护不能被扩大为长期全窗口接管。
- 若修改静态层交接时序，必须重新检查静态层残留、首帧空窗、真实控件提前露出和资源释放。
- 窗口过程只传递数据，Tk 工作回到主线程；不要在原生回调中直接调用 Tcl。
- 电池模式仍可能出现短暂背景板，不把当前结果宣称为所有性能环境下的数学保证。
