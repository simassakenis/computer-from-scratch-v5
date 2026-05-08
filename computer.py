import tkinter as tk
import time


console_address = 1000072

# Memory and disk are byte arrays: every element is one integer from 0 to 255.
memory = [0] * 4000000
disk = [0] * len(memory)


def as8(value):
    # Store one machine value as 8 big-endian bytes.
    value = value % (2**64)
    return [
        (value >> 56) & 255,
        (value >> 48) & 255,
        (value >> 40) & 255,
        (value >> 32) & 255,
        (value >> 24) & 255,
        (value >> 16) & 255,
        (value >> 8) & 255,
        value & 255,
    ]


def asint(value):
    # Read 8 memory bytes back into one signed 64-bit machine value.
    result = 0
    for byte in value:
        result = result * 256 + byte
    if result >= 2**63:
        result -= 2**64
    return result


for address, value in [
    (0, 24),
    (8, 500000),
    (16, 500000),
]:
    disk[address : address + 8] = as8(value)

for address in range(console_address, console_address + 128 * 32 * 8, 8):
    disk[address : address + 8] = [0, 0, 0, 0, 0, 0, 0, ord(" ")]


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

    def draw(self):
        rows = []
        for y in range(32):
            row = []
            for x in range(128):
                address = console_address + (y * 128 + x) * 8
                value = asint(memory[address : address + 8])
                row.append(chr(value & 255))
            rows.append("".join(row))

        self.label["text"] = "\n".join(rows)
        self.root.update_idletasks()


def keyboard_step(screen):
    key = screen.read_key()

    waiting_for_keypress = asint(memory[1000048 : 1000048 + 8])

    if waiting_for_keypress == 1 and key is not None:
        memory[1000056 : 1000056 + 8] = as8(key)
        memory[1000048 : 1000048 + 8] = [0] * 8


def cpu_step(memory, equal_flag, greater_flag):
    # Fetch one 24-byte instruction: opcode, operand1, operand2.
    instruction_pointer = asint(memory[0:8])
    opcode = asint(memory[instruction_pointer : instruction_pointer + 8])
    operand1 = asint(memory[instruction_pointer + 8 : instruction_pointer + 16])
    operand2 = asint(memory[instruction_pointer + 16 : instruction_pointer + 24])

    # Slots are addressed relative to the current base pointer.
    base_pointer = asint(memory[8:16])
    stack_top_pointer = asint(memory[16:24])

    advance_instruction_pointer = True

    if opcode == 0:
        # idle: do nothing and keep pointing at this instruction.
        advance_instruction_pointer = False
    elif opcode == 1:
        # move: slot(operand2) = slot(operand1).
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = memory[
            base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8
        ]
    elif opcode == 2:
        # moveNumber: slot(operand2) = operand1.
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(operand1)
    elif opcode == 3:
        # moveFromPointer: slot(operand2) = value at address slot(operand1).
        address = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = memory[address : address + 8]
    elif opcode == 4:
        # moveToPointer: value at address slot(operand2) = slot(operand1).
        address = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        memory[address : address + 8] = memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8]
    elif opcode == 5:
        # add: slot(operand2) = slot(operand2) + slot(operand1).
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (a + b) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
    elif opcode == 6:
        # addNumber: slot(operand2) = slot(operand2) + operand1.
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (value + operand1) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
    elif opcode == 7:
        # subtract: slot(operand2) = slot(operand2) - slot(operand1).
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (b - a) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
    elif opcode == 8:
        # shiftLeft: slot(operand2) = slot(operand2) << slot(operand1).
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (b << a) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
    elif opcode == 9:
        # shiftLeftByNumber: slot(operand2) = slot(operand2) << operand1.
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (value << operand1) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
    elif opcode == 10:
        # shiftRight: slot(operand2) = slot(operand2) >> slot(operand1).
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (b % (2**64)) >> a
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
    elif opcode == 11:
        # shiftRightByNumber: slot(operand2) = slot(operand2) >> operand1.
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (value % (2**64)) >> operand1
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
    elif opcode == 12:
        # bitwiseAnd: slot(operand2) = slot(operand2) & slot(operand1).
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = a & b
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
    elif opcode == 13:
        # bitwiseAndWithNumber: slot(operand2) = slot(operand2) & operand1.
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = value & operand1
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
    elif opcode == 14:
        # pushNumber: write operand1 at stack top, then advance stack top.
        memory[stack_top_pointer : stack_top_pointer + 8] = as8(operand1)
        stack_top_pointer += 8
        memory[16:24] = as8(stack_top_pointer)
    elif opcode == 15:
        # compare: set ALU flags by comparing slot(operand1) to slot(operand2).
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        equal_flag = 1 if a == b else 0
        greater_flag = 1 if a > b else 0
    elif opcode == 16:
        # compareToNumber: set ALU flags by comparing slot(operand1) to operand2.
        value = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        equal_flag = 1 if value == operand2 else 0
        greater_flag = 1 if value > operand2 else 0
    elif opcode == 17:
        # jumpIfEqual: jump to operand1 if the equal flag is set.
        if equal_flag == 1:
            instruction_pointer = operand1
            advance_instruction_pointer = False
    elif opcode == 18:
        # jumpIfGreater: jump to operand1 if the greater flag is set.
        if greater_flag == 1:
            instruction_pointer = operand1
            advance_instruction_pointer = False
    elif opcode == 19:
        # jump: set instruction pointer to operand1.
        instruction_pointer = operand1
        advance_instruction_pointer = False
    elif opcode == 20:
        # call: push return address and old base, set new base, then jump.
        return_address = instruction_pointer + 24
        old_base_pointer = base_pointer
        for address, value in [
            (stack_top_pointer, return_address),
            (stack_top_pointer + 8, old_base_pointer),
            (8, stack_top_pointer + 16),
            (16, stack_top_pointer + 16),
        ]:
            memory[address : address + 8] = as8(value)
        instruction_pointer = operand1
        advance_instruction_pointer = False
    elif opcode == 21:
        # return: restore return address, base pointer, and stack top.
        return_address = asint(memory[base_pointer - 16 : base_pointer - 8])
        old_base_pointer = asint(memory[base_pointer - 8 : base_pointer])
        new_stack_top_pointer = base_pointer - 16
        for address, value in [
            (0, return_address),
            (8, old_base_pointer),
            (16, new_stack_top_pointer),
        ]:
            memory[address : address + 8] = as8(value)
        instruction_pointer = return_address
        advance_instruction_pointer = False

    if advance_instruction_pointer:
        instruction_pointer += 24

    memory[0:8] = as8(instruction_pointer)
    return memory, equal_flag, greater_flag


def console_step(screen):
    screen.draw()


if __name__ == "__main__":
    memory[:] = disk[:]
    equal_flag = 0
    greater_flag = 0
    screen = TkScreen()

    while True:
        keyboard_step(screen)
        memory, equal_flag, greater_flag = cpu_step(memory, equal_flag, greater_flag)
        console_step(screen)
        time.sleep(0.05)
