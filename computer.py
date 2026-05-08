import tkinter as tk
import time


console_address = 1000072

MOVE = 1
MOVE_NUMBER = 2
MOVE_FROM_POINTER = 3
MOVE_TO_POINTER = 4
ADD = 5
ADD_NUMBER = 6
SUBTRACT = 7
SHIFT_LEFT = 8
SHIFT_LEFT_BY_NUMBER = 9
SHIFT_RIGHT = 10
SHIFT_RIGHT_BY_NUMBER = 11
BITWISE_AND = 12
BITWISE_AND_WITH_NUMBER = 13
PUSH_NUMBER = 14
COMPARE = 15
COMPARE_TO_NUMBER = 16
JUMP_IF_EQUAL = 17
JUMP_IF_GREATER = 18
JUMP = 19
CALL = 20
RETURN = 21

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


def assemble(source, start_address):
    labels = {}
    address = start_address
    i = 0

    while i < len(source):
        if isinstance(source[i], str):
            labels[source[i]] = address
            i += 1
        else:
            address += 24
            i += 3

    program = []
    i = 0

    while i < len(source):
        if isinstance(source[i], str):
            i += 1
            continue

        opcode = source[i]
        operand1 = source[i + 1]
        operand2 = source[i + 2]

        if isinstance(operand1, str):
            operand1 = labels[operand1]
        if isinstance(operand2, str):
            operand2 = labels[operand2]

        program += as8(opcode)
        program += as8(operand1)
        program += as8(operand2)
        i += 3

    return program


