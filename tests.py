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
