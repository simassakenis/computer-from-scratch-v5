# computer-from-scratch-v5

This is a minimal simulated computer with memory, CPU, keyboard, disk, console, and a small terminal operating system loaded from `os.txt`.

When powered on (`python computer.py`), the computer copies the first `500000` sacred bytes from disk into memory and then executes instructions one by one forever, until the computer is powered off. The instruction pointer starts at `24`, so the CPU starts interpreting memory at address `24` as instructions.

Using the computer means running one program, then another program, and so on. The preloaded terminal OS listens for keyboard input until Enter, interprets the input as a program invocation, and executes it. A program is just an arbitrary number of bytes read from any arbitrary address on disk. A program can print characters to the console. The command before Enter is interpreted as:

```text
<programDiskAddress> <programLength> <programInput>
```

Values are typed as hex numbers and can omit leading zeros. Values are separated by spaces, and the final value is ended by Enter. The OS reads the program from disk into memory at `3000000`, calls it with `programInputStart` and `numProgramInputBytes`, then listens for the next command.

The disk currently includes two user programs. `readFromDiskProgram` reads bytes from disk and prints each 8-byte value as 16 hex characters. `writeToDiskProgram` parses hex input and writes those 8-byte values to disk. At the moment, `readFromDiskProgram` starts at disk address `5592` and is `984` bytes long. `writeToDiskProgram` starts at disk address `6576` and is `1584` bytes long.

For example, here is how to write a tiny program to disk address `500000` that prints `hi`, and then run it. This keeps the new program after the `0..<500000` disk space used for startup values and OS code.

First type this command and press Enter. It invokes `writeToDiskProgram` and writes the new program bytes to disk:

```text
19b0 630 7a120 e 68 0 15 d08 0 e 69 0 15 d08 0 16 0 0
```

Then type this command and press Enter. It runs the program at disk address `500000`, length `120` bytes:

```text
7a120 78
```

The values typed above are:

```text
19b0  address of writeToDiskProgram
630   length of writeToDiskProgram
7a120 disk address to write the new program to

e 68 0   pushNumber 104, ASCII h
15 d08 0 call writeToTranscript
e 69 0   pushNumber 105, ASCII i
15 d08 0 call writeToTranscript
16 0 0   return

7a120 disk address of the new program
78    length of the new program
```

After the second Enter, the console should show `hi` on the program output line, then a fresh `terminalOS % ` prompt below it. The program above calls `writeToTranscript` at the hard-coded address `3336`, encoded as `d08`.

Memory is byte-addressed and currently has `10000000` bytes. Machine values are 8 bytes. Most instructions operate on slots. A slot is an 8-byte value at an offset from the current base pointer: `slot(0)` is at the base pointer, `slot(1)` is 8 bytes after it, and `slot(-1)` is 8 bytes before it.

Each instruction is 24 bytes: 8 bytes for opcode, 8 bytes for operand 1, and 8 bytes for operand 2. Unused operands are `0`. When an instruction changes something, operand 2 is usually the destination.

- `move 4 5`: `slot(5) = slot(4)`
- `moveNumber 27 3`: `slot(3) = 27`
- `moveFromPointer 3 4`: `slot(4) = memory[slot(3)]`
- `moveToPointer 3 4`: `memory[slot(4)] = slot(3)`
- `add 3 4`: `slot(4) = slot(4) + slot(3)`
- `addNumber 27 3`: `slot(3) = slot(3) + 27`
- `subtract 3 4`: `slot(4) = slot(4) - slot(3)`
- `shiftLeft 3 4`: `slot(4) = slot(4) << slot(3)`
- `shiftLeftByNumber 27 4`: `slot(4) = slot(4) << 27`
- `shiftRight 3 4`: `slot(4) = slot(4) >> slot(3)`
- `shiftRightByNumber 27 4`: `slot(4) = slot(4) >> 27`
- `bitwiseAnd 3 4`: `slot(4) = slot(4) & slot(3)`
- `bitwiseAndWithNumber 15 4`: `slot(4) = slot(4) & 15`
- `pushNumber 27`: push `27` to the stack
- `pop`: move the stack top back by one slot
- `compare 3 4`: compare `slot(3)` to `slot(4)` and set ALU flags
- `compareToNumber 3 67`: compare `slot(3)` to `67` and set ALU flags
- `jumpIfEqual 4000000`: jump if the equal flag is set
- `jumpIfGreater 4000000`: jump if the greater flag is set
- `jump 4000000`: jump unconditionally
- `call 4000000`: push return address and old base pointer, set a new base pointer, then jump
- `return`: restore stack top, base pointer, and instruction pointer

The current memory layout is:

