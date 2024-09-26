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
except ImportError:
    print("Missing dependencies, Installing.")
    os._exit(1)
    os.system("pip install pillow pynput pystray requests customtkinter pywin32")


print("Initialized")

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
        print(f"Downloading Icon")
        url = "https://github.com/FloofyIV/Skipper/blob/main/Icon.ico?raw=true"
        response = requests.get(url)
        if response.status_code == 200:
            with open(icon_path, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Failed; {response.status_code}")
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
            togglegui()
        elif win32api.GetAsyncKeyState(win32con.VK_END):
            togglehop()
        time.sleep(0.1)

def togglehop():
    global enabled
    enabled = not enabled

delay = 0.002
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
            lambda item: togglegui()
        ),
        pystray.MenuItem(
            lambda item: "Disable" if enabled else "Enable", 
            lambda item: togglehop()
        ),
        pystray.MenuItem("Quit", lambda item: quit())
    )
    print("Minimized - Tray") 
    icon.run()

def udelay():
    global delay
    try:
        delay = float(delay_entry.get())
    except ValueError:
        return None

def togglegui():
    global guitoggle, gui_thread, root, delay_entry
    guitoggle = not guitoggle
    if guitoggle:
        if not gui_thread or not gui_thread.is_alive():
            gui_thread = threading.Thread(target=create_gui)
            gui_thread.start()
        else:
            if root:
                root.deiconify()
                root.lift()
    else:
        if root:
            root.withdraw()

def create_gui():
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

    tk.CTkButton(root, text="Update", command=udelay, fg_color="#2F2F2F", hover_color="#292929").pack(pady=10)

    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    root.mainloop()

def open_gui():
    global gui_thread
    if not gui_thread or not gui_thread.is_alive():
        gui_thread = threading.Thread(target=create_gui)
        gui_thread.start()
    else:
        if root:
            root.deiconify()

executor = ThreadPoolExecutor(max_workers=1)
listener = mouse.Listener(on_scroll=on_scroll)

listener_thread = threading.Thread(target=listener.start)
listener_thread.start()

keyboard_listener_thread = threading.Thread(target=qolbinds)
keyboard_listener_thread.start()

tray()