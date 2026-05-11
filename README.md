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
