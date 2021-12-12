#!/usr/bin/env python3

import random
import numpy as np
import json
from Crypto.Cipher import AES
import base64

import flag_data




def pad(s):
    block_size = 16
    remainder = len(s) % block_size
    padding_needed = block_size - remainder
    return s + padding_needed * ' '

def rotate45(qubit):
    r = {"r": 1.0/pow(2, 0.5),"i": -1.0/pow(2, 0.5)}
    return {"r": round(qubit["r"]*r["r"]-qubit["i"]*r["i"],1), "i": round(qubit["r"]*r["i"] + qubit["i"]*r["r"],1)}

def process_patterns(client_patt, satellite_patt, shared_key):
    res = ''
    for c, s, bit in zip(client_patt, satellite_patt, shared_key):
        if c==s:
            res += bit
    return res

def decode_client_seq(client_patt, client_qubits):
    res_bits = ''
    for basis, qubit in zip(client_patt, client_qubits):
        if basis == "lol":
            qubit = rotate45(qubit)
        # иногда, в физическом мире (не эмуляции) мы можем получить фигню.
        # Так что просто взять кубит из базы не выйдет, надо считать вероятности 
        # и генерить последовательность на основании этих распределений
        is_zero = round(pow(qubit['r'],2),1)
        is_one  = round(pow(qubit['i'],2),1)
        res_bits += str( np.random.choice([0,1], p = [is_zero, is_one]) )
    return res_bits

def generate_satellite_basis():
    basis = [random.choice(["kek", "lol"]) for i in range(len(flag_data.KEY)*32)]
    return basis


def process_user_data(user_json):

    user_basis  = json.loads(user_json)['basis']
    user_qubits = json.loads(user_json)['qubits']

    sat_basis = generate_satellite_basis()
    client_bits = decode_client_seq(user_basis, user_qubits)
    real_key = process_patterns(user_basis, sat_basis, client_bits)[:128]
    secret_key = int(real_key, 2).to_bytes(128//8, byteorder="big")

    flag = pad(flag_data.FLAG)
    cipher_config = AES.new(secret_key, AES.MODE_ECB)
    flag_ciphered = cipher_config.encrypt(flag.encode())
    
    return json.dumps({"basis":sat_basis, "flag": base64.b64encode(flag_ciphered).decode()})


from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["POST"])
def parse():
    content = request.get_json()
    return process_user_data(content)

app.run(host="0.0.0.0", port=31337)