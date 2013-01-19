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
    # myStats.button.turn.update([['increment', [1]],['all_in', False],['fold', False],['call', False],['three_bet', False],['raise', True],])
    
                           ___________
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
        self.tb = [0,0,0,0] # threebet [raises, amount, raises%,amount_avg ]
        #TODO further than threebets?
        self.opts  = {'three_bet': self._three_bet, 'call': self._call, 'fold':self._fold,\
                            'all_in':self._all_in, 'raiser':self._raiser, 'hands':self._increment}
                            # anything we can call
    
                #########################################
                #  CALCULATE     STATS(Priva            #
                #########################################
###### Number of hands that get to Stage
    @property
    def _increment(self):
        return self.hands
    @_increment.setter
    def _increment(self, uselessArg):
        self.hands +=1
    
    
######  RAISE
    @property
    def _raiser(self):
        return self.r
    
    @_raiser.setter
    def _raiser(self, amount, action):
        if(action):#if raised
            self.r[1] += amount # add in amount
            self.r[0] += 1 # increment raises number
        self.r[3] = self.r[0]/self.hands# update percent raises
        self.r[3] = self.r[1]/self.r[0]# update average amount
########  ALL IN 
    @property
    def _all_in(self):
        return self.ai
    
    @_all_in.setter
    def _all_in_preflop(self, all_in): # count all_ins
        if(all_in): # if op goes all in
            self.ai[0] += 1 # increment our number
        self.ai[1] = self.ai[0]/self.hands # update percent

#######  FOLD
    @property
    def _fold(self):
        return self.f

    @_fold.setter
    def _fold(self, folded):
        if(folded):
            self.f[0] += 1
        self.f[1] = self.f[0]/self.hands
##### CALL
    @property
    def _call(self):
        return self.c
    @_call.setter
    def _call(self, called):
        if(called):
            self.c[0] += 1
        self.c[1] = self.c[0]/self.hands
########  3 Bet
    @property
    def _three_bet(self):
        return self.tb
    @_three_bet.setter
    def _three_bet(self, amount, three_bet):
        if(three_bet):
            self.tb[1] += amount # add in amount
            self.tb[0] += 1 # increment three_bet number
        self.r[3] = self.tb[0]/self.hands# update percent three_bet
        self.r[3] = self.tb[1]/self.r[0]# update average amount
    
###### PUBLIC METHODS
    def update(self, updates): # send me queries in the form of [ [action, [data]], [action, [data]], [action, [data]] ]
        # be sure to include increment with no [data]
        # send in a blank request to update percents like update(None)
        if not updates:
            updates = [['all_in', None],['fold', None],['call', None],['three_bet', None],['raise', None]]
        for update in updates:
            self.opts[update[0]](update[1])

    def read(self): # reads all and returns a dictionary
        self.update(None) # ensures percents updated
        a = self._three_bet
        b = self._call
        c = self._fold
        d = self._all_in
        e = self._raiser
        f = self._increment
        return {'three_bet': a, 'call': b, 'fold':c,'all_in': d, 'raiser':e, 'hands':f}

"""

                           ___________
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


# wraps the states for button/nobutton
# call like this
# myStats = Stats()
# data = myStats.nobutton.preFlop.read()
# myStats.button.turn.update([['increment', [1]],['all_in', False],['fold', False],['call', False],['three_bet', False],['raise', True],])
class Stats(object):
    def __init__(self):
        self.button = Trackers()
        self.nobutton = Trackers()
    










