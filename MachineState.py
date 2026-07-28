'''
This project is made by:
Rounak Kumar -- 2401EC07,
J.N. Lohithaswan -- 2401EC44
'''

import re

registerBinary = {
    'r0' : '0000',
    'r1' : '0001',
    'r2' : '0010',
    'r3' : '0011',
    'r4' : '0100',
    'r5' : '0101',
    'r6' : '0110',
    'r7' : '0111',
    'r8' : '1000',
    'r9' : '1001',
    'r10' : '1010',
    'r11' : '1011',
    'r12' : '1100',
    'r13' : '1101',
    'r14' : '1110', #sp 
    'r15' : '1111' #ra
}

opcodesBinary = {
    'add': '00000',
    'not': '01000',
    'beq': '10000',
    'sub': '00001',
    'mov': '01001',
    'bgt': '10001',
    'mul': '00010',
    'lsl': '01010',
    'b': '10010',
    'div': '00011',
    'lsr': '01011',
    'call': '10011',
    'mod': '00100',
    'asr': '01100',
    'ret': '10100',
    'cmp': '00101',
    'nop': '01101',
    'and': '00110',
    'ld': '01110',
    'or': '00111',
    'st': '01111' 
}

delimitersCharacters = ' ,'
delimiters = re.compile(fr'[{delimitersCharacters}]+')

zeroAddressInstructions = ['nop','ret']
oneAddressInstructions = ['call','beq','bgt','b']
twoAddressInstructions = ['cmp','not','mov']
threeAddressInstructions = ['add','sub','mul','div','mod','and','or','lsl','lsr','asr']
memoryInstructions = ['ld','st']


instructionAddressSize = {}

for instr in zeroAddressInstructions:
    instructionAddressSize[instr] = 0

for instr in oneAddressInstructions:
    instructionAddressSize[instr] = 1

for instr in twoAddressInstructions:
    instructionAddressSize[instr] = 2

for instr in threeAddressInstructions:
    instructionAddressSize[instr] = 3

for instr in memoryInstructions:
    # we take the instruction address size as -1 for these to handle base index offset
    instructionAddressSize[instr] = -1