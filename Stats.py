"""
Stats provides a Tracker class which is a way to track oponent actions (fold, all in, raise, call) at all states( pre/post flop, turn, river).
Make 2 instances, one for has button, one for does not have button.
--Written By Jeremy Rubin --
-- Jan 18th 2013 --
    
API:/Users/jeremyrubin/Desktop/MIT/Pokerbots/pythonbot 2/pokerbots2013/Player.py
    # wraps the states for button/nobutton
    # call like this
    # myStats = Stats()
    # data = myStats.nobutton.preFlop.read()
    # myStats.button.turn.update([['increment', True],['all_in', False],['fold', False],['check', False],['call', False],['three_bet', 0],['raise', 0],['cont_bet', 0]])
    
                           _____________
                           _     |     _                                       
                          / \   _|_   / \                                      
                         ( O )-/   \-( O )                                     
     |                    \_/ /\___/\ \_/                    |                 
     |_______________________( ( . ) )_______________________|             
                              \_____/                                    
    
    
                                         
    
"""
######################################
## THis is the tracker class        ##
## TODO: clean up shared fields to  ##
## Save memory                      ##
## add more fields?                 ##
######################################

class Tracker(object):
    def __init__(self):
        # Objects to hold shit! #
        self.hands = 0
        self.r = [0,0,0,0] # raise [raises, amount, raises%,amount_avg ]
        self.ai = [0,0] # all in  [all ins, percent]
        self.f = [0,0] # fold [ folds percent]
        self.c = [0,0] # call [calls, percent]
        self.ch = [0,0] # check [check, percent]
        self.tb = [0,0,0,0] # threebet [raises, amount, raises%,amount_avg ]
        self.cb = [0,0,0,0] # c-bet [raise, amount, raise%, amount_avg ]
        self.of = [0,0] # our fold [folds, percent]
        #TODO further than threebets?
        self.opts  = {'cont_bet':self._cont_bet, 'three_bet': self._three_bet, 'call': self._call, 'fold':self._fold,\
                            'our_fold':self._our_fold, 'all_in':self._all_in, 'raiser':self._raiser, 'check':self._check, 'increment':property(self._increment)}
                            # anything we can call

    

        # Set up aggro level tracking
        self.aggroStats = AggressionStats()
    
                #########################################
                #  CALCULATE     STATS(Priva            #
                #########################################
###### Number of hands that get to Stage
    @property
    def _increment(self):
        return self.hands
    @_increment.setter
    def _increment(self, action):
        if action:
            self.hands +=1

    
######  RAISE
    @property
    def _raiser(self):
        return self.r
    
    @_raiser.setter
    def _raiser(self, amount):
        amount = int(amount)
        if amount != 0:#if raised
            self.r[1] += amount # add in amount
            self.r[0] += 1 # increment raises number
        if self.r[0] != 0:
            self.r[2] = 1.0*self.r[0]/self.hands# update percent raises
            self.r[3] = self.r[1]/self.r[0]# update average amount
########  ALL IN 
    @property
    def _all_in(self):
        return self.ai
    
    @_all_in.setter
    def _all_in(self, all_in): # count all_ins
        if(all_in): # if op goes all in
            self.ai[0] += 1 # increment our number
        if self.ai[0] != 0:
            self.ai[1] = 1.0*self.ai[0]/self.hands # update percent

#######  FOLD
    @property
    def _fold(self):
        return self.f

    @_fold.setter
    def _fold(self, folded):
        if(folded):
            self.f[0] += 1
        if self.f[0] != 0:
            self.f[1] = 1.0*self.f[0]/self.hands
    
    
#######  OUR FOLD
    @property
    def _our_fold(self):
        return self.of

    @_our_fold.setter
    def _our_fold(self, folded):
        if(folded):
            self.of[0] += 1
        if self.of[0] != 0:
            self.of[1] = 1.0*self.of[0]/self.hands


