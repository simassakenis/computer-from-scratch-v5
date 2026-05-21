# Computer From Scratch

![Computer diagram](diagram.jpeg)

A minimal simulated computer implemented from scratch in Python (`computer.py`), plus a minimal operating system in ~600 lines of machine code (`os.txt`). See `demo.mp4` for how it can be used. Demo recording to be added.

When you run `python computer.py`, you will see a new window pop up that simulates the display of this computer, and you can use your keyboard to simulate keyboard input. You use this computer by running programs one at a time. Each program is identified by its address on disk and length, so for example typing `2628 3d8 0 8` and pressing Enter will make the computer run a program starting at address `2628` on disk and spanning `3d8` bytes, with two input values: `0` and `8`. Values are space-separated hex numbers and can omit leading zeros.

There are only two programs at first, `readFromDiskProgram` and `writeToDiskProgram`, but you can use `writeToDiskProgram` to write your own program somewhere on disk and then invoke it by its starting address and length. For example, to write a program that prints `hi`, type this into the terminal and press Enter:

```text
$ 2a00 630 7a120 f 68 0 16 ab0 0 f 69 0 16 ab0 0 17 0 0
```

In this command, `2a00` is the address of `writeToDiskProgram`, `630` is its length, `7a120` is the disk address to write the new program to, and `f 68 0 16 ab0 0 f 69 0 16 ab0 0 17 0 0` is the machine code of the new program.

Then type this and press Enter to run it:

```text
$ 7a120 78
```

In this command, `7a120` is the disk address of the new program, and `78` is the length of the new program.

The full interaction should look like this:

```text
$ 2a00 630 7a120 f 68 0 16 ab0 0 f 69 0 16 ab0 0 17 0 0
$ 7a120 78
hi
$ 
```

## What is a computer?

This computer consists of memory, a CPU, disk, keyboard, and display.

Memory is byte-addressed and currently has `10000000` bytes. Machine values are 8 bytes. When powered on, the computer copies the first `500000` sacred bytes from disk into memory.

CPU is a hardwired electric circuit that implements some predefined set of instructions. The instruction pointer is a special value at memory address `1000000`; it tells the CPU which instruction to execute next. The base pointer is a special value at memory address `1000008`; most instructions operate on slots relative to this pointer. A slot is an 8-byte value at an offset from the current base pointer: `slot(0)` is at the base pointer, `slot(1)` is 8 bytes after it, and `slot(-1)` is 8 bytes before it.

Each instruction is 24 bytes: 8 bytes for opcode, 8 bytes for operand 1, and 8 bytes for operand 2. Unused operands are `0`. When an instruction changes something, operand 2 is usually the destination.

| Opcode | Instruction | Effect |
| --- | --- | --- |
| `0` | `idle` | Do nothing and keep the instruction pointer on this instruction. |
| `1` | `moveNumberToAddress 27 123456` | `memory[123456] = 27` |
| `2` | `move 4 5` | `slot(5) = slot(4)` |
| `3` | `moveNumber 27 3` | `slot(3) = 27` |
| `4` | `moveFromPointer 3 4` | `slot(4) = memory[slot(3)]` |
| `5` | `moveToPointer 3 4` | `memory[slot(4)] = slot(3)` |
| `6` | `add 3 4` | `slot(4) = slot(4) + slot(3)` |
| `7` | `addNumber 27 3` | `slot(3) = slot(3) + 27` |
| `8` | `subtract 3 4` | `slot(4) = slot(4) - slot(3)` |
| `9` | `shiftLeft 3 4` | `slot(4) = slot(4) << slot(3)` |
| `10` | `shiftLeftByNumber 27 4` | `slot(4) = slot(4) << 27` |
| `11` | `shiftRight 3 4` | `slot(4) = slot(4) >> slot(3)` |
| `12` | `shiftRightByNumber 27 4` | `slot(4) = slot(4) >> 27` |
| `13` | `bitwiseAnd 3 4` | `slot(4) = slot(4) & slot(3)` |
| `14` | `bitwiseAndWithNumber 15 4` | `slot(4) = slot(4) & 15` |
| `15` | `pushNumber 27` | Push `27` to the stack. |
| `16` | `pop` | Move the stack top back by one slot. |
| `17` | `compare 3 4` | Compare `slot(3)` to `slot(4)` and set ALU flags. |
| `18` | `compareToNumber 3 67` | Compare `slot(3)` to `67` and set ALU flags. |
| `19` | `jumpIfEqual 4000000` | Jump if the equal flag is set. |
| `20` | `jumpIfGreater 4000000` | Jump if the greater flag is set. |
| `21` | `jump 4000000` | Jump unconditionally. |
| `22` | `call 4000000` | Push return address and old base pointer, set a new base pointer, then jump. |
| `23` | `return` | Restore stack top, base pointer, and instruction pointer. |

