# AIGER
Python version of tools to work with AIG formatted files<br />


There are two versions of the code here. One is a standard py file. The other is a Jupyter notebook. The model and stim files for the jupyter notebook are hardcoded in the first cell.<br />

For the py file:<br />
```
python aigsim.py -h
usage: aigsim.py [-h] [-m M] [-s S] [-v0] [-v1] [-p0] [-p1] [-p2]

optional arguments:
  -h, --help  show this help message and exit
  -m M        Model Filename
  -s S        Stim Filename
  -v0         Model Statistics
  -v1         Model Output
  -p0         Print Option: Include simulation step
  -p1         Print Option: Include and gate states
  -p2         Print Option: Include coverage
```
A standard invocation:<br />

`python aigsim.py -m modelFile.aag -s stimFile.txt`

Verbose option -v0 prints model statistics:<br />
```
Model
maxvar      =  7
num_inputs  =  2
num_latches =  2
num_outputs =  1
num_ands    =  3
aiger_symbol - Type: Input  lit:  2                    input: I0      name:I0        
aiger_symbol - Type: Input  lit:  4                    input: I1      name:I1        
aiger_symbol - Type: Latch  lit: 12 next:  6 reset:  0 input: A0      name:L0        
aiger_symbol - Type: Latch  lit: 10 next:  8 reset:  0 input: A1      name:L1        
aiger_symbol - Type: Output lit: 14                    input: A2      name:O0        
aiger_symbol - Type: And    lit:  6 rhs0:  2  rhs1:  4 input: I0  I1  name:A0        
aiger_symbol - Type: And    lit:  8 rhs0:  4  rhs1:  7 input: I1  A0* name:A1        
aiger_symbol - Type: And    lit: 14 rhs0: 11  rhs1: 12 input: L1* L0  name:A2        
```
Verbose option -v1 with no print options prints model state at the end of each step of execution where<br />
- Column 1 = latches before step<br />
- Column 2 = input stimuli<br />
- Column 3 = output states<br />
- Column 4 = latches after step<br />

Example output from aigTestSMV2.aag.txt:<br />
```
00 11 0 10 
10 11 1 10 
10 10 1 00 
00 10 0 00 
00 11 0 10 
10 00 1 00  
```

Adding print option -p0 prints model state after the end of each step of execution with the addition of the and gate states:<br />
- Column 1 = model step<br />
- Column 2 = latches before step<br />
- Column 3 = input stimuli<br />
- Column 4 = output states<br />
- Column 5 = latches after step<br />

Example output from aigTestSMV2.aag.txt:<br />
```
   1 00 11 0 10 
   2 10 11 1 10 
   3 10 10 1 00 
   4 00 10 0 00 
   5 00 11 0 10 
   6 10 00 1 00 
```
Adding print option -p1 prints model state after the end of each step of execution with the addition of the and gate states:<br />
- Column 1 = model step<br />
- Column 2 = latches before step<br />
- Column 3 = input stimuli<br />
- Column 4 = output states<br />
- Column 5 = latches after step<br />
- Column 6 = and gate states<br />

```
   1 00 11 0 10 100 
   2 10 11 1 10 101 
   3 10 10 1 00 001 
   4 00 10 0 00 000 
   5 00 11 0 10 100 
   6 10 00 1 00 001 
   ```
 
 Adding print option -p2 prints model coverage. Each latch has two bits where the lower bit is having seen a '0' input and the upper bit denotes having seen a '1' input. Each and gate has four bits, two for each input. The upper two bits are the i0 input and the lower two bits are the i1 input. Like the latches, the upper bit of the pair denotes having seen a '1' and the lower a '0':<br />
- Column 1 = model step<br />
- Column 2 = latches before step<br />
- Column 3 = input stimuli<br />
- Column 4 = output states<br />
- Column 5 = latches after step<br />
- Column 6 = and gate states<br />
- Column 7 = latch coverage<br />
- Column 8 = and coverage<br />

**Note:** It is not recommended to use this option with models containing large numbers of and gates.

```
   1 00 11 0 10 100 0101 101001100110
   2 10 11 1 10 101 1101 101001101110
   3 10 10 1 00 001 1101 111011111110
   4 00 10 0 00 000 1101 111011111110
   5 00 11 0 10 100 1101 111011111110
   6 10 00 1 00 001 1101 111111111110
   ```

Print options may be used in any combination. -v1 is required to enable any print option.

# Model Files
The following model files are provided in the examples directory:
`aigTestSMV2.aag.txt`             - A simple toggling latch with enable. Stim file = stim1.txt
`counter.aag`                     - An AIGER benchmark file for a complex counter. Stim file = stimCounter.txt
`random_n_19_1_2_16_14_2_abc.aag` - An AIGER competition file with over 1M and gates. Stim file = stim3.txt

**Note:** `random_n_19_1_2_16_14_2_abc.aag` is an extremely large model with over 1M gates. Caution recommended on verbose print options used.
