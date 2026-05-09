# computer-from-scratch-v5

A minimal simulated computer with byte-addressed memory, a tiny CPU, memory-mapped IO, and a small terminal operating system loaded from `disk.txt`.

## Instructions

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

## Startup

When powered on, the computer copies the disk image into memory and then executes instructions forever. The first three 8-byte values on disk initialize the instruction pointer, base pointer, and stack top pointer.

The preloaded program is a minimal terminal OS. It listens for keyboard input until Enter. Enter itself is not written to the transcript or console. The command before Enter is interpreted as:

```text
<programDiskAddress><programLength><programInput>
```

`programDiskAddress` and `programLength` are each typed as 16 hex characters. The OS reads that program from disk into memory at `3000000`, calls it with `programInputStart` and `numProgramInputBytes`, then listens for the next command.

Example: write a tiny program to disk address `100000` that prints `hi`.

First type this command and press Enter. It invokes `writeToDiskProgram` and writes the new program bytes to disk:

```text
00000000000012d8000000000000046800000000000186a0000000000000000e00000000000000680000000000000000000000000000001500000000000009480000000000000000000000000000000e00000000000000690000000000000000000000000000001500000000000009480000000000000000000000000000001600000000000000000000000000000000
```

Broken into 16-hex-character values, that command is:

```text
00000000000012d8  address of writeToDiskProgram
0000000000000468  length of writeToDiskProgram
00000000000186a0  disk address to write the new program to
000000000000000e  pushNumber opcode
0000000000000068  ASCII h
0000000000000000  unused operand
0000000000000015  call opcode
0000000000000948  address of writeToTranscript
0000000000000000  unused operand
000000000000000e  pushNumber opcode
0000000000000069  ASCII i
0000000000000000  unused operand
0000000000000015  call opcode
0000000000000948  address of writeToTranscript
0000000000000000  unused operand
0000000000000016  return opcode
0000000000000000  unused operand
0000000000000000  unused operand
```

Then type this command and press Enter. It runs the program at disk address `100000`, length `120` bytes:

```text
00000000000186a00000000000000078
```

Broken down:

```text
00000000000186a0  disk address of the new program
0000000000000078  length of the new program
```

After the second Enter, the console should show `hi` appended after the typed command.

## Preloaded Programs

The disk currently includes two user programs:

- `readFromDiskProgram`: reads bytes from disk and prints each 8-byte value as 16 hex characters
- `writeToDiskProgram`: parses hex input and writes those 8-byte values to disk

At the moment, `readFromDiskProgram` starts at disk address `3768` and is `1056` bytes long. `writeToDiskProgram` starts at disk address `4824`.

Some OS functions are useful for user programs to call directly. In the current disk image:

- `writeToTranscript` is at address `2376`
- `readFromDisk` is at address `3048`
- `writeToDisk` is at address `3408`

For example, the `hi` program above calls `writeToTranscript` at the hard-coded address `2376`, encoded as `0000000000000948`.

## Memory Layout

```text
0: instruction pointer
8: base pointer
16: stack top pointer
24..<500000: operating system program
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
3000000..: loaded user program, then user program stack
```

## IO Contracts

Keyboard IO: the program sets `1000048` to `1`. The keyboard hardware writes the pressed key to `1000056` and resets `1000048` to `0`.

Disk IO: the program writes disk address to `1000008`, memory address to `1000016`, byte count to `1000024`, then sets either `1000032` for read or `1000040` for write. Disk hardware performs the copy and resets the waiting flag to `0`.

Console IO: console cells start at `1000072`; each cell is one 8-byte character value. `1000064` stores the next console write address.

## Calling Convention

Arguments are pushed before `call`. The call instruction pushes the return address and old base pointer, then sets the base pointer to the new frame.

Inside a function, non-negative slots are local variables. Negative slots refer to caller-provided values and call metadata: `slot(-1)` is old base pointer, `slot(-2)` is return address, and arguments live below those slots.
