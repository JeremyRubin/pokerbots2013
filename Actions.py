class Actions():
    
    def __init__(self):
        self.canBet = [False, 'BET', 0, 0]
        self.canCall = [False, 'CALL']
        self.canCheck = [False, 'CHECK']
        self.canDiscard = [False, 'DISCARD']
        self.canFold = [False, 'FOLD']
        self.canRaise = [False, 'RAISE', 0, 0]
        self.hand_history_actions = []
        self.recent_actions = []
        self.potSize='0'

    def setLegalActions(self,legalActions):
        for action in legalActions:
            if 'BET' in action:
                self.canBet[0] = True
                betSplit = action.split(':')
                self.canBet[2] = betSplit[1]
                self.canBet[3] = betSplit[2]
            if 'CALL' in action:
                self.canCall[0] = True
            if 'CHECK' in action:
                self.canCheck[0] = True
            if 'DISCARD' in action:
                self.canDiscard[0] = True
            if 'FOLD' in action:
                self.canFold[0] = True
            if 'RAISE' in action:
                self.canRaise[0] = True
                raiseSplit = action.split(':')
                self.canRaise[2] = raiseSplit[1]
                self.canRaise[3] = raiseSplit[2]

    def getLegalActions(self):
        return [self.canBet, self.canCall, self.canCheck, self.canDiscard, self.canFold, self.canRaise]

    def setLastActions(self,lastActions):
        self.recent_actions = [action.split(':') for action in lastActions]
        for action in self.recent_actions:
            self.hand_history_actions.append(action)

    def getRecentActions(self):
        return self.recent_actions

    def getHandHistory(self):
        return self.hand_history_actions

    def setPotSize(self,potSize):
        self.potSize = potSize

    def getPotSize(self):
        return self.potSize
