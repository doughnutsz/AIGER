import sys
import argparse

from dataclasses import dataclass

import aigsimgates as ag

# Implementation of a very stripped down version of the C program aigsim

# Source Files
# modelFile = 'aigTestSMV2.aag.txt'
# stimFile  = 'stim1.txt'
modelFile = 'aigTestLatch.aag.txt'
stimFile  = 'stimELatchSmall.txt'

STORE_PATH = '/Users/john/Jupyter/Machine Learning'

validInput = {"0","1"}

from dataclasses import dataclass
        
@dataclass
class Reader:
    
    inFile = ''
    
    def _init_(self):
        pass
    
    def openFile(self,file):
        
        self.inFile = open(file)
        
    def readHeader(self,model):
        
        args = (self.inFile.readline()).split()
        
        if args[0] != 'aag':
            return -1
        
        if len(args) < 6:
            sys.exit('Insufficient model parameters MILOA minimum requirement')
            
        model.maxvar      = int(args[1])
        model.num_inputs  = int(args[2])
        model.num_latches = int(args[3])
        model.num_outputs = int(args[4])
        model.num_ands    = int(args[5])
        
        if len(args) >= 7:
            model.num_bad = int(args[6])
            
        if len(args) >= 8:
            model.num_constraints = int(args[7])
       
        if len(args) >= 9:
            model.num_justice = int(args[8])

        if len(args) >= 10:
            model.num_fairness = int(args[9])

        return 0
    
    def validateInput(self,numArgs,errStr,verbose):
        
        args = (self.inFile.readline()).split()
        
        err = 0
        if len(args) < numArgs:
            print(errStr)
            err = -1
        
        if verbose == True:
            print(args)
            
        return args,err

#--------------------------------------------------------------------------------------

    def readModel(self,model):
        
        verbose = False
        gateList = [0] * (model.maxvar + 1)
        gateList[0] = ag.aiger_const(0,'Constant',0)
        
        model.inputs = [0]*model.num_inputs
        for i in range(0,model.num_inputs):
            args,err = self.validateInput(1,'Invalid model definition - Input',verbose)
            if err == 0:
                model.inputs[i] = ag.aiger_input(int(args[0]),'Input',i)
                gateList[int(int(args[0])/2)] = model.inputs[i]
                 
        model.latches = [0]*model.num_latches
        for i in range(0,model.num_latches):
            args,err = self.validateInput(2,'Invalid model definition - Latches',verbose)
            if err == 0:
                if len(args) == 2:
                    args.append('0')
                model.latches[i] = ag.aiger_latch(int(args[0]),int(args[1]),int(args[2]),i)
                gateList[int(int(args[0])/2)] = model.latches[i]
        
        model.outputs = [0]*model.num_outputs
        for i in range(0,model.num_outputs):
            args,err = self.validateInput(1,'Invalid model definition - Output',verbose)
            if err == 0:
                model.outputs[i] = ag.aiger_output(int(args[0]),'Output',i)
        
        # Read but ignore any bad states
        for i in range(0,model.num_bad):
            args,err = self.validateInput(1,'Invalid model definition - Bad State',verbose)
            
        # Read but ignore any constraints 
        for i in range(0,model.num_constraints):
            args,err = self.validateInput(1,'Invalid model definition - Constraints',verbose)

        # Read but ignore any justice properties 
        if model.num_justice > 0:
            for j in range(0,model.num_justice):
                tmp = (self.inFile.readline()).split()

            for j in range(0,model.num_justice):
                tmp1 = (self.inFile.readline()).split()
                tmp2 = (self.inFile.readline()).split()

        model.ands = [0]*model.num_ands
        for i in range(0,model.num_ands):
            args,err = self.validateInput(3,'Invalid model definition - Ands',verbose)
            if err == 0:
                model.ands[i] = ag.aiger_and(int(args[0]),int(args[1]),int(args[2]),i)
                gateList[int(int(args[0])/2)] = model.ands[i]

        for i in range(0,model.num_inputs):
            model.inputs[i].connect(gateList)
  
        for i in range(0,model.num_latches):
            model.latches[i].connect(gateList)

        for i in range(0,model.num_outputs):
            model.outputs[i].connect(gateList)

        for i in range(0,model.num_ands):
            model.ands[i].connect(gateList)

#--------------------------------------------------------------------------------------
              
    def getStim(self):
        
        args = (self.inFile.readline()).split()
        
        return args

#--------------------------------------------------------------------------------------
           
