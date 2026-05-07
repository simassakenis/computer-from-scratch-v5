import tkinter as tk
import time


console_address = 1024
memory = [0] * (console_address + 128 * 32)
console_pointer = console_address


class TkScreen:
    def __init__(self):
        self.pending_key = None
        self.root = tk.Tk()
        self.root.title("Minimal Computer Console")

        self.label = tk.Label(
            self.root,
            bg="white",
            fg="black",
            font=("Menlo", 14),
            justify="left",
            anchor="nw",
        )
        self.label.pack()
        self.root.bind("<KeyPress>", self.on_key)

    def on_key(self, event):
        if event.char:
            self.pending_key = ord(event.char)

    def read_key(self):
        self.root.update()

        key = self.pending_key
        self.pending_key = None
        return key

    def draw(self, cells):
        rows = []
        for y in range(32):
            start = y * 128
            row = cells[start : start + 128]
            rows.append("".join(chr(cell) for cell in row))

        self.label["text"] = "\n".join(rows)
        self.root.update_idletasks()


def keyboard_step(screen):
    key = screen.read_key()

    if key is not None:
        memory[0] = key
        memory[1] = 1


def cpu_step():
    global console_pointer

    if memory[1] == 1:
        memory[console_pointer] = memory[0]
        memory[1] = 0
        console_pointer += 1

        if console_pointer == console_address + 128 * 32:
            console_pointer = console_address


def console_step(screen):
    screen.draw(memory[console_address : console_address + 128 * 32])


if __name__ == "__main__":
    memory[0] = ord(" ")
    memory[1] = 0
    memory[console_address : console_address + 128 * 32] = [ord(" ")] * (128 * 32)
    screen = TkScreen()

    while True:
        keyboard_step(screen)
        cpu_step()
        console_step(screen)
        time.sleep(0.05)
