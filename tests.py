import computer


def read8(memory, address):
    return computer.asint(memory[address : address + 8])


def write8(memory, address, value):
    memory[address : address + 8] = computer.as8(value)


def instruction(opcode, operand1=0, operand2=0):
    return computer.as8(opcode) + computer.as8(operand1) + computer.as8(operand2)


def slot(memory, index):
    return read8(memory, 8) + index * 8


def label_addresses(source):
    opcodes = {
        "move",
        "moveNumber",
        "moveFromPointer",
        "moveToPointer",
        "add",
        "addNumber",
        "subtract",
        "shiftLeft",
        "shiftLeftByNumber",
        "shiftRight",
        "shiftRightByNumber",
        "bitwiseAnd",
        "bitwiseAndWithNumber",
        "pushNumber",
        "pop",
        "compare",
        "compareToNumber",
        "jumpIfEqual",
        "jumpIfGreater",
        "jump",
        "call",
        "return",
    }
    labels = {}
    address = 0

    for raw_line in source.splitlines():
        line = raw_line.split("//")[0].rstrip()
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

    return labels


def console(memory, length):
    result = []
    for address in range(1000072, 1000072 + length * 8, 8):
        result.append(chr(read8(memory, address) & 255))
    return "".join(result)


def test_idle():
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
    memory[24 : 24 + 24] = instruction(0)

    memory, equal_flag, greater_flag = computer.cpu_step(memory, 0, 0)

    assert read8(memory, 0) == 24
    assert equal_flag == 0
    assert greater_flag == 0


def test_move_and_move_number():
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
    program = instruction(2, 42, 0) + instruction(1, 0, 1)
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(2):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert read8(memory, slot(memory, 1)) == 42


def test_pointer_moves():
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
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

    assert read8(memory, 3000) == 65
    assert read8(memory, slot(memory, 2)) == 65


def test_arithmetic():
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
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

    assert read8(memory, slot(memory, 1)) == 3


def test_shift_and_bitwise():
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
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

    assert read8(memory, slot(memory, 1)) == 2


def test_push_number_and_pop():
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
    program = instruction(14, 55) + instruction(15)
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(2):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert read8(memory, 2000) == 55
    assert read8(memory, 16) == 2000
    assert equal_flag == 0
    assert greater_flag == 0


def test_compare_to_number_and_jump_if_equal():
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
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

    assert read8(memory, slot(memory, 1)) == 9


def test_compare_and_jump_if_greater():
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
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

    assert read8(memory, slot(memory, 2)) == 8


def test_jump():
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
    program = instruction(20, 72) + instruction(2, 1, 0) + instruction(2, 2, 0)
    memory[24 : 24 + len(program)] = program
    equal_flag = 0
    greater_flag = 0

    for _ in range(2):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert read8(memory, slot(memory, 0)) == 2


def test_call_and_return():
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
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

    assert read8(memory, 8) == 2000
    assert read8(memory, 16) == 2008
    assert read8(memory, slot(memory, 1)) == 123


def test_os_echoes_typed_character():
    disk = computer.assemble(computer.operating_system_source)
    memory = [0] * len(disk)
    memory[:] = disk[:]
    keys = [ord("a")]
    equal_flag = 0
    greater_flag = 0

    for cycle in range(2000):
        if cycle % 10 == 0 and keys and read8(memory, 1000048) == 1:
            write8(memory, 1000056, keys.pop(0))
            write8(memory, 1000048, 0)
        memory, disk = computer.disk_step(memory, disk)
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert console(memory, 1) == "a"


def test_os_invokes_read_disk_program():
    disk = computer.assemble(computer.operating_system_source)
    memory = [0] * len(disk)
    memory[:] = disk[:]

    labels = label_addresses(computer.operating_system_source)
    program_start = labels["readFromDiskProgram"]
    program_length = labels["writeToDiskProgram"] - program_start
    command = (
        f"{program_start:016x}"
        f"{program_length:016x}"
        f"{0:016x}"
        f"{8:016x}"
    )
    keys = [ord(character) for character in command] + [10]
    expected = command + "0000000000000018"
    equal_flag = 0
    greater_flag = 0

    for cycle in range(5000):
        if cycle % 10 == 0 and keys and read8(memory, 1000048) == 1:
            write8(memory, 1000056, keys.pop(0))
            write8(memory, 1000048, 0)
        memory, disk = computer.disk_step(memory, disk)
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

    assert keys == []
    assert console(memory, len(expected)) == expected


def run(test):
    test()
    print(f"success: {test.__name__}")


if __name__ == "__main__":
    run(test_idle)
    run(test_move_and_move_number)
    run(test_pointer_moves)
    run(test_arithmetic)
    run(test_shift_and_bitwise)
    run(test_push_number_and_pop)
    run(test_compare_to_number_and_jump_if_equal)
    run(test_compare_and_jump_if_greater)
    run(test_jump)
    run(test_call_and_return)
    run(test_os_echoes_typed_character)
    run(test_os_invokes_read_disk_program)
