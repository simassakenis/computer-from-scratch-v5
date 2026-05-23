import tkinter as tk


# Runs the simulated computer until stopped
def run_computer():
    # Tkinter receives keypresses and renders the memory-mapped display
    tkinter_window = tkinter_window_init()

    # Memory and disk are byte arrays: every element is one integer from 0 to 255
    disk = assemble(open("os.txt").read())
    memory = [0] * 10000000

    # Power-on loads the sacred startup and operating system bytes into memory
    memory[:500000] = disk[:500000]
    equal_flag = 0
    greater_flag = 0

    while True:
        memory, equal_flag, greater_flag = cpu_step(memory, equal_flag, greater_flag)
        memory, disk = disk_step(memory, disk)
        memory = keyboard_step(memory, tkinter_window)
        display_step(memory, tkinter_window)


# Helper that executes one CPU instruction
def cpu_step(memory, equal_flag, greater_flag):
    # Assumes control registers live at 1000000, 1000008, and 1000016
    # Fetch one 24-byte instruction: opcode, operand1, operand2
    instruction_pointer = asint(memory[1000000 : 1000000 + 8])
    opcode = asint(memory[instruction_pointer : instruction_pointer + 8])
    operand1 = asint(memory[instruction_pointer + 8 : instruction_pointer + 16])
    operand2 = asint(memory[instruction_pointer + 16 : instruction_pointer + 24])

    # Slots are addressed relative to the current base pointer
    base_pointer = asint(memory[1000008 : 1000008 + 8])
    stack_top_pointer = asint(memory[1000016 : 1000016 + 8])

    if opcode == 0:
        # idle: do nothing and keep pointing at this instruction
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer)
    elif opcode == 1:
        # moveNumberToAddress: value at address operand2 = operand1
        memory[operand2 : operand2 + 8] = as8(operand1)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 2:
        # move: slot(operand2) = slot(operand1)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = memory[
            base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8
        ]
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 3:
        # moveNumber: slot(operand2) = operand1
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(operand1)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 4:
        # moveFromPointer: slot(operand2) = value at address slot(operand1)
        address = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = memory[address : address + 8]
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 5:
        # moveToPointer: value at address slot(operand2) = slot(operand1)
        address = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        memory[address : address + 8] = memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8]
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 6:
        # add: slot(operand2) = slot(operand2) + slot(operand1)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (a + b) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 7:
        # addNumber: slot(operand2) = slot(operand2) + operand1
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (value + operand1) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 8:
        # subtract: slot(operand2) = slot(operand2) - slot(operand1)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (b - a) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 9:
        # shiftLeft: slot(operand2) = slot(operand2) << slot(operand1)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (b << a) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 10:
        # shiftLeftByNumber: slot(operand2) = slot(operand2) << operand1
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (value << operand1) % (2**64)
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 11:
        # shiftRight: slot(operand2) = slot(operand2) >> slot(operand1)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (b % (2**64)) >> a
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 12:
        # shiftRightByNumber: slot(operand2) = slot(operand2) >> operand1
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = (value % (2**64)) >> operand1
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 13:
        # bitwiseAnd: slot(operand2) = slot(operand2) & slot(operand1)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = a & b
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 14:
        # bitwiseAndWithNumber: slot(operand2) = slot(operand2) & operand1
        value = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        value = value & operand1
        memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8] = as8(value)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 15:
        # pushNumber: write operand1 at stack top, then advance stack top
        memory[stack_top_pointer : stack_top_pointer + 8] = as8(operand1)
        stack_top_pointer += 8
        memory[1000016 : 1000016 + 8] = as8(stack_top_pointer)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 16:
        # pop: move stack top back by one slot
        stack_top_pointer -= 8
        memory[1000016 : 1000016 + 8] = as8(stack_top_pointer)
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 17:
        # compare: set ALU flags by comparing slot(operand1) to slot(operand2)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        equal_flag = 1 if a == b else 0
        greater_flag = 1 if a > b else 0
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 18:
        # compareToNumber: set ALU flags by comparing slot(operand1) to operand2
        value = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        equal_flag = 1 if value == operand2 else 0
        greater_flag = 1 if value > operand2 else 0
        memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 19:
        # jumpIfEqual: jump to operand1 if the equal flag is set
        if equal_flag == 1:
            memory[1000000 : 1000000 + 8] = as8(operand1)
        else:
            memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 20:
        # jumpIfGreater: jump to operand1 if the greater flag is set
        if greater_flag == 1:
            memory[1000000 : 1000000 + 8] = as8(operand1)
        else:
            memory[1000000 : 1000000 + 8] = as8(instruction_pointer + 24)
    elif opcode == 21:
        # jump: set instruction pointer to operand1
        memory[1000000 : 1000000 + 8] = as8(operand1)
    elif opcode == 22:
        # call: push return address and old base, set new base, then jump
        return_address = instruction_pointer + 24
        old_base_pointer = base_pointer
        # Push return address
        memory[stack_top_pointer : stack_top_pointer + 8] = as8(return_address)
        # Push old base pointer
        memory[stack_top_pointer + 8 : stack_top_pointer + 16] = as8(old_base_pointer)
        # Set base pointer to the callee frame
        memory[1000008 : 1000008 + 8] = as8(stack_top_pointer + 16)
        # Set stack top to the callee frame
        memory[1000016 : 1000016 + 8] = as8(stack_top_pointer + 16)
        # Jump to callee
        memory[1000000 : 1000000 + 8] = as8(operand1)
    elif opcode == 23:
        # return: restore return address, base pointer, and stack top
        return_address = asint(memory[base_pointer - 16 : base_pointer - 8])
        old_base_pointer = asint(memory[base_pointer - 8 : base_pointer])
        new_stack_top_pointer = base_pointer - 16
        # Restore old base pointer
        memory[1000008 : 1000008 + 8] = as8(old_base_pointer)
        # Restore stack top to before return address
        memory[1000016 : 1000016 + 8] = as8(new_stack_top_pointer)
        # Jump back to caller
        memory[1000000 : 1000000 + 8] = as8(return_address)
    return memory, equal_flag, greater_flag