##### CALL
    @property
    def _call(self):
        return self.c
    @_call.setter
    def _call(self, called):
        if(called):
            self.c[0] += 1
        if self.c[0] != 0:
            self.c[1] = 1.0*self.c[0]/self.hands
##### CHECK
    @property
    def _check(self):
        return self.ch
    @_check.setter
    def _check(self, checked):
        if(checked):
            self.ch[0] += 1
        if self.ch[0] != 0:
            self.ch[1] = 1.0*self.ch[0]/self.hands
########  3 Bet
    @property
    def _three_bet(self):
        return self.tb
    @_three_bet.setter
    def _three_bet(self, amount):
        amount = int(amount)
        if amount != 0:
            self.tb[1] += amount # add in amount
            self.tb[0] += 1 # increment three_bet number
        if self.tb[0] != 0:
            self.tb[2] = 1.0*self.tb[0]/self.hands# update percent three_bet
            self.tb[3] = 1.0*self.tb[1]/self.tb[0]# update average amount

######### c-Bet
    @property
    def _cont_bet(self):
        return self.cb
    @_cont_bet.setter
    def _cont_bet(self, amount):
        amount = int(amount)
        if amount != 0:
            self.cb[1] += amount # add in amount
            self.cb[0] += 1 # increment cont_bet number
        if self.cb[0] != 0:
            self.cb[2] = 1.0*self.cb[0]/self.hands# update percent cont_bet
            self.cb[3] = 1.0*self.cb[1]/self.cb[0]# update average amount
    



####### SCRAPER METHODS
    
    # self.button.preFlop.stageUpdate(preflop_actions,self.fields)
    # Will update opp. stats at the end of the hand
    def stageUpdate(self,actions,scraper):
    
        self.update([['increment', True]])
        self.raise_count = 0
    
        for action in actions:
            
            if action[-1] == scraper.fields['yourName']:
            
                if action[0] == 'FOLD':
                    self.update([['our_fold', True]])
            
            elif action[-1] == scraper.fields['oppName']:
                    
                if action[0] == 'CALL':
                    self.update([['call', True]])
                    scraper.put_in_pot += int(lastIteratedAction[1])
                
                elif action[0] == 'CHECK':
                    self.update([['check', True]])
                    
                elif action[0] == 'FOLD':
                    self.update([['fold', True]])
            
                elif action[0] == 'RAISE':
                    self.update([['raiser', action[1]]])
                    self.raise_count += 1
                    scraper.put_in_pot += int(action[1])
                    
                    if actions[0][0] != 'DEAL':
                        if self.raise_count >= 1:
                            self.update([['three_bet', action[1]]])
                    else:
                        if self.raise_count >= 2:
                            self.update([['three_bet', action[1]]])
                        
                elif action[0] == 'BET':
                    self.update([['raiser', action[1]]])
                    self.raise_count += 1
                    scraper.put_in_pot += int(action[1])
            
            lastIteratedAction = action
            
            if not scraper.all_in:
                if scraper.put_in_pot == scraper.fields['stackSize']:
                    self.update([['all_in', True]])
                    scraper.all_in = True
        
        if scraper.fields['button']:
            if scraper.previous_raise_count >= 1 and actions[1][0] == 'BET' and actions[1][2] == scraper.fields['oppName']:
                self.update([['cont_bet', actions[1][1]]])
                
        elif not scraper.fields['button']:
            if scraper.previous_raise_count >= 1 and actions[2][0] == 'BET' and actions[2][2] == scraper.fields['oppName']:
                self.update([['cont_bet', actions[2][1]]])

        scraper.previous_raise_count = self.raise_count

        # Sets our aggro stats for this stage
        self.aggroStats.setLevels(self.read(),scraper,actions)
        


    
