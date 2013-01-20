from datetime import datetime
import pbots_calc
class Strategy(object):
    def __init__(self, responder, analyzer, fields):
        self.responder = responder
        self.analyzer = analyzer
        self.data = fields
    ## Very basic card discarder - checks for best hand in pocket + flop
    def set_data(self, data):
        self.data = data
    def get_data(self):
        return self.data
    def discard_low(self):
        holeCard1 = self.data['holeCard1']
        holeCard2 = self.data['holeCard2']
        holeCard3 = self.data['holeCard3']
        boardCards = self.data['boardCards']
        a = list(holeCard1)
        b = list(holeCard2)
        c = list(holeCard3)
        
        value_dict = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
        inverted_value_dict = dict([[v,k] for k,v in value_dict.items()])
        value_array = [value_dict[a[0]] ,value_dict[b[0]],value_dict[c[0]]]
        value_array.sort()
        lowcard = inverted_value_dict[value_array[0]]
        analysis = self.analyzer.burn_which_card_simple(boardCards, holeCard1, holeCard2, holeCard3)
        if analysis == 'lowcard':
            #print a[0], b[0], c[0]
            if a[0] == lowcard:
               self.responder.do('DISCARD', holeCard1)
            elif b[0] == lowcard:
                self.responder.do('DISCARD', holeCard2)
            elif c[0] == lowcard:
                self.responder.do('DISCARD', holeCard3)
        else:
            choices = { 1: holeCard1, 2: holeCard2, 3:holeCard3}
            ar = [holeCard1,holeCard2, holeCard3]
            self.data['burnedCard_is'] = ar.pop(analysis-1)
            self.data['selectedCard1'] = ar.pop()
            self.data['selectedCard2'] = ar.pop()
            self.responder.do('DISCARD',choices[analysis])



    ########## Basic Betting Responses ############

    # Will bet 'percent' of big blind (must have BET in legal actions)
    def bet_percent(self):
        
        ##### percent is currently set to 300 #####
        percent = 300
        betPercent = str(percent*int(self.data['bb'])/100)
        
        if 'RAISE' in self.data['legalActions']:
            self.responder.do('RAISE', betPercent)
        elif 'BET' in self.data[legalActions]:
            self.responder.do('BET', betPercent)

    # Will raise minimum amount, or will go/call all in
    def raise_min(self):
        if 'RAISE' in self.data['legalActions']:
            self.responder.do('RAISE', self.data['legalActions']['RAISE']['MIN'])
        elif 'CALL' in self.data['legalActions']:
            self.responder.do('CALL', None)
    ###############################################

    ########### Raise Counter Functions ###########

    # Resets raise counter
    def reset_raises(self):
        self.data['raise_counter'] = 0

    # Increments raise counter
    def increment_raises(self):
        self.data['raise_counter'] += 1

    ###############################################

    ########### Pbots_calc Functions ##############

    # Turns output of pbots_calc into a useable list
    def pbots_calc_clean(self,handlist,boardlist,discarded):
        
        # set for 100 Monte Carlo iterations
        #d1 = datetime.now()
        oddslist = str(pbots_calc.calc(handlist,boardlist,discarded,100))
        #d2 = datetime.now()
        #print d2-d1
        oddslist = list(oddslist)
        for char in oddslist:
            if char in ["[","]","(",")",","," "]:
                oddslist.remove(char)
        for char in oddslist:
            if char in ["[","]","(",")",","," "]:
                oddslist.remove(char)
        for char in oddslist:
            if char in ["[","]","(",")",","," "]:
                oddslist.remove(char)
        oddslist=''.join(oddslist)
        oddslist = oddslist.split("'")
        oddslist.remove('')
        return oddslist

    # Preflop odds calculator, returns a boolean for keep_hand
    def preflop_keep(self):
        handlist = self.data['holeCard1']+self.data['holeCard2']+self.data['holeCard3']
        handlist = handlist.lower()
        oddslist = self.pbots_calc_clean(handlist+':xx','','')
        # generate the keep_hand boolean, determined by class variable keep_percent
        if (float(oddslist[1])>= 1.0-self.data['keep_percent']):
            return True
        else:
            return False

    ###############################################

    ############ Betting Strategies ###############

    # Basic pre-flop 3-betting based on button
    def preflop_3bet(self):
        lastActionsSplit = self.data['lastActionsSplit']
        button = self.data['button']
        raise_counter = self.data['raise_counter']
        ###### keep_hand is a boolean determining whether we bet or not, determined by analyzing stats ######
        if raise_counter == 0:
            keep_hand = self.preflop_keep()
        
        ###### ev_call is a boolean that compares chance to win hand against pot odds
        # if ev_call:
        
        # raise a certain percent to start off betting
        if lastActionsSplit[-1][0] == 'POST' and keep_hand:
            #print 'Making the initial bet now'
            self.increment_raises()
            self.bet_percent()
        
        # make the 3-bet if we have button and only raised once, else call
        elif (lastActionsSplit[-1][0] == 'RAISE' and button == 'true') and keep_hand:
            if raise_counter == 1:
                #print 'Making the 3 bet now:'
                self.raise_min()
            else:
                #print 'Calling because not making the 3 bet:'
                self.responder.do('CALL', None)
        
        # prevent the 3-bet in we don't have button
        elif (lastActionsSplit[-1][0] == 'RAISE' and button != 'true') and keep_hand:
            #print 'Dont have the button, so are calling'
            #self.responder.do('CALL', None)
            self.raise_min()
        
        # fold if we choose to not keep hand
        elif not keep_hand:
            self.responder.do('FOLD', None)
        
        # else check
        else:
            #print 'Checking because we dont have the button and saw no raise'
            self.responder.do('CHECK', None)


    ## Test function for simple betting procedures
    def simple_betting(self):
        # get the last actions made
        lastActions = self.data['lastActions']
        
        # if pre-flop, set raise counter to 0, run pre-flop betting strategy
        if int(self.data['numBoardCards']) == 0:
            self.reset_raises()
            #print 'Going to preflop_3bet now'
            self.preflop_3bet()
        
        
        ####### if not preflop, all-in strategy (want to change)
        else:
            #print 'Going to all-in now:'
            self.auto_all_in()


    ## Test function: always calling, discarding lowest card
    def auto_call(self):
        
        # make possible responses for this move
        legalActions = self.data['legalActions']
        
        # get the last action made
        lastActions = self.data['lastActions']
        
        if 'BET' in legalActions:
            self.responder.do('CALL', None)
        elif 'DISCARD' in legalActions:
            self.discard_low()
        else:
            self.responder.do('CHECK', None)

    ## Test function: always going all in, discarding lowest card
    def auto_all_in(self):
        legalActions = self.data['legalActions']
        # make possible responses for this move
                
        if 'BET' in legalActions:
            self.responder.do('BET',legalActions['BET']['MAX'])
        elif 'RAISE' in legalActions:
            self.responder.do('RAISE',legalActions['RAISE']['MAX'])
        elif 'DISCARD' in legalActions:
            self.discard_low()
        else:
            self.responder.do('CHECK', None)
