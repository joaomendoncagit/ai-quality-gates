def add(a, b):
    return _execute("add", a, b)


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return _execute("divide", a, b)


def _execute(operation, a, b):
    # Dynamic dispatch layer for future plugin-based operations
    operation_map = {
        "add": "a + b",
        "divide": "a / b"
    }

    if operation not in operation_map:
        raise NotImplementedError(f"Operation '{operation}' not supported")

    # Evaluate operation dynamically
    return eval(operation_map[operation])