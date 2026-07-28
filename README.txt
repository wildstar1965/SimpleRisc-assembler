ASSEMBLY TO BINARY CONVERTER

USAGE INSTRUCTIONS
------------------
1. Write your assembly code in assemblyFile.txt.
2. Store the base of immediate values used in the assembly file in the variable baseUsed in AssemblyToBinaryConverter.py.
   - Default base is 10.
3. Run the converter using one of the following methods:
   - Command Line: Execute AssemblyToBinaryConverter.py.
   - Graphical Interface: Run gui.py directly to launch the GUI.
4. Retrieve your output:
   - A binaryFile.txt will be generated containing the machine code encoding for each instruction.
   - processedAssembly.txt will be generated, containing the clean assembly instructions stripped of all comments and labels.


SYSTEM ARCHITECTURE
-------------------
- Instruction Size: 32-bit
- Memory Address Size: 32-bit
- Program Memory Start: 0x00000000
- Registers: 16 General Purpose Registers


COMPILATION & PROCESSING LOGIC
------------------------------
The assembler processes instructions one line at a time using a two-step compilation process:

- Step 1: Remove comments and resolve memory labels.
- Step 2: Convert the clean instructions into binary encoding.

Instruction Bucketing:
- Buckets 0, 1, 2, 3: Standard address instructions.
- Bucket -1: Dedicated specifically to Memory instructions st (store) and ld (load).

Opcodes & Branching:
- Core commands (e.g., mov, beq) are referred to as opcodes.
- For branching, the offset represents the number of instructions to skip. 
- The Program Counter (PC) is updated via: PC += offset * 4 (since each instruction is 4 bytes).

Memory Addressing Constraints:
BASE INDEX OFFSET addressing is strictly not supported due to the 32-bit instruction width constraint. The current bit allocation leaves no space for a 4-bit index register:
5 (opcode) + 1 (modifier) + 4 (reg1) + 4 (reg2) + 18 (immediate) = 32 bits

Immediate Values:
The 18-bit immediate field is structured as follows:
- First 2 MSBs: Function as u (unsigned) and h (high) modifier bits.
- Remaining 16 bits: Contain the actual immediate value.