@dataclass
class Model:

    stepNum         = 0
    maxvar          = 0
    num_inputs      = 0
    num_latches     = 0
    num_outputs     = 0
    num_ands        = 0
    num_bad         = 0
    num_constraints = 0
    num_justice     = 0
    num_fairness    = 0

    inputs  = [] # [0..num_inputs]
    latches = [] # [0..num_latches]
    outputs = [] # [0..num_outputs]

    ands    = [] # [0..num_ands]
    
    current = [] # [0..maxvar+1] - holds current output of each gate

    def _init_(self):
        pass
    
    def initModel(self):
        self.stepNum = 0
        self.current = [0] * (self.maxvar + 1) # for index simplicity, index 0 is unused
        
        # Initialize the latches    
        # - Note this code does not support reset reset values outside {0,1}.
        
        for i in range(0,self.num_latches):
            self.current[int((self.latches[i].lit)/2)] = self.latches[i].reset
        
    # Does not support ground or don't care values
    
    def validateInput(self,args):
        
        err = 0
        if len(args) == self.num_inputs:
            current = [0] * self.num_inputs
            for i in range (self.num_inputs):
                if validInput.issuperset(args.rstrip()):   
                    current[i] = int(args[i])
                else:
                    print('invalid characters in input string')
                    err = -1
                    
        else:
            print('invalid input string length')
            err = -1

        return current,err
        
    def getCurVal(self,lit):
        val = self.current[int(lit/2)]
        if lit%2 != 0:
            val = int(bin(val+1)[-1])
        
        return val
    
    def step(self,args,verbose):
        
        for i in range(0,self.num_inputs):
            self.inputs[i].prepStep()
            
        for i in range(0,self.num_latches):
            self.latches[i].prepStep()

        for i in range(0,self.num_ands):            
            self.ands[i].prepStep()
        
        stim,err = self.validateInput(args)  

        # Process the input stimuli
        for i in range(0,self.num_inputs):
            self.inputs[i].curVal = stim[i]

        # Process the latches
        for i in range(0,self.num_latches):
            self.latches[i].step()

        # Process the and gates
        for i in range(0,self.num_ands):
            self.ands[i].step()
            
         # Process the output gates
        for i in range(0,self.num_outputs):
            self.outputs[i].step()

        if verbose == True:
            self.printState(self.stepNum)
        self.stepNum += 1
    
    def printResults(self):
        
        for i in range(0,self.num_latches):
            print('{:1}'.format(self.latches[i].curVal),end='')
        print(' ',end='')

        for i in range(0,self.num_inputs):
            print('{:1}'.format(self.inputs[i].curVal),end='')
        print(' ',end='')
            
        for i in range(0,self.num_outputs):
            print('{:1}'.format(self.outputs[i].curVal),end='')
        print(' ',end='')
        
        for i in range(0,self.num_latches):
            print('{:1}'.format(self.latches[i].nextVal),end='')

        print('')
        
    def printSelf(self):
        print('Model')
        print('-----')
        print('maxvar      = ',self.maxvar)
        print('num_inputs  = ',self.num_inputs)
        print('num_latches = ',self.num_latches)
        print('num_outputs = ',self.num_outputs)
        print('num_ands    = ',self.num_ands)
        
        for i in range(0,self.num_inputs):
            self.inputs[i].printSelf()
            
        for i in range(0,self.num_latches):
            self.latches[i].printSelf()
            
        for i in range(0,self.num_outputs):
            self.outputs[i].printSelf()
            
        for i in range(0,self.num_ands):
            self.ands[i].printSelf()
        
    def printState(self,stepNum=0):
    
        print("{:4d} ".format(stepNum),end='')
        for i in range(0,self.num_latches):
            print("{:1d}".format(self.latches[i].curVal),end='')
        print(' ',end='')
            
        for i in range(0,self.num_inputs):
            print("{:1d}".format(self.inputs[i].curVal),end='')
        print(' ',end='')
            
        for i in range(0,self.num_latches):
            print("{:1d}".format(self.latches[i].nextVal),end='')
        print(' ',end='')
            
        for i in range(0,self.num_outputs):
            print("{:1d}".format(self.outputs[i].curVal),end='')
        print(' ',end='')
            
        for i in range(0,self.num_ands):
            print("{:1d}".format(self.ands[i].curVal),end='')
            
        print('')
       
def main():

    verbose0 = False
    verbose1 = False
    verbose2 = False

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', type=str, default='', help='Model Filename')
    parser.add_argument('-s', type=str, default='', help='Stim Filename')
    parser.add_argument('-v0', action='store_true', help='Model Statistics')
    parser.add_argument('-v1', action='store_true', help='Model Output')
    parser.add_argument('-v2', action='store_true', help='Model Output with and gates')
    
    args = parser.parse_args()
    
    if args.m == '':
        sys.exit('No model file provided')
    else:
        modelFile = args.m
    
    if args.s == '':
        sys.exit('No stim file provided')
    else:
        stimFile = args.s

    if args.v0 == True:
        verbose0 = True
    
    if args.v1 == True:
        verbose1 = True
        
    if args.v2 == True:
        verbose2 = True
	
    model = Model()

    reader = Reader()
    reader.openFile(modelFile)
    reader.readHeader(model)
    reader.readModel(model)

    if verbose0 == True:
        model.printSelf()
        
    model.initModel()

    reader = Reader()
    reader.openFile(stimFile)

    done = False
    
    while done != True:
        stim = reader.getStim()
        if len(stim) > 0:
            if stim[0] == '.':
                done = True
            else:
                model.step(stim[0],verbose2)
                if verbose1 == True:
                    model.printResults()
            
        else:
            print('Stim file not properly terminated. Last line should only contain a period')
            done = True

if __name__== "__main__":
    main()