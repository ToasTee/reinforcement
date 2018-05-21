# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for i in range(self.iterations):
            tempV = util.Counter()
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    tempV[state] = 0
                else:
                    actions = self.mdp.getPossibleActions(state)
                    maxV = -99999
                    for action in actions:
                        total = 0
                        for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
                            total += prob * (self.mdp.getReward(state, action, nextState) + (self.discount * self.values[nextState]))
                        maxV = max(total, maxV)
                        tempV[state] = maxV
            self.values = tempV



    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        # Q(s,a) = Sum_s'( T(s,a,s') + [R(s,a,s') + yV*(s')])
        q = 0
        #transitions = self.mdp.getTransitionStatesAndProbs(state, action)
        for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            q += prob * (self.mdp.getReward(state, action, nextState) + self.discount * self.values[nextState])
        return q

        util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        # V*(s) = max_a Q(s,a)
        if self.mdp.isTerminal(state):
            return None
        value = -99999999
        policy = None
        for action in self.mdp.getPossibleActions(state):
            #if self.computeQValueFromValues(state, action) >= value:
            tempV = self.computeQValueFromValues(state, action)
            if tempV >= value:
                value = tempV
                policy = action
        return policy

        util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()
        statelen = len(states)
        for i in range(self.iterations):
            state = states[i % statelen]

            if not self.mdp.isTerminal(state):
                self.values[state] = self.computeQValueFromValues(state, self.computeActionFromValues(state))


class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        predecessors = {}
        states = self.mdp.getStates()
        for state in states:
            actions = self.mdp.getPossibleActions(state)
            if not self.mdp.isTerminal(state):
                for action in actions:
                    for nextState, prob in self.mdp.getTransitionStatesAndProbs(state,action):
                        if prob > 0.0:
                            if not self.mdp.isTerminal(nextState):
                                predecessors[nextState] = set()
                                predecessors[nextState].add(state)

        queue = util.PriorityQueue()
        for state in states:
            actions = self.mdp.getPossibleActions(state)
            if not self.mdp.isTerminal(state):
                maxQV = max([self.getQValue(state,action) for action in actions])
                diff = abs(self.values[state] - maxQV)
                queue.push(state, -diff)


        for i in range(self.iterations):
            if queue.isEmpty():
                return

            state = queue.pop()
            self.values[state] = max([self.getQValue(state, action) for action in actions])

            for pred in list(predecessors[state]):
                actions = self.mdp.getPossibleActions(pred)
                q = max([self.getQValue(state,action) for action in actions])
                d = abs(self.values[pred] - q)

                if d > self.theta:
                    queue.update(pred, -d)