operating_system_source = [
    "terminal",
    PUSH_NUMBER, 1000064, 0,
    PUSH_NUMBER, 1000072, 0,
    MOVE_TO_POINTER, 1, 0,
    MOVE_NUMBER, 1000000, 0,
    MOVE_NUMBER, 2000000, 1,
    MOVE_TO_POINTER, 1, 0,
    MOVE_FROM_POINTER, 0, 1,
    PUSH_NUMBER, 0, 0,
    JUMP, "terminalLoop", 0,

    "terminalLoop",
    CALL, "listenForKeypress", 0,
    COMPARE_TO_NUMBER, 2, 8,
    JUMP_IF_EQUAL, "ifBackspace", 0,
    JUMP, "elseBackspace", 0,

    "ifBackspace",
    PUSH_NUMBER, 0, 0,
    MOVE_FROM_POINTER, 0, 3,
    COMPARE, 3, 1,
    JUMP_IF_GREATER, "ifNonEmptyInput", 0,
    JUMP, "terminalLoop", 0,

    "ifNonEmptyInput",
    CALL, "removeLastCharacterFromTranscript", 0,
    JUMP, "terminalLoop", 0,

    "elseBackspace",
    CALL, "writeToTranscript", 0,
    COMPARE_TO_NUMBER, 2, 10,
    JUMP_IF_EQUAL, "ifEnter", 0,
    JUMP, "terminalLoop", 0,

    "ifEnter",
    PUSH_NUMBER, 0, 0,
    PUSH_NUMBER, 0, 0,
    MOVE, 1, 4,
    CALL, "parse8ByteValue", 0,
    MOVE_NUMBER, 0, 4,
    PUSH_NUMBER, 0, 0,
    MOVE, 1, 5,
    ADD_NUMBER, 128, 5,
    CALL, "parse8ByteValue", 0,
    ADD_NUMBER, 128, 5,
    PUSH_NUMBER, 0, 0,
    MOVE_FROM_POINTER, 0, 6,
    SUBTRACT, 5, 6,
    ADD_NUMBER, -8, 6,
    PUSH_NUMBER, 0, 0,
    MOVE, 3, 7,
    PUSH_NUMBER, 3000000, 0,
    PUSH_NUMBER, 0, 0,
    MOVE, 4, 9,
    CALL, "readFromDisk", 0,
    MOVE_NUMBER, 16, 7,
    MOVE_FROM_POINTER, 7, 8,
    MOVE_NUMBER, 3000000, 9,
    ADD, 4, 9,
    MOVE_TO_POINTER, 5, 9,
    ADD_NUMBER, 8, 9,
    MOVE_TO_POINTER, 6, 9,
    ADD_NUMBER, 8, 9,
    MOVE_TO_POINTER, 9, 7,
    CALL, 3000000, 0,
    MOVE_TO_POINTER, 8, 7,
    MOVE_FROM_POINTER, 0, 1,
    JUMP, "terminalLoop", 0,

    "listenForKeypress",
    PUSH_NUMBER, 1000048, 0,
    PUSH_NUMBER, 1, 0,
    MOVE_TO_POINTER, 1, 0,
    JUMP, "listenForKeypressLoop", 0,

    "listenForKeypressLoop",
    MOVE_FROM_POINTER, 0, 1,
    COMPARE_TO_NUMBER, 1, 0,
    JUMP_IF_EQUAL, "listenForKeypressLoopExit", 0,
    JUMP, "listenForKeypressLoop", 0,

    "listenForKeypressLoopExit",
    MOVE_NUMBER, 1000056, 1,
    MOVE_FROM_POINTER, 1, -3,
    RETURN, 0, 0,

    "removeLastCharacterFromTranscript",
    PUSH_NUMBER, 1000000, 0,
    PUSH_NUMBER, 0, 0,
    MOVE_FROM_POINTER, 0, 1,
    COMPARE_TO_NUMBER, 1, 2000000,
    JUMP_IF_GREATER, "regularRemoveLastCharacter", 0,
    JUMP, "removeLastCharacterExit", 0,

    "regularRemoveLastCharacter",
    PUSH_NUMBER, 0, 0,
    ADD_NUMBER, -8, 1,
    MOVE_TO_POINTER, 2, 1,
    MOVE_TO_POINTER, 1, 0,
    JUMP, "removeLastCharacterFromConsole", 0,

    "removeLastCharacterFromConsole",
    MOVE_NUMBER, 1000064, 0,
    MOVE_FROM_POINTER, 0, 1,
    COMPARE_TO_NUMBER, 1, 1000072,
    JUMP_IF_GREATER, "regularRemoveLastCharacterFromConsole", 0,
    JUMP, "removeLastCharacterExit", 0,

    "regularRemoveLastCharacterFromConsole",
    ADD_NUMBER, -8, 1,
    MOVE_TO_POINTER, 2, 1,
    MOVE_TO_POINTER, 1, 0,
    JUMP, "removeLastCharacterExit", 0,

    "removeLastCharacterExit",
    RETURN, 0, 0,

    "writeToTranscript",
    PUSH_NUMBER, 1000000, 0,
    PUSH_NUMBER, 0, 0,
    MOVE_FROM_POINTER, 0, 1,
    MOVE_TO_POINTER, -3, 1,
    ADD_NUMBER, 8, 1,
    MOVE_TO_POINTER, 1, 0,
    JUMP, "writeToConsole", 0,

    "writeToConsole",
    MOVE_NUMBER, 1000064, 0,
    MOVE_FROM_POINTER, 0, 1,
    COMPARE_TO_NUMBER, 1, 1032840,
    JUMP_IF_EQUAL, "shiftConsoleBack", 0,
    JUMP, "regularWriteToConsole", 0,

    "shiftConsoleBack",
    ADD_NUMBER, -8, 1,
    PUSH_NUMBER, 1000080, 0,
    PUSH_NUMBER, 1000072, 0,
    PUSH_NUMBER, 0, 0,
    JUMP, "shiftConsoleBackLoop", 0,

    "shiftConsoleBackLoop",
    MOVE_FROM_POINTER, 2, 4,
    MOVE_TO_POINTER, 4, 3,
    ADD_NUMBER, 8, 2,
    ADD_NUMBER, 8, 3,
    COMPARE_TO_NUMBER, 2, 1032840,
    JUMP_IF_EQUAL, "regularWriteToConsole", 0,
    JUMP, "shiftConsoleBackLoop", 0,

    "regularWriteToConsole",
    MOVE_TO_POINTER, -3, 1,
    ADD_NUMBER, 8, 1,
    MOVE_TO_POINTER, 1, 0,
    RETURN, 0, 0,

    "readFromDisk",
    PUSH_NUMBER, 1000008, 0,
    MOVE_TO_POINTER, -5, 0,
    MOVE_NUMBER, 1000016, 0,
    MOVE_TO_POINTER, -4, 0,
    MOVE_NUMBER, 1000024, 0,
    MOVE_TO_POINTER, -3, 0,
    MOVE_NUMBER, 1000032, 0,
    PUSH_NUMBER, 1, 0,
    MOVE_TO_POINTER, 1, 0,
    JUMP, "readFromDiskLoop", 0,

    "readFromDiskLoop",
    MOVE_FROM_POINTER, 0, 1,
    COMPARE_TO_NUMBER, 1, 0,
    JUMP_IF_EQUAL, "readFromDiskLoopExit", 0,
    JUMP, "readFromDiskLoop", 0,

    "readFromDiskLoopExit",
    RETURN, 0, 0,

    "writeToDisk",
    PUSH_NUMBER, 1000008, 0,
    MOVE_TO_POINTER, -5, 0,
    MOVE_NUMBER, 1000016, 0,
    MOVE_TO_POINTER, -4, 0,
    MOVE_NUMBER, 1000024, 0,
    MOVE_TO_POINTER, -3, 0,
    MOVE_NUMBER, 1000040, 0,
    PUSH_NUMBER, 1, 0,
    MOVE_TO_POINTER, 1, 0,
    JUMP, "writeToDiskLoop", 0,

    "writeToDiskLoop",
    MOVE_FROM_POINTER, 0, 1,
    COMPARE_TO_NUMBER, 1, 0,
    JUMP_IF_EQUAL, "writeToDiskLoopExit", 0,
    JUMP, "writeToDiskLoop", 0,

    "writeToDiskLoopExit",
    RETURN, 0, 0,

    "readFromDiskProgram",
    COMPARE_TO_NUMBER, -3, 256,
    JUMP_IF_EQUAL, "readFromDiskProgramValidInput", 0,
    JUMP, "readFromDiskProgramInvalidInput", 0,

    "readFromDiskProgramInvalidInput",
    RETURN, 0, 0,

    "readFromDiskProgramValidInput",
    PUSH_NUMBER, 0, 0,
    PUSH_NUMBER, 0, 0,
    MOVE, -4, 1,
    CALL, "parse8ByteValue", 0,
    PUSH_NUMBER, 0, 0,
    MOVE, -4, 2,
    ADD_NUMBER, 128, 2,
    CALL, "parse8ByteValue", 0,
    MOVE_NUMBER, 8, 2,
    PUSH_NUMBER, 0, 0,
    MOVE_FROM_POINTER, 2, 3,
    ADD_NUMBER, 56, 3,
    PUSH_NUMBER, 0, 0,
    MOVE, 3, 4,
    ADD, 1, 4,
    PUSH_NUMBER, 0, 0,
    MOVE, 4, 5,
    MOVE_TO_POINTER, 0, 5,
    ADD_NUMBER, 8, 5,
    MOVE_TO_POINTER, 3, 5,
    ADD_NUMBER, 8, 5,
    MOVE_TO_POINTER, 1, 5,
    ADD_NUMBER, 8, 5,
    PUSH_NUMBER, 16, 0,
    MOVE_TO_POINTER, 5, 6,
    CALL, "readFromDisk", 0,
    ADD_NUMBER, -8, 5,
    MOVE, 3, 0,
    MOVE, 4, 1,
    ADD_NUMBER, -8, 1,
    JUMP, "readFromDiskProgramPrintLoop", 0,

    "readFromDiskProgramPrintLoop",
    COMPARE, 0, 1,
    JUMP_IF_GREATER, "readFromDiskProgramPrintLoopExit", 0,
    JUMP, "readFromDiskProgramPrintLoopBody", 0,

    "readFromDiskProgramPrintLoopBody",
    MOVE_FROM_POINTER, 0, 2,
    MOVE_TO_POINTER, 2, 5,
    CALL, "print8ByteValue", 0,
    ADD_NUMBER, 8, 0,
    JUMP, "readFromDiskProgramPrintLoop", 0,

    "readFromDiskProgramPrintLoopExit",
    RETURN, 0, 0,

    "writeToDiskProgram",
    COMPARE_TO_NUMBER, -3, 128,
    JUMP_IF_GREATER, "writeToDiskProgramValidInput", 0,
    JUMP, "writeToDiskProgramInvalidInput", 0,

    "writeToDiskProgramInvalidInput",
    RETURN, 0, 0,

    "writeToDiskProgramValidInput",
    PUSH_NUMBER, 0, 0,
    PUSH_NUMBER, 0, 0,
    MOVE, -4, 1,
    CALL, "parse8ByteValue", 0,
    ADD_NUMBER, 128, 1,
    PUSH_NUMBER, 8, 0,
    PUSH_NUMBER, 0, 0,
    MOVE_FROM_POINTER, 2, 3,
    ADD_NUMBER, 56, 3,
    PUSH_NUMBER, 0, 0,
    MOVE, 3, 4,
    ADD_NUMBER, 8, 4,
    PUSH_NUMBER, 0, 0,
    MOVE, 3, 5,
    ADD_NUMBER, 16, 5,
    PUSH_NUMBER, 0, 0,
    MOVE, -4, 6,
    ADD, -3, 6,
    ADD_NUMBER, -16, 6,
    MOVE_NUMBER, 16, 2,
    JUMP, "writeToDiskProgramReadLoop", 0,

    "writeToDiskProgramReadLoop",
    COMPARE, 1, 6,
    JUMP_IF_GREATER, "writeToDiskProgramReadLoopExit", 0,
    JUMP, "writeToDiskProgramReadLoopBody", 0,

    "writeToDiskProgramReadLoopBody",
    MOVE_TO_POINTER, 1, 4,
    MOVE_TO_POINTER, 5, 1,
    CALL, "parse8ByteValue", 0,
    ADD_NUMBER, 16, 1,
    ADD_NUMBER, 8, 4,
    ADD_NUMBER, 8, 5,
    JUMP, "writeToDiskProgramReadLoop", 0,

    "writeToDiskProgramReadLoopExit",
    ADD_NUMBER, -8, 4,
    MOVE, 4, 5,
    SUBTRACT, 3, 5,
    MOVE_TO_POINTER, 0, 4,
    ADD_NUMBER, 8, 4,
    MOVE_TO_POINTER, 3, 4,
    ADD_NUMBER, 8, 4,
    MOVE_TO_POINTER, 5, 4,
    ADD_NUMBER, 8, 4,
    MOVE_TO_POINTER, 4, 2,
    CALL, "writeToDisk", 0,
    RETURN, 0, 0,

    "parse8ByteValue",
    PUSH_NUMBER, 0, 0,
    MOVE, -3, 0,
    PUSH_NUMBER, 0, 0,
    MOVE, -3, 1,
    ADD_NUMBER, 120, 1,
    PUSH_NUMBER, 0, 0,
    PUSH_NUMBER, 0, 0,
    PUSH_NUMBER, 0, 0,
    JUMP, "parse8ByteValueLoop", 0,

    "parse8ByteValueLoop",
    COMPARE, 0, 1,
    JUMP_IF_GREATER, "parse8ByteValueLoopExit", 0,
    JUMP, "parse8ByteValueLoopBody", 0,

    "parse8ByteValueLoopBody",
    MOVE_FROM_POINTER, 0, 3,
    MOVE_NUMBER, 0, 4,
    COMPARE_TO_NUMBER, 3, 48,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody0", 0,
    COMPARE_TO_NUMBER, 3, 49,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody1", 0,
    COMPARE_TO_NUMBER, 3, 50,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody2", 0,
    COMPARE_TO_NUMBER, 3, 51,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody3", 0,
    COMPARE_TO_NUMBER, 3, 52,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody4", 0,
    COMPARE_TO_NUMBER, 3, 53,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody5", 0,
    COMPARE_TO_NUMBER, 3, 54,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody6", 0,
    COMPARE_TO_NUMBER, 3, 55,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody7", 0,
    COMPARE_TO_NUMBER, 3, 56,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody8", 0,
    COMPARE_TO_NUMBER, 3, 57,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody9", 0,
    COMPARE_TO_NUMBER, 3, 97,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody10", 0,
    COMPARE_TO_NUMBER, 3, 98,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody11", 0,
    COMPARE_TO_NUMBER, 3, 99,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody12", 0,
    COMPARE_TO_NUMBER, 3, 100,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody13", 0,
    COMPARE_TO_NUMBER, 3, 101,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody14", 0,
    COMPARE_TO_NUMBER, 3, 102,
    JUMP_IF_EQUAL, "parse8ByteValueLoopBody15", 0,

    "parse8ByteValueLoopBody0",
    MOVE_NUMBER, 0, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody1",
    MOVE_NUMBER, 1, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody2",
    MOVE_NUMBER, 2, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody3",
    MOVE_NUMBER, 3, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody4",
    MOVE_NUMBER, 4, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody5",
    MOVE_NUMBER, 5, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody6",
    MOVE_NUMBER, 6, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody7",
    MOVE_NUMBER, 7, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody8",
    MOVE_NUMBER, 8, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody9",
    MOVE_NUMBER, 9, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody10",
    MOVE_NUMBER, 10, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody11",
    MOVE_NUMBER, 11, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody12",
    MOVE_NUMBER, 12, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody13",
    MOVE_NUMBER, 13, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody14",
    MOVE_NUMBER, 14, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBody15",
    MOVE_NUMBER, 15, 4,
    JUMP, "parse8ByteValueLoopBodyContinue", 0,

    "parse8ByteValueLoopBodyContinue",
    SHIFT_LEFT_BY_NUMBER, 4, 2,
    ADD, 4, 2,
    ADD_NUMBER, 8, 0,
    JUMP, "parse8ByteValueLoop", 0,

    "parse8ByteValueLoopExit",
    MOVE, 2, -4,
    RETURN, 0, 0,

    "print8ByteValue",
    PUSH_NUMBER, 60, 0,
    PUSH_NUMBER, 0, 0,
    PUSH_NUMBER, 0, 0,
    JUMP, "print8ByteValueLoop", 0,

    "print8ByteValueLoop",
    COMPARE_TO_NUMBER, 0, 0,
    JUMP_IF_GREATER, "print8ByteValueLoopBody", 0,
    COMPARE_TO_NUMBER, 0, 0,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody", 0,
    JUMP, "print8ByteValueLoopExit", 0,

    "print8ByteValueLoopBody",
    MOVE, -3, 1,
    SHIFT_RIGHT, 0, 1,
    BITWISE_AND_WITH_NUMBER, 15, 1,
    MOVE_NUMBER, 48, 2,
    COMPARE_TO_NUMBER, 1, 0,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody0", 0,
    COMPARE_TO_NUMBER, 1, 1,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody1", 0,
    COMPARE_TO_NUMBER, 1, 2,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody2", 0,
    COMPARE_TO_NUMBER, 1, 3,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody3", 0,
    COMPARE_TO_NUMBER, 1, 4,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody4", 0,
    COMPARE_TO_NUMBER, 1, 5,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody5", 0,
    COMPARE_TO_NUMBER, 1, 6,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody6", 0,
    COMPARE_TO_NUMBER, 1, 7,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody7", 0,
    COMPARE_TO_NUMBER, 1, 8,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody8", 0,
    COMPARE_TO_NUMBER, 1, 9,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody9", 0,
    COMPARE_TO_NUMBER, 1, 10,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody10", 0,
    COMPARE_TO_NUMBER, 1, 11,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody11", 0,
    COMPARE_TO_NUMBER, 1, 12,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody12", 0,
    COMPARE_TO_NUMBER, 1, 13,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody13", 0,
    COMPARE_TO_NUMBER, 1, 14,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody14", 0,
    COMPARE_TO_NUMBER, 1, 15,
    JUMP_IF_EQUAL, "print8ByteValueLoopBody15", 0,

    "print8ByteValueLoopBody0",
    MOVE_NUMBER, 48, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody1",
    MOVE_NUMBER, 49, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody2",
    MOVE_NUMBER, 50, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody3",
    MOVE_NUMBER, 51, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody4",
    MOVE_NUMBER, 52, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody5",
    MOVE_NUMBER, 53, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody6",
    MOVE_NUMBER, 54, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody7",
    MOVE_NUMBER, 55, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody8",
    MOVE_NUMBER, 56, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody9",
    MOVE_NUMBER, 57, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody10",
    MOVE_NUMBER, 97, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody11",
    MOVE_NUMBER, 98, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody12",
    MOVE_NUMBER, 99, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody13",
    MOVE_NUMBER, 100, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody14",
    MOVE_NUMBER, 101, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBody15",
    MOVE_NUMBER, 102, 2,
    JUMP, "print8ByteValueLoopBodyContinue", 0,

    "print8ByteValueLoopBodyContinue",
    CALL, "writeToTranscript", 0,
    ADD_NUMBER, -4, 0,
    JUMP, "print8ByteValueLoop", 0,

    "print8ByteValueLoopExit",
    RETURN, 0, 0,
]


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


def keyboard_step(memory, screen):
    key = screen.read_key()

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

    operating_system = assemble(operating_system_source, 24)
    disk[24 : 24 + len(operating_system)] = operating_system

    memory[:] = disk[:]
    equal_flag = 0
    greater_flag = 0
    screen = TkScreen()

    while True:
        memory = keyboard_step(memory, screen)
        memory, disk = disk_step(memory, disk)
        memory, equal_flag, greater_flag = cpu_step(memory, equal_flag, greater_flag)
        memory = console_step(memory, screen)
        time.sleep(0.001)
