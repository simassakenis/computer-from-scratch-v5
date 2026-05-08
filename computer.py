import tkinter as tk
import time


console_address = 1000072

def as8(value):
    # Store one machine value as 8 big-endian bytes
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
    # Read 8 memory bytes back into one signed 64-bit machine value
    result = 0
    for byte in value:
        result = result * 256 + byte
    if result >= 2**63:
        result -= 2**64
    return result


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

    def draw(self, memory):
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


def keyboard_step(memory, screen):
    key = screen.read_key()

    waiting_for_keypress = asint(memory[1000048 : 1000048 + 8])

    if waiting_for_keypress == 1 and key is not None:
        memory[1000056 : 1000056 + 8] = as8(key)
        memory[1000048 : 1000048 + 8] = [0] * 8
    return memory


def cpu_step(memory, equal_flag, greater_flag):
    # Fetch one 24-byte instruction: opcode, operand1, operand2
    instruction_pointer = asint(memory[0:8])
    opcode = asint(memory[instruction_pointer : instruction_pointer + 8])
    operand1 = asint(memory[instruction_pointer + 8 : instruction_pointer + 16])
    operand2 = asint(memory[instruction_pointer + 16 : instruction_pointer + 24])

    # Slots are addressed relative to the current base pointer
    base_pointer = asint(memory[8:16])
    stack_top_pointer = asint(memory[16:24])

    if opcode == 0:
        # idle: do nothing and keep pointing at this instruction
        memory[0:8] = as8(instruction_pointer)
    elif opcode == 1:
        # move: slot(operand2) = slot(operand1)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = memory[
            base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8
        ]
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 2:
        # moveNumber: slot(operand2) = operand1
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(operand1)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 3:
        # moveFromPointer: slot(operand2) = value at address slot(operand1)
        address = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = memory[address : address + 8]
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 4:
        # moveToPointer: value at address slot(operand2) = slot(operand1)
        address = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        memory[address : address + 8] = memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8]
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 5:
        # add: slot(operand2) = slot(operand2) + slot(operand1)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (a + b) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 6:
        # addNumber: slot(operand2) = slot(operand2) + operand1
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (value + operand1) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 7:
        # subtract: slot(operand2) = slot(operand2) - slot(operand1)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (b - a) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 8:
        # shiftLeft: slot(operand2) = slot(operand2) << slot(operand1)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (b << a) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 9:
        # shiftLeftByNumber: slot(operand2) = slot(operand2) << operand1
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (value << operand1) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 10:
        # shiftRight: slot(operand2) = slot(operand2) >> slot(operand1)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (b % (2**64)) >> a
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 11:
        # shiftRightByNumber: slot(operand2) = slot(operand2) >> operand1
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (value % (2**64)) >> operand1
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 12:
        # bitwiseAnd: slot(operand2) = slot(operand2) & slot(operand1)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = a & b
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 13:
        # bitwiseAndWithNumber: slot(operand2) = slot(operand2) & operand1
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = value & operand1
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 14:
        # pushNumber: write operand1 at stack top, then advance stack top
        memory[stack_top_pointer : stack_top_pointer + 8] = as8(operand1)
        stack_top_pointer += 8
        memory[16:24] = as8(stack_top_pointer)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 15:
        # compare: set ALU flags by comparing slot(operand1) to slot(operand2)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        equal_flag = 1 if a == b else 0
        greater_flag = 1 if a > b else 0
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 16:
        # compareToNumber: set ALU flags by comparing slot(operand1) to operand2
        value = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        equal_flag = 1 if value == operand2 else 0
        greater_flag = 1 if value > operand2 else 0
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 17:
        # jumpIfEqual: jump to operand1 if the equal flag is set
        if equal_flag == 1:
            memory[0:8] = as8(operand1)
        else:
            memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 18:
        # jumpIfGreater: jump to operand1 if the greater flag is set
        if greater_flag == 1:
            memory[0:8] = as8(operand1)
        else:
            memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 19:
        # jump: set instruction pointer to operand1
        memory[0:8] = as8(operand1)
    elif opcode == 20:
        # call: push return address and old base, set new base, then jump
        return_address = instruction_pointer + 24
        old_base_pointer = base_pointer
        # Push return address
        memory[stack_top_pointer : stack_top_pointer + 8] = as8(return_address)
        # Push old base pointer
        memory[stack_top_pointer + 8 : stack_top_pointer + 16] = as8(old_base_pointer)
        # Set base pointer to the callee frame
        memory[8:16] = as8(stack_top_pointer + 16)
        # Set stack top to the callee frame
        memory[16:24] = as8(stack_top_pointer + 16)
        # Jump to callee
        memory[0:8] = as8(operand1)
    elif opcode == 21:
        # return: restore return address, base pointer, and stack top
        return_address = asint(memory[base_pointer - 16 : base_pointer - 8])
        old_base_pointer = asint(memory[base_pointer - 8 : base_pointer])
        new_stack_top_pointer = base_pointer - 16
        # Restore old base pointer
        memory[8:16] = as8(old_base_pointer)
        # Restore stack top to before return address
        memory[16:24] = as8(new_stack_top_pointer)
        # Jump back to caller
        memory[0:8] = as8(return_address)
    return memory, equal_flag, greater_flag


def console_step(memory, screen):
    screen.draw(memory)
    return memory


if __name__ == "__main__":
    # Memory and disk are byte arrays: every element is one integer from 0 to 255
    disk = [0] * 4000000
    memory = [0] * len(disk)

    for address, value in [
        (0, 24),
        (8, 500000),
        (16, 500000),
    ]:
        disk[address : address + 8] = as8(value)

    memory[:] = disk[:]
    equal_flag = 0
    greater_flag = 0
    screen = TkScreen()

    while True:
        memory = keyboard_step(memory, screen)
        memory, equal_flag, greater_flag = cpu_step(memory, equal_flag, greater_flag)
        memory = console_step(memory, screen)
        time.sleep(0.05)