```text
0: instruction pointer
8: base pointer
16: stack top pointer
24..<500000: operating system program
    3336: writeToTranscript
    4872: readFromDisk
    5232: writeToDisk
    5592: readFromDiskProgram
    6576: writeToDiskProgram
    8160: parse8ByteValue
    10992: print8ByteValue
500000..<1000000: operating system stack
1000000: next transcript write address
1000008: disk IO disk address
1000016: disk IO memory address
1000024: disk IO byte count
1000032: disk IO read waiting flag
1000040: disk IO write waiting flag
1000048: keyboard waiting flag
1000056: keyboard value
1000064: next console write address
1000072..<1032840: console, 128 by 32 cells, 8 bytes per cell
2000000..<3000000: transcript
3000000..<10000000: loaded user program, then user program stack
```

Keyboard IO works by setting `1000048` to `1`. The keyboard hardware writes the pressed key to `1000056` and resets `1000048` to `0`.

To read from disk, write disk address to `1000008`, memory address to `1000016`, byte count to `1000024`, and set `1000032` to `1`. Disk hardware copies from disk to memory and resets `1000032` to `0`.

To write to disk, write disk address to `1000008`, memory address to `1000016`, byte count to `1000024`, and set `1000040` to `1`. Disk hardware copies from memory to disk and resets `1000040` to `0`.

Console IO uses the memory region starting at `1000072`. Each console cell is one 8-byte character value. `1000064` stores the next console write address.

Function calling works as follows. Arguments are pushed before `call`. The call instruction pushes the return address and old base pointer, then sets the base pointer to the new frame. Inside a function, non-negative slots are local variables. Negative slots refer to caller-provided values and call metadata: `slot(-1)` is old base pointer, `slot(-2)` is return address, and arguments live below those slots.

**OS Pseudocode**

This is the operating system source from `os.txt`, written as compact pseudocode.

```text
initialize:
    consoleCursor = 1000072
    transcriptCursor = 2000000
    jump terminal

terminal:
    printTerminalPrefix()
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

        readFromDisk(programDiskAddress, 3000000, programLength)
        program(programInputStart, programInputLength)

        writeToTranscript(Enter)
        jump terminal

printTerminalPrefix() -> nothing:
    writeToTranscript("t")
    writeToTranscript("e")
    writeToTranscript("r")
    writeToTranscript("m")
    writeToTranscript("i")
    writeToTranscript("n")
    writeToTranscript("a")
    writeToTranscript("l")
    writeToTranscript("O")
    writeToTranscript("S")
    writeToTranscript(" ")
    writeToTranscript("%")
    writeToTranscript(" ")
    return

listenForKeypress() -> character:
    valueAt(1000048) = 1

    while valueAt(1000048) != 0:
        continue

    return valueAt(1000056)

removeLastCharacterFromTranscript() -> nothing:
    if transcriptCursor <= 2000000:
        return

    transcriptCursor -= 8
    valueAt(transcriptCursor) = 0
    removeLastCharacterFromConsole()
    return

removeLastCharacterFromConsole() -> nothing:
    if consoleCursor <= 1000072:
        return

    consoleCursor -= 8
    valueAt(consoleCursor) = 0
    return

writeToTranscript(character) -> nothing:
    valueAt(transcriptCursor) = character
    transcriptCursor += 8

    if character != Enter:
        writeToConsole(character)
        return

    while isConsoleAtLineEnd() == 0:
        writeToConsole(Space)

    writeToConsole(Space)
    removeLastCharacterFromConsole()
    return

isConsoleAtLineEnd() -> 0 or 1:
    lineEnd = 1001096

    while lineEnd <= 1032840:
        if consoleCursor == lineEnd:
            return 1
        lineEnd += 1024

    return 0

writeToConsole(character) -> nothing:
    if consoleCursor == 1032840:
        consoleCursor -= 1024
        readAddress = 1001096
        writeAddress = 1000072

        while readAddress != 1032840:
            valueAt(writeAddress) = valueAt(readAddress)
            readAddress += 8
            writeAddress += 8

    valueAt(consoleCursor) = character
    consoleCursor += 8
    return

readFromDisk(diskAddress, memoryAddress, numBytes) -> nothing:
    valueAt(1000008) = diskAddress
    valueAt(1000016) = memoryAddress
    valueAt(1000024) = numBytes
    valueAt(1000032) = 1

    while valueAt(1000032) != 0:
        continue
    return

writeToDisk(diskAddress, memoryAddress, numBytes) -> nothing:
    valueAt(1000008) = diskAddress
    valueAt(1000016) = memoryAddress
    valueAt(1000024) = numBytes
    valueAt(1000040) = 1

    while valueAt(1000040) != 0:
        continue
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
```
