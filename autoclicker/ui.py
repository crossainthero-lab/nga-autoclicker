"""Tkinter front end for the shared click engine."""
import queue

from .core import ClickEngine, save_settings, validate_cps
from .platform import parse_hotkey, start_listener


def run_ui(keyboard, mouse, cps, hotkey):
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ImportError as exc:
        raise RuntimeError('Tkinter is required for the UI. Install your system Python Tk package (for example, python3-tk on Debian/Ubuntu).') from exc
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise RuntimeError(f'Could not open the UI: {exc}') from exc
    root.title('NGA Auto Clicker')
    root.resizable(False, False)
    root.configure(padx=24, pady=20)
    events = queue.SimpleQueue()
    controller = mouse.Controller()
    engine = ClickEngine(lambda: controller.click(mouse.Button.left), cps, events.put)
    listener = None
    cps_var = tk.StringVar(value=f'{cps:g}')
    hotkey_var = tk.StringVar(value=hotkey)
    status_var = tk.StringVar(value='Stopped')
    detail_var = tk.StringVar(value=f'Press {hotkey} to start or stop')

    frame = ttk.Frame(root)
    frame.grid(sticky='nsew')
    ttk.Label(frame, text='Auto Clicker', font=('TkDefaultFont', 18, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 4))
    ttk.Label(frame, text='Clicks at your current mouse position.').grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 18))
    ttk.Label(frame, text='Clicks per second').grid(row=2, column=0, sticky='w', padx=(0, 20), pady=5)
    ttk.Entry(frame, textvariable=cps_var, width=22).grid(row=2, column=1, pady=5)
    ttk.Label(frame, text='Toggle hotkey').grid(row=3, column=0, sticky='w', pady=5)
    ttk.Entry(frame, textvariable=hotkey_var, width=22).grid(row=3, column=1, pady=5)
    ttk.Label(frame, text='Examples: F8, a, ctrl+shift+a').grid(row=4, column=1, sticky='w', pady=(0, 12))
    ttk.Label(frame, textvariable=status_var, font=('TkDefaultFont', 12, 'bold')).grid(row=5, column=0, sticky='w', pady=(10, 0))
    ttk.Label(frame, textvariable=detail_var).grid(row=6, column=0, columnspan=2, sticky='w', pady=(4, 14))

    def apply():
        nonlocal listener
        try:
            new_cps = validate_cps(cps_var.get())
            new_hotkey = hotkey_var.get().strip()
            parse_hotkey(keyboard, new_hotkey)
            # Start the new listener before retiring the old one, so failed changes retain the old binding.
            new_listener = start_listener(keyboard, new_hotkey, engine.toggle)
            try:
                save_settings(new_cps, new_hotkey)
            except OSError:
                new_listener.stop()
                raise
            old_listener, listener = listener, new_listener
            if old_listener:
                old_listener.stop()
            engine.set_cps(new_cps)
            detail_var.set(f'Press {new_hotkey} to start or stop')
        except (ValueError, OSError, RuntimeError) as exc:
            messagebox.showerror('Invalid settings', str(exc), parent=root)

    ttk.Button(frame, text='Apply settings', command=apply).grid(row=7, column=0, sticky='ew', padx=(0, 8))
    ttk.Button(frame, text='Start / Stop', command=engine.toggle).grid(row=7, column=1, sticky='ew')

    def poll():
        while not events.empty():
            status_var.set('Clicking' if events.get() else 'Stopped')
        root.after(50, poll)

    def close():
        if listener:
            listener.stop()
        engine.close()
        root.destroy()

    try:
        listener = start_listener(keyboard, hotkey, engine.toggle)
        root.protocol('WM_DELETE_WINDOW', close)
        root.after(50, poll)
        root.mainloop()
    finally:
        if listener:
            listener.stop()
        engine.close()
    return 0
