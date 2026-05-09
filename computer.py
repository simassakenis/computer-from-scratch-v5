import tkinter as tk


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


def assemble(source):
    opcodes = {
        "move": 1,
        "moveNumber": 2,
        "moveFromPointer": 3,
        "moveToPointer": 4,
        "add": 5,
        "addNumber": 6,
        "subtract": 7,
        "shiftLeft": 8,
        "shiftLeftByNumber": 9,
        "shiftRight": 10,
        "shiftRightByNumber": 11,
        "bitwiseAnd": 12,
        "bitwiseAndWithNumber": 13,
        "pushNumber": 14,
        "pop": 15,
        "compare": 16,
        "compareToNumber": 17,
        "jumpIfEqual": 18,
        "jumpIfGreater": 19,
        "jump": 20,
        "call": 21,
        "return": 22,
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
        if parts[0] in opcodes:
            address += 24
        else:
            address += 8 * len(parts)
        lines.append(parts)

    address = 0
    for parts in lines:
        values = parts

        if parts[0] in opcodes:
            values = [opcodes[parts[0]], *parts[1:]]
            values += [0] * (3 - len(values))

        for value in values:
            value = labels[value] if value in labels else int(value)
            disk[address : address + 8] = as8(value)
            address += 8

    return disk


operating_system_source = """
instructionPointerStartValue
    24
basePointerStartValue
    500000
stackPointerStartValue
    500000
terminal
    pushNumber 1000064
    pushNumber 1000072
    moveToPointer 1 0
    moveNumber 1000000 0
    moveNumber 2000000 1
    moveToPointer 1 0
    moveFromPointer 0 1
    pushNumber 0
    jump terminalLoop
terminalLoop
    call listenForKeypress
    compareToNumber 2 8
    jumpIfEqual ifBackspace
    jump elseBackspace
ifBackspace
    pushNumber 0
    moveFromPointer 0 3
    compare 3 1
    jumpIfGreater ifNonEmptyInput
    pop
    jump terminalLoop
ifNonEmptyInput
    call removeLastCharacterFromTranscript
    pop
    jump terminalLoop
elseBackspace
    compareToNumber 2 10
    jumpIfEqual ifEnter
    jump elseBackspaceElseEnter
ifEnter
    pushNumber 0
    pushNumber 0
    move 1 4
    call parse8ByteValue
    moveNumber 0 4
    pushNumber 0
    move 1 5
    addNumber 128 5
    call parse8ByteValue
    addNumber 128 5
    pushNumber 0
    moveFromPointer 0 6
    subtract 5 6
    pushNumber 0
    move 3 7
    pushNumber 3000000
    pushNumber 0
    move 4 9
    call readFromDisk
    moveNumber 16 7
    moveFromPointer 7 8
    moveNumber 3000000 9
    add 4 9
    moveToPointer 5 9
    addNumber 8 9
    moveToPointer 6 9
    addNumber 8 9
    moveToPointer 9 7
    call 3000000
    moveToPointer 8 7
    moveFromPointer 0 1
    pop
    pop
    pop
    pop
    pop
    pop
    pop
    jump terminalLoop
elseBackspaceElseEnter
    call writeToTranscript
    jump terminalLoop
listenForKeypress
    pushNumber 1000048
    pushNumber 1
    moveToPointer 1 0
    jump listenForKeypressLoop
listenForKeypressLoop
    moveFromPointer 0 1
    compareToNumber 1 0
    jumpIfEqual listenForKeypressLoopExit
    jump listenForKeypressLoop
listenForKeypressLoopExit
    moveNumber 1000056 1
    moveFromPointer 1 -3
    return
removeLastCharacterFromTranscript
    pushNumber 1000000
    pushNumber 0
    moveFromPointer 0 1
    compareToNumber 1 2000000
    jumpIfGreater regularRemoveLastCharacter
    jump removeLastCharacterExit
regularRemoveLastCharacter
    pushNumber 0
    addNumber -8 1
    moveToPointer 2 1
    moveToPointer 1 0
    jump removeLastCharacterFromConsole
removeLastCharacterFromConsole
    moveNumber 1000064 0
    moveFromPointer 0 1
    compareToNumber 1 1000072
    jumpIfGreater regularRemoveLastCharacterFromConsole
    jump removeLastCharacterExit
regularRemoveLastCharacterFromConsole
    addNumber -8 1
    moveToPointer 2 1
    moveToPointer 1 0
    jump removeLastCharacterExit
removeLastCharacterExit
    return
writeToTranscript
    pushNumber 1000000
    pushNumber 0
    moveFromPointer 0 1
    moveToPointer -3 1
    addNumber 8 1
    moveToPointer 1 0
    jump writeToConsole
writeToConsole
    moveNumber 1000064 0
    moveFromPointer 0 1
    compareToNumber 1 1032840
    jumpIfEqual shiftConsoleBack
    jump regularWriteToConsole
shiftConsoleBack
    addNumber -8 1
    pushNumber 1000080
    pushNumber 1000072
    pushNumber 0
    jump shiftConsoleBackLoop
shiftConsoleBackLoop
    moveFromPointer 2 4
    moveToPointer 4 3
    addNumber 8 2
    addNumber 8 3
    compareToNumber 2 1032840
    jumpIfEqual regularWriteToConsole
    jump shiftConsoleBackLoop
regularWriteToConsole
    moveToPointer -3 1
    addNumber 8 1
    moveToPointer 1 0
    return
readFromDisk
    pushNumber 1000008
    moveToPointer -5 0
    moveNumber 1000016 0
    moveToPointer -4 0
    moveNumber 1000024 0
    moveToPointer -3 0
    moveNumber 1000032 0
    pushNumber 1
    moveToPointer 1 0
    jump readFromDiskLoop
readFromDiskLoop
    moveFromPointer 0 1
    compareToNumber 1 0
    jumpIfEqual readFromDiskLoopExit
    jump readFromDiskLoop
readFromDiskLoopExit
    return
writeToDisk
    pushNumber 1000008
    moveToPointer -5 0
    moveNumber 1000016 0
    moveToPointer -4 0
    moveNumber 1000024 0
    moveToPointer -3 0
    moveNumber 1000040 0
    pushNumber 1
    moveToPointer 1 0
    jump writeToDiskLoop
writeToDiskLoop
    moveFromPointer 0 1
    compareToNumber 1 0
    jumpIfEqual writeToDiskLoopExit
    jump writeToDiskLoop
writeToDiskLoopExit
    return
readFromDiskProgram
    compareToNumber -3 256
    jumpIfEqual readFromDiskProgramValidInput
    jump readFromDiskProgramInvalidInput
readFromDiskProgramInvalidInput
    return
readFromDiskProgramValidInput
    pushNumber 0
    pushNumber 0
    move -4 1
    call parse8ByteValue
    pushNumber 0
    move -4 2
    addNumber 128 2
    call parse8ByteValue
    moveNumber 8 2
    pushNumber 0
    moveFromPointer 2 3
    addNumber 56 3
    pushNumber 0
    move 3 4
    add 1 4
    pushNumber 0
    move 4 5
    moveToPointer 0 5
    addNumber 8 5
    moveToPointer 3 5
    addNumber 8 5
    moveToPointer 1 5
    addNumber 8 5
    pushNumber 16
    moveToPointer 5 6
    call readFromDisk
    addNumber -8 5
    move 3 0
    move 4 1
    addNumber -8 1
    jump readFromDiskProgramPrintLoop
readFromDiskProgramPrintLoop
    compare 0 1
    jumpIfGreater readFromDiskProgramPrintLoopExit
    jump readFromDiskProgramPrintLoopBody
readFromDiskProgramPrintLoopBody
    moveFromPointer 0 2
    moveToPointer 2 5
    call print8ByteValue
    addNumber 8 0
    jump readFromDiskProgramPrintLoop
readFromDiskProgramPrintLoopExit
    return
writeToDiskProgram
    compareToNumber -3 128
    jumpIfGreater writeToDiskProgramValidInput
    jump writeToDiskProgramInvalidInput
writeToDiskProgramInvalidInput
    return
writeToDiskProgramValidInput
    pushNumber 0
    pushNumber 0
    move -4 1
    call parse8ByteValue
    addNumber 128 1
    pushNumber 8
    pushNumber 0
    moveFromPointer 2 3
    addNumber 56 3
    pushNumber 0
    move 3 4
    addNumber 8 4
    pushNumber 0
    move 3 5
    addNumber 16 5
    pushNumber 0
    move -4 6
    add -3 6
    addNumber -16 6
    moveNumber 16 2
    jump writeToDiskProgramReadLoop
writeToDiskProgramReadLoop
    compare 1 6
    jumpIfGreater writeToDiskProgramReadLoopExit
    jump writeToDiskProgramReadLoopBody
writeToDiskProgramReadLoopBody
    moveToPointer 1 4
    moveToPointer 5 1
    call parse8ByteValue
    addNumber 16 1
    addNumber 8 4
    addNumber 8 5
    jump writeToDiskProgramReadLoop
writeToDiskProgramReadLoopExit
    addNumber -8 4
    move 4 5
    subtract 3 5
    moveToPointer 0 4
    addNumber 8 4
    moveToPointer 3 4
    addNumber 8 4
    moveToPointer 5 4
    addNumber 8 4
    moveToPointer 4 2
    call writeToDisk
    return
parse8ByteValue
    pushNumber 0
    move -3 0
    pushNumber 0
    move -3 1
    addNumber 120 1
    pushNumber 0
    pushNumber 0
    pushNumber 0
    jump parse8ByteValueLoop
parse8ByteValueLoop
    compare 0 1
    jumpIfGreater parse8ByteValueLoopExit
    jump parse8ByteValueLoopBody
parse8ByteValueLoopBody
    moveFromPointer 0 3
    moveNumber 0 4
    compareToNumber 3 48
    jumpIfEqual parse8ByteValueLoopBody0
    compareToNumber 3 49
    jumpIfEqual parse8ByteValueLoopBody1
    compareToNumber 3 50
    jumpIfEqual parse8ByteValueLoopBody2
    compareToNumber 3 51
    jumpIfEqual parse8ByteValueLoopBody3
    compareToNumber 3 52
    jumpIfEqual parse8ByteValueLoopBody4
    compareToNumber 3 53
    jumpIfEqual parse8ByteValueLoopBody5
    compareToNumber 3 54
    jumpIfEqual parse8ByteValueLoopBody6
    compareToNumber 3 55
    jumpIfEqual parse8ByteValueLoopBody7
    compareToNumber 3 56
    jumpIfEqual parse8ByteValueLoopBody8
    compareToNumber 3 57
    jumpIfEqual parse8ByteValueLoopBody9
    compareToNumber 3 97
    jumpIfEqual parse8ByteValueLoopBody10
    compareToNumber 3 98
    jumpIfEqual parse8ByteValueLoopBody11
    compareToNumber 3 99
    jumpIfEqual parse8ByteValueLoopBody12
    compareToNumber 3 100
    jumpIfEqual parse8ByteValueLoopBody13
    compareToNumber 3 101
    jumpIfEqual parse8ByteValueLoopBody14
    compareToNumber 3 102
    jumpIfEqual parse8ByteValueLoopBody15
parse8ByteValueLoopBody0
    moveNumber 0 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody1
    moveNumber 1 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody2
    moveNumber 2 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody3
    moveNumber 3 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody4
    moveNumber 4 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody5
    moveNumber 5 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody6
    moveNumber 6 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody7
    moveNumber 7 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody8
    moveNumber 8 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody9
    moveNumber 9 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody10
    moveNumber 10 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody11
    moveNumber 11 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody12
    moveNumber 12 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody13
    moveNumber 13 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody14
    moveNumber 14 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBody15
    moveNumber 15 4
    jump parse8ByteValueLoopBodyContinue
parse8ByteValueLoopBodyContinue
    shiftLeftByNumber 4 2
    add 4 2
    addNumber 8 0
    jump parse8ByteValueLoop
parse8ByteValueLoopExit
    move 2 -4
    return
print8ByteValue
    pushNumber 60
    pushNumber 0
    pushNumber 0
    jump print8ByteValueLoop
print8ByteValueLoop
    compareToNumber 0 0
    jumpIfGreater print8ByteValueLoopBody
    compareToNumber 0 0
    jumpIfEqual print8ByteValueLoopBody
    jump print8ByteValueLoopExit
print8ByteValueLoopBody
    move -3 1
    shiftRight 0 1
    bitwiseAndWithNumber 15 1
    moveNumber 48 2
    compareToNumber 1 0
    jumpIfEqual print8ByteValueLoopBody0
    compareToNumber 1 1
    jumpIfEqual print8ByteValueLoopBody1
    compareToNumber 1 2
    jumpIfEqual print8ByteValueLoopBody2
    compareToNumber 1 3
    jumpIfEqual print8ByteValueLoopBody3
    compareToNumber 1 4
    jumpIfEqual print8ByteValueLoopBody4
    compareToNumber 1 5
    jumpIfEqual print8ByteValueLoopBody5
    compareToNumber 1 6
    jumpIfEqual print8ByteValueLoopBody6
    compareToNumber 1 7
    jumpIfEqual print8ByteValueLoopBody7
    compareToNumber 1 8
    jumpIfEqual print8ByteValueLoopBody8
    compareToNumber 1 9
    jumpIfEqual print8ByteValueLoopBody9
    compareToNumber 1 10
    jumpIfEqual print8ByteValueLoopBody10
    compareToNumber 1 11
    jumpIfEqual print8ByteValueLoopBody11
    compareToNumber 1 12
    jumpIfEqual print8ByteValueLoopBody12
    compareToNumber 1 13
    jumpIfEqual print8ByteValueLoopBody13
    compareToNumber 1 14
    jumpIfEqual print8ByteValueLoopBody14
    compareToNumber 1 15
    jumpIfEqual print8ByteValueLoopBody15
print8ByteValueLoopBody0
    moveNumber 48 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody1
    moveNumber 49 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody2
    moveNumber 50 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody3
    moveNumber 51 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody4
    moveNumber 52 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody5
    moveNumber 53 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody6
    moveNumber 54 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody7
    moveNumber 55 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody8
    moveNumber 56 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody9
    moveNumber 57 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody10
    moveNumber 97 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody11
    moveNumber 98 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody12
    moveNumber 99 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody13
    moveNumber 100 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody14
    moveNumber 101 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBody15
    moveNumber 102 2
    jump print8ByteValueLoopBodyContinue
print8ByteValueLoopBodyContinue
    call writeToTranscript
    addNumber -4 0
    jump print8ByteValueLoop
print8ByteValueLoopExit
    return
"""


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
        if event.keysym == "Return":
            self.pending_key = 10
        elif event.keysym == "BackSpace":
            self.pending_key = 8
        elif event.char:
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
                if value == 0:
                    value = ord(" ")
                row.append(chr(value & 255))
            rows.append("".join(row))

        self.label["text"] = "\n".join(rows)
        self.root.update_idletasks()


def keyboard_step(memory, tkinter_window):
    key = tkinter_window.read_key()

    waiting_for_keypress = asint(memory[1000048 : 1000048 + 8])

    if waiting_for_keypress == 1 and key is not None:
        memory[1000056 : 1000056 + 8] = as8(key)
        memory[1000048 : 1000048 + 8] = [0] * 8
    return memory


def disk_step(memory, disk):
    is_waiting_for_disk_read = asint(memory[1000032 : 1000032 + 8])
    is_waiting_for_disk_write = asint(memory[1000040 : 1000040 + 8])

    if is_waiting_for_disk_read == 1:
        disk_address = asint(memory[1000008 : 1000008 + 8])
        memory_address = asint(memory[1000016 : 1000016 + 8])
        num_bytes = asint(memory[1000024 : 1000024 + 8])
        memory[memory_address : memory_address + num_bytes] = disk[disk_address : disk_address + num_bytes]
        memory[1000032 : 1000032 + 8] = as8(0)

    if is_waiting_for_disk_write == 1:
        disk_address = asint(memory[1000008 : 1000008 + 8])
        memory_address = asint(memory[1000016 : 1000016 + 8])
        num_bytes = asint(memory[1000024 : 1000024 + 8])
        disk[disk_address : disk_address + num_bytes] = memory[memory_address : memory_address + num_bytes]
        memory[1000040 : 1000040 + 8] = as8(0)

    return memory, disk


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
        # pop: move stack top back by one slot
        stack_top_pointer -= 8
        memory[16:24] = as8(stack_top_pointer)
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 16:
        # compare: set ALU flags by comparing slot(operand1) to slot(operand2)
        a = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        b = asint(memory[base_pointer + operand2 * 8 : base_pointer + operand2 * 8 + 8])
        equal_flag = 1 if a == b else 0
        greater_flag = 1 if a > b else 0
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 17:
        # compareToNumber: set ALU flags by comparing slot(operand1) to operand2
        value = asint(memory[base_pointer + operand1 * 8 : base_pointer + operand1 * 8 + 8])
        equal_flag = 1 if value == operand2 else 0
        greater_flag = 1 if value > operand2 else 0
        memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 18:
        # jumpIfEqual: jump to operand1 if the equal flag is set
        if equal_flag == 1:
            memory[0:8] = as8(operand1)
        else:
            memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 19:
        # jumpIfGreater: jump to operand1 if the greater flag is set
        if greater_flag == 1:
            memory[0:8] = as8(operand1)
        else:
            memory[0:8] = as8(instruction_pointer + 24)
    elif opcode == 20:
        # jump: set instruction pointer to operand1
        memory[0:8] = as8(operand1)
    elif opcode == 21:
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
    elif opcode == 22:
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


def console_step(memory, tkinter_window):
    tkinter_window.draw(memory)


if __name__ == "__main__":
    # Tkinter receives keypresses and renders the memory-mapped console
    tkinter_window = TkScreen()

    # Memory and disk are byte arrays: every element is one integer from 0 to 255
    disk = assemble(operating_system_source)
    memory = [0] * 5000000

    # Power-on loads the plugged-in disk image into memory
    memory[: len(disk)] = disk[:]
    equal_flag = 0
    greater_flag = 0

    while True:
        memory = keyboard_step(memory, tkinter_window)
        memory, equal_flag, greater_flag = cpu_step(memory, equal_flag, greater_flag)
        memory, disk = disk_step(memory, disk)
        console_step(memory, tkinter_window)
