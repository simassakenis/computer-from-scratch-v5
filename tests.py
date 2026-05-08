import computer


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


def read8(memory, address):
    value = 0
    for byte in memory[address : address + 8]:
        value = value * 256 + byte
    return value


def write8(memory, address, value):
    memory[address : address + 8] = as8(value)


def instruction(opcode, operand1=0, operand2=0):
    return as8(opcode) + as8(operand1) + as8(operand2)


def reset(program):
    memory = [0] * 4000000
    write8(memory, 0, 24)
    write8(memory, 8, 2000)
    write8(memory, 16, 2000)
    memory[24 : 24 + len(program)] = program
    return memory, 0, 0


def slot(memory, index):
    return read8(memory, 8) + index * 8


def run_steps(memory, equal_flag, greater_flag, count):
    for _ in range(count):
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)
    return memory, equal_flag, greater_flag


def label_addresses(source, start_address):
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

    return labels


def boot_os():
    disk = [0] * 4000000
    memory = [0] * len(disk)

    write8(disk, 0, 24)
    write8(disk, 8, 500000)
    write8(disk, 16, 500000)

    operating_system = computer.assemble(computer.operating_system_source, 24)
    disk[24 : 24 + len(operating_system)] = operating_system
    memory[:] = disk[:]

    return memory, disk, 0, 0


def run_os_with_keys(keys, stop, max_cycles=1000000):
    memory, disk, equal_flag, greater_flag = boot_os()
    keys = list(keys)

    for _ in range(max_cycles):
        if read8(memory, 1000048) == 1 and keys:
            write8(memory, 1000056, keys.pop(0))
            write8(memory, 1000048, 0)

        memory, disk = computer.disk_step(memory, disk)
        memory, equal_flag, greater_flag = computer.cpu_step(memory, equal_flag, greater_flag)

        if stop(memory, keys):
            return memory, disk

    raise AssertionError("OS test did not finish")


def transcript(memory):
    end = read8(memory, 1000000)
    result = []
    for address in range(2000000, end, 8):
        result.append(chr(read8(memory, address) & 255))
    return "".join(result)


def console_prefix(memory, length):
    result = []
    for address in range(1000072, 1000072 + length * 8, 8):
        result.append(chr(read8(memory, address) & 255))
    return "".join(result)


def test_idle():
    memory, equal_flag, greater_flag = reset(instruction(0))
    memory, _, _ = computer.cpu_step(memory, equal_flag, greater_flag)
    assert read8(memory, 0) == 24


def test_move_and_move_number():
    memory, equal_flag, greater_flag = reset(instruction(2, 42, 0) + instruction(1, 0, 1))
    memory, _, _ = run_steps(memory, equal_flag, greater_flag, 2)
    assert read8(memory, slot(memory, 1)) == 42


def test_pointer_moves():
    memory, equal_flag, greater_flag = reset(
        instruction(2, 3000, 0)
        + instruction(2, 65, 1)
        + instruction(4, 1, 0)
        + instruction(3, 0, 2)
    )
    memory, _, _ = run_steps(memory, equal_flag, greater_flag, 4)
    assert read8(memory, 3000) == 65
    assert read8(memory, slot(memory, 2)) == 65


def test_arithmetic():
    memory, equal_flag, greater_flag = reset(
        instruction(2, 7, 0)
        + instruction(2, 5, 1)
        + instruction(5, 0, 1)
        + instruction(6, -2, 1)
        + instruction(7, 0, 1)
    )
    memory, _, _ = run_steps(memory, equal_flag, greater_flag, 5)
    assert read8(memory, slot(memory, 1)) == 3


def test_shift_and_bitwise():
    memory, equal_flag, greater_flag = reset(
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
    memory, _, _ = run_steps(memory, equal_flag, greater_flag, 9)
    assert read8(memory, slot(memory, 1)) == 2


def test_push_number():
    memory, equal_flag, greater_flag = reset(instruction(14, 55))
    memory, _, _ = computer.cpu_step(memory, equal_flag, greater_flag)
    assert read8(memory, 2000) == 55
    assert read8(memory, 16) == 2008


def test_compare_to_number_and_jump_if_equal():
    memory, equal_flag, greater_flag = reset(
        instruction(2, 5, 0)
        + instruction(16, 0, 5)
        + instruction(17, 120)
        + instruction(2, 1, 1)
        + instruction(2, 9, 1)
    )
    memory, _, _ = run_steps(memory, equal_flag, greater_flag, 4)
    assert read8(memory, slot(memory, 1)) == 9


def test_compare_and_jump_if_greater():
    memory, equal_flag, greater_flag = reset(
        instruction(2, 9, 0)
        + instruction(2, 3, 1)
        + instruction(15, 0, 1)
        + instruction(18, 144)
        + instruction(2, 1, 2)
        + instruction(2, 8, 2)
    )
    memory, _, _ = run_steps(memory, equal_flag, greater_flag, 5)
    assert read8(memory, slot(memory, 2)) == 8


def test_jump():
    memory, equal_flag, greater_flag = reset(
        instruction(19, 72) + instruction(2, 1, 0) + instruction(2, 2, 0)
    )
    memory, _, _ = run_steps(memory, equal_flag, greater_flag, 2)
    assert read8(memory, slot(memory, 0)) == 2


def test_call_and_return():
    memory, equal_flag, greater_flag = reset(
        instruction(14, 123)
        + instruction(20, 120)
        + instruction(1, 0, 1)
        + instruction(0)
        + instruction(1, -3, 0)
        + instruction(21)
    )
    memory, _, _ = run_steps(memory, equal_flag, greater_flag, 5)
    assert read8(memory, 8) == 2000
    assert read8(memory, 16) == 2008
    assert read8(memory, slot(memory, 1)) == 123


def test_os_echoes_typed_character():
    memory, _ = run_os_with_keys(
        [ord("a")],
        lambda memory, keys: not keys and console_prefix(memory, 1) == "a",
    )
    assert transcript(memory) == "a"
    assert console_prefix(memory, 1) == "a"


def test_os_invokes_read_disk_program():
    labels = label_addresses(computer.operating_system_source, 24)
    program_start = labels["readFromDiskProgram"]
    program_length = labels["writeToDiskProgram"] - program_start
    command = (
        f"{program_start:016x}"
        f"{program_length:016x}"
        f"{0:016x}"
        f"{8:016x}"
    )
    expected_output = "0000000000000018"
    expected = command + "\n" + expected_output

    memory, _ = run_os_with_keys(
        [ord(character) for character in command] + [10],
        lambda memory, keys: not keys and console_prefix(memory, len(expected)) == expected,
    )

    assert transcript(memory) == expected
    assert console_prefix(memory, len(expected)) == expected


def run(test):
    test()
    print(f"success: {test.__name__}")


if __name__ == "__main__":
    run(test_idle)
    run(test_move_and_move_number)
    run(test_pointer_moves)
    run(test_arithmetic)
    run(test_shift_and_bitwise)
    run(test_push_number)
    run(test_compare_to_number_and_jump_if_equal)
    run(test_compare_and_jump_if_greater)
    run(test_jump)
    run(test_call_and_return)
    run(test_os_echoes_typed_character)
    run(test_os_invokes_read_disk_program)
