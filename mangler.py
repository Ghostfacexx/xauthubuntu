#!/usr/bin/python3
"""Wordlister with GUI, a categorized wordlist generator and mangler written in Python 3."""
# Original by Ananke: https://github.com/4n4nk3
# GUI adaptation by Grok

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from copy import copy
from itertools import permutations
import os
import random

class Wordlister:
    LEET_TRANSLATIONS = str.maketrans('oOaAeEiIsS', '0044331155')
    CATEGORIES = ['name', 'initials', 'years', 'tags']

    def __init__(self, params):
        self.params = params
        self.wordlist = set()

    def leet_and_append_and_prepend(self, line_leet: str) -> set:
        line_leet = line_leet.translate(self.LEET_TRANSLATIONS)
        result = {line_leet + '\n'}
        if self.params['append']:
            result.add(f'{line_leet}{self.params["append"]}\n')
        if self.params['prepend']:
            result.add(f'{self.params["prepend"]}{line_leet}\n')
        return result

    def get_input_words(self, input_texts: dict) -> dict:
        words = {}
        for cat in self.CATEGORIES:
            words[cat] = set(line.strip() for line in input_texts[cat].splitlines() if line.strip())
            if not words[cat]:
                raise ValueError(f"No valid words provided for {cat.capitalize()}!")
            
            prepped_words = copy(words[cat])
            if self.params['cap'] or self.params['up']:
                for word in words[cat]:
                    if self.params['cap']:
                        prepped_words.add(word.capitalize())
                    if self.params['up']:
                        prepped_words.add(word.upper())
            words[cat] = prepped_words
        return words
    
    def printer(self, combination: tuple, order: list):
        line_printer = ''.join(combination)
        min_len = int(self.params['min'])
        max_len = int(self.params['max'])
        if min_len <= len(line_printer) <= max_len:
            self.wordlist.add(line_printer + '\n')
            if self.params['append'] and len(line_printer) + len(self.params['append']) <= max_len:
                self.wordlist.add(f'{line_printer}{self.params["append"]}\n')
            if self.params['prepend'] and len(line_printer) + len(self.params['prepend']) <= max_len:
                self.wordlist.add(f'{self.params["prepend"]}{line_printer}\n')
            if self.params['leet']:
                self.wordlist.update(self.leet_and_append_and_prepend(line_printer))

    def run(self):
        input_words = self.get_input_words(self.params['input'])
        start_cat = self.params['start']
        randomize = self.params['randomize']
        order = self.params['order'] if not randomize else None

        # Define the order of categories
        if randomize:
            remaining_cats = [cat for cat in self.CATEGORIES if cat != start_cat]
            random.shuffle(remaining_cats)
            full_order = [start_cat] + remaining_cats
        else:
            full_order = [start_cat] + [self.params['order'][i] for i in range(2, 5)]

        # Generate combinations for each length up to perm
        for length in range(1, int(self.params['perm']) + 1):
            for cat_perm in permutations(full_order, length):
                word_lists = [input_words[cat] for cat in cat_perm]
                for word_combo in self._product(word_lists):
                    self.printer(word_combo, cat_perm)

        if self.params['sort']:
            self.wordlist = sorted(self.wordlist, key=len)
        with open(self.params['output'], 'w') as f_out:
            f_out.writelines(self.wordlist)

    def _product(self, word_lists):
        if not word_lists:
            return [()]
        result = []
        for item in word_lists[0]:
            for sub_combo in self._product(word_lists[1:]):
                result.append((item,) + sub_combo)
        return result

class WordlisterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordlister - Categorized Wordlist Generator")
        self.root.geometry("600x600")
        self.root.minsize(500, 400)
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        # Set output file to ver.txt in script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.params = {
            'input': {'name': '', 'initials': '', 'years': '', 'tags': ''},
            'output': os.path.join(script_dir, 'ver.txt'),
            'perm': '1', 'min': '1', 'max': '10',
            'leet': False, 'cap': False, 'up': False, 'append': '', 'prepend': '', 'sort': False,
            'start': 'name', 'randomize': True, 'order': {2: 'initials', 3: 'years', 4: 'tags'}
        }
        self.create_widgets()

    def create_widgets(self):
        # Main container
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)

        # Canvas and Scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Style
        style = ttkb.Style()
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TCheckbutton", font=("Arial", 9))
        style.configure("TButton", font=("Arial", 10))

        # Input Section
        input_frame = ttk.LabelFrame(scrollable_frame, text="Input Categories", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        self.input_texts = {}
        for idx, cat in enumerate(['Names', 'Initials', 'Years', 'Tags']):
            ttk.Label(input_frame, text=f"{cat} (one per line):").grid(row=idx*2, column=0, padx=5, pady=2, sticky="w")
            self.input_texts[cat.lower()] = tk.Text(input_frame, height=3, width=40, font=("Arial", 9))
            self.input_texts[cat.lower()].grid(row=idx*2+1, column=0, padx=5, pady=2, sticky="ew")

        # Order Section
        order_frame = ttk.LabelFrame(scrollable_frame, text="Combination Order", padding=10)
        order_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        order_frame.columnconfigure(0, weight=1)

        ttk.Label(order_frame, text="Start with:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.start_var = tk.StringVar(value='name')
        ttk.Combobox(order_frame, textvariable=self.start_var, values=['name', 'initials', 'years', 'tags'], state='readonly', width=15).grid(row=0, column=1, padx=5, pady=2, sticky="w")

        self.randomize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(order_frame, text="Randomize remaining positions", variable=self.randomize_var, command=self.toggle_order_fields).grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="w")

        self.order_vars = {}
        self.order_menus = {}
        for idx, pos in enumerate(range(2, 5)):
            ttk.Label(order_frame, text=f"Position {pos}:").grid(row=idx+2, column=0, padx=5, pady=2, sticky="w")
            self.order_vars[pos] = tk.StringVar(value=self.params['order'][pos])
            menu = ttk.Combobox(order_frame, textvariable=self.order_vars[pos], values=['name', 'initials', 'years', 'tags'], state='readonly', width=15)
            menu.grid(row=idx+2, column=1, padx=5, pady=2, sticky="w")
            self.order_menus[pos] = menu
        self.toggle_order_fields()

        # Parameters Section
        param_frame = ttk.LabelFrame(scrollable_frame, text="Parameters", padding=10)
        param_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        param_frame.columnconfigure(1, weight=1)

        ttk.Label(param_frame, text="Max Categories to Combine:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.perm_entry = ttk.Entry(param_frame, width=10, font=("Arial", 9))
        self.perm_entry.insert(0, "1")
        self.perm_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(param_frame, text="Min Password Length:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.min_entry = ttk.Entry(param_frame, width=10, font=("Arial", 9))
        self.min_entry.insert(0, "1")
        self.min_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(param_frame, text="Max Password Length:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.max_entry = ttk.Entry(param_frame, width=10, font=("Arial", 9))
        self.max_entry.insert(0, "10")
        self.max_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # Mutagen Section
        mutagen_frame = ttk.LabelFrame(scrollable_frame, text="Mutagen Options", padding=10)
        mutagen_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.leet_var = tk.BooleanVar()
        self.cap_var = tk.BooleanVar()
        self.up_var = tk.BooleanVar()
        self.sort_var = tk.BooleanVar()
        ttk.Checkbutton(mutagen_frame, text="Leet Speak (e.g., o->0, a->@)", variable=self.leet_var).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(mutagen_frame, text="Capitalize Words", variable=self.cap_var).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(mutagen_frame, text="Uppercase Words", variable=self.up_var).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(mutagen_frame, text="Sort by Length", variable=self.sort_var).grid(row=3, column=0, padx=5, pady=2, sticky="w")

        # Append/Prepend Section
        append_frame = ttk.LabelFrame(scrollable_frame, text="Append/Prepend", padding=10)
        append_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        append_frame.columnconfigure(1, weight=1)

        ttk.Label(append_frame, text="Append Word:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.append_entry = ttk.Entry(append_frame, width=20, font=("Arial", 9))
        self.append_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(append_frame, text="Prepend Word:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.prepend_entry = ttk.Entry(append_frame, width=20, font=("Arial", 9))
        self.prepend_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        # Run Button
        ttk.Button(scrollable_frame, text="Generate Wordlist", command=self.run_wordlister, style="primary.TButton").grid(row=5, column=0, padx=10, pady=20)

        # Status Label
        self.status_label = ttk.Label(scrollable_frame, text="Output will be saved as ver.txt in script directory", font=("Arial", 9))
        self.status_label.grid(row=6, column=0, padx=10, pady=10)

        # Configure grid weights
        scrollable_frame.columnconfigure(0, weight=1)
        for i in range(7):
            scrollable_frame.rowconfigure(i, weight=1)

    def toggle_order_fields(self):
        state = 'disabled' if self.randomize_var.get() else 'normal'
        for pos in range(2, 5):
            self.order_menus[pos].configure(state=state)

    def run_wordlister(self):
        try:
            # Collect parameters
            for cat in self.CATEGORIES:
                self.params['input'][cat] = self.input_texts[cat].get("1.0", tk.END).strip()
            self.params['perm'] = self.perm_entry.get().strip()
            self.params['min'] = self.min_entry.get().strip()
            self.params['max'] = self.max_entry.get().strip()
            self.params['leet'] = self.leet_var.get()
            self.params['cap'] = self.cap_var.get()
            self.params['up'] = self.up_var.get()
            self.params['append'] = self.append_entry.get().strip()
            self.params['prepend'] = self.prepend_entry.get().strip()
            self.params['sort'] = self.sort_var.get()
            self.params['start'] = self.start_var.get()
            self.params['randomize'] = self.randomize_var.get()
            if not self.params['randomize']:
                for pos in range(2, 5):
                    self.params['order'][pos] = self.order_vars[pos].get()
                order_set = {self.params['start']} | set(self.params['order'].values())
                if len(order_set) != 4:
                    raise ValueError("Each category must be used exactly once in the order!")

            # Validate inputs
            if not self.params['input']['name'].strip():
                raise ValueError("Please enter at least one name!")
            if not self.params['perm'].isdigit() or int(self.params['perm']) < 1 or int(self.params['perm']) > 4:
                raise ValueError("Max categories to combine must be a positive integer <= 4!")
            if not self.params['min'].isdigit() or int(self.params['min']) < 1:
                raise ValueError("Minimum length must be a positive integer!")
            if not self.params['max'].isdigit() or int(self.params['max']) < int(self.params['min']):
                raise ValueError("Maximum length must be a positive integer and >= minimum length!")

            # Run Wordlister
            wordlister = Wordlister(self.params)
            wordlister.run()
            self.status_label.configure(text=f"Success! Output saved to {self.params['output']}", foreground="green")
            messagebox.showinfo("Success", f"Wordlist generated and saved to {self.params['output']}")

        except ValueError as e:
            self.status_label.configure(text=str(e), foreground="red")
            messagebox.showerror("Error", str(e))
        except Exception as e:
            self.status_label.configure(text="An unexpected error occurred!", foreground="red")
            messagebox.showerror("Error", "An unexpected error occurred: " + str(e))

if __name__ == "__main__":
    root = ttkb.Window(themename="flatly")
    app = WordlisterGUI(root)
    root.mainloop()
