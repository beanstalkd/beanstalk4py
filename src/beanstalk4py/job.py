class Job(object):
    class State(object):
        ready    = 0x0100
        reserved = 0x0101
        delayed  = 0x0102
        buried   = 0x0103