# Helper that performs pending memory-mapped disk reads and writes
def disk_step(memory, disk):
    # Assumes disk IO uses 1000024 for disk address, 1000032 for memory address,
    # 1000040 for byte count, 1000048 for read waiting, and 1000056 for write waiting
    is_waiting_for_disk_read = asint(memory[1000048 : 1000048 + 8])
    is_waiting_for_disk_write = asint(memory[1000056 : 1000056 + 8])

    if is_waiting_for_disk_read == 1:
        disk_address = asint(memory[1000024 : 1000024 + 8])
        memory_address = asint(memory[1000032 : 1000032 + 8])
        num_bytes = asint(memory[1000040 : 1000040 + 8])
        memory[memory_address : memory_address + num_bytes] = disk[disk_address : disk_address + num_bytes]
        memory[1000048 : 1000048 + 8] = as8(0)

    if is_waiting_for_disk_write == 1:
        disk_address = asint(memory[1000024 : 1000024 + 8])
        memory_address = asint(memory[1000032 : 1000032 + 8])
        num_bytes = asint(memory[1000040 : 1000040 + 8])
        disk[disk_address : disk_address + num_bytes] = memory[memory_address : memory_address + num_bytes]
        memory[1000056 : 1000056 + 8] = as8(0)

    return memory, disk


# Helper that copies a pending Tkinter keypress into keyboard IO memory
def keyboard_step(memory, tkinter_window):
    # Assumes keyboard IO uses 1000064 for waiting and 1000072 for key value
    waiting_for_keypress = asint(memory[1000064 : 1000064 + 8])
    # Tkinter event processing is expensive, so only poll it when the OS is listening for input
    if waiting_for_keypress != 1:
        return memory

    tkinter_window["root"].update()
    key = tkinter_window["pending_key"]
    tkinter_window["pending_key"] = None

    if waiting_for_keypress == 1 and key is not None:
        memory[1000072 : 1000072 + 8] = as8(key)
        memory[1000064 : 1000064 + 8] = [0] * 8
    return memory


