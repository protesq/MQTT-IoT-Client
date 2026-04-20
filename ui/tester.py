import queue
import threading
import time
import tkinter as tk
from core import connect, manager as mgr

_ui_queue = queue.Queue()
ack_received = []

_client = connect.make_client("iot-tester", clean_session=True)

def _on_connect(c, userdata, flags, reason_code, properties):
    c.subscribe("iot/discovery", qos=1)
    c.subscribe("iot/+/data", qos=1)
    _ui_queue.put(("log", f"Bağlandı: {reason_code}"))

def _on_message(c, userdata, message):
    import json
    try:
        payload = json.loads(message.payload.decode())
    except Exception:
        return
    if message.topic == "iot/discovery":
        device_id = payload.get("id")
        if device_id:
            mgr.device_list[device_id] = payload
        _ui_queue.put(("refresh", None))
    elif message.topic.endswith("/data") and payload.get("ack"):
        ack_received.append(payload.get("mode"))
        _ui_queue.put(("log", f"[ACK] mode={payload.get('mode')} | Toplam: {len(ack_received)}"))
        _ui_queue.put(("update", len(ack_received)))

_client.on_connect = _on_connect
_client.on_message = _on_message

def run_test(device_id, count):
    import json
    ack_received.clear()
    _ui_queue.put(("log", f"--- Test başladı → {device_id} ({count} mesaj) ---"))
    _ui_queue.put(("update", 0))

    for i in range(count):
        _client.publish(
            f"iot/{device_id}/cmd",
            json.dumps({"mode": f"test_mode_{i}"}),
            qos=1
        )
        _ui_queue.put(("log", f"[GÖNDERİLDİ] test_mode_{i}"))
        time.sleep(0.1)

    time.sleep(1)
    alınan = len(ack_received)
    if alınan == count:
        _ui_queue.put(("log", f"✓ Test GEÇTI — Gönderilen: {count} | ACK: {alınan}"))
    else:
        _ui_queue.put(("log", f"✗ Test BAŞARISIZ — Gönderilen: {count} | ACK: {alınan}"))
    _ui_queue.put(("done", None))

def start_test(device_listbox, count_entry, btn):
    selection = device_listbox.curselection()
    if not selection:
        _ui_queue.put(("log", "Önce bir cihaz seçin."))
        return
    try:
        count = int(count_entry.get())
    except ValueError:
        _ui_queue.put(("log", "Geçersiz mesaj sayısı."))
        return
    device_id = list(mgr.device_list.keys())[selection[0]]
    btn.config(state=tk.DISABLED)
    threading.Thread(target=run_test, args=(device_id, count), daemon=True).start()

def _poll(root, device_listbox, recv_var, btn):
    try:
        while True:
            action, data = _ui_queue.get_nowait()
            if action == "log":
                log_listbox.insert(tk.END, data)
                log_listbox.see(tk.END)
            elif action == "refresh":
                device_listbox.delete(0, tk.END)
                for did, info in mgr.device_list.items():
                    device_listbox.insert(tk.END, f"{did}  [{info.get('state', '?')}]")
            elif action == "update":
                recv_var.set(f"ACK: {data}")
            elif action == "done":
                btn.config(state=tk.NORMAL)
    except queue.Empty:
        pass
    root.after(100, _poll, root, device_listbox, recv_var, btn)

def home():
    global log_listbox

    root = tk.Tk()
    root.title("MQTT Cihaz Testi")
    root.geometry("750x580")

    tk.Label(root, text="Cihazlar", font=("Arial", 11, "bold")).pack()
    device_listbox = tk.Listbox(root, height=6, width=90)
    device_listbox.pack(padx=8)

    ctrl = tk.Frame(root)
    ctrl.pack(pady=6)
    tk.Label(ctrl, text="Mesaj sayısı:").pack(side=tk.LEFT)
    count_entry = tk.Entry(ctrl, width=6)
    count_entry.insert(0, "10")
    count_entry.pack(side=tk.LEFT, padx=4)

    recv_var = tk.StringVar(value="ACK: 0")
    tk.Label(ctrl, textvariable=recv_var, width=12).pack(side=tk.LEFT, padx=8)

    btn = tk.Button(ctrl, text="Seçili Cihaza Test Gönder")
    btn.config(command=lambda: start_test(device_listbox, count_entry, btn))
    btn.pack(side=tk.LEFT, padx=6)

    tk.Label(root, text="Loglar", font=("Arial", 11, "bold")).pack()
    log_listbox = tk.Listbox(root, height=20, width=90)
    log_listbox.pack(padx=8, pady=4)

    _client.connect(connect.BROKER, connect.PORT)
    _client.loop_start()

    root.after(100, _poll, root, device_listbox, recv_var, btn)
    root.mainloop()

    _client.loop_stop()
    _client.disconnect()
