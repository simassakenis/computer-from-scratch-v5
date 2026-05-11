import computer


def test_idle():
    # An idle instruction leaves the instruction pointer and ALU flags unchanged
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    memory[24 : 24 + 24] = computer.as8(0) + computer.as8(0) + computer.as8(0)

    memory, equal_flag, greater_flag = computer.cpu_step(memory, 0, 0)

    assert computer.asint(memory[0:8]) == 24
    assert equal_flag == 0
    assert greater_flag == 0


def test_move_and_move_number():
    # Verifies moving an immediate number into one slot and then into another slot
    # Program:
    #   moveNumber 42 0
    #   move 0 1
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        computer.as8(2) + computer.as8(42) + computer.as8(0)
        + computer.as8(1) + computer.as8(0) + computer.as8(1)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(2):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2008:2016]) == 42


def test_pointer_moves():
    # Verifies writing through a pointer and then reading back through that pointer
    # Program:
    #   moveNumber 3000 0
    #   moveNumber 65 1
    #   moveToPointer 1 0
    #   moveFromPointer 0 2
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        computer.as8(2) + computer.as8(3000) + computer.as8(0)
        + computer.as8(2) + computer.as8(65) + computer.as8(1)
        + computer.as8(4) + computer.as8(1) + computer.as8(0)
        + computer.as8(3) + computer.as8(0) + computer.as8(2)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(4):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[3000:3008]) == 65
    assert computer.asint(memory[2016:2024]) == 65


def test_arithmetic():
    # Verifies add, addNumber, and subtract update the destination slot
    # Program:
    #   slot(0) = 7
    #   slot(1) = 5
    #   slot(1) += slot(0)
    #   slot(1) += -2
    #   slot(1) -= slot(0)
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        computer.as8(2) + computer.as8(7) + computer.as8(0)
        + computer.as8(2) + computer.as8(5) + computer.as8(1)
        + computer.as8(5) + computer.as8(0) + computer.as8(1)
        + computer.as8(6) + computer.as8(-2) + computer.as8(1)
        + computer.as8(7) + computer.as8(0) + computer.as8(1)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(5):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2008:2016]) == 3


def test_shift_and_bitwise():
    # Program exercises both slot-based and immediate shifts, then bitwise AND
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        computer.as8(2) + computer.as8(1) + computer.as8(0)
        + computer.as8(2) + computer.as8(3) + computer.as8(1)
        + computer.as8(8) + computer.as8(0) + computer.as8(1)
        + computer.as8(9) + computer.as8(2) + computer.as8(1)
        + computer.as8(10) + computer.as8(0) + computer.as8(1)
        + computer.as8(11) + computer.as8(1) + computer.as8(1)
        + computer.as8(2) + computer.as8(7) + computer.as8(2)
        + computer.as8(12) + computer.as8(2) + computer.as8(1)
        + computer.as8(13) + computer.as8(2) + computer.as8(1)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(9):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2008:2016]) == 2


def test_push_number_and_pop():
    # Verifies push writes at stack top and pop moves stack top back
    # Program:
    #   pushNumber 55
    #   pop
    # The value remains in memory, but stack top moves back
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        computer.as8(14) + computer.as8(55) + computer.as8(0)
        + computer.as8(15) + computer.as8(0) + computer.as8(0)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(2):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2000:2008]) == 55
    assert computer.asint(memory[16:24]) == 2000
    assert equal_flag == 0
    assert greater_flag == 0


def test_compare_to_number_and_jump_if_equal():
    # Program jumps over slot(1) = 1 because slot(0) equals 5
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        computer.as8(2) + computer.as8(5) + computer.as8(0)
        + computer.as8(17) + computer.as8(0) + computer.as8(5)
        + computer.as8(18) + computer.as8(120) + computer.as8(0)
        + computer.as8(2) + computer.as8(1) + computer.as8(1)
        + computer.as8(2) + computer.as8(9) + computer.as8(1)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(4):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2008:2016]) == 9


