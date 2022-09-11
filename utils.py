import os


def create_path(path):
    try:
        os.mkdir(path)
    except OSError:
        pass
    except Exception as e:
        print(e)


def megabytes_to_bytes(n):
    return n * 1024 * 1000


def bytes_to_megabytes(n):
    return round(n / 1024 / 1000, 2)
