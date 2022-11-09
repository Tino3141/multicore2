# multicore

Assumptions
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

Assumptions on Analysis
* Execution cycles per core is the number of cycles the core was doing computation or waiting. 
  Cycles where the core is terminated is not counted.

TODO
- [ ] Figure out bus delay times "sending a cache block with N words (each word is 4 bytes) to another cache 
takes 2N cycle"
  