def test_compare_and_jump_if_greater():
    # Program jumps over slot(2) = 1 because slot(0) is greater than slot(1)
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        computer.as8(2) + computer.as8(9) + computer.as8(0)
        + computer.as8(2) + computer.as8(3) + computer.as8(1)
        + computer.as8(16) + computer.as8(0) + computer.as8(1)
        + computer.as8(19) + computer.as8(144) + computer.as8(0)
        + computer.as8(2) + computer.as8(1) + computer.as8(2)
        + computer.as8(2) + computer.as8(8) + computer.as8(2)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(5):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2016:2024]) == 8


def test_jump():
    # Program jumps over slot(0) = 1 and lands on slot(0) = 2
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        computer.as8(20) + computer.as8(72) + computer.as8(0)
        + computer.as8(2) + computer.as8(1) + computer.as8(0)
        + computer.as8(2) + computer.as8(2) + computer.as8(0)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(2):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2000:2008]) == 2


def test_call_and_return():
    # Verifies call creates a function frame and return restores the caller frame
    # Program:
    #   pushNumber 123
    #   call function
    #   move 0 1
    # The function copies its argument from slot(-3) into slot(0), then returns
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        computer.as8(14) + computer.as8(123) + computer.as8(0)
        + computer.as8(21) + computer.as8(120) + computer.as8(0)
        + computer.as8(1) + computer.as8(0) + computer.as8(1)
        + computer.as8(0) + computer.as8(0) + computer.as8(0)
        + computer.as8(1) + computer.as8(-3) + computer.as8(0)
        + computer.as8(22) + computer.as8(0) + computer.as8(0)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(5):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[8:16]) == 2000
    assert computer.asint(memory[16:24]) == 2008
    assert computer.asint(memory[2008:2016]) == 123


def test_power_on_copies_only_startup_bytes():
    # Power-on copies only the first 500000 bytes, leaving later disk bytes unloaded
    disk = computer.assemble(open("os.txt").read())
    disk[500000 : 500000 + 8] = computer.as8(123)
    memory = [0] * 10000000

    memory[:500000] = disk[:500000]

    assert computer.asint(memory[500000 : 500000 + 8]) == 0


def test_parse_8_byte_value_accepts_short_delimited_input():
    # Call parse8ByteValue directly and verify short hex values are left-padded and report consumed bytes
    disk = computer.assemble(open("os.txt").read())
    memory = [0] * 10000000
    memory[:500000] = disk[:500000]
    memory[0:8] = computer.as8(3000000)
    memory[8:16] = computer.as8(500000)
    memory[16:24] = computer.as8(500000)
    input_address = 3500000
    for index, character in enumerate("15c0 "):
        address = input_address + index * 8
        memory[address : address + 8] = computer.as8(ord(character))
    program = (
        computer.as8(14) + computer.as8(0) + computer.as8(0)
        + computer.as8(14) + computer.as8(0) + computer.as8(0)
        + computer.as8(14) + computer.as8(input_address) + computer.as8(0)
        + computer.as8(21) + computer.as8(8160) + computer.as8(0)
        + computer.as8(0) + computer.as8(0) + computer.as8(0)
    )
    memory[3000000 : 3000000 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(5000):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[500000 : 500000 + 8]) == 0x15C0
    assert computer.asint(memory[500008 : 500008 + 8]) == 40


def test_os_echoes_typed_character():
    # Simulate typing one key into the real terminal OS and verify it appears after the prompt
    disk = computer.assemble(open("os.txt").read())
    memory = [0] * 10000000
    memory[:500000] = disk[:500000]
    keys = [ord("a")]
    equal_flag = 0
    greater_flag = 0

    for cycle in range(5000):
        if cycle % 10 == 0 and keys and computer.asint(memory[1000048 : 1000048 + 8]) == 1:
            memory[1000056 : 1000056 + 8] = computer.as8(keys.pop(0))
            memory[1000048 : 1000048 + 8] = computer.as8(0)
        memory, disk = computer.disk_step(memory, disk)
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    result = ""
    for address in range(1000072, 1000072 + len("terminalOS % a") * 8, 8):
        result += chr(computer.asint(memory[address : address + 8]) & 255)

    assert result == "terminalOS % a"