###### PUBLIC METHODS
    def update(self, updates): # send me queries in the form of [ [action, [data]], [action, [data]], [action, [data]] ]
        # be sure to include increment with no [data]
        # send in a blank request to update percents like update(None)
        if updates == None:
            updates = [['cont_bet', '0'],['all_in', False],['our_fold',False],['fold', False],['call', False],['three_bet', '0'],['raiser', '0'],['check', False]]
        for update in updates:
            ####self.opts[update[0]](update[1])
            if update[0] == 'cont_bet':
                self._cont_bet = update[1]
            elif update[0] == 'three_bet':
                self._three_bet = update[1]
            elif update[0] == 'call':
                self._call = update[1]
            elif update[0] == 'fold':
                self._fold = update[1]
            elif update[0] == 'our_fold':
                self._our_fold = update[1]
            elif update[0] == 'all_in':
                self._all_in = update[1]
            elif update[0] == 'raiser':
                self._raiser = update[1]
            elif update[0] == 'check':
                self._check = update[1]
            elif update[0] =='increment':
                self._increment = update[1]


    def read(self): # reads all and returns a dictionary
        self.update(None) # ensures percents updated
        a = self._cont_bet
        b = self._three_bet
        c = self._call
        d = self._fold
        e = self._all_in
        f = self._raiser
        g = self._check
        h = self._increment
        i = self.aggroStats.aggroLevel
        j = self.aggroStats.looseLevel
        k = self._our_fold
        return {'cont_bet': a, 'three_bet': b, 'call': c, 'fold':d, 'all_in': e, 'raiser':f, 'check':g, 'hands':h, 'aggroLevel':i, 'looseLevel':j, 'our_fold':k}

"""

                           _____________
                           _     |     _                                       
                          / \   _|_   / \                                      
                         ( O )-/   \-( O )                                     
     |                    \_/ /\___/\ \_/                    |                 
     |_______________________( ( . ) )_______________________|             
                              \_____/                                    
    
    
This class Handles the Tracker Class
"""


# wraps the various states
class Trackers(object):
    def __init__(self):
        self.preFlop = Tracker()
        self.postFlop = Tracker()
        self.turn = Tracker()
        self.river = Tracker()


# Variables to pass through while scraping
class Scrapers():
    def __init__(self):
        self.put_in_pot = 0
        self.all_in = False
        self.previous_raise_count = 0
        self.fields = []


# wraps the states for button/nobutton
# call like this
# myStats = Stats()
# data = myStats.nobutton.preFlop.read()
# myStats.button.turn.update([['increment', True],['all_in', False],['fold', False],['check', False],['call', False],['three_bet', 0],['raise', 0],['cont_bet', 0]])

class Stats(object):
    def __init__(self):
        self.button = Trackers()
        self.nobutton = Trackers()
    
    
    
    # run at the end of hand to update all stats for that hand
    def endOfHandUpdate(self,fields):
    
        scraper = Scrapers()
        scraper.fields = fields
        handHistorySplit = scraper.fields['handHistorySplit']
        button = scraper.fields['button']
        preflop_actions=[]
        flop_actions=[]
        turn_actions=[]
        river_actions=[]
        
        
        
        # further divide the hand history by deals
        if ['DEAL','FLOP'] in handHistorySplit:
            preflop_actions = handHistorySplit[:handHistorySplit.index(['DEAL','FLOP'])]
            
            if ['DEAL','TURN'] in handHistorySplit:
                flop_actions = handHistorySplit[handHistorySplit.index(['DEAL','FLOP']):handHistorySplit.index(['DEAL','TURN'])]
                    
                if ['DEAL','RIVER'] in handHistorySplit:
                    turn_actions = handHistorySplit[handHistorySplit.index(['DEAL','TURN']):handHistorySplit.index(['DEAL','RIVER'])]
                    river_actions = handHistorySplit[handHistorySplit.index(['DEAL','RIVER']):]
                    
                else:
                    turn_actions = handHistorySplit[handHistorySplit.index(['DEAL','TURN']):]
                        
            else:
                flop_actions = handHistorySplit[handHistorySplit.index(['DEAL','FLOP']):]
                                                                       
        else:
            preflop_actions = handHistorySplit[:]
    
    
    
    
        # Button
        if button == 'true':
        
            ### Preflop
            self.button.preFlop.stageUpdate(preflop_actions,scraper)
            
            ### Flop
            if flop_actions != [] and flop_actions != [['DEAL','FLOP']]:
            
                self.button.postFlop.stageUpdate(flop_actions,scraper)

            ### Turn
            if turn_actions != [] and turn_actions != [['DEAL','TURN']]:
                
                self.button.turn.stageUpdate(turn_actions,scraper)

            ### River
            if river_actions != [] and river_actions != [['DEAL','RIVER']]:
                
                self.button.river.stageUpdate(river_actions,scraper)

            
        # Not Button
        if button == 'false':
        
            ### Preflop
            self.nobutton.preFlop.stageUpdate(preflop_actions,scraper)
           
            ### Flop
            if flop_actions != [] and flop_actions != [['DEAL','FLOP']]:

                self.nobutton.postFlop.stageUpdate(flop_actions,scraper)

            ### Turn
            if turn_actions != [] and turn_actions != [['DEAL','TURN']]:

                self.nobutton.turn.stageUpdate(turn_actions,scraper)

            ### River
            if river_actions != [] and river_actions != [['DEAL','RIVER']]:
 
                self.nobutton.river.stageUpdate(river_actions,scraper)

