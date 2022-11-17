import os
import argparse
import logging
from computer import Computer
from definitions import PROTOCOLS

def readFile(dir):
    
    # Contains all instructions for every core
    instructions = []
    for file_name in os.listdir(dir):
        
        # instruction list per core
        instrList = []
        with open(dir+"/"+file_name, "r") as f:
            lines = f.readlines()
            print(len(lines))

            for line in lines:
                words = line.split()
                
                # Every line contains 2 entries: first instruction type, second memory location or time spent on instruction
                tmp = (int(words[0]), int(words[1], 16))
                instrList.append(tmp)
        instructions.append(instrList)
    return instructions     

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--protocol", default="MOESI", choices=['MESI', 'MOESI', 'Dragon'])
    parser.add_argument("-i", "--input", default="bodytrack_four", choices=['blackscholes_four', 'bodytrack_four', 'fluidanimate_four', 'test_four'])
    parser.add_argument("-c", "--cache", default=1024, type=int)
    parser.add_argument("-a", "--associativity", default=4, type=int)
    parser.add_argument("-b", "--block", default=16, type=int)

    
    ARGS = parser.parse_args()

    log_file = f"{ARGS.input}_{ARGS.protocol}.log"
    logging.basicConfig(level=logging.DEBUG, filename=log_file, filemode='w')
    logging.info("Starting to read file %s", ARGS.input)

    instructions = readFile("./{}".format(ARGS.input))

    logging.info("Finished reading file %s", ARGS.input)
    computer = None
    if ARGS.protocol == "MESI":
        computer = Computer(instructions, ARGS.block, ARGS.associativity, ARGS.cache, protocol=PROTOCOLS.MESI)
    elif ARGS.protocol == "Dragon":
        computer = Computer(instructions, ARGS.block, ARGS.associativity, ARGS.cache, protocol=PROTOCOLS.Dragon)
    elif ARGS.protocol == "MOESI":
        computer = Computer(instructions, ARGS.block, ARGS.associativity, ARGS.cache, protocol=PROTOCOLS.MOESI)
    else: 
        raise "Invalid protocol specified"
        
    logging.info("Starting the computer")
    computer.start()
    logging.info("Closing the computer")

if __name__ == "__main__":
    main()