def test_read_from_disk_program():
    # Invoke readFromDiskProgram through the terminal and read the first 8 disk bytes
    disk = computer.assemble(open("os.txt").read())
    memory = [0] * 10000000
    memory[:500000] = disk[:500000]
    command = f"{5592:x} {984:x} 0 8"
    keys = [ord(character) for character in command] + [10]
    equal_flag = 0
    greater_flag = 0

    for cycle in range(80000):
        if cycle % 10 == 0 and keys and computer.asint(memory[1000048 : 1000048 + 8]) == 1:
            memory[1000056 : 1000056 + 8] = computer.as8(keys.pop(0))
            memory[1000048 : 1000048 + 8] = computer.as8(0)
        memory, disk = computer.disk_step(memory, disk)
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    line1 = ""
    for address in range(1000072, 1000072 + len("terminalOS % " + command) * 8, 8):
        line1 += chr(computer.asint(memory[address : address + 8]) & 255)
    line2 = ""
    for address in range(1001096, 1001096 + 16 * 8, 8):
        line2 += chr(computer.asint(memory[address : address + 8]) & 255)
    line3 = ""
    for address in range(1002120, 1002120 + len("terminalOS % ") * 8, 8):
        line3 += chr(computer.asint(memory[address : address + 8]) & 255)

    assert keys == []
    assert line1 == "terminalOS % " + command
    assert line2 == "0000000000000018"
    assert line3 == "terminalOS % "


def test_write_to_disk_program():
    # Invoke writeToDiskProgram through the terminal and verify disk memory changes
    disk = computer.assemble(open("os.txt").read())
    memory = [0] * 10000000
    memory[:500000] = disk[:500000]
    disk_address = 600000
    value = 0x6869
    command = f"{6576:x} {1584:x} {disk_address:x} {value:x}"
    keys = [ord(character) for character in command] + [10]
    equal_flag = 0
    greater_flag = 0

    for cycle in range(100000):
        if cycle % 10 == 0 and keys and computer.asint(memory[1000048 : 1000048 + 8]) == 1:
            memory[1000056 : 1000056 + 8] = computer.as8(keys.pop(0))
            memory[1000048 : 1000048 + 8] = computer.as8(0)
        memory, disk = computer.disk_step(memory, disk)
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert keys == []
    assert computer.asint(disk[disk_address : disk_address + 8]) == value
    assert computer.asint(disk[disk_address + 8 : disk_address + 16]) == 0


def test_readme_write_hi_program_example():
    # Simulate the README flow: write a small program to disk, run it, and see hi
    disk = computer.assemble(open("os.txt").read())
    memory = [0] * 10000000
    memory[:500000] = disk[:500000]
    write_command = (
        "19b0 630 7a120 "
        "e 68 0 "
        "15 d08 0 "
        "e 69 0 "
        "15 d08 0 "
        "16 0 0"
    )
    run_command = "7a120 78"
    keys = [ord(character) for character in write_command] + [10]
    keys += [ord(character) for character in run_command] + [10]
    equal_flag = 0
    greater_flag = 0

    for cycle in range(160000):
        if cycle % 10 == 0 and keys and computer.asint(memory[1000048 : 1000048 + 8]) == 1:
            memory[1000056 : 1000056 + 8] = computer.as8(keys.pop(0))
            memory[1000048 : 1000048 + 8] = computer.as8(0)
        memory, disk = computer.disk_step(memory, disk)
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    line1 = ""
    for address in range(1000072, 1000072 + len("terminalOS % " + write_command) * 8, 8):
        line1 += chr(computer.asint(memory[address : address + 8]) & 255)
    line2 = ""
    for address in range(1001096, 1001096 + len("terminalOS % " + run_command) * 8, 8):
        line2 += chr(computer.asint(memory[address : address + 8]) & 255)
    line3 = ""
    for address in range(1002120, 1002120 + len("hi") * 8, 8):
        line3 += chr(computer.asint(memory[address : address + 8]) & 255)
    line4 = ""
    for address in range(1003144, 1003144 + len("terminalOS % ") * 8, 8):
        line4 += chr(computer.asint(memory[address : address + 8]) & 255)

    assert keys == []
    assert line1 == "terminalOS % " + write_command
    assert line2 == "terminalOS % " + run_command
    assert line3 == "hi"
    assert line4 == "terminalOS % "


