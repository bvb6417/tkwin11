"""Real Windows HWND regressions for the configurable transition workaround."""
import ctypes
import sys
import time
import tkinter as tk
from tkinter import ttk
import unittest

import tkwin11 as ui


@unittest.skipUnless(sys.platform == 'win32', 'Requires Windows HWNDs')
class WindowFlickerWorkaroundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ui.enable_dpi_awareness()

    def setUp(self):
        ui.uninstall()
        self.roots = []

    def tearDown(self):
        for root in reversed(self.roots):
            if root.winfo_exists():
                root.update_idletasks()
                root.destroy()
        ui.uninstall()

    def pump(self, seconds=0.2):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            for root in self.roots:
                root.update()
            time.sleep(0.005)

    def window(self, enabled=None, parent=None):
        root = tk.Toplevel(parent) if parent else tk.Tk()
        if not parent:
            self.roots.append(root)
        root.geometry('640x420+120+120')
        root.attributes('-topmost', True)
        ui.apply_theme(root)
        toolbar = ttk.Frame(root, height=48)
        toolbar.pack(fill='x')
        toolbar.pack_propagate(False)
        entry = ttk.Entry(root)
        entry.insert(0, 'before')
        entry.pack(fill='x', padx=20, pady=20)
        tk.Frame(root, background='#145aaf').pack(fill='both', expand=True)
        chrome = ui.WindowChrome(root, toolbar, window_flicker_workaround=enabled)
        self.pump(0.4)
        root.lift()
        self.pump(0.1)
        return root, chrome, entry

    def assert_released(self, chrome):
        animation = chrome._restore_animation
        self.assertIsNone(animation.overlay)
        self.assertIsNone(animation.job)
        self.assertIsNone(animation.dc)
        self.assertFalse(chrome._restore_pending)

    def test_install_can_explicitly_disable_workaround(self):
        ui.install(window_flicker_workaround=False)
        root, chrome, _ = self.window()
        self.assertFalse(chrome.window_flicker_workaround)
        self.assertIsNone(chrome._restore_animation)
        self.assertIsNone(getattr(chrome, '_erase_brush', None))
        chrome.begin_erase_guard()
        self.assertFalse(chrome._erase_guard_active)
        chrome.minimize()
        self.pump()
        root.deiconify()
        self.pump()
        self.assertIsNone(chrome._restore_animation)

    def test_install_default_enables_inheritance_and_allows_override(self):
        ui.install()
        root, chrome, _ = self.window()
        self.assertTrue(chrome.window_flicker_workaround)
        child, inherited, _ = self.window(parent=root)
        self.assertTrue(inherited.window_flicker_workaround)
        child.destroy()
        child, overridden, _ = self.window(enabled=False, parent=root)
        self.assertFalse(overridden.window_flicker_workaround)
        self.assertIsNone(overridden._restore_animation)
        child.destroy()
        ui.install(window_flicker_workaround=False)
        child, inherited, _ = self.window(parent=root)
        self.assertTrue(inherited.window_flicker_workaround)
        child.destroy()
        _, future, _ = self.window()
        self.assertFalse(future.window_flicker_workaround)

    def test_uninstall_only_affects_future_roots(self):
        ui.install(window_flicker_workaround=True)
        root, chrome, _ = self.window()
        ui.uninstall()
        self.assertTrue(chrome.window_flicker_workaround)
        _, future, _ = self.window()
        self.assertFalse(future.window_flicker_workaround)

    def test_titlebar_accepts_per_window_opt_in(self):
        root = tk.Tk()
        self.roots.append(root)
        bar = ui.FluentTitleBar(root, window_flicker_workaround=True)
        bar.pack(fill='x')
        self.pump()
        self.assertTrue(bar.chrome.window_flicker_workaround)

    def test_withdraw_then_show_has_no_stale_overlay(self):
        root, chrome, entry = self.window(enabled=True)
        root.withdraw()
        self.pump()
        entry.delete(0, 'end')
        entry.insert(0, 'after')
        root.deiconify()
        self.pump(0.6)
        self.assert_released(chrome)
        self.assertEqual(entry.get(), 'after')

    def test_withdraw_during_handoff_cancels_overlay(self):
        root, chrome, _ = self.window(enabled=True)
        chrome.minimize()
        self.pump()
        root.deiconify()
        self.pump(0.06)
        self.assertIsNotNone(chrome._restore_animation.job)
        root.withdraw()
        self.pump()
        self.assert_released(chrome)
        root.deiconify()
        self.pump(0.5)
        self.assert_released(chrome)

    def test_occluded_capture_falls_back_without_foreign_pixels(self):
        root, chrome, _ = self.window(enabled=True)
        cover = tk.Toplevel(root)
        cover.overrideredirect(True)
        cover.geometry('240x160+280+300')
        cover.configure(background='#ed17a8')
        cover.attributes('-topmost', True)
        cover.lift()
        self.pump()
        animation = chrome._restore_animation
        self.assertFalse(animation.capture(chrome.hwnd))
        self.assertIsNone(animation.dc)
        chrome.minimize()
        self.pump()
        cover.destroy()
        root.deiconify()
        self.pump(0.5)
        self.assert_released(chrome)
        root.lift()
        self.pump()
        self.assertTrue(animation.capture(chrome.hwnd))
        animation.g.GetPixel.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        animation.g.GetPixel.restype = ctypes.c_uint32
        self.assertEqual(animation.g.GetPixel(animation.dc, 320, 300), 0xaf5a14)
        animation.discard()

    def test_restore_handoff_releases_bitmap_and_timer(self):
        root, chrome, _ = self.window(enabled=True)
        chrome.minimize()
        self.assertTrue(chrome._restore_pending)
        self.pump()
        root.deiconify()
        self.pump(0.06)
        self.assertIsNotNone(chrome._restore_animation.overlay)
        self.assertIsNotNone(chrome._restore_animation.job)
        self.pump(0.6)
        self.assert_released(chrome)

    def test_rapid_second_minimize_does_not_reuse_old_bitmap(self):
        root, chrome, _ = self.window(enabled=True)
        chrome.minimize()
        self.pump()
        root.deiconify()
        self.pump(0.06)
        self.assertTrue(chrome._restore_animation.busy)
        chrome.minimize()
        self.pump()
        self.assert_released(chrome)
        root.deiconify()
        self.pump(0.6)
        self.assert_released(chrome)

    def test_native_system_commands_restore_and_release(self):
        root, chrome, _ = self.window(enabled=True)
        chrome.u.PostMessageW(chrome.hwnd, 0x0112, 0xf020, 0)
        self.pump(0.3)
        self.assertTrue(chrome.u.IsIconic(chrome.hwnd))
        self.assertTrue(chrome._restore_pending)
        chrome.u.PostMessageW(chrome.hwnd, 0x0112, 0xf120, 0)
        self.pump(0.8)
        self.assertFalse(chrome.u.IsIconic(chrome.hwnd))
        self.assert_released(chrome)


if __name__ == '__main__':
    unittest.main()
