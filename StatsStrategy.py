from datetime import datetime
import pbots_calc
import random


class Strategy(object):

    def __init__(self, responder, analyzer, fields, stats):
        self.responder = responder
        self.analyzer = analyzer
        self.data = fields
        self.stats = stats
        self.aggro = AggroModifiers(self.data)
        
    
    
    def set_data(self, data):
        self.data = data
    
    def get_data(self):
        return self.data
    
    
    ## Very basic card discarder - checks for best hand in pocket + flop
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
                self.data['burnedCard_is'] = self.data['holeCard1']
                self.data['selectedCard1'] = self.data['holeCard2']
                self.data['selectedCard2'] = self.data['holeCard3']
                self.responder.do('DISCARD', holeCard1)
            elif b[0] == lowcard:
                self.data['burnedCard_is'] = self.data['holeCard2']
                self.data['selectedCard1'] = self.data['holeCard1']
                self.data['selectedCard2'] = self.data['holeCard3']
                self.responder.do('DISCARD', holeCard2)
            elif c[0] == lowcard:
                self.data['burnedCard_is'] = self.data['holeCard3']
                self.data['selectedCard1'] = self.data['holeCard2']
                self.data['selectedCard2'] = self.data['holeCard1']
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
        elif 'BET' in self.data['legalActions']:
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
        
        # set for 10000 Monte Carlo iterations
        #d1 = datetime.now()
        oddslist = str(pbots_calc.calc(handlist,boardlist,discarded,10000))
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

    # Odds calculator, returns a boolean for keep_hand
    def keep_hand_check(self):
        
        boardlist = ''
        for card in self.data['boardCards']:
            boardlist += card
        
        if self.data['numBoardCards'] == 0:
            self.data['burnedCard_is'] = None
            keep_percent = self.aggro.LooseMod['keep_percent_preflop']
            handlist = self.data['holeCard1']+self.data['holeCard2']+self.data['holeCard3']
        
        elif self.data['numBoardCards'] == 3:
            self.data['burnedCard_is'] = None
            keep_percent = self.aggro.LooseMod['keep_percent_flop']
            handlist = self.data['holeCard1']+self.data['holeCard2']+self.data['holeCard3']
            
        elif self.data['numBoardCards'] == 4:
            keep_percent = self.aggro.LooseMod['keep_percent_turn']
            handlist = self.data['selectedCard1'] + self.data['selectedCard2']
        
        elif self.data['numBoardCards'] == 5:
            keep_percent = self.aggro.LooseMod['keep_percent_river']
            handlist = self.data['selectedCard1'] + self.data['selectedCard2']
        
        handlist = handlist.lower()
        boardlist = boardlist.lower()
        
        if self.data['burnedCard_is'] == None:
            oddslist = self.pbots_calc_clean(handlist+':xx',boardlist,'')
            
        else:
            oddslist = self.pbots_calc_clean(handlist+':xx',boardlist,self.data['burnedCard_is'])
    
        print 'Calculated EV: '+str(oddslist)
        print
        # generate the keep_hand boolean, determined by keep_percent
        if (float(oddslist[1])>= 1.0-keep_percent):
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
            keep_hand = self.keep_hand_check()
        
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


    # Will get the data relevant to the current state of the game
    def setBettingStateStats(self):
        
        if self.data['button'] == 'true':
            if self.data['numBoardCards'] == 0:
                return self.stats.button.preFlop.read()
            if self.data['numBoardCards'] == 3:
                return self.stats.button.postFlop.read()
            if self.data['numBoardCards'] == 4:
                return self.stats.button.turn.read()
            if self.data['numBoardCards'] == 5:
                return self.stats.button.river.read()

        elif self.data['button'] == 'false':
            if self.data['numBoardCards'] == 0:
                return self.stats.nobutton.preFlop.read()
            if self.data['numBoardCards'] == 3:
                return self.stats.nobutton.postFlop.read()
            if self.data['numBoardCards'] == 4:
                return self.stats.nobutton.turn.read()
            if self.data['numBoardCards'] == 5:
                return self.stats.nobutton.river.read()
                
                




                
                
                
    # Strategy centered around moving to the opposite spectrum of the opponent
    def counter_betting(self):
    
        
        lastActionsSplit = self.data['lastActionsSplit']
        currentStats = self.setBettingStateStats()
        
        
        unpredictableRoll = random.randint(1,101)/100.0 # not implemented yet
        raiseRoll = random.randint(1,101)/100.0
        checkRoll = random.randint(1,101)/100.0
        callRoll = random.randint(1,101)/100.0
        
        # Will ignore the data unless 20 hands have gotten to that stage
        if currentStats['hands'] < 20:
            self.aggro.AggroMod = self.aggro.aggro3
            self.aggro.LooseMod = self.aggro.loose3
            
        else:
            self.aggro.setStrategy(currentStats)

        # Check for EV against current keep_percent
        keep_hand = self.keep_hand_check()
        
        # Discard using the lowest EV
        if self.data['legalActions']['DISCARD']:
            
            self.discard_low()
    
    
        elif keep_hand:
            if raiseRoll <= self.aggro.AggroMod['raiseFreq']:
                self.aggroRaise() 
            else:
                if self.data['legalActions']['CALL']:
                    self.responder.do('CALL', None)
                else:
                    self.responder.do('CHECK', None)

        else:
            
            if self.data['legalActions']['FOLD']:
                self.responder.do('FOLD', None)
            else:
                self.responder.do('CHECK', None)




    # Tight aggressive strategy
    def TAG(self):
    
        self.aggro.AggroMod = self.aggro.aggro4
        self.aggro.LooseMod = self.aggro.loose2
        
        raiseRoll = random.randint(1,101)/100.0
        
        keep_hand = self.keep_hand_check()
        
        if self.data['legalActions']['DISCARD']:
            self.discard_low()
            
        elif keep_hand:
            if raiseRoll <= self.aggro.AggroMod['raiseFreq']:
                self.aggroRaise() 
            else:
                if self.data['legalActions']['CALL']:
                    self.responder.do('CALL', None)
                else:
                    self.responder.do('CHECK', None)

        else:
            print 'Fold because not keep_hand'
            if self.data['legalActions']['FOLD']:
                self.responder.do('FOLD', None)
            else:
                self.responder.do('CHECK', None)
        







    # Betting function centered on using our current Aggro state
    def aggroRaise(self):
    
        legalActions = self.data['legalActions']
        
        if self.data['legalActions']['RAISE']['True']:
            amount = self.aggro.AggroMod['raiseLevel'] * int(legalActions['RAISE']['MIN'])
            if amount > int(legalActions['RAISE']['MAX']):
                self.responder.do('RAISE',legalActions['RAISE']['MAX'])
            else:
                self.responder.do('RAISE',str(amount))
            
        elif self.data['legalActions']['BET']['True']:
            amount = self.aggro.AggroMod['raiseLevel'] * int(legalActions['BET']['MIN'])
            if amount > int(legalActions['BET']['MAX']):
                self.responder.do('BET',legalActions['BET']['MAX'])
            else:
                self.responder.do('BET',str(amount))
        else:
            self.responder.do('CALL',None)

            
            
                
            
        
        
        

        
            
    
    
    


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






