# Multicore Cache Coherence Protocol Simulator

## Overview

This repository is a multicore architecture simulation with 3 cache coherance protocols implemented (MESI, MOESI, Dragon). Cache size, cache associativity, and block size are all adjustable in the simulator for each coherance protocol. 

## How to Run

To run the simulator on your own computer make be updated to Python version 3.10.6 or later and pull this repository. The simulator can be run using the following command. 
```
<Python> simulator.py -p <Protocol type> -i <instruction directory>
```
All analytical results will be printed in a log file named 
```
<instruction directory_protocol>.log 
```
For more advanced tests, cache size can also be specified with the -c parameter, associativity can be specified with the -a parameter, and block size can be specified with the -b parameter.

# Architecture Testing and Results

## Assumptions
Due to the large array of multicore architecture designs, we made some basic assumptions that our simulator relies upon in order to gain consistency and accuracy on the metrics outputted by the simulator. 

* 100 cycle wait for fetching block from memory and 100 cycle wait for eviction 
  does not occur in parallel 
* Core reading from cache for state takes 1 cycle
* Core updating cache's state takes 1 cycle, unless an eviction occurs in which
  case it is 100 cycles. 
* We always flush on a BusRdX unless we are in an invalid state
* When going from invalid to shared, if all other cores are on share, invalid core 
  goes to shared immediately 
* If multiple flushes occur to the same address, we only flush once and ignore
  the rest
* We assume if multiple writes are occuring since they overwrite each other, we don't have to wait for other cores to flush
* Assuming bus transaction packet size is 1 word. Only sending 1 enum and 1 address per us transaction
* Memory address is 32-bit. Note that the address shown in the example trace file is 24 bits  because  the  8  most  significant  bits  are  sometimes  0.  So  the  address  0x817b08  is actually 0x00817b08
* Each memory reference accesses 32-bit (4-bytes) of data. That is word  size is 4-bytes. 
* We are only interested in the data cache and will not model the instruction cache.
* We are only interested in the data cache and will not model the instruction cache.
* L1 data cache uses write-back, write-allocate policy and LRU replacement policy. 
* L1 data caches are kept coherent using cache coherence protocol. 
* Initially all the caches are empty. 
* The  bus  uses  first  come  first  serve  arbitration  policy  when  multiple  processor attempt bus transactions simultaneously. Ties are broken arbitrarily.
* The L1 data caches are backed up by main memory --- there is no L2 data cache. 
* L1 cache hit is 1 cycle. Fetching a block from memory to cache takes additional 100 cycles. Sending a word from one cache to another (e.g., BusUpdate) takes only 2 cycles. However, sending a cache block with N words (each word is 4 bytes) to another cache takes 2N cycle. Assume that evicting a dirty cache block to memory when it gets replaced is 100 cycles.

## Assumptions on Analysis
* Execution cycles per core is the number of cycles the core was doing computation or waiting. 
  Cycles where the core is terminated is not counted.

Link to testing and analysis for Multicore Assignment 2 is here: https://docs.google.com/document/d/1snTwnJfbubvrIEZE2q-X5KE_iscI-k3hduRIcJERjRM/edit?usp=sharing
  