# Helper that renders display memory into the Tkinter window
def display_step(memory, tkinter_window):
    # Assumes 1000088 stores the next display write address and 1000096 starts a 128 by 32 display
    display_write_address = asint(memory[1000088 : 1000088 + 8])
    # Avoid redrawing the whole Tkinter display unless a display write changed it
    previous_display_write_address = tkinter_window.get("last_display_write_address")
    if previous_display_write_address == display_write_address:
        return
    # Avoid redrawing when the new printed character is Space
    if previous_display_write_address is not None and previous_display_write_address < display_write_address:
        last_added_character = asint(memory[display_write_address - 8 : display_write_address])
        if last_added_character == 32:
            tkinter_window["last_display_write_address"] = display_write_address
            return
    tkinter_window["last_display_write_address"] = display_write_address

    rows = []
    for y in range(32):
        row = []
        for x in range(128):
            address = 1000096 + (y * 128 + x) * 8
            value = asint(memory[address : address + 8])
            if value == 0:
                value = ord(" ")
            row.append(chr(value & 255))
        rows.append("".join(row))

    tkinter_window["label"]["text"] = "\n".join(rows)
    tkinter_window["root"].update_idletasks()


# Helper that initializes a minimal Tkinter-backed display window
def tkinter_window_init():
    tkinter_window = {}
    tkinter_window["pending_key"] = None
    tkinter_window["root"] = tk.Tk()
    tkinter_window["root"].title("")

    tkinter_window["label"] = tk.Label(
        tkinter_window["root"],
        bg="white",
        fg="black",
        font=("Menlo", 11),
        justify="left",
        anchor="nw",
    )
    tkinter_window["label"].pack()

    def on_key(event):
        if event.keysym == "Return":
            tkinter_window["pending_key"] = 10
        elif event.keysym == "BackSpace":
            tkinter_window["pending_key"] = 8
        elif event.char:
            tkinter_window["pending_key"] = ord(event.char)

    tkinter_window["root"].bind("<KeyPress>", on_key)
    tkinter_window["root"].lift()
    tkinter_window["root"].after(0, tkinter_window["root"].focus_force)
    return tkinter_window


# Helper that turns disk source text into the initial disk bytes
def assemble(source):
    opcodes = {
        "moveNumberToAddress": 1,
        "move": 2,
        "moveNumber": 3,
        "moveFromPointer": 4,
        "moveToPointer": 5,
        "add": 6,
        "addNumber": 7,
        "subtract": 8,
        "shiftLeft": 9,
        "shiftLeftByNumber": 10,
        "shiftRight": 11,
        "shiftRightByNumber": 12,
        "bitwiseAnd": 13,
        "bitwiseAndWithNumber": 14,
        "pushNumber": 15,
        "pop": 16,
        "compare": 17,
        "compareToNumber": 18,
        "jumpIfEqual": 19,
        "jumpIfGreater": 20,
        "jump": 21,
        "call": 22,
        "return": 23,
    }
    disk = [0] * 4000000
    labels = {}
    lines = []
    address = 0

    for raw_line in source.splitlines():
        line = raw_line.rstrip()
        if line == "":
            continue

        if not line[0].isspace():
            labels[line.rstrip(":")] = address
            continue

        parts = line.split()
        address += 8 * len(parts)
        lines.append(parts)

    address = 0
    for parts in lines:
        values = parts

        if parts[0] in opcodes:
            values = [opcodes[parts[0]], *parts[1:]]

        for value in values:
            value = labels[value] if value in labels else int(value)
            disk[address : address + 8] = as8(value)
            address += 8

    return disk


# Helper that turns one machine value into 8 memory bytes
def as8(value):
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


# Helper that turns 8 memory bytes into one signed machine value
def asint(value):
    result = 0
    for byte in value:
        result = result * 256 + byte
    if result >= 2**63:
        result -= 2**64
    return result


if __name__ == "__main__":
    run_computer()
