import os


LOG_FILE = None


def setLogFile(path: str):
    """Set module-level debug flag for logging."""
    global LOG_FILE
    LOG_FILE = path


def LOG(*args, indent: int = 0, log_file: str, **kwargs):
    """
    Conditional logger. When debug is enabled via `set_debug(True)`,
    this prints to stdout and optionally appends the same output to
    `log_file` if provided.

    Parameters:
    - args: values to print (same semantics as built-in `print`).
    - indent: number of spaces to prefix the message with.
    - log_file: optional path to append the message to.
    - kwargs: forwarded to `print` for stdout (e.g., end, sep).
    """

    prefix = ' ' * indent
    # Build the message string similar to print()
    sep = kwargs.pop('sep', ' ')
    end = kwargs.pop('end', '\n')
    try:
        message = prefix + sep.join(str(a) for a in args) + end
    except Exception:
        # Fallback if conversion fails
        message = prefix + ' '.join(map(str, args)) + end
    try:
        dirn = os.path.dirname(log_file)
        if dirn:
            os.makedirs(dirn, exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as fh:
            fh.write(message)
    except Exception:
        # Avoid raising from logger
        pass

