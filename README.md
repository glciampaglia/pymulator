# pymulator
Reproducible simulation for lazy Python programmers

Simple management tool for discrete simulators (e.g. urn models):
    - Specify parameters scans in configuration file -- _nested for loops no more!_
    - Automatically average out replications to smooth out sampling noise
    - Returns data frame for easy manipulation, observable saved alongside parameters for easy plotting
    - Store internal state of PRNG for replication

Desiderata:
    - Specify statistics other than the sampling average
    - Automatic plot generation
    - Parallel execution
