"""
The task is to simulate an M/M/k system with a single queue.
Complete the skeleton code and produce results for three experiments.
The study is mainly to show various results of a queue against its ro parameter.
ro is defined as the ratio of arrival rate vs service rate.
For the sake of comparison, while plotting results from simulation, also produce the analytical results.
"""

import numpy as np
import heapq
import random
import matplotlib.pyplot as plt
import math


# Parameters
class Params:
    def __init__(self, lambd, mu, k):
        self.lambd = lambd  # interarrival rate
        self.mu = mu  # service rate
        self.k = k
    # Note lambd and mu are not mean value, they are rates i.e. (1/mean)

# Write more functions if required


# States and statistical counters
class States:
    def __init__(self):
        # States
        self.queue = []
        # Declare other states variables that might be needed
        # self.BUSY = 1
        # self.IDLE = 0
        self.Q_LIMIT = 1000
        self.total_delay = 0.0
        self.num_custs_delayed = 0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.time_last_event = 0.0
        # Statistics
        self.util = 0.0
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0
        self.server_status = 0

    def update(self, sim, event):
        time_since_last_event = sim.simclock - self.time_last_event
        self.time_last_event = sim.simclock
        self.area_num_in_q += len(sim.states.queue) * time_since_last_event
        # self.avgQlength = self.area_num_in_q/sim.simclock
        self.area_server_status += sim.states.server_status * time_since_last_event

    def finish(self, sim):
        self.avgQdelay = sim.states.total_delay/sim.states.num_custs_delayed
        self.avgQlength = sim.states.area_num_in_q/sim.simclock
        self.util = sim.states.area_server_status/sim.simclock

    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print('MMk Results: lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        print('MMk Total customer served: %d' % (self.served))
        print('MMk Average queue length: %lf' % (self.avgQlength))
        print('MMk Average customer delay in queue: %lf' % (self.avgQdelay))
        print('MMk Time-average server utility: %lf' % (self.util))
        
        print('\n\nAnalytical Results:')
        print('MMk Results: lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        print('MMk Average queue length: %lf' % ((sim.params.lambd**2)/(sim.params.mu*(sim.params.mu-sim.params.lambd))))
        print('MMk Average customer delay in queue: %lf' % (sim.params.lambd/(sim.params.mu*(sim.params.mu-sim.params.lambd))))
        print('MMk server utility factor: %lf' % (sim.params.lambd/sim.params.mu))

    def getResults(self, sim):
        # self.avgQlength = self.area_num_in_q/sim.simclock
        return (self.avgQlength, self.avgQdelay, self.util)

# Write more functions if required


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None
        # self.arrivalTime = None
        # self.departureTime = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType


class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim):
        print('start event ', self.eventTime)
        # arrivalEvent = ArrivalEvent(self.eventTime, sim)
        # sim.scheduleEvent(arrivalEvent)


class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        # Complete this function
        print('exit event ', self.eventTime)
        # DepartureEvent(self.eventTime, sim, sim.simclock)


class ArrivalEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim
        self.delay = 0.0
        self.arrivalTime = None
    def process(self, sim):
        if(sim.simclock>1000):
            print('here i exit event insertion', sim.simclock)
            sim.scheduleEvent(ExitEvent(sim.simclock, self))
        if(sim.states.server_status == 1):
            if(len(sim.states.queue) > sim.states.Q_LIMIT):
                print('overflow at array time limit ', sim.simclock)
                sim.scheduleEvent(ExitEvent(sim.simclock, sim))
            heapq.heappush(sim.states.queue, (sim.simclock, sim))
            print('server busy in arrival process', len(sim.states.queue))
        else:
            self.arrivalTime = self.eventTime
            print('server idle in arrival process', self.eventTime, self.arrivalTime)
            sim.states.total_delay += self.delay
            sim.states.server_status = 1 ## sim.states.BUSY
            sim.states.num_custs_delayed += 1
            sim.states.served += 1
            departureTime = sim.simclock + random.expovariate(sim.params.mu)
            departureEvent = DepartureEvent(departureTime, sim, self.eventTime)
            sim.scheduleEvent(departureEvent)
            print('departure time ', departureTime)
        self.arrivalTime = sim.simclock+random.expovariate(sim.params.lambd)
        arrivalEvent = ArrivalEvent(self.arrivalTime, self)
        sim.scheduleEvent(arrivalEvent)


class DepartureEvent(Event):
    def __init__(self, eventTime, sim, arrivalTime):
        self.eventTime = eventTime
        self.eventType = 'DEPART'
        self.sim = sim
        self.delay = 0.0
        self.arrivalTime = arrivalTime
    def process(self, sim):
        if(len(sim.states.queue) == 0):
            sim.states.server_status = 0 ## sim.states.IDLE
            print('departure event when queue is empty server status idle at', sim.simclock, self.arrivalTime)
        else:
            print('departure event when event in queue, queue length ', len(sim.states.queue), ' at ', sim.simclock,
                  ' arrival time ', self.arrivalTime)
            time, event = heapq.heappop(sim.states.queue)
            print('queue pop time ', time)
            sim.states.served += 1
            self.delay = sim.simclock - time ## self.arrivalTime
            sim.states.total_delay += self.delay
            sim.states.num_custs_delayed += 1
            departureTime = sim.simclock + random.expovariate(sim.params.mu)
            departureEvent = DepartureEvent(departureTime, sim, time) ## self.arrivalTime)
            sim.scheduleEvent(departureEvent)
            print('departure : total delay ', sim.states.total_delay, 'self delay ', self.delay, ' at ', sim.simclock, 
                ' with arrival time ',self.arrivalTime, ' & depart time ', departureTime, 
                ' & queue length ', len(sim.states.queue))


class Simulator:
    def __init__(self, seed):
        self.eventQ = []
        self.simclock = 0
        self.seed = seed
        self.params = None
        self.states = None
        self.arrivalTime = None
        self.departureTime = None
        # self.server_status = 0

    def initialize(self):
        self.simclock = 0
        self.scheduleEvent(StartEvent(0, self))

    def configure(self, params, states):
        self.params = params
        self.states = states

    def now(self):
        return self.simclock

    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))

    def run(self):
        random.seed(self.seed)
        self.initialize()

        while len(self.eventQ) > 0:
            time, event = heapq.heappop(self.eventQ)  ## arrivaltime, event

            if event.eventType == 'DEPART':
                print(event.eventTime, 'EVENT', event, event.arrivalTime)
            else:
                print(event.eventTime, 'Event', event)
            self.simclock = time

            if event.eventType == 'EXIT':
                break
            elif event.eventType == 'START':
                time_next_event = random.expovariate(self.params.lambd)
                arrivalEvent = ArrivalEvent(self.simclock+time_next_event, self)
                self.scheduleEvent(arrivalEvent)  ## new arrival event push
            else:
                event.process(self) ## arrival and depart
            
            if self.states != None:
                self.states.update(self, event)
                
        self.states.finish(self)

    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)


def experiment1():
    seed = 101
    sim = Simulator(seed)
    sim.configure(Params(5.0 / 60, 8.0 / 60, 1), States())
    sim.run()
    sim.printResults()


def experiment2():
    seed = 110
    mu = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for ro in ratios:
        sim = Simulator(seed)
        sim.configure(Params(mu * ro, mu, 1), States())
        sim.run()
        ## sim.printResults()

        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(ratios, avglength)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(ratios, avgdelay)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(ratios, util)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Util')

    plt.show()


def experiment3():
    # Similar to experiment2 but for different values of k; 1, 2, 3, 4
    # Generate the same plots
    # Fix lambd = (5.0/60), mu = (8.0/60) and change value of k
    seed = 110
    ratios = [k for k in range(1, 5)]

    avglength = []
    avgdelay = []
    util = []

    for ro in ratios:
        sim = Simulator(seed)
        sim.configure(Params(5.0/60, 8.0/60, ro), States())
        sim.run()
        sim.printResults()

        print('####################################################')

        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(ratios, avglength)
    plt.xlabel('Server k')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(ratios, avgdelay)
    plt.xlabel('Server k')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(ratios, util)
    plt.xlabel('Server k')
    plt.ylabel('Util')

    plt.show()


def main():
    # experiment1()
    # print('################################ EXPERIMENT 2####################################')
    experiment2()
    # experiment3()


if __name__ == "__main__":
    main()
