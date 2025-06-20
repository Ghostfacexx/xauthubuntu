#!/usr/bin/python3
"""Wordlister with GUI, a wordlist generator and mangler written in Python 3."""
# Original by Ananke: https://github.com/4n4nk3
# GUI adaptation by Grok

import tkinter as tk
from tkinter import messagebox
from copy import copy
from itertools import permutations
import os

class Wordlister:
    LEET_TRANSLATIONS = str.maketrans('oOaAeEiIsS', '0044331155')

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

    def get_input_words(self, input_text: str) -> set:
        words = set(line.strip() for line in input_text.splitlines() if line.strip())
        if not words:
            raise ValueError("No valid words provided!")
        
        prepped_words = copy(words)
        if self.params['cap'] or self.params['up']:
            for word in words:
                if self.params['cap']:
                    prepped_words.add(word.capitalize())
                if self.params['up']:
                    prepped_words.add(word.upper())
        return prepped_words
    
    def printer(self, permutation: tuple):
        if len(set(map(str.lower, permutation))) == len(permutation):
            line_printer = ''.join(permutation)
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
        for x in range(int(self.params['perm'])):
            for perm in permutations(input_words, x + 1):
                self.printer(perm)
        
        if self.params['sort']:
            self.wordlist = sorted(self.wordlist, key=len)    
        with open(self.params['output'], 'w') as f_out:
            f_out.writelines(self.wordlist)

class WordlisterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordlister - Wordlist Generator")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # Set output file to ver.txt in script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.params = {
            'input': '', 'output': os.path.join(script_dir, 'ver.txt'),
            'perm': '1', 'min': '1', 'max': '10',
            'leet': False, 'cap': False, 'up': False, 'append': '', 'prepend': '', 'sort': False
        }
        self.create_widgets()

    def create_widgets(self):
        # Input Text Box
        tk.Label(self.root, text="Enter Words (one per line):", bg="#f0f0f0", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.input_text = tk.Text(self.root, height=5, width=50, font=("Arial", 10))
        self.input_text.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Permutation Count
        tk.Label(self.root, text="Max Words to Combine:", bg="#f0f0f0", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.perm_entry = tk.Entry(self.root, width=10, font=("Arial", 10))
        self.perm_entry.insert(0, "1")
        self.perm_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Min Length
        tk.Label(self.root, text="Min Password Length:", bg="#f0f0f0", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.min_entry = tk.Entry(self.root, width=10, font=("Arial", 10))
        self.min_entry.insert(0, "1")
        self.min_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Max Length
        tk.Label(self.root, text="Max Password Length:", bg="#f0f0f0", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.max_entry = tk.Entry(self.root, width=10, font=("Arial", 10))
        self.max_entry.insert(0, "10")
        self.max_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Mutagen Options
        tk.Label(self.root, text="Mutagen Options:", bg="#f0f0f0", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.leet_var = tk.BooleanVar()
        self.cap_var = tk.BooleanVar()
        self.up_var = tk.BooleanVar()
        self.sort_var = tk.BooleanVar()
        tk.Checkbutton(self.root, text="Leet Speak (e.g., o->0, a->@)", variable=self.leet_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=6, column=0, columnspan=2, padx=10, pady=2, sticky="w")
        tk.Checkbutton(self.root, text="Capitalize Words", variable=self.cap_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=7, column=0, columnspan=2, padx=10, pady=2, sticky="w")
        tk.Checkbutton(self.root, text="Uppercase Words", variable=self.up_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=8, column=0, columnspan=2, padx=10, pady=2, sticky="w")
        tk.Checkbutton(self.root, text="Sort by Length", variable=self.sort_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=9, column=0, columnspan=2, padx=10, pady=2, sticky="w")

        # Append
        tk.Label(self.root, text="Append Word:", bg="#f0f0f0", font=("Arial", 12)).grid(row=10, column=0, padx=10, pady=5, sticky="w")
        self.append_entry = tk.Entry(self.root, width=20, font=("Arial", 10))
        self.append_entry.grid(row=10, column=1, padx=5, pady=5, sticky="w")

        # Prepend
        tk.Label(self.root, text="Prepend Word:", bg="#f0f0f0", font=("Arial", 12)).grid(row=11, column=0, padx=10, pady=5, sticky="w")
        self.prepend_entry = tk.Entry(self.root, width=20, font=("Arial", 10))
        self.prepend_entry.grid(row=11, column=1, padx=5, pady=5, sticky="w")

        # Run Button
        tk.Button(self.root, text="Generate Wordlist", command=self.run_wordlister, bg="#4CAF50", fg="white", font=("Arial", 12)).grid(row=12, column=0, columnspan=3, pady=20)

        # Status Label
        self.status_label = tk.Label(self.root, text="Output will be saved as ver.txt in script directory", bg="#f0f0f0", font=("Arial", 10))
        self.status_label.grid(row=13, column=0, columnspan=3, pady=10)

    def run_wordlister(self):
        try:
            # Collect parameters
            self.params['input'] = self.input_text.get("1.0", tk.END).strip()
            self.params['perm'] = self.perm_entry.get().strip()
            self.params['min'] = self.min_entry.get().strip()
            self.params['max'] = self.max_entry.get().strip()
            self.params['leet'] = self.leet_var.get()
            self.params['cap'] = self.cap_var.get()
            self.params['up'] = self.up_var.get()
            self.params['append'] = self.append_entry.get().strip()
            self.params['prepend'] = self.prepend_entry.get().strip()
            self.params['sort'] = self.sort_var.get()

            # Validate inputs
            if not self.params['input'].strip():
                raise ValueError("Please enter at least one word!")
            if not self.params['perm'].isdigit() or int(self.params['perm']) < 1:
                raise ValueError("Max words to combine must be a positive integer!")
            if not self.params['min'].isdigit() or int(self.params['min']) < 1:
                raise ValueError("Minimum length must be a positive integer!")
            if not self.params['max'].isdigit() or int(self.params['max']) < int(self.params['min']):
                raise ValueError("Maximum length must be a positive integer and >= minimum length!")

            # Run Wordlister
            wordlister = Wordlister(self.params)
            wordlister.run()
            self.status_label.config(text=f"Success! Output saved to {self.params['output']}", fg="green")
            messagebox.showinfo("Success", f"Wordlist generated and saved to {self.params['output']}")

        except ValueError as e:
            self.status_label.config(text=str(e), fg="red")
            messagebox.showerror("Error", str(e))
        except Exception as e:
            self.status_label.config(text="An unexpected error occurred!", fg="red")
            messagebox.showerror("Error", "An unexpected error occurred: " + str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = WordlisterGUI(root)
    root.mainloop()
