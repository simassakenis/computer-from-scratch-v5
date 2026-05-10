import computer


def instruction(opcode, operand1=0, operand2=0):
    return computer.as8(opcode) + computer.as8(operand1) + computer.as8(operand2)


def test_idle():
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    memory[24 : 24 + 24] = instruction(0)

    memory, equal_flag, greater_flag = computer.cpu_step(memory, 0, 0)

    assert computer.asint(memory[0:8]) == 24
    assert equal_flag == 0
    assert greater_flag == 0


def test_move_and_move_number():
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = instruction(2, 42, 0) + instruction(1, 0, 1)
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(2):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2008:2016]) == 42


def test_pointer_moves():
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        instruction(2, 3000, 0)
        + instruction(2, 65, 1)
        + instruction(4, 1, 0)
        + instruction(3, 0, 2)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(4):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[3000:3008]) == 65
    assert computer.asint(memory[2016:2024]) == 65


def test_arithmetic():
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        instruction(2, 7, 0)
        + instruction(2, 5, 1)
        + instruction(5, 0, 1)
        + instruction(6, -2, 1)
        + instruction(7, 0, 1)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(5):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2008:2016]) == 3


def test_shift_and_bitwise():
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        instruction(2, 1, 0)
        + instruction(2, 3, 1)
        + instruction(8, 0, 1)
        + instruction(9, 2, 1)
        + instruction(10, 0, 1)
        + instruction(11, 1, 1)
        + instruction(2, 7, 2)
        + instruction(12, 2, 1)
        + instruction(13, 2, 1)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(9):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2008:2016]) == 2


def test_push_number_and_pop():
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = instruction(14, 55) + instruction(15)
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
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        instruction(2, 5, 0)
        + instruction(17, 0, 5)
        + instruction(18, 120)
        + instruction(2, 1, 1)
        + instruction(2, 9, 1)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(4):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2008:2016]) == 9


def test_compare_and_jump_if_greater():
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        instruction(2, 9, 0)
        + instruction(2, 3, 1)
        + instruction(16, 0, 1)
        + instruction(19, 144)
        + instruction(2, 1, 2)
        + instruction(2, 8, 2)
    )
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(5):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2016:2024]) == 8


def test_jump():
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = instruction(20, 72) + instruction(2, 1, 0) + instruction(2, 2, 0)
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(2):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[2000:2008]) == 2


def test_call_and_return():
    memory = [0] * 10000000
    memory[0:8] = computer.as8(24)
    memory[8:16] = computer.as8(2000)
    memory[16:24] = computer.as8(2000)
    program = (
        instruction(14, 123)
        + instruction(21, 120)
        + instruction(1, 0, 1)
        + instruction(0)
        + instruction(1, -3, 0)
        + instruction(22)
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
    disk = computer.assemble(open("disk.txt").read())
    disk[500000 : 500000 + 8] = computer.as8(123)
    memory = [0] * 10000000

    memory[:500000] = disk[:500000]

    assert computer.asint(memory[500000 : 500000 + 8]) == 0


def test_os_echoes_typed_character():
    disk = computer.assemble(open("disk.txt").read())
    memory = [0] * 10000000
    memory[:500000] = disk[:500000]
    keys = [ord("a")]
    equal_flag = 0
    greater_flag = 0

    for cycle in range(2000):
        if cycle % 10 == 0 and keys and computer.asint(memory[1000048 : 1000048 + 8]) == 1:
            memory[1000056 : 1000056 + 8] = computer.as8(keys.pop(0))
            memory[1000048 : 1000048 + 8] = computer.as8(0)
        memory, disk = computer.disk_step(memory, disk)
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert computer.asint(memory[1000072 : 1000072 + 8]) == ord("a")


def test_read_from_disk_program():
    disk = computer.assemble(open("disk.txt").read())
    memory = [0] * 10000000
    memory[:500000] = disk[:500000]
    command = f"{3768:016x}{1056:016x}{0:016x}{8:016x}"
    keys = [ord(character) for character in command] + [10]
    expected = command + "0000000000000018"
    equal_flag = 0
    greater_flag = 0

    for cycle in range(5000):
        if cycle % 10 == 0 and keys and computer.asint(memory[1000048 : 1000048 + 8]) == 1:
            memory[1000056 : 1000056 + 8] = computer.as8(keys.pop(0))
            memory[1000048 : 1000048 + 8] = computer.as8(0)
        memory, disk = computer.disk_step(memory, disk)
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    result = ""
    for address in range(1000072, 1000072 + len(expected) * 8, 8):
        result += chr(computer.asint(memory[address : address + 8]) & 255)

    assert keys == []
    assert result == expected


def test_write_to_disk_program():
    disk = computer.assemble(open("disk.txt").read())
    memory = [0] * 10000000
    memory[:500000] = disk[:500000]
    disk_address = 600000
    value = 0x6869
    command = f"{4824:016x}{1128:016x}{disk_address:016x}{value:016x}"
    keys = [ord(character) for character in command] + [10]
    equal_flag = 0
    greater_flag = 0

    for cycle in range(10000):
        if cycle % 10 == 0 and keys and computer.asint(memory[1000048 : 1000048 + 8]) == 1:
            memory[1000056 : 1000056 + 8] = computer.as8(keys.pop(0))
            memory[1000048 : 1000048 + 8] = computer.as8(0)
        memory, disk = computer.disk_step(memory, disk)
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert keys == []
    assert computer.asint(disk[disk_address : disk_address + 8]) == value
    assert computer.asint(disk[disk_address + 8 : disk_address + 16]) == 0


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
        test_os_echoes_typed_character,
        test_read_from_disk_program,
        test_write_to_disk_program,
    ]:
        test()
        print(f"success: {test.__name__}")
