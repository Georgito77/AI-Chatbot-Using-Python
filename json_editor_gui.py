
import tkinter as tk
from tkinter import ttk, messagebox
import json

FILE_PATH = "bot.json"

# Load JSON data
def load_data():
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

data = load_data()

# Save JSON data
def save_data():
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    messagebox.showinfo("Saved", "Changes saved to bot.json")

# GUI Setup
root = tk.Tk()
root.title("ChatBot JSON Editor")
root.geometry("800x500")

# Entry fields
fields = {
    "intent": tk.StringVar(),
    "bot_response": tk.StringVar(),
    "category": tk.StringVar(),
    "context": tk.StringVar(),
}

tk.Label(root, text="Intent").place(x=400, y=10)
tk.Entry(root, textvariable=fields["intent"], width=40).place(x=500, y=10)

tk.Label(root, text="Bot Response").place(x=400, y=40)
tk.Entry(root, textvariable=fields["bot_response"], width=40).place(x=500, y=40)

tk.Label(root, text="Category").place(x=400, y=70)
tk.Entry(root, textvariable=fields["category"], width=40).place(x=500, y=70)

tk.Label(root, text="Context").place(x=400, y=100)
tk.Entry(root, textvariable=fields["context"], width=40).place(x=500, y=100)

# Listboxes for user_input, required_words, variations
def listbox_with_label(title, x, y):
    tk.Label(root, text=title).place(x=x, y=y)
    lb = tk.Listbox(root, height=5)
    lb.place(x=x, y=y+20)
    entry = tk.Entry(root, width=20)
    entry.place(x=x, y=y+120)

    def add_item():
        lb.insert(tk.END, entry.get())
        entry.delete(0, tk.END)

    def remove_item():
        if lb.curselection():
            lb.delete(lb.curselection())

    tk.Button(root, text="+", command=add_item).place(x=x+150, y=y+120)
    tk.Button(root, text="-", command=remove_item).place(x=x+180, y=y+120)
    return lb

lb_input = listbox_with_label("User Input", 10, 10)
lb_required = listbox_with_label("Required Words", 210, 10)
lb_variations = listbox_with_label("Variations", 10, 180)

# Entry List
entry_list = tk.Listbox(root)
entry_list.place(x=400, y=150, width=380, height=250)

def update_listbox():
    entry_list.delete(0, tk.END)
    for i, item in enumerate(data):
        entry_list.insert(tk.END, f"{i+1}. {item['intent']}")

update_listbox()

# Load selected entry
def load_entry(event=None):
    selection = entry_list.curselection()
    if not selection:
        return
    index = selection[0]
    entry = data[index]

    fields["intent"].set(entry.get("intent", ""))
    fields["bot_response"].set(entry.get("bot_response", ""))
    fields["category"].set(entry.get("category", ""))
    fields["context"].set(entry.get("context", ""))

    lb_input.delete(0, tk.END)
    for word in entry.get("user_input", []):
        lb_input.insert(tk.END, word)

    lb_required.delete(0, tk.END)
    for word in entry.get("required_words", []):
        lb_required.insert(tk.END, word)

    lb_variations.delete(0, tk.END)
    for word in entry.get("variations", []):
        lb_variations.insert(tk.END, word)

entry_list.bind("<<ListboxSelect>>", load_entry)

# Save or update current entry
def save_entry():
    selection = entry_list.curselection()
    if not selection:
        return
    index = selection[0]

    updated = {
        "response_type": "chitchat",  # could be made dynamic
        "intent": fields["intent"].get(),
        "user_input": list(lb_input.get(0, tk.END)),
        "bot_response": fields["bot_response"].get(),
        "required_words": list(lb_required.get(0, tk.END)),
        "category": fields["category"].get(),
        "context": fields["context"].get(),
        "enabled": True,
        "variations": list(lb_variations.get(0, tk.END))
    }

    data[index] = updated
    update_listbox()
    messagebox.showinfo("Updated", "Entry updated.")

# Add new entry
def add_entry():
    new = {
        "response_type": "chitchat",
        "intent": fields["intent"].get(),
        "user_input": list(lb_input.get(0, tk.END)),
        "bot_response": fields["bot_response"].get(),
        "required_words": list(lb_required.get(0, tk.END)),
        "category": fields["category"].get(),
        "context": fields["context"].get(),
        "enabled": True,
        "variations": list(lb_variations.get(0, tk.END))
    }
    data.append(new)
    update_listbox()
    messagebox.showinfo("Added", "New entry added.")

# Delete selected entry
def delete_entry():
    selection = entry_list.curselection()
    if not selection:
        return
    index = selection[0]
    del data[index]
    update_listbox()
    messagebox.showinfo("Deleted", "Entry deleted.")

# Buttons
tk.Button(root, text="Save Entry", command=save_entry).place(x=400, y=420)
tk.Button(root, text="Add New", command=add_entry).place(x=500, y=420)
tk.Button(root, text="Delete", command=delete_entry).place(x=600, y=420)
tk.Button(root, text="Save to File", command=save_data, bg="green", fg="white").place(x=680, y=460)

root.mainloop()
