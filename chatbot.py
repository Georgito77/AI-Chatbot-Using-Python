
import tkinter as tk
from tkinter import Canvas, Scrollbar, Frame
import json
import random
import re
from datetime import datetime
import wikipedia
import requests

# Load knowledge base
with open("bot.json", "r", encoding="utf-8") as file:
    responses = json.load(file)

wikipedia.set_lang("en")

def preprocess_input(user_input):
    return re.findall(r'\b\w+\b', user_input.lower())

def match_response(user_words):
    best_match = None
    best_score = 0
    for entry in responses:
        if not entry.get("enabled", True):
            continue
        required_words = entry.get("required_words", [])
        if all(word in user_words for word in required_words):
            match_score = sum(1 for word in user_words if word in entry.get("user_input", []))
            if match_score > best_score:
                best_score = match_score
                best_match = entry
    return best_match

def try_simple_math(user_input):
    try:
        expression = re.sub(r"[^0-9+\-*/(). ]", "", user_input)
        if expression:
            result = eval(expression)
            return f"The answer is {result}"
    except:
        return None
    return None

def try_natural_language_math(user_input):
    words = user_input.lower().split()
    numbers = [int(word) for word in words if word.isdigit()]
    if len(numbers) < 2:
        return None
    if "add" in words or "plus" in words:
        return f"The result is {numbers[0] + numbers[1]}"
    elif "subtract" in words or "minus" in words:
        if "from" in words:
            return f"The result is {numbers[1] - numbers[0]}"
        return f"The result is {numbers[0] - numbers[1]}"
    elif "multiply" in words or "times" in words:
        return f"The result is {numbers[0] * numbers[1]}"
    elif "divide" in words or "divided" in words:
        if numbers[1] == 0:
            return "You can't divide by zero!"
        return f"The result is {numbers[0] / numbers[1]}"
    return None

def get_definition(user_input):
    words = user_input.lower().split()
    if "define" in words or "definition" in words or "meaning" in words:
        for word in words:
            if word not in ["define", "definition", "meaning", "of", "what", "does", "the"]:
                term = word
                break
        else:
            return None

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}"
        try:
            response = requests.get(url)
            data = response.json()
            if isinstance(data, list):
                meaning = data[0]["meanings"][0]["definitions"][0]["definition"]
                return f"📘 Definition of {term}: {meaning}"
            else:
                return f"Sorry, I couldn't find a definition for '{term}'."
        except:
            return "Something went wrong trying to look that up."
    return None

def chatbot_response(user_input):
    words = preprocess_input(user_input)
    match = match_response(words)
    if match:
        all_responses = [match["bot_response"]] + match.get("variations", [])
        chosen = random.choice(all_responses)
        if "{{time}}" in chosen:
            chosen = chosen.replace("{{time}}", datetime.now().strftime("%H:%M"))
        return chosen

    definition = get_definition(user_input)
    if definition:
        return definition

    math_natural = try_natural_language_math(user_input)
    if math_natural:
        return math_natural

    math_answer = try_simple_math(user_input)
    if math_answer:
        return math_answer

    try:
        summary = wikipedia.summary(user_input, sentences=2)
        return f"📚 According to Wikipedia: {summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Too broad. Try: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "I couldn't find anything on that."
    except Exception as ex:
        return f"Error: {ex}"

# GUI Setup
def send_message():
    user_input = entry.get().strip()
    if not user_input:
        return
    add_message(user_input, "user")
    entry.delete(0, tk.END)
    response = chatbot_response(user_input)
    add_message(response, "bot")

def add_message(msg, sender="bot"):
    bubble = tk.Label(chat_frame,
                      text=msg,
                      bg="#e0e0e0" if sender == "bot" else "#6200ee",
                      fg="black" if sender == "bot" else "white",
                      wraplength=300,
                      justify="left" if sender == "bot" else "right",
                      font=("Arial", 10),
                      padx=10,
                      pady=6,
                      anchor="e" if sender == "user" else "w")
    bubble.pack(anchor="e" if sender == "user" else "w", padx=10, pady=5, fill="x", expand=True)
    canvas.update_idletasks()
    canvas.yview_moveto(1)

root = tk.Tk()
root.title("ChatBot")
root.geometry("400x600")
root.config(bg="white")

# Header
header = tk.Frame(root, bg="#6200ee", height=50)
header.pack(fill="x")
tk.Label(header, text="ChatBot", fg="white", bg="#6200ee", font=("Arial", 14, "bold")).pack(pady=10)

# Chat area
chat_area = tk.Frame(root, bg="white")
chat_area.pack(fill="both", expand=True)

canvas = Canvas(chat_area, bg="white", highlightthickness=0)
scrollbar = Scrollbar(chat_area, orient="vertical", command=canvas.yview)
chat_frame = Frame(canvas, bg="white")

chat_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=chat_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Entry and send button
entry_frame = tk.Frame(root, bg="white")
entry_frame.pack(fill="x", padx=10, pady=10)

entry = tk.Entry(entry_frame, font=("Arial", 12), width=28, bd=1, relief="solid")
entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
entry.bind("<Return>", lambda e: send_message())

send_btn = tk.Button(entry_frame, text="Send", command=send_message, bg="#6200ee", fg="white", font=("Arial", 10, "bold"))
send_btn.pack(side="right")

add_message("🤖 Hey there! I'm ChatBot. Ask me anything.", "bot")

root.mainloop()
