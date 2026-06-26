import marshal
import dis
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('api/__pycache__/views.cpython-313.pyc', 'rb') as f:
    f.read(16)
    main_code = marshal.load(f)
    for c in main_code.co_consts:
        if hasattr(c, 'co_name') and c.co_name == 'serialize_book':
            print("Disassembly of serialize_book:")
            dis.dis(c)