The CPU executes instructions one by one forever, until the computer is powered off. The instruction pointer starts at `0`, so the CPU starts interpreting memory at address `0` as instructions.

Disk stores the operating system and user programs. The OS reads a program from disk into memory at `2000000`, calls it with `programInputStart` and `numProgramInputBytes`, then listens for the next command. The command before Enter is interpreted as:

```text
<programDiskAddress> <programLength> <programInput>
```

To read from disk, write disk address to `1000032`, memory address to `1000040`, byte count to `1000048`, and set `1000056` to `1`. Disk hardware copies from disk to memory and resets `1000056` to `0`. To write to disk, use the same address/count registers and set `1000064` to `1`; disk hardware copies from memory to disk and resets `1000064` to `0`.

Keyboard input works by setting `1000072` to `1`. The keyboard hardware writes the pressed key to `1000080` and resets `1000072` to `0`.

Display output uses the memory region starting at `1000096`. Each display cell is one 8-byte character value, and `1000088` stores the next display write address.

The current memory layout is:

```text
0..<500000: operating system program
    2736 (0xab0): writeToTranscript
    4272 (0x10b0): readFromDisk
    4632 (0x1218): writeToDisk
    4992 (0x1380): parse8ByteValue
    7824 (0x1e90): print8ByteValue
    9768 (0x2628): readFromDiskProgram
    10752 (0x2a00): writeToDiskProgram
500000..<1000000: operating system stack
1000000: instruction pointer
1000008: base pointer
1000016: stack top pointer
1000024: next transcript write address
1000032: disk IO disk address
1000040: disk IO memory address
1000048: disk IO byte count
1000056: disk IO read waiting flag
1000064: disk IO write waiting flag
1000072: keyboard waiting flag
1000080: keyboard value
1000088: next display write address
1000096..<1032864: display, 128 by 32 cells, 8 bytes per cell
1032864..<2000000: transcript
2000000..<10000000: loaded user program, then user program stack
```

Function calling works as follows. Arguments are pushed before `call`. The call instruction pushes the return address and old base pointer, then sets the base pointer to the new frame. Inside a function, non-negative slots are local variables. Negative slots refer to caller-provided values and call metadata: `slot(-1)` is old base pointer, `slot(-2)` is return address, and arguments live below those slots.

## What is an operating system?

On its own, a computer can execute instructions from address `0` onwards forever, so it will run whatever program you load there. To make it continually usable, we can load a meta-program: an operating system that lets us execute other programs.

This is the operating system source from `os.txt`, written as compact pseudocode.

