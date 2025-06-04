import tkinter as tk
from tkinter import messagebox, scrolledtext
import datetime
import threading
import time
from plyer import notification
from playsound import playsound
import json
import os

DATA_FILE = "medicines.json"
medicine_list = []

def load_medicines():
    medicine_list.clear()
    listbox.delete(0, tk.END)
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            for item in data:
                name = item["name"]
                time_str = item["time"]
                repeat = item.get("repeat", False)
                med_time = datetime.datetime.strptime(time_str, "%I:%M %p").time()
                medicine_list.append({
                    "name": name,
                    "time": med_time,
                    "repeat": repeat
                })
                listbox.insert(tk.END, f"{name} at {time_str} {'(Daily)' if repeat else ''}")

def save_medicines():
    data = [{
        "name": med["name"],
        "time": med["time"].strftime("%I:%M %p"),
        "repeat": med["repeat"]
    } for med in medicine_list]
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_medicine():
    name = med_name_entry.get()
    time_str = med_time_entry.get()
    repeat = repeat_var.get()

    if not name or not time_str:
        messagebox.showwarning("Missing Info", "Please enter both medicine name and time.")
        return

    try:
        med_time = datetime.datetime.strptime(time_str, "%I:%M %p").time()
        medicine_list.append({
            "name": name,
            "time": med_time,
            "repeat": repeat
        })
        listbox.insert(tk.END, f"{name} at {time_str} {'(Daily)' if repeat else ''}")
        save_medicines()
        med_name_entry.delete(0, tk.END)
        med_time_entry.delete(0, tk.END)
        repeat_var.set(False)
        update_upcoming_reminders()
    except ValueError:
        messagebox.showerror("Invalid Time Format", "Use time format like 08:30 AM or 07:45 PM")

def select_medicine(event):
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        med = medicine_list[index]
        med_name_entry.delete(0, tk.END)
        med_name_entry.insert(0, med["name"])
        med_time_entry.delete(0, tk.END)
        med_time_entry.insert(0, med["time"].strftime("%I:%M %p"))
        repeat_var.set(med.get("repeat", False))

def edit_medicine():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        name = med_name_entry.get()
        time_str = med_time_entry.get()
        repeat = repeat_var.get()
        try:
            med_time = datetime.datetime.strptime(time_str, "%I:%M %p").time()
            medicine_list[index] = {
                "name": name,
                "time": med_time,
                "repeat": repeat
            }
            listbox.delete(index)
            listbox.insert(index, f"{name} at {time_str} {'(Daily)' if repeat else ''}")
            save_medicines()
            med_name_entry.delete(0, tk.END)
            med_time_entry.delete(0, tk.END)
            repeat_var.set(False)
            update_upcoming_reminders()
        except ValueError:
            messagebox.showerror("Invalid Time Format", "Use format like 08:30 AM")
    else:
        messagebox.showinfo("No Selection", "Please select a medicine to edit.")

def delete_medicine():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        del medicine_list[index]
        listbox.delete(index)
        save_medicines()
        med_name_entry.delete(0, tk.END)
        med_time_entry.delete(0, tk.END)
        repeat_var.set(False)
        update_upcoming_reminders()
    else:
        messagebox.showinfo("No Selection", "Please select a medicine to delete.")

def check_reminders():
    notified = set()
    while True:
        now = datetime.datetime.now().time().replace(second=0, microsecond=0)
        today = datetime.date.today()

        for med in medicine_list:
            med_name = med["name"]
            med_time = med["time"]
            repeat = med.get("repeat", False)
            key = (med_name, med_time.strftime("%I:%M %p"), today)

            if now == med_time:
                if repeat or key not in notified:
                    notification.notify(
                        title="💊 Medicine Reminder",
                        message=f"Time to take: {med_name}",
                        timeout=10
                    )
                    try:
                        playsound("notification.mp3")
                    except:
                        pass
                    notified.add(key)

        time.sleep(30)

def update_upcoming_reminders():
    upcoming_listbox.delete(0, tk.END)
    now = datetime.datetime.now()
    for med in medicine_list:
        med_time_today = datetime.datetime.combine(now.date(), med["time"])
        diff = (med_time_today - now).total_seconds() / 60  # minutes difference
        if 0 <= diff <= 60:
            repeat_text = "(Daily)" if med.get("repeat", False) else ""
            upcoming_listbox.insert(tk.END, f"{med['name']} at {med['time'].strftime('%I:%M %p')} {repeat_text}")

def update_upcoming_loop():
    while True:
        update_upcoming_reminders()
        time.sleep(60)

# GUI Setup
root = tk.Tk()
root.title("Medicine Reminder 2.0")
root.geometry("500x600")
root.configure(padx=15, pady=15)

# Frames for layout
input_frame = tk.Frame(root)
input_frame.pack(fill=tk.X, pady=10)

buttons_frame = tk.Frame(root)
buttons_frame.pack(fill=tk.X, pady=10)

list_frame = tk.Frame(root)
list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

upcoming_frame = tk.Frame(root)
upcoming_frame.pack(fill=tk.BOTH, expand=True, pady=10)

# Input fields
tk.Label(input_frame, text="Medicine Name:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W)
med_name_entry = tk.Entry(input_frame, font=("Arial", 12))
med_name_entry.grid(row=0, column=1, padx=10)

tk.Label(input_frame, text="Dosage Time (e.g., 08:30 AM):", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W)
med_time_entry = tk.Entry(input_frame, font=("Arial", 12))
med_time_entry.grid(row=1, column=1, padx=10)

repeat_var = tk.BooleanVar()
repeat_check = tk.Checkbutton(input_frame, text="Repeat Daily", variable=repeat_var, font=("Arial", 12))
repeat_check.grid(row=2, column=1, sticky=tk.W, pady=5)

# Buttons
tk.Button(buttons_frame, text="Add Medicine", command=add_medicine, font=("Arial", 12)).grid(row=0, column=0, padx=5)
tk.Button(buttons_frame, text="Edit Selected", command=edit_medicine, font=("Arial", 12)).grid(row=0, column=1, padx=5)
tk.Button(buttons_frame, text="Delete Selected", command=delete_medicine, font=("Arial", 12)).grid(row=0, column=2, padx=5)

# Scheduled Medicines Listbox
tk.Label(list_frame, text="Scheduled Medicines:", font=("Arial", 14, "bold")).pack(anchor=tk.W)
listbox = tk.Listbox(list_frame, font=("Arial", 12))
listbox.pack(fill=tk.BOTH, expand=True)
listbox.bind('<<ListboxSelect>>', select_medicine)

# Upcoming Reminders Listbox
tk.Label(upcoming_frame, text="Upcoming Reminders (Next 60 min):", font=("Arial", 14, "bold")).pack(anchor=tk.W)
upcoming_listbox = tk.Listbox(upcoming_frame, font=("Arial", 12), fg="blue")
upcoming_listbox.pack(fill=tk.BOTH, expand=True)

load_medicines()
update_upcoming_reminders()

# Background threads
threading.Thread(target=check_reminders, daemon=True).start()
threading.Thread(target=update_upcoming_loop, daemon=True).start()

root.mainloop()