# Class for converting stats into aggression & loose factors
class AggressionStats(object):
    
    
    def __init__(self):
        self.aggroLevel = None
        self.looseLevel = None
    
        # Modifiers to be used in aggro/loose calcs
        self.raiserModifier = 1.2
        self.threeBetModifier = 1.5
        self.allInModifier = 2.0
        self.checkModifier = 1.5
        self.cBetModifier = 1.2
        self.foldModifier = 1.7
        self.callModifier = 1.2
    
    
    # The actual algorithm for converting the stats to aggro/loose
    def setLevels(self,stats,scraper,actions):
    
        aggrocalc = 1.0*((stats['raiser'][0] * self.raiserModifier * stats['raiser'][3]/scraper.fields['bb'])+(stats['three_bet'][0] * self.threeBetModifier * stats['three_bet'][3]/scraper.fields['bb'])+(stats['all_in'][0] * self.allInModifier)+(stats['cont_bet'][0] * self.cBetModifier * stats['cont_bet'][3] / scraper.fields['bb'])-(stats['call'][0] * self.callModifier))/stats['hands']
            
            
        loosecalc = 1.0*(stats['hands'] - stats['fold'][0] - stats['our_fold'][0])/(1+stats['hands'] - (stats['our_fold'][0]))

        print
        print 'Aggro Calculation: '+str(aggrocalc)
        print
        print 'Loose Calcuation: '+str(loosecalc)
        print
        # Ranges to classify opponents aggro and loose levels
        # Separated by preflop and everything after the flop
        if actions[0][0] != 'DEAL':
            if aggrocalc > 40:
                self.aggroLevel = 4
            elif aggrocalc > 35:
                self.aggroLevel = 3
            elif aggrocalc > 30:
                self.aggroLevel = 2
            else:
                self.aggroLevel = 1


            if loosecalc > 0.90:
                self.looseLevel = 4
            elif loosecalc > 0.80:
                self.looseLevel = 3
            elif loosecalc > 0.70:
                self.looseLevel = 2
            else:
                self.looseLevel = 1


        else:
            if aggrocalc > 35:
                self.aggroLevel = 4
            elif aggrocalc > 30:
                self.aggroLevel = 3
            elif aggrocalc > 25:
                self.aggroLevel = 2
            else:
                self.aggroLevel = 1


            if loosecalc > 0.80:
                self.looseLevel = 4
            elif loosecalc > 0.70:
                self.looseLevel = 3
            elif loosecalc > 0.60:
                self.looseLevel = 2
            else:
                self.looseLevel = 1

            


















