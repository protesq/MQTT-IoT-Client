import queue
import tkinter as tk
from core import manager

log_listbox = None
device_listbox = None
_ui_queue = queue.Queue()

def on_mqtt_message(topic, payload):
    if topic == "iot/discovery":
        _ui_queue.put(("log", f"[DISCOVERY] {payload.get('id', '?')}  [{payload.get('state', '?')}]"))
        _ui_queue.put(("refresh", None))
    elif topic.endswith("/data") and payload.get("ack"):
        device_id = topic.split("/")[1]
        _ui_queue.put(("log", f"[ACK] {device_id}  mode={payload.get('mode')}"))
    else:
        _ui_queue.put(("log", f"[{topic}] {payload}"))

def _poll_ui_queue(root):
    try:
        while True:
            action, data = _ui_queue.get_nowait()
            if action == "log":
                show_logs(data)
            elif action == "refresh":
                refresh_device_list()
    except queue.Empty:
        pass
    root.after(100, _poll_ui_queue, root)

def refresh_device_list():
    if device_listbox is None:
        return
    device_listbox.delete(0, tk.END)
    for device_id, info in manager.device_list.items():
        state = info.get("state", "?")
        device_listbox.insert(tk.END, f"{device_id}  [{state}]")

def start_logging():
    manager.on_message_callback = on_mqtt_message
    manager.connect_()
    show_logs("Bağlantı kuruldu, dinleniyor...")

def stop_logging():
    manager.disconnect()
    show_logs("Bağlantı kesildi.")

def send_command():
    selection = device_listbox.curselection()
    if not selection:
        show_logs("Önce bir cihaz seçin.")
        return
    device_id = list(manager.device_list.keys())[selection[0]]
    mode = cmd_entry.get().strip()
    if not mode:
        show_logs("Komut boş olamaz.")
        return
    manager.send_command(device_id, mode)
    show_logs(f"→ [{device_id}] mode: {mode}")

def show_logs(text):
    if log_listbox is not None:
        log_listbox.insert(tk.END, text)
        log_listbox.see(tk.END)

def home():
    global log_listbox, device_listbox, cmd_entry

    root = tk.Tk()
    root.title("MQTT IoT Logger")
    root.geometry("1080x720")

    tk.Label(root, text="Cihazlar", font=("Arial", 12, "bold")).pack()
    device_listbox = tk.Listbox(root, height=8, width=100)
    device_listbox.pack()

    tk.Label(root, text="Komut (mode)").pack()
    cmd_entry = tk.Entry(root, width=40)
    cmd_entry.pack()

    tk.Button(root, text="Seçili Cihaza Gönder", command=send_command).pack(pady=4)

    tk.Label(root, text="Loglar", font=("Arial", 12, "bold")).pack()
    log_listbox = tk.Listbox(root, height=12, width=100)
    log_listbox.pack()

    frame = tk.Frame(root)
    frame.pack(pady=6)
    tk.Button(frame, text="Bağlan", command=start_logging).pack(side=tk.LEFT, padx=4)
    tk.Button(frame, text="Bağlantıyı Kes", command=stop_logging).pack(side=tk.LEFT, padx=4)
    tk.Button(frame, text="Çıkış", command=root.destroy).pack(side=tk.LEFT, padx=4)

    root.after(100, _poll_ui_queue, root)
    root.mainloop()
