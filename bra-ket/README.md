# Crypto | Bra-Ket

## Информация

> Мой домашний самообучающийся бот BB-84 последнее время стал сильно виснуть, как будто буквально принимает сигналы из космоса. Я сдампил часть нового сгенерированного кода, он конечно выглядит несуразно, сгенерирован роботом же, но поможешь разобраться? Там какая-то странная крипта.

## Деплой

Сервер на фласке, необходим сервер

## Выдать участникам

Исходники: [server.py](pub/server.py)

## Описание
Таск на "квантовую" криптографию, по факту странное PPC на изучение квантового протокола связи

## Решение

В таске я попытался сделать реализацию
квантового протокола BB84. Но, в чистой реализации, он бы просто палился и я специально немного покораптил код.

Суть решения сводится к раскуриванию протокола и написания клиента.

## Флаг

`CUP{d0_y0u_kn0w_wh4t_s0m3_s5tt3l1t3s_us3_qu4ntum_k3y_sh4r1ng}`

## Мое Решение

```
import json
import random
import flag_data
from Crypto.Cipher import AES
import base64
qubit_database = {
    "kek" : [{"r": 1.0,"i": 0.0}, {"r": 0.0,"i": 1.0}],
    "lol" : [{"r": 1.0/pow(2, 0.5),"i": 1.0/pow(2, 0.5)}, {"r": -1.0/pow(2, 0.5),"i": 1.0/pow(2, 0.5)}]
}

def process_basics(client_basis, server_basis, code):
    key = ''
    for var_c, var_s, bit in zip(client_basis, server_basis,code):
        if var_c == var_s:
            key += bit
    return key

BITS = 10

code = [random.choice("01") for _ in range(len(flag_data.KEY)*32)]
basis = [random.choice(["kek", "lol"]) for i in range(len(flag_data.KEY)*32)]
qubits = [qubit_database[basis][int(var)] for var, basis in zip(code, basis)]

jsn = json.dumps({"basis":basis, "qubits": qubits})

print("Code: {} \n Sequences: {}".format(code, jsn))
print("Trying to connect")

import requests

r = requests.post("http://localhost:31337", json=jsn)
print(r.status_code, r.text)
data = r.json()
key = process_basics(basis, data['basis'], code)[:128]
secret_key = int(key, 2).to_bytes(128//8, byteorder="big")
cipher_config = AES.new(secret_key, AES.MODE_ECB)
flag_ciphered = cipher_config.decrypt(base64.b64decode(data['flag']))

print(flag_ciphered)
```