def str_rjust(string, sym, length):
    while len(string) < length:
        string += sym[0]
    return string


def str_ljust(string, sym, length):
    while len(string) < length:
        string = sym[0] + string
    return string


def str_cjust(stringl, stringr, sym, length):
    if len(stringl) + len(stringr) > length:
        stringl = stringl[:length//2]
        stringr = stringr[:length//2]
    return stringl + sym*(length - len(stringl) - len(stringr)) + stringr


def progress_bar(expiry, steps_count, length):
    prog = "|" * (length * expiry // steps_count)
    progress = str_rjust(prog, " ", length)
    return f'[{progress}]'
