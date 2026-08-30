"""
====================================================================
 SIMPLE JAVA BYTECODE SIMULATOR (subset)
====================================================================
Supports: ldc, iload, istore, iadd, isub, imul, idiv,
          ifeq, iflt, ifgt, read, print

Design (kept deliberately simple so it is easy to modify in an exam):

1. INSTRUCTIONS  -> a plain Python list of strings, one per line,
                    exactly as read from the input file.
                    instructions[pc] is the current instruction.

2. OPERAND STACK -> a plain Python list used as a stack.
                    push  = stack.append(x)
                    pop   = stack.pop()
                    top   = stack[-1]

3. LOCAL VARS    -> a plain Python list of fixed size (default 10),
                    all initialised to 0.
                    locals[i] = value of local variable i.

4. PROGRAM COUNTER (PC) -> a single integer, pc.
                    Normally pc = pc + 1 after each instruction.
                    A taken conditional jump sets pc = target instead.

Execution loop:
    while pc < len(instructions):
        read instructions[pc]
        split into opcode and (optional) argument
        run the matching branch (if/elif chain)
        each branch is responsible for moving pc forward,
        EXCEPT arithmetic / stack / io instructions which just do
        "pc += 1" at the bottom of the loop (see NEXT_PC pattern below)
====================================================================
"""

MAX_STACK_SIZE = 10      # as required by the project statement
MAX_LOCALS = 20          # "you may use a larger size if you need it"


def load_program(filename):
    """python simulator.py testA.txt
    Reads a bytecode program from a text file: one instruction per line.
    Blank lines and lines starting with '#' (comments) are ignored.
    Returns a list of instruction strings, e.g. ["ldc 5", "istore 0", ...]
    """
    instructions = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            instructions.append(line)
    return instructions


def run(instructions, input_values=None, trace=False):
    """
    Executes the given list of instructions.

    input_values: optional list of ints to feed to `read`, instead of
                  asking the real keyboard (very useful for automated
                  testing during the exam!). If None, input() is used.

    trace: if True, prints pc / instruction / stack / locals after
           every step (this is exactly the kind of thing an examiner
           may ask you to add -- here it's already built in as a flag).

    Returns the list of everything that was `print`-ed (as ints),
    so test code can check the output automatically.
    """
    stack = []                 # operand stack
    local_vars = [0] * MAX_LOCALS
    pc = 0                     # program counter
    printed_output = []

    # a private cursor into input_values, if we're using canned input
    input_cursor = [0]

    def do_read():
        if input_values is not None:
            value = input_values[input_cursor[0]]
            input_cursor[0] += 1
        else:
            value = int(input())
        return value

    while pc < len(instructions):
        line = instructions[pc]
        parts = line.split()
        opcode = parts[0]
        arg = int(parts[1]) if len(parts) > 1 else None

        if trace:
            print(f"[pc={pc:3}] {line:<12} stack={stack} locals={local_vars[:6]}")

        # ---------- default: most instructions just move to pc+1 ----------
        next_pc = pc + 1

        if opcode == "ldc":
            # push a constant onto the stack
            stack.append(arg)

        elif opcode == "iload":
            # push the value of local variable `arg`
            stack.append(local_vars[arg])

        elif opcode == "istore":
            # pop the top of stack into local variable `arg`
            value = stack.pop()
            local_vars[arg] = value

        elif opcode == "iadd":
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)

        elif opcode == "isub":
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)

        elif opcode == "imul":
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)

        elif opcode == "idiv":
            b = stack.pop()
            a = stack.pop()
            stack.append(a // b)   # integer division

        elif opcode == "ifeq":
            value = stack.pop()
            if value == 0:
                next_pc = arg          # jump!
        elif opcode == "iflt":
            value = stack.pop()
            if value < 0:
                next_pc = arg
        elif opcode == "ifgt":
            value = stack.pop()
            if value > 0:
                next_pc = arg

        elif opcode == "read":
            stack.append(do_read())

        elif opcode == "print":
            # prints the value on top of the stack WITHOUT removing it
            # (the spec only says "prints the integer on top of the
            #  stack" -- it does not say the stack shrinks). Note this
            # design choice: an examiner could ask you to make print
            # pop instead -- that is a one-line change (see guide).
            print(stack[-1])
            printed_output.append(stack[-1])
        elif opcode == "sort3down":
            c = stack.pop()
            b = stack.pop()
            a = stack.pop()

            values = [a, b, c]
            values.sort(reverse=True)

            stack.extend(values)

            print(stack)   # temporary testing line

        else:
            raise ValueError(f"Unknown instruction: {opcode}")

        pc = next_pc

    return printed_output


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python simulator.py <program.txt>")
        sys.exit(1)
    program = load_program(sys.argv[1])
    run(program)
