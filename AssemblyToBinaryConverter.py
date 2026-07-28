'''
This project is made by:
Rounak Kumar -- 2401EC07,
J.N. Lohithaswan -- 2401EC44
'''

import MachineState
import re

class Engine:

    def __init__(self,assemblyFileName='',hexFileName='hex.txt',baseUsed=10):

        self.assemblyFileName = assemblyFileName
        self.assemblyLanguageBaseUsed = baseUsed
        self.hexFileName = hexFileName
        self.programCounter = 0
        self.currentInstruction = ''
        self.labelMap = {} #labels mapped to their memory addresses
        self.modifierBits = '00' # '00'  Bits u , h

    def raiseError(self,errorMessage):
        print(f'!!!ERROR: {errorMessage} !!!')
        print(f'Invalid Instruction at Line {self.programCounter//4+1}: \'{self.currentInstruction}\'')
        self.assemblyFile.close()
        self.hexFile.close()
        raise ValueError(f'!!!ERROR: {errorMessage} !!! \nInvalid Instruction at Line {self.programCounter//4+1}: \'{self.currentInstruction}\'')

    def stripComment(self,instruction):
        commentStartIndex = instruction.find('//')
        if commentStartIndex==-1:
            return instruction.strip(' \n')
        else:
            return instruction[:commentStartIndex].strip(' \n')

    def removeLabelAndUpdateLabelMap(self,instruction):
        didMatch = re.match(r'^\s*([A-Za-z0-9_]+)\:\s*(.*)',instruction)
        if didMatch:
            label = didMatch.group(1)
            self.labelMap[label] = self.programCounter
            return didMatch.group(2)
        else:
            return instruction

    def isImmediate(self,value):
        try:
            int(value, self.assemblyLanguageBaseUsed)
            return True
        except ValueError:
            return False
    
    def getBinary(self,value,bits):
        value = str(value)
        number = int(value,self.assemblyLanguageBaseUsed) #number in base 10
        return format((number & ((1 << bits) - 1)), f'0{bits}b')

    def makeLowerCaseExceptLabel(self,tokens):
        if MachineState.instructionAddressSize.get(tokens[0].lower(),None) == 1:
            tokens[0] = tokens[0].lower()
        else:
            tokens = [token.lower() for token in tokens]
        return tokens

    def zeroAddressInstructionDecoder(self,tokens):
        #Assembly Format --> Opcode  
        if len(tokens)>1:
            self.raiseError('Too many Paramters')
        elif len(tokens)<1:
            self.raiseError('Incomplete Paramters')
        binary = ''
        opcode = MachineState.opcodesBinary.get(tokens[0])
        binary += opcode
        binary += format(0,'027b') #27 0s as the offset
        return binary

    def oneAddressInstructionDecoder(self,tokens):
        # Assembly Format --> Opcode Label/Address
        '''
        We store the offset in the last 27 bits where offset = (Label Address - PC)//4
        Offset is a signed number stored as 2s complementary
        '''
        if len(tokens)>2:
            self.raiseError('Too many Paramters')
        elif len(tokens)<2:
            self.raiseError('Incomplete Paramters')
        memoryOffset = 0
        binary = ''
        opcode = tokens[0]
        binary += MachineState.opcodesBinary.get(opcode)
        if tokens[1].isnumeric(): #memoryOffset value is supplied directly
            memoryOffset = int(tokens[1],self.assemblyLanguageBaseUsed)
        else:
            target = self.labelMap.get(tokens[1],None) # find the corresponding address from the label
            if target==None:
                self.raiseError('Label \''+tokens[1]+'\' not found')
            else:
                memoryOffset = target-self.programCounter
        instructionOffset = memoryOffset // 4        
        binary += self.getBinary(instructionOffset,27) #bitmasking to convert -ve number in 2s complementary 27 bit format
        return binary
    
    def twoAddressInstructionDecoder(self,tokens):
        # Assembly Format --> Opcode Rd , Rs1/Imm
        if len(tokens)>3:
            self.raiseError('Too many Paramters')
        elif len(tokens)<3:
            self.raiseError('Incomplete Paramters')
        binary = ''
        opcode = tokens[0]
        binary += MachineState.opcodesBinary.get(opcode)
        RIbit = 1 if self.isImmediate(tokens[2]) else 0 #register immediate bit
        binary += str(RIbit) 
        if tokens[1] in MachineState.registerBinary:
            binary += MachineState.registerBinary.get(tokens[1]) #Destination Register
            if RIbit:
                binary += self.modifierBits
                binary += self.getBinary(tokens[2],16) #Immediate Value
                binary += '0000'
            else:
                if tokens[2] in MachineState.registerBinary:
                    binary += MachineState.registerBinary.get(tokens[2]) #Source Register 
                    binary += '0'*18
                else:
                    self.raiseError('Invalid Register Used')
        else:
            self.raiseError('Invalid Register Used') #Like R1x1 or r123
        return binary

    def threeAddressInstructionDecoder(self,tokens):
        # Assembly Format --> Opcode Rd , Rs1 , Rs2/Imm
        if len(tokens)>4:
            self.raiseError('Too many Paramters')
        elif len(tokens)<4:
            self.raiseError('Incomplete Paramters')
        binary = ''
        opcode = tokens[0]
        binary += MachineState.opcodesBinary.get(opcode)
        RIbit = 1 if self.isImmediate(tokens[3]) else 0 #register immediate bit
        binary += str(RIbit) 
        if tokens[1] in MachineState.registerBinary and tokens[2] in MachineState.registerBinary:
            binary += MachineState.registerBinary.get(tokens[1],None) #Destination Register
            binary += MachineState.registerBinary.get(tokens[2],None) #Source Register 1
            if RIbit:
                binary += self.modifierBits
                binary += self.getBinary(tokens[3],16) #Immediate Value
            else:
                if tokens[3] in MachineState.registerBinary:
                    binary += MachineState.registerBinary.get(tokens[3],None) #Source Register 2
                    binary += '0'*14
                else:
                    self.raiseError('Invalid Register Used')
        else:
            self.raiseError('Invalid Register Used') #Like R1x1 or r123
        return binary
    
    def memoryAddressInstructionDecoder(self,tokens):
        # Assembly Format --> Opcode Rd , R2/Imm[R1]
        if len(tokens)>3:
            self.raiseError('Too many Paramters')
        elif len(tokens)<3:
            self.raiseError('Incomplete Paramters')
        binary = ''
        opcode = tokens[0]
        binary += MachineState.opcodesBinary.get(opcode)
        pattern = re.match(r'^(.*)\[(.+)\]$',tokens[2])
        if not pattern:
            self.raiseError('Instruction Format Not Correct')
        base = pattern.group(2) #register
        offset = pattern.group(1) #register or immediate
        if offset == None or offset.strip()=='':
            offset = '0'
        RIbit = 1 if self.isImmediate(offset) else 0 #register immediate bit
        binary += str(RIbit)
        if tokens[1] in MachineState.registerBinary and base in MachineState.registerBinary:
            binary += MachineState.registerBinary.get(tokens[1]) #Destination Register
            binary += MachineState.registerBinary.get(base) #Base Register
            if RIbit:
                binary += self.modifierBits
                binary += self.getBinary(offset,16) #Immediate Value
            else:
                if offset in MachineState.registerBinary:
                    binary += MachineState.registerBinary.get(offset) #Offset Register 
                    binary += '0'*14
                else:
                    self.raiseError('Invalid Register Used')
        else:
            self.raiseError('Invalid Register Used')
        return binary

    def extractAndUpdateModifierBits(self,opcode):
        if len(opcode)==0:
            return ''
        if opcode in MachineState.opcodesBinary:
            self.modifierBits = '00'
            return opcode
        elif opcode[:-1] in MachineState.opcodesBinary:
            if opcode[-1] == 'u':
                self.modifierBits = '10'
                return opcode[:-1]
            elif opcode[-1] == 'h':
                self.modifierBits = '01'
                return opcode[:-1]
            else:
                return opcode
        else:
            return opcode
        

    def decodeTokens(self,tokens):
        binary = ''
        tokens[0] = self.extractAndUpdateModifierBits(tokens[0])
        opcodeBinary = MachineState.opcodesBinary.get(tokens[0],None)
        if  opcodeBinary==None: 
            self.raiseError('Illegal Opcode --> '+tokens[0])
        opcodeAddressType = MachineState.instructionAddressSize.get(tokens[0],None)
        if opcodeAddressType==0:
            binary = self.zeroAddressInstructionDecoder(tokens)
        elif opcodeAddressType==1:
            binary = self.oneAddressInstructionDecoder(tokens)
        elif opcodeAddressType==2:
            binary = self.twoAddressInstructionDecoder(tokens)
        elif opcodeAddressType==3:
            binary = self.threeAddressInstructionDecoder(tokens)
        elif opcodeAddressType==-1:
            binary = self.memoryAddressInstructionDecoder(tokens)
        else:
            self.raiseError('Opcode Address Type not found')
        return binary

    def preprocess(self,file): #resolve labels and removes comments
        newFileName = 'processedAssembly.txt'
        newFile = open(newFileName,'w')
        self.programCounter = 0
        for instruction in file:
            #handles comment removal and removing extra white spaces
            instruction = self.stripComment(instruction)
            #Handle Labels
            instruction = self.removeLabelAndUpdateLabelMap(instruction) #removes label from instruction and stores it in the label hashmap
            if instruction: # if we got only label in the line then no need to increment Program Counter and no instruction present
                newFile.write(instruction+'\n')
                self.programCounter += 4
        file.close()
        newFile.close()
        return open(newFileName,'r')
    
    def run(self):
        try:
            self.assemblyFile = open(self.assemblyFileName,'r')
        except:
            print('!! File ',self.assemblyFileName,' not found !!')
        self.hexFile = open(self.hexFileName,'w')
        self.assemblyFile = self.preprocess(self.assemblyFile) #removes comments finds and store labels 
        self.programCounter = 0
        for instruction in self.assemblyFile:
            instruction = instruction.strip() #removes \n
            self.currentInstruction = instruction
            tokens = re.split(MachineState.delimiters,instruction)
            tokens = self.makeLowerCaseExceptLabel(tokens)
            self.hexFile.write(format(int(self.decodeTokens(tokens),2),'08x')+'\n')
            self.programCounter += 4
            print(tokens)

        self.assemblyFile.close()
        self.hexFile.close()
        print('SUCCESSFULLY COMPILED. HexFile stored in -->',self.hexFileName)

if __name__ == '__main__':
    assemblyFileName = 'assemblyFile.txt'
    hexFileName = 'hexFile.txt'
    baseUsed = 10 # the base of immediate values supplied in the assembly file
    binaryEngine = Engine(assemblyFileName,hexFileName,baseUsed)
    binaryEngine.run()
