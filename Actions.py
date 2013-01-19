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

    ######### Simple Response Functions ########

    # Sends action to engine
    def return_action(action):
        # Action should be a string, all caps, from legal actions)
        s.send(action+"\n")

    # Use this after flop analysis function to discard a card
    def discard(card):
        print card
        ## Card must be a string
        return_action('DISCARD:'+card)

    # Use this to fold
    def fold():
        return_action('FOLD')

    # Use this to call
    def call():
        return_action('CALL')

    # Use this to check
    def check():
        return_action('CHECK')

    # Use this to bet/raise
    def bet_raise(amount):
        if Player.possible_responses[0][0]:
            return_action('BET:'+str(amount))
        elif Player.possible_responses[5][0]:
            return_action('RAISE:'+str(amount))

    ## Very basic card discarder; always dumps the lowest card
    def discard_low():
        a = list(Player.holeCard1)
        b = list(Player.holeCard2)
        c = list(Player.holeCard3)
        
        value_dict = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
        inverted_value_dict = dict([[v,k] for k,v in value_dict.items()])
        value_array = [value_dict[a[0]] ,value_dict[b[0]],value_dict[c[0]]]
        value_array.sort()
        lowcard = inverted_value_dict[value_array[0]]
        

        analysis = analysis_engine.burn_which_card_simple(Player.boardCards, Player.holeCard1,Player.holeCard2,Player.holeCard3)

        if analysis == 'lowcard':
            print a[0], b[0], c[0]
            if a[0] == lowcard:
                discard(Player.holeCard1)
            elif b[0] == lowcard:
                discard(Player.holeCard2)
            elif c[0] == lowcard:
                discard(Player.holeCard3)
        else:
            choices = { 1: Player.holeCard1, 2:Player.holeCard2, 3:Player.holeCard3}
            ar = [Player.holeCard1,Player.holeCard2,Player.holeCard3]
            Player.burnedCard_is = ar.pop(analysis-1)
            Player.selectedCard1 = ar.pop()
            Player.selectedCard2 = ar.pop()
            discard(choices[analysis])