# Class to hold the aggro&loose modifiers for ourself
class AggroModifiers(object):

        def __init__(self,fields):
            self.AggroMod = {
            'raiseFreq' : None,
            'raiseLevel': None,
            'callFreq' : None,
            'checkFreq' : None,
            'unpredictable' : None}
            
            self.LooseMod = {
            'keep_percent_preflop': None,
            'keep_percent_flop': None,
            'keep_percent_turn': None,
            'keep_percent_river': None}
    
            self.aggro1 = {
            'raiseFreq' : 0.50,
            'raiseLevel': 1,
            'callFreq' : 0.50,
            'checkFreq' : 0.50,
            'unpredictable' : 0.15}
    
            self.aggro2 = {
            'raiseFreq' : 0.60,
            'raiseLevel': 2,
            'callFreq' : 0.60,
            'checkFreq' : 0.40,
            'unpredictable' : 0.20}
    
            self.aggro3 = {
            'raiseFreq' : 0.70,
            'raiseLevel': 3,
            'callFreq' : 0.70,
            'checkFreq' : 0.30,
            'unpredictable' : 0.25}
    
            self.aggro4 = {
            'raiseFreq' : 0.80,
            'raiseLevel': 4,
            'callFreq' : 0.80,
            'checkFreq' : 0.20,
            'unpredictable' : 0.30}
    
            self.loose1 = {
            'keep_percent_preflop': 0.45,
            'keep_percent_flop': 0.40,
            'keep_percent_turn': 0.35,
            'keep_percent_river': 0.30}
            
            self.loose2 = {
            'keep_percent_preflop': 0.50,
            'keep_percent_flop': 0.45,
            'keep_percent_turn': 0.40,
            'keep_percent_river': 0.35}
            
            self.loose3 = {
            'keep_percent_preflop': 0.45,
            'keep_percent_flop': 0.40,
            'keep_percent_turn': 0.35,
            'keep_percent_river': 0.30}
    
            self.loose4 = {
            'keep_percent_preflop': 0.50,
            'keep_percent_flop': 0.45,
            'keep_percent_turn': 0.40,
            'keep_percent_river': 0.35}
            

        # Current sets our strategy to the opposite spectrum of opponent
        def setStrategy(self,currentStats):
        
            self.currentStats = currentStats
            
            if self.currentStats['aggroLevel'] == 4:
            
                self.AggroMod = self.aggro4

            if self.currentStats['aggroLevel'] == 3:
            
                self.AggroMod = self.aggro3
                
            if self.currentStats['aggroLevel'] == 2:
            
                self.AggroMod = self.aggro2

            if self.currentStats['aggroLevel'] == 1:
            
                self.AggroMod = self.aggro1


            if self.currentStats['looseLevel'] == 4:
            
                self.LooseMod = self.loose4

            if self.currentStats['looseLevel'] == 3:
            
                self.LooseMod = self.loose3
                
            if self.currentStats['looseLevel'] == 2:
            
                self.LooseMod = self.loose2

            if self.currentStats['looseLevel'] == 1:
            
                self.LooseMod = self.loose1

            



            



    












