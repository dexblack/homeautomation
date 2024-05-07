import pprint

DEBUG_LEVEL = 2  # Adjust this constant to set the debug level

def dbgprint(*args, level=1):
    """
    Debug print function that prints the arguments if the specified debug level is met or exceeded.
    
    Args:
        *args: Variable-length argument list.
        level (int): Debug level of the message. Messages with levels less than or equal to DEBUG_LEVEL will be printed.
    """
    if level <= DEBUG_LEVEL:
        for arg in args:
            pprint.pprint(arg)

def info(*args):
    """Prints an informational message."""
    dbgprint("[INFO]", *args, level=1)

def debug(*args):
    """Prints a debug message."""
    dbgprint("[DEBUG]", *args, level=2)

def trace(*args):
    """Prints a trace message."""
    dbgprint("[TRACE]", *args, level=3)