#standard class definition for general state machine
class SM:
    #particular machines are initialized with a startState, which this method
    #sets the machine's state to
    def start(self):
        self.state = self.startState
        
    #uses machine's getNextValues method to update the state on input inp and 
    #return output
    def step(self, inp):
        (s, o) = self.getNextValues(self.state, inp)
        self.state = s
        return o
    
    #some machines include a done method, which returns True when the machine 
    #is finished; here the default method always returns False
    def done(self, state):
        return False
    
    #this method runs the machine (from its start state) on a list of inputs, 
    #until the machine reaches its done state (if ever), returning the list of
    #outputs
    def transduce(self, inputs):
        self.start()
        return [self.step(inp) for inp in inputs if not self.done(self.state)]
    
    #this method runs the machine on n inputs of None, returning the list of 
    #outputs
    def run(self, n = 10):
        return self.transduce([None] * n)
    
    #the default startState is None
    startState = None
    
    #the default getNextValues method uses the machine's getNextState method, 
    #which is useful for defining machines whose next state and output are 
    #identical
    def getNextValues(self, state, inp):
        nextState = self.getNextState(state, inp)
        return (nextState, nextState)



#the Delay state machine always outputs its state, which is its previous input
class Delay(SM):
    def __init__(self, v0):
        self.startState = v0
    def getNextValues(self, state, inp):
        return (inp, state)

#the Cascade state machine takes the output of one machine and feeds it into a
#second machine as input, followed by outputting the output of the second
#machine
class Cascade(SM):
    def __init__(self, m1, m2):
        self.startState = (m1.startState, m2.startState)
        self.m1 = m1
        self.m2 = m2
    def getNextValues(self, state, inp):
        m1NextState = self.m1.getNextValues(state[0], inp)[0]
        m1Output = self.m1.getNextValues(state[0], inp)[1]
        m2NextState = self.m2.getNextValues(state[1], m1Output)[0]
        m2Output = self.m2.getNextValues(state[1], m1Output)[1]
        return ((m1NextState, m2NextState), m2Output)

#the safeAdd function is used later to prevent errors if input is undefined
def safeAdd(v1, v2):
    if v1 == 'undefined' or v2 == 'undefined':
        return 'undefined'
    else:
        return v1 + v2

#the Parallel state machine runs two machines in parallel, giving the same
#input to both machines and outputting a tuple of their respective outputs
class Parallel(SM):
    def __init__(self, sm1, sm2):
        self.m1 = sm1
        self.m2 = sm2
        self.startState = (sm1.startState, sm2.startState)
    def getNextValues(self, state, inp):
        (s1, s2) = state
        (newS1, o1) = self.m1.getNextValues(s1, inp)
        (newS2, o2) = self.m2.getNextValues(s2, inp)
        return ((newS1, newS2), (o1, o2))

#the Feedback state machine feeds the output of a machine into it as its input
class Feedback(SM):
    def __init__(self, sm):
        self.m = sm
        self.startState = self.m.startState
    def getNextValues(self, state, inp):
        (ignore, o) = self.m.getNextValues(state, 'undefined')
        (newS, ignore) = self.m.getNextValues(state, o)
        return (newS, o)

#the splitValue function handles 'undefined' input for the Adder state machine
#(defined below)
def splitValue(v):
    if v == 'undefined':
        return ('undefined', 'undefined')
    else:
        return v

#the Adder state machine takes an ordered pair of numbers as input and outputs
#their sum (or 'undefined')
class Adder(SM):
    def getNextState(self, state, inp):
        (i1, i2) = splitValue(inp)
        return safeAdd(i1, i2)

#here we use the previously defined state machines to define a state machine
#that computes the Fibonacci sequence (use the run(n) method to output the first
#n Fibonacci numbers)
fib = Cascade(Feedback(Cascade(Parallel(Delay(1), Cascade(Delay(1), \
    Delay(0))), Adder())), Delay(1))