```text
initialize:
    basePointer = 500000
    stackPointer = 500016
    displayCursor = 1000096
    transcriptCursor = 1032864
    transcriptCursorPointer = 1000024
    inputStart = 0
    jump terminal

terminal:
    writeToTranscript("$")
    writeToTranscript(" ")
    inputStart = transcriptCursor

    while True:
        character = listenForKeypress()

        if character == Backspace:
            if transcriptCursor > inputStart:
                removeLastCharacterFromTranscript()
            continue

        writeToTranscript(character)

        if character != Enter:
            continue

        programDiskAddress, bytesRead1 = parse8ByteValue(inputStart)
        programLength, bytesRead2 = parse8ByteValue(inputStart + bytesRead1)

        programInputStart = inputStart + bytesRead1 + bytesRead2
        programInputLength = transcriptCursor - programInputStart

        readFromDisk(programDiskAddress, 2000000, programLength)
        program(programInputStart, programInputLength)

        writeToTranscript(Enter)
        jump terminal

listenForKeypress() -> character:
    valueAt(1000072) = 1

    while valueAt(1000072) != 0:
        continue

    return valueAt(1000080)

removeLastCharacterFromTranscript() -> nothing:
    if transcriptCursor <= 1032864:
        return

    transcriptCursor -= 8
    valueAt(transcriptCursor) = 0
    removeLastCharacterFromDisplay()
    return

removeLastCharacterFromDisplay() -> nothing:
    if displayCursor <= 1000096:
        return

    displayCursor -= 8
    valueAt(displayCursor) = 0
    return

writeToTranscript(character) -> nothing:
    valueAt(transcriptCursor) = character
    transcriptCursor += 8

    if character != Enter:
        writeToDisplay(character)
        return

    while isDisplayAtLineEnd() == 0:
        writeToDisplay(Space)

    writeToDisplay(Space)
    removeLastCharacterFromDisplay()
    return

isDisplayAtLineEnd() -> 0 or 1:
    lineEnd = 1001120

    while lineEnd <= 1032864:
        if displayCursor == lineEnd:
            return 1
        lineEnd += 1024

    return 0

writeToDisplay(character) -> nothing:
    if displayCursor == 1032864:
        displayCursor -= 1024
        readAddress = 1001120
        writeAddress = 1000096

        while readAddress != 1032864:
            valueAt(writeAddress) = valueAt(readAddress)
            readAddress += 8
            writeAddress += 8

    valueAt(displayCursor) = character
    displayCursor += 8
    return

readFromDisk(diskAddress, memoryAddress, numBytes) -> nothing:
    valueAt(1000032) = diskAddress
    valueAt(1000040) = memoryAddress
    valueAt(1000048) = numBytes
    valueAt(1000056) = 1

    while valueAt(1000056) != 0:
        continue
    return

writeToDisk(diskAddress, memoryAddress, numBytes) -> nothing:
    valueAt(1000032) = diskAddress
    valueAt(1000040) = memoryAddress
    valueAt(1000048) = numBytes
    valueAt(1000064) = 1

    while valueAt(1000064) != 0:
        continue
    return

parse8ByteValue(inputStart) -> value, numberOfBytesRead:
    readAddress = inputStart
    numberOfCharacters = 0
    numberOfBytesRead = 0

    while numberOfCharacters < 16:
        numberOfBytesRead += 8
        character = valueAt(readAddress)

        if character == Space or character == Enter:
            break

        numberOfCharacters += 1
        readAddress += 8

    if numberOfCharacters == 16:
        character = valueAt(readAddress)
        if character == Space or character == Enter:
            numberOfBytesRead += 8

    readAddress = inputStart
    numberOfMissingCharacters = 16 - numberOfCharacters
    result = 0
    i = 0

    while i < 16:
        value = 0

        if i >= numberOfMissingCharacters:
            character = valueAt(readAddress)

            if character == "0":
                value = 0
            if character == "1":
                value = 1
            if character == "2":
                value = 2
            if character == "3":
                value = 3
            if character == "4":
                value = 4
            if character == "5":
                value = 5
            if character == "6":
                value = 6
            if character == "7":
                value = 7
            if character == "8":
                value = 8
            if character == "9":
                value = 9
            if character == "a":
                value = 10
            if character == "b":
                value = 11
            if character == "c":
                value = 12
            if character == "d":
                value = 13
            if character == "e":
                value = 14
            if character == "f":
                value = 15

            readAddress += 8

        result = result << 4
        result += value
        i += 1

    return result, numberOfBytesRead

print8ByteValue(value) -> nothing:
    shiftAmount = 60

    while shiftAmount >= 0:
        digit = (value >> shiftAmount) & 15
        character = "0"

        if digit == 0:
            character = "0"
        if digit == 1:
            character = "1"
        if digit == 2:
            character = "2"
        if digit == 3:
            character = "3"
        if digit == 4:
            character = "4"
        if digit == 5:
            character = "5"
        if digit == 6:
            character = "6"
        if digit == 7:
            character = "7"
        if digit == 8:
            character = "8"
        if digit == 9:
            character = "9"
        if digit == 10:
            character = "a"
        if digit == 11:
            character = "b"
        if digit == 12:
            character = "c"
        if digit == 13:
            character = "d"
        if digit == 14:
            character = "e"
        if digit == 15:
            character = "f"

        writeToTranscript(character)
        shiftAmount -= 4
    return

readFromDiskProgram(programInputStart, numProgramInputBytes) -> nothing:
    diskAddress, bytesRead1 = parse8ByteValue(programInputStart)
    numBytes, bytesRead2 = parse8ByteValue(programInputStart + bytesRead1)

    bufferStart = base + 56
    bufferEnd = bufferStart + numBytes

    readFromDisk(diskAddress, bufferStart, numBytes)

    printAddress = bufferStart
    highestPrintAddress = bufferEnd - 8

    while printAddress <= highestPrintAddress:
        print8ByteValue(valueAt(printAddress))
        printAddress += 8
    return

writeToDiskProgram(programInputStart, numProgramInputBytes) -> nothing:
    diskAddress, bytesRead = parse8ByteValue(programInputStart)
    writeContentInputStart = programInputStart + bytesRead
    programInputEnd = programInputStart + numProgramInputBytes

    readAddress = writeContentInputStart
    bufferSize = 0

    while readAddress < programInputEnd:
        character = valueAt(readAddress)
        readAddress += 8
        if character == Space or character == Enter:
            bufferSize += 8

    bufferStart = base + 128
    writeAddress = bufferStart
    readAddress = writeContentInputStart

    while readAddress < programInputEnd:
        value, bytesRead = parse8ByteValue(readAddress)
        valueAt(writeAddress) = value
        writeAddress += 8
        readAddress += bytesRead

    writeToDisk(diskAddress, bufferStart, bufferSize)
    return
```

## Inspiration

This project was heavily inspired by Ben Eater and Andrej Karpathy. It is a personal project purely for educational purposes.