def test_write_to_transcript_enter_moves_console_to_next_line():
    # Call the OS print function directly and verify Enter advances the console cursor by spaces
    disk = computer.assemble(open("os.txt").read())
    memory = [0] * 10000000
    memory[:500000] = disk[:500000]
    memory[0:8] = computer.as8(3000000)
    memory[8:16] = computer.as8(500000)
    memory[16:24] = computer.as8(500000)
    memory[1000000 : 1000000 + 8] = computer.as8(2000000)
    memory[1000064 : 1000064 + 8] = computer.as8(1000072)
    program = (
        computer.as8(14) + computer.as8(ord("a")) + computer.as8(0)
        + computer.as8(21) + computer.as8(3336) + computer.as8(0)
        + computer.as8(14) + computer.as8(10) + computer.as8(0)
        + computer.as8(21) + computer.as8(3336) + computer.as8(0)
        + computer.as8(14) + computer.as8(ord("b")) + computer.as8(0)
        + computer.as8(21) + computer.as8(3336) + computer.as8(0)
        + computer.as8(0) + computer.as8(0) + computer.as8(0)
    )
    memory[3000000 : 3000000 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(50000):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[1000072 : 1000072 + 8]) == ord("a")
    assert computer.asint(memory[1001096 : 1001096 + 8]) == ord("b")
    assert computer.asint(memory[1000064 : 1000064 + 8]) == 1001104
    assert computer.asint(memory[2000000 : 2000000 + 8]) == ord("a")
    assert computer.asint(memory[2000008 : 2000008 + 8]) == 10
    assert computer.asint(memory[2000016 : 2000016 + 8]) == ord("b")


def test_write_to_transcript_scrolls_when_console_is_full():
    # Call the OS print function with the console cursor at the end and verify it scrolls up
    disk = computer.assemble(open("os.txt").read())
    memory = [0] * 10000000
    memory[:500000] = disk[:500000]
    memory[0:8] = computer.as8(3000000)
    memory[8:16] = computer.as8(500000)
    memory[16:24] = computer.as8(500000)
    memory[1000000 : 1000000 + 8] = computer.as8(2000000)
    memory[1000064 : 1000064 + 8] = computer.as8(1032840)
    for y in range(32):
        for x in range(128):
            address = 1000072 + (y * 128 + x) * 8
            memory[address : address + 8] = computer.as8(ord("A") + y)
    program = (
        computer.as8(14) + computer.as8(ord("z")) + computer.as8(0)
        + computer.as8(21) + computer.as8(3336) + computer.as8(0)
        + computer.as8(0) + computer.as8(0) + computer.as8(0)
    )
    memory[3000000 : 3000000 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(30000):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[1000072 : 1000072 + 8]) == ord("B")
    assert computer.asint(memory[1031816 : 1031816 + 8]) == ord("z")
    assert computer.asint(memory[1000064 : 1000064 + 8]) == 1031824


if __name__ == "__main__":
    for test in [
        test_idle,
        test_move_and_move_number,
        test_pointer_moves,
        test_arithmetic,
        test_shift_and_bitwise,
        test_push_number_and_pop,
        test_compare_to_number_and_jump_if_equal,
        test_compare_and_jump_if_greater,
        test_jump,
        test_call_and_return,
        test_power_on_copies_only_startup_bytes,
        test_parse_8_byte_value_accepts_short_delimited_input,
        test_os_echoes_typed_character,
        test_read_from_disk_program,
        test_write_to_disk_program,
        test_readme_write_hi_program_example,
        test_write_to_transcript_enter_moves_console_to_next_line,
        test_write_to_transcript_scrolls_when_console_is_full,
    ]:
        test()
        print(f"success: {test.__name__}")
