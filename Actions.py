""""
Implements data parsing functions!
    
Class-ified Jan 19th by Jeremy
Originally Written By Justin
    
"""
class ActionResponder(object):
    def __init__(self, socket):
        self.funcs = {'DISCARD':self._discard,'BET':self._bet,\
                      'RAISE':self._raise, 'CALL':self._call,\
                      'FOLD':self._fold,'CHECK':self._check}
        self.socket = socket
    def do(self, action, arg):
        self.funcs[action](arg)
    
    def _return_action(self, action):
        # Action should be a string, all caps, from legal actions)
        self.socket.send(action+"\n")
    
    # Use this after flop analysis function to discard a card
    def _discard(self, card):
        ## Card must be a string
        self._return_action('DISCARD:'+str(card))
    
    # Use this to fold
    def _fold(self, ignore):
        self._return_action('FOLD')
    
    # Use this to call
    def _call(self, ignore):
        self._return_action('CALL')
    
    # Use this to check
    def _check(self, ignore):
        self._return_action('CHECK')
    
    # Use this to bet/raise
    def _raise(self, amount):
        self._return_action('RAISE:'+str(amount))
    def _bet(self, amount):
        self._return_action('BET:'+str(amount))


class Parser(object):
    #Shitload of of fields!
    def __init__(self,fields):
        self.fields = fields
    def parse(self, data):  #main parser, processes DATA.
        word = data.split()
        if word[0] == "GETACTION":
            self.fields['action'] = "GETACTION"
            self.fields['potSize'] = int(word[1])
            self.fields['numBoardCards'] = int(word[2])
            tempBC=int(self.fields['numBoardCards'])
            self.fields['boardCards']=word[3:3+tempBC]
            
            self.fields['numLastActions']=word[3+tempBC]
            tempLast=int(self.fields['numLastActions'])
            self.fields['lastActions']=word[4+tempBC:4+tempBC+tempLast]
            
            self.fields['lastActionsSplit']=[action.split(':') for action in self.fields['lastActions']]
            
            for action in self.fields['lastActions']:
                self.fields['handHistory'].append(action)
            
            for action in self.fields['lastActionsSplit']:
                self.fields['handHistorySplit'].append(action)
            
            self.fields['numLegalActions']=word[4+tempBC+tempLast]
            tempLegal=int(self.fields['numLegalActions'])
            ugly_action_array = word[5+tempBC+tempLast:5+tempBC+tempLast+tempLegal]
            
            legals = {'BET':{'True':False},'CALL':False,'CHECK':False,'DISCARD':False,'FOLD':False,'RAISE':{'True':False}}
            for action in ugly_action_array:
                if 'BET' in action:
                    betSplit = action.split(':')
                    legals['BET'] = {'True':True,'MIN':betSplit[1],'MAX':betSplit[2]}
                if 'CALL' in action:
                    legals['CALL'] = True
                if 'CHECK' in action:
                    legals['CHECK'] = True
                if 'DISCARD' in action:
                    legals['DISCARD'] = True
                if 'FOLD' in action:
                    legals['FOLD'] = True
                if 'RAISE' in action:
                    raiseSplit = action.split(':')
                    legals['RAISE'] = {'True':True,'MIN':raiseSplit[1],'MAX':raiseSplit[2]}

            self.fields['legalActions'] = legals
        
        
            timeBank = word[-1]
        elif word[0] == "NEWHAND":
            self.fields['action'] = "NEWHAND"
            self.fields['handId'] = word[1]
            self.fields['button'] = word[2]
            self.fields['holeCard1'] = word[3]
            self.fields['holeCard2'] = word[4]
            self.fields['holeCard3'] = word[5]
            yourBank = word[6]
            oppBank = word[7]
            timeBank = word[8]
                
            self.fields['handHistory'] = []
            self.fields['handHistorySplit']=[]
        #preFlopHand(holeCard3,holeCard2,holeCard1)
        elif word[0] == "HANDOVER":
            self.fields['action'] = "HANDOVER"
            yourBank= word[1]
            oppBank = word[2]
            
            self.fields['numBoardCards'] = int(word[3])
            tempBC = int(self.fields['numBoardCards'])
            self.fields['boardCards'] = word[4:4+tempBC]
            
            self.fields['numLastActions'] = word[4+tempBC]
            tempLast = int(self.fields['numLastActions'])
            self.fields['lastActions'] = word[5+tempBC:5+tempBC+tempLast]
            
            self.fields['lastActionsSplit']=[action.split(':') for action in self.fields['lastActions']]
            
            for action in self.fields['lastActions']:
                self.fields['handHistory'].append(action)
            
            for action in self.fields['lastActionsSplit']:
                self.fields['handHistorySplit'].append(action)
            
            timeBank = word[-1]
        elif word[0] == "KEYVALUE":
            self.fields['action'] = word[0]
            key = word[1]
            value = word[2]
        elif word[0] == "NEWGAME":
            self.fields['action'] = word[0]
            self.fields['yourName'] = word[1]
            self.fields['oppName'] = word[2]
            self.fields['stackSize'] = int(word[3])
            self.fields['bb'] = int(word[4])
            numHands = word[5]
            timeBank = word[6]
        elif word[0] == "REQUESTKEYVALUES":
            self.fields['action'] = word[0]
            bytesLeft = word[1]
        return self.fields