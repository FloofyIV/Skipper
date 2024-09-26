try:
    from PIL import Image
    import threading
    import os
    from pynput import mouse
    from concurrent.futures import ThreadPoolExecutor
    import time
    import pystray
    import requests
    import customtkinter as tk
    import win32api
    import win32con
    import json
    import ctypes
except ImportError:
    os._exit(1)
    os.system("pip install pillow pynput pystray requests customtkinter pywin32")

def on_scroll(x, y, dx, dy):
    if enabled and dy != 0 and executor._work_queue.qsize() < 15:
        executor.submit(hop)

def hop():
    win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)
    time.sleep(0.002)
    win32api.keybd_event(win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0)

def create_image():
    temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "Skipper")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    icon_path = os.path.join(temp_dir, "Icon.ico")
    if not os.path.exists(icon_path):
        url = "https://github.com/FloofyIV/Skipper/blob/main/Icon.ico?raw=true"
        response = requests.get(url)
        if response.status_code == 200:
            with open(icon_path, 'wb') as f:
                f.write(response.content)
        else:
            ctypes.windll.user32.MessageBoxW(0, f"Failed to download icon; HTTP status code: {response.status_code}", "Error", 0x10)
            os._exit(1)
    return Image.open(icon_path)

def quit():
    listener.stop()
    os._exit(0)

def qolbinds():
    while True:
        if win32api.GetAsyncKeyState(win32con.VK_DELETE):
            quit()
        elif win32api.GetAsyncKeyState(win32con.VK_HOME):
            tgui()
        elif win32api.GetAsyncKeyState(win32con.VK_END):
            togglehop()
        time.sleep(0.1)

def togglehop():
    global enabled
    enabled = not enabled

config_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "Skipper", "config.json")

def rconfig():
    global delay
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            delay = config.get('delay', 0.002)
    else:
        delay = 0.002

def wconfig():
    with open(config_path, 'w') as f:
        json.dump({'delay': delay}, f)

rconfig()
enabled = True
guitoggle = False
gui_thread = None

def tray():
    icon = pystray.Icon("Skipper")
    icon.icon = create_image()
    icon.title = "Skipper"
    icon.menu = pystray.Menu(
        pystray.MenuItem(
            lambda item: "Close GUI" if guitoggle else "Open GUI", 
            lambda item: tgui()
        ),
        pystray.MenuItem(
            lambda item: "Disable" if enabled else "Enable", 
            lambda item: togglehop()
        ),
        pystray.MenuItem("Quit", lambda item: quit())
    )
    icon.run()

def udelay():
    global delay
    try:
        delay = float(delay_entry.get())
    except ValueError:
        return None

def tgui():
    global guitoggle, gui_thread, root, delay_entry
    guitoggle = not guitoggle
    if guitoggle:
        if not gui_thread or not gui_thread.is_alive():
            gui_thread = threading.Thread(target=buildgui)
            gui_thread.start()
        else:
            if root:
                root.deiconify()
                root.lift()
    else:
        if root:
            root.withdraw()

def buildgui():
    global root, delay_entry
    root = tk.CTk()
    root.title("Skipper")
    root.geometry("225x135")
    root.iconbitmap(os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "Skipper", "Icon.ico"))

    window_width = 225
    window_height = 135
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    tk.CTkLabel(root, text="Set Delay (seconds):").pack(pady=5)
    delay_entry = tk.CTkEntry(root)
    delay_entry.pack(pady=5)
    delay_entry.insert(0, str(delay))

    tk.CTkButton(root, text="Update", command=lambda: [udelay(), wconfig()], fg_color="#2F2F2F", hover_color="#292929").pack(pady=10)

    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    root.mainloop()

executor = ThreadPoolExecutor(max_workers=1)
listener = mouse.Listener(on_scroll=on_scroll)

listener_thread = threading.Thread(target=listener.start)
listener_thread.start()

keyboard_listener_thread = threading.Thread(target=qolbinds)
keyboard_listener_thread.start()

tray()
