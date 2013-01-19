import argparse
import socket
import sys
import random
import pprint
from datetime import datetime
import pbots_calc

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""



def preFlopHand(card1,card2,card3):
    a = list(card1)
    b = list(card2)
    c = list(card3)
    value_dict = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
    inverted_value_dict = dict([[v,k] for k,v in value_dict.items()])
    if(a[1] == b[1] or a[1] == c[1] or b[1] == c[1]):
        if(a[1] == b[1] and a[1] == c[1]):
            suit_match_level = 3
        else:
            suit_match_level = 2
    else:
        suit_match_level = 1

    value_array = [value_dict[a[0]] ,value_dict[b[0]],value_dict[c[0]] ]
    value_array.sort()
    spread = [value_array[2] - value_array[0], value_array[2] - value_array[1]]
    three_of_a_kind, pairs = False, False

    if(spread[0] != 0 and spread[1] != 0):
        pairs = False
        three_of_a_kind = False
    elif(spread[0] != 0 or spread[1] != 0): #can't standalone, should have a xor
        pairs = True
    else:
        three_of_a_kind = True
    print 'pairs', pairs, 'three_of_a_kind', three_of_a_kind, 'suits', suit_match_level
def Flop(card1, card2, card3, flop1, flop2, flop3):
    a = list(card1)
    b = list(card2)
    c = list(card3)
    d = list(flop1)
    e = list(flop2)
    f = list(flop3)
    
    
    value_dict = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
    inverted_value_dict = dict([[v,k] for k,v in value_dict.items()])
 
#########################
###################### =Jeremy
class Analyzer():
################ This sector contains 5 card analysis. Only optimizations needed
    def flush_hand_plus_river(self, hand): # computes if a given set of 5 contains a flush
        # takes input in [[A,h],[K,d]....] format
        suits = []
        for card in hand:
            suits.append(card[1]) # collect all suits
        if(suits.count(suits[0]) == 5): # if the count of the first el is 5, its a flush
            return True
        else:
            return False

    def same_value_based_hand_plus_river(self, hand): # computes if a given set of 5 contains any kind of pairs
        # in [[A,h],[K,d]....] format
        values = []
        for card in hand:
            values.append(card[0]) # collect all values
        sum = 0
        for card in values:
            sum += values.count(card) # sum is unique to type of pair based hand (17, 13, 11, 9, 7 , 5)
        return sum

    def straight_hand_plus_river(self, hand, value_dict): # computes if a given set of 5 contains any kind of straight
        # takes a hand in [[A,h],[K,d]....] format, value dict in 2:2, ... A:14 format
        values = []
        vcheck =[]
        for card in hand:
            values.append(value_dict[card[0]])# assemble the values of the straight
        values.sort() # arrange in increasing order
        for x in range(0, 5): #go over hand indices
            vcheck.append(values[x] - x)# values[x] - x: consider [2,3,4,5,6] => [2,2,2,2,2]
        if( (vcheck.count(vcheck[0]) == 5) or ( (vcheck.count(vcheck[0]) == 4) and (vcheck.count(10) == 1) ) ):# count the same gaps, and count Ace as 1 too
           return True
        else:
           return False
           
    def what_is_hand_plus_river(self, hand): # compile the straight, flush, and pairing functions
            # takes hand of 5 in an array like ['Ah','Tc'....]
        value_dict = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14} # value_dict for straights
        which_pairing =  {7: 'one pair', 9 : 'two pair',
        13 : 'full house',11:'three of a kind',
        17:'four of a kind',5:False} # paring dictionary for sum values TODO: move these for better speed
        cardHand = []
        highCard = [['2','s']]# lowest possible card, meant to be ignored/swapped
        for card in hand:
            cardSplit = list(card) #split card into a char array
            cardHand.append(cardSplit) # assemble a hand array like [[card1], [card2]...]
            if value_dict[cardSplit[0]] >= value_dict[highCard[-1][0]]: # if high card found, replace
                highCard[0] = cardSplit

        sum = self.same_value_based_hand_plus_river(cardHand)# get pairing result
        pairality = which_pairing[sum]# get pairality
        if(pairality):
            return pairality, highCard
        else:
            curvature = self.straight_hand_plus_river(cardHand, value_dict) # is hand straight
            color = self.flush_hand_plus_river(cardHand) # is hand flush
            if(color and curvature): #is hand straight flush
                if (highCard[0] != 'K'): # is this a royal?
                    return 'straight flush', highCard
                else:
                    return 'royal flush' 
            elif(color):# this is a flush
                return 'flush', highCard
            elif(curvature): #this is a straight
                return 'straight', highCard
            else: # Nothing here
                return 'none', highCard

    #######################################

################################# This block creates possible opponent hands based on what you don't have
    def last_possibilities(self, boardCards, holeCard1, holeCard2, holeCard3):
        # input in form of 'Ac Ac Ac Ac Ac', 'Ac', 'Ac', Ac'
        allCards = ['2h','3h','4h','5h','6h','7h','8h','9h','Th','Jh','Qh','Kh','Ah','2s','3s','4s','5s','6s','7s','8s','9s','Ts','Js','Qs','Ks','As','2d','3d','4d','5d','6d','7d','8d','9d','Td','Jd','Qd','Kd','Ad','2c','3c','4c','5c','6c','7c','8c','9c','Tc','Jc','Qc','Kc','Ac'] # list of all cards
        possible_hands = []
        possible_selections = []
        boardOnly = boardCards.split(' ')
        holeCards = [holeCard1, holeCard2, holeCard3]
        board_plus_hole = boardOnly[:]
        board_plus_hole.extend(holeCards)
        
        for card in board_plus_hole: # remove cards I have
            allCards.remove(card)
        
        for card in allCards:# select 1 card
            allCards.remove(card) # remove it
            for card1 in allCards: # combine with all other cards
                possible_hands.append([card,card1]) # put it into possible_hands
        
        for hand in possible_hands:# pick a possible hand TODO: make a function to handle this
            boardOnlyCopy = boardOnly[:] # save a copy of the board
            for one in boardOnlyCopy:# pull out one card
                boardOnlyCopy.remove(one) # remove that one
                boardOnlyCopyCopy = boardOnlyCopy[:]# save a copy of remaining cards
                for two in boardOnlyCopyCopy:# pull one out of the remaining cards
                    boardOnlyCopyCopy.remove(two)# remove it
                    boardOnlyCopyCopyCopy = boardOnlyCopyCopy[:]# save a copy of reamaining (board - 2
                    for three in boardOnlyCopyCopyCopy:# of the remaining 3 cards
                        h = hand + [one, two, three] # concat a hand
                        hs = self.what_is_hand_plus_river(h) #get a vaule
                        possible_selections.append(hs) # append to possibilities
            
            h0 = hand[0]# manually done for when I select only one card from my pocket because I was lazy
            h1 = hand[1]
            b0 = boardOnly[0]
            b1 = boardOnly[1]
            b2 = boardOnly[2]
            b3 = boardOnly[3]
            b4 = boardOnly[4]
            possible_selections.append(self.what_is_hand_plus_river([h0,b0,b1,b2,b4]))
            possible_selections.append(self.what_is_hand_plus_river([h0,b0,b1,b4,b3]))
            possible_selections.append(self.what_is_hand_plus_river([h0,b0,b4,b2,b3]))
            possible_selections.append(self.what_is_hand_plus_river([h0,b4,b1,b2,b3]))
            possible_selections.append(self.what_is_hand_plus_river([h0,b0,b1,b2,b3]))

            possible_selections.append(self.what_is_hand_plus_river([h1,b0,b1,b2,b4]))
            possible_selections.append(self.what_is_hand_plus_river([h1,b0,b1,b4,b3]))
            possible_selections.append(self.what_is_hand_plus_river([h1,b0,b4,b2,b3]))
            possible_selections.append(self.what_is_hand_plus_river([h1,b4,b1,b2,b3]))
            possible_selections.append(self.what_is_hand_plus_river([h1,b0,b1,b2,b3]))
        return possible_selections
        #returns a  list like [ ['flush', ['K','s']], ....]

##############################################


    def player_best_five(self, boardCards, selectedCard1, selectedCard2): # a lot in common with last_possibilities
        possible_selections = []
        h0 = selectedCard1
        h1 = selectedCard2
        boardOnly = boardCards.split(' ')
        hand = [h0, h1]
        boardOnlyCopy = boardOnly[:] # save a copy of the board
        for one in boardOnlyCopy:# pull out one card
            boardOnlyCopy.remove(one) # remove that one
            boardOnlyCopyCopy = boardOnlyCopy[:]# save a copy of remaining cards
            for two in boardOnlyCopyCopy:# pull one out of the remaining cards
                boardOnlyCopyCopy.remove(two)# remove it
                boardOnlyCopyCopyCopy = boardOnlyCopyCopy[:]# save a copy of reamaining (board - 2
                for three in boardOnlyCopyCopyCopy:# of the remaining 3 cards
                    h = hand + [one, two, three] # concat a hand
                    hs = self.what_is_hand_plus_river(h) #get a vaule
                    possible_selections.append(hs) # append to possibilities
        
        b0 = boardOnly[0]
        b1 = boardOnly[1]
        b2 = boardOnly[2]
        b3 = boardOnly[3]
        b4 = boardOnly[4]
        possible_selections.append(self.what_is_hand_plus_river([h0,b0,b1,b2,b4]))
        possible_selections.append(self.what_is_hand_plus_river([h0,b0,b1,b4,b3]))
        possible_selections.append(self.what_is_hand_plus_river([h0,b0,b4,b2,b3]))
        possible_selections.append(self.what_is_hand_plus_river([h0,b4,b1,b2,b3]))
        possible_selections.append(self.what_is_hand_plus_river([h0,b0,b1,b2,b3]))
        possible_selections.append(self.what_is_hand_plus_river([h1,b0,b1,b2,b4]))
        possible_selections.append(self.what_is_hand_plus_river([h1,b0,b1,b4,b3]))
        possible_selections.append(self.what_is_hand_plus_river([h1,b0,b4,b2,b3]))
        possible_selections.append(self.what_is_hand_plus_river([h1,b4,b1,b2,b3]))
        possible_selections.append(self.what_is_hand_plus_river([h1,b0,b1,b2,b3]))
        return possible_selections
            
            
    def sort_hands_by_value(self, hands): # sorts out hands! Vital as can be for computing percent wins - if order is off, all fails
        val_list = []
        vals = {'royal flush':1, 'straight flush':2, 'four of a kind':3, 'full house':4, 'flush':5,'straight':6,'three of a kind':7, 'two pair':8, 'one pair':9, 'none':10}
        # values of hands, ascending
        for hand in hands:
            val_list.append([vals[hand[0]], hand[1]])
        val_list.sort(key=lambda x: x[0]) # sort by value of best combo.
        return val_list


    def winning_percent(self, boardCards, selectedCard1, selectedCard2, burnedCard1): # this function runs the main order of events to compute chance of winning
        # input in form of 'Ac Ac Ac Ac Ac', 'Ac', 'Ac', 'Ac'
        d1 = datetime.now() 
        value_dict = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
        vals = {'royal flush':1, 'straight flush':2, 'four of a kind':3, 'full house':4, 'flush':5,'straight':6,'three of a kind':7, 'two pair':8, 'one pair':9, 'none':10}

#        pprint.pprint([boardCards, selectedCard1, selectedCard2, burnedCard1])
        opponent_hands = self.last_possibilities(boardCards, selectedCard1, selectedCard2, burnedCard1)# get all possible opponent hands
        #opponent_hands_sorted = self.sort_hands_by_value(opponent_hands) # sort them with the function
        #print opponent_hands
        player_hands = self.player_best_five(boardCards, selectedCard1, selectedCard2)#get all possible player hands
        player_hands_sorted = self.sort_hands_by_value(player_hands)# sort them

        player_best = player_hands_sorted[0]
        player_best_val = player_best[0]
        player_best_high = player_best[1][0][0]
        
        sumw = 0
        suml = 0
        for opponent_current in opponent_hands:
            opponent_current_val = vals[opponent_current[0]]
        
            opponent_current_high = opponent_current[1][0][0]
            #print opponent_current_high, player_best_high
            if(opponent_current_val < player_best_val):
                pass
                suml += 1
                #print 'loose'
            elif((opponent_current_val == player_best_val) and (value_dict[opponent_current_high] > value_dict[player_best_high])):
                pass
                suml += 1
                #print 'loose'
            elif((opponent_current_val == player_best_val) and (value_dict[opponent_current_high] == value_dict[player_best_high])):
                pass
                suml += 0.5
                #print 'tie'
            else:
                sumw+=1
                #print 'win'
                #break
        percent_win = (sumw/(sumw+suml))
        d2 = datetime.now()
        #print d2-d1
        #print percent
        return percent_win

    def debug(self):
        for i in range(0,10):
            allCards = ['2h','3h','4h','5h','6h','7h','8h','9h','Th','Jh','Qh','Kh','Ah','2s','3s','4s','5s','6s','7s','8s','9s','Ts','Js','Qs','Ks','As','2d','3d','4d','5d','6d','7d','8d','9d','Td','Jd','Qd','Kd','Ad','2c','3c','4c','5c','6c','7c','8c','9c','Tc','Jc','Qc','Kc','Ac']
            random.shuffle(allCards)
            s = self.winning_percent(allCards.pop()+' '+allCards.pop()+' '+allCards.pop()+' '+allCards.pop()+' '+allCards.pop(), allCards.pop(), allCards.pop(), allCards.pop())
            print s
################### pre-flop:
    def anneal_before_flop_choice(self, holeCard1, holeCard2, holeCard3, cycles):
        i = 0
        awin = 0
        bwin = 0
        cwin = 0
        while(i < cycles):
            i += 1
            allCards = ['2h','3h','4h','5h','6h','7h','8h','9h','Th','Jh','Qh','Kh','Ah','2s','3s','4s','5s','6s','7s','8s','9s','Ts','Js','Qs','Ks','As','2d','3d','4d','5d','6d','7d','8d','9d','Td','Jd','Qd','Kd','Ad','2c','3c','4c','5c','6c','7c','8c','9c','Tc','Jc','Qc','Kc','Ac']
            allCards.remove(holeCard1)
            allCards.remove(holeCard2)
            allCards.remove(holeCard3)
            random.shuffle(allCards)
            potential_cards = allCards.pop()+' '+allCards.pop()+' '+allCards.pop()+' '+allCards.pop()+' '+allCards.pop()
            awin += self.winning_percent(potential_cards, holeCard1, holeCard2, holeCard3)
            bwin += self.winning_percent(potential_cards, holeCard3, holeCard1, holeCard2)
        
            cwin += self.winning_percent(potential_cards, holeCard3, holeCard2, holeCard1)
        print '1'
        return [[holeCard1, cwin/cycles], [holeCard2,bwin/cycles], [holeCard3,awin/cycles]]

    def run_anneals(self):
        allCards = ['2h','3h','4h','5h','6h','7h','8h','9h','Th','Jh','Qh','Kh','Ah','2s','3s','4s','5s','6s','7s','8s','9s','Ts','Js','Qs','Ks','As','2d','3d','4d','5d','6d','7d','8d','9d','Td','Jd','Qd','Kd','Ad','2c','3c','4c','5c','6c','7c','8c','9c','Tc','Jc','Qc','Kc','Ac']
        all_3_hands = []
        for card in allCards:
            allCards.remove(card)
            cloneAllCards = allCards[:]
            for card1 in cloneAllCards:
                cloneAllCards.remove(card1)
                for card2 in cloneAllCards:
                    all_3_hands.append([card, card1, card2])
        #pprint.pprint( all_3_hands)
        all =[]
        print len(all_3_hands)
        i=0
        for hand in all_3_hands:
            i+=1
            if i%1000 == 0:
                print '1k'
            s = self.anneal_before_flop_choice(hand[0],hand[1],hand[2],10)
            all.append(s)
        print all

#####################
    def what_is_hand_at_flop(self, hand): # compile the straight, flush, and pairing functions
        # takes hand of 5 in an array like ['Ah','Tc'....]
        value_dict = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14} # value_dict for straights
        which_pairing =  {7: 'one pair', 9 : 'two pair',
        13 : 'full house',11:'three of a kind',
        17:'four of a kind',5:False} # paring dictionary for sum values TODO: move these for better speed
        cardHand = []
        highCard = [['2','s']]# lowest possible card, meant to be ignored/swapped
        for card in hand:
            cardSplit = list(card) #split card into a char array
            cardHand.append(cardSplit) # assemble a hand array like [[card1], [card2]...]
            if value_dict[cardSplit[0]] >= value_dict[highCard[-1][0]]: # if high card found, replace
                highCard[0] = cardSplit
        
        sum = self.same_value_based_hand_plus_river(cardHand)# get pairing result
        pairality = which_pairing[sum]# get pairality
        if(pairality):
            return pairality, highCard
        else:
            curvature = self.straight_hand_plus_river(cardHand, value_dict) # is hand straight
            color = self.flush_hand_plus_river(cardHand) # is hand flush
            if(color and curvature): #is hand straight flush
                if (highCard[0] != 'K'): # is this a royal?
                    return 'straight flush', highCard
                else:
                    return 'royal flush'
            elif(color):# this is a flush
                return 'flush', highCard
            elif(curvature): #this is a straight
                return 'straight', highCard
            else: # Nothing here
                return 'none', highCard
    

    def flush_hand_likelyhood_flop(self, hand): # computes if a given set of 5 contains a flush
        # takes input in [[A,h],[K,d]....] format
        suits = []
        for card in hand:
            suits.append(card[1]) # collect all suits
        if(suits.count(suits[0]) == 5): # if the count of the first el is 5, its a flush
            return True
        else:
            return False

    def same_value_based_hand_likelyhood_flop(self, hand): # computes if a given set of 5 contains any kind of pairs
        # in [[A,h],[K,d]....] format
        values = []
        for card in hand:
            values.append(card[0]) # collect all values
        sum = 0
        for card in values:
            sum += values.count(card) # sum is unique to type of pair based hand (17, 13, 11, 9, 7 , 5)
        return sum
    
    def straight_hand_likelyhood_flop(self, hand, value_dict): # computes if a given set of 5 contains any kind of straight
        # takes a hand in [[A,h],[K,d]....] format, value dict in 2:2, ... A:14 format
        values = []
        vcheck =[]
        for card in hand:
            values.append(value_dict[card[0]])# assemble the values of the straight
        values.sort() # arrange in increasing order
        for x in range(0, 5): #go over hand indices
            vcheck.append(values[x] - x)# values[x] - x: consider [2,3,4,5,6] => [2,2,2,2,2]
        straight_height = vcheck[0]
        for x in range(0,5):
            vcheck[x] = vcheck[x]-straight_height+1
        gaps = []
        for x in range(1,5):
            gaps.append(vcheck[x]-vcheck[x-1])
        linears = gaps.count(1)
        linear1s = gaps.count(2)
        linear2s = gap.count(3)
        tooWide = 4-linear1s-linear2s -linears
        if tooWide >=3:
            return 0
        elif tooWide == 2:
            if linear2s == 2:
                return 'not bad'
            elif linear2s == 1:
                if linear1s == 1:
                    return 'better than not bad'
                else:
                    'better than better than not bad'
            else:
                return 'better than better than better than not bad'
        elif tooWide == 1:
            if linear2s == 3:
                pass
            if linear2s == 2:
                return 'not bad'
            if linear2s == 1:
                if linear1s == 1:
                    return 'better than not bad'
                else:
                    'better than better than not bad'
            else:
                return 'better than better than better than not bad'
            
        else:
            pass
            
    

    def burn_which_card_simple(self, boardCards, holeCard1, holeCard2, holeCard3):
        vals = {'royal flush':1, 'straight flush':2, 'four of a kind':3, 'full house':4, 'flush':5,'straight':6,'three of a kind':7, 'two pair':8, 'one pair':9, 'none':10}
        a = self.what_is_hand_at_flop(boardCards + [holeCard1, holeCard2])
        a_val = vals[a[0]]# sort them
        #a_val = a_hands_sorted[0][0]
        b = self.what_is_hand_at_flop(boardCards + [holeCard3, holeCard1])
        b_val = vals[b[0]]
        #b_val = b_hands_sorted[0][0]
        c = self.what_is_hand_at_flop(boardCards + [holeCard3, holeCard2])
        c_val = vals[c[0]]# sort them
        
        #c_val = c_hands_sorted[0][0]
        a_lowest = (a_val < c_val) and (a_val < b_val)
        b_lowest = (b_val < a_val) and (b_val < c_val)
        c_lowest = (c_val < a_val) and (c_val < b_val)
        print a_lowest, b_lowest, c_lowest
        if c_lowest:
            return 1
        elif a_lowest:
            return 3
        elif b_lowest:
            return 2
        else:
            #x = random.randrange(1,4)
            return 'lowcard'
        


analysis_engine = Analyzer()
    #####################=Jeremy


#### Justin's work ####



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
    print b
    print '#################'
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
    

    #

############################################

########## Make List Functions #############

# Returns list of possible_responses to engine
# bet is [0], call is [1], check is [2], discard is [3], fold is [4], raise is [5]
def make_possible_responses():
    
    canBet = [False, 'BET', 0, 0]
    canCall = [False, 'CALL']
    canCheck = [False, 'CHECK']
    canDiscard = [False, 'DISCARD']
    canFold = [False, 'FOLD']
    canRaise = [False, 'RAISE', 0, 0]
    for action in Player.legalActions:
        if 'BET' in action:
            canBet[0] = True
            betSplit = action.split(':')
            canBet[2] = betSplit[1]
            canBet[3] = betSplit[2]
        if 'CALL' in action:
            canCall[0] = True
        if 'CHECK' in action:
            canCheck[0] = True
        if 'DISCARD' in action:
            canDiscard[0] = True
        if 'FOLD' in action:
            canFold[0] = True
        if 'RAISE' in action:
            canRaise[0] = True
            raiseSplit = action.split(':')
            canRaise[2] = raiseSplit[1]
            canRaise[3] = raiseSplit[2]
    return [canBet, canCall, canCheck, canDiscard, canFold, canRaise]

# Will parse to recieve the last actions in a better list
def get_last_actions():
    i = 0
    actionList = Player.lastActions[:]
    for action in Player.lastActions:
        actionSplit = action.split(':')
        actionList[i] = actionSplit
        i += 1
    return actionList

###############################################

########## Basic Betting Responses ############

# Will bet 'percent' of big blind (must have BET in legal actions)
def bet_percent():
    
    ##### percent is currently set to 300 #####
    percent = 300
    betPercent = str(percent*int(Player.bb)/100)
    
    bet_raise(betPercent)

# Will raise minimum amount, or will go/call all in
def raise_min():
    
    if Player.possible_responses[5][0]:
        bet_raise(Player.possible_responses[5][2])
    elif Player.possible_responses[1][0]:
        call()

###############################################

########### Raise Counter Functions ###########

# Resets raise counter
def reset_raises():
    Player.raise_counter = 0

# Increments raise counter
def increment_raises():
    Player.raise_counter += 1

###############################################

########### Pbots_calc Functions ##############

# Turns output of pbots_calc into a useable list
def pbots_calc_clean(handlist,boardlist,discarded):
    
    # set for 100 Monte Carlo iterations
    d1 = datetime.now()
    oddslist = str(pbots_calc.calc(handlist,boardlist,discarded,100))
    d2 = datetime.now()
    print d2-d1
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
def preflop_keep():
    handlist = Player.holeCard1+Player.holeCard2+Player.holeCard3
    handlist = handlist.lower()
    oddslist = pbots_calc_clean(handlist+':xx','','')
    
    # generate the keep_hand boolean, determined by class variable keep_percent
    if float(oddslist[1])>= 1-Player.keep_percent:
        return True
    else:
        return False

###############################################

############ Betting Strategies ###############

# Basic pre-flop 3-betting based on button
def preflop_3bet():
    
    ###### keep_hand is a boolean determining whether we bet or not, determined by analyzing stats ######
    if Player.raise_counter == 0:
        keep_hand = preflop_keep()
    
    ###### ev_call is a boolean that compares chance to win hand against pot odds
    # if ev_call:
    
    
    # raise a certain percent to start off betting
    if Player.last_actions[-1][0] == 'POST' and keep_hand:
        #print 'Making the initial bet now'
        increment_raises()
        bet_percent()
    
    # make the 3-bet if we have button and only raised once, else call
    elif (Player.last_actions[-1][0] == 'RAISE' and Player.button == 'true') and keep_hand:
        if Player.raise_counter == 1:
            #print 'Making the 3 bet now:'
            raise_min()
        else:
            #print 'Calling because not making the 3 bet:'
            call()
    
    # prevent the 3-bet in we don't have button
    elif (Player.last_actions[-1][0] == 'RAISE' and Player.button != 'true') and keep_hand:
        #print 'Dont have the button, so are calling'
        call()
    
    # fold if we choose to not keep hand
    elif not keep_hand:
        fold()
    
    # else check
    else:
        #print 'Checking because we dont have the button and saw no raise'
        check()


## Test function for simple betting procedures
def simple_betting():
    
    # make possible responses for this move
    Player.possible_responses = make_possible_responses()
    
    # get the last actions made
    Player.last_actions = get_last_actions()
    
    # if pre-flop, set raise counter to 0, run pre-flop betting strategy
    if int(Player.numBoardCards) == 0:
        reset_raises()
        #print 'Going to preflop_3bet now'
        preflop_3bet()
    
    
    ####### if not preflop, all-in strategy (want to change)
    else:
        #print 'Going to all-in now:'
        auto_all_in()


## Test function: always calling, discarding lowest card
def auto_call():
    
    # make possible responses for this move
    Player.possible_responses = make_possible_responses()
    
    # get the last action made
    Player.last_actions = get_last_actions()
    
    if Player.possible_responses[1][0]:
        call()
    elif Player.possible_responses[3][0]:
        discard_low()
    else:
        check()

## Test function: always going all in, discarding lowest card
def auto_all_in():
    
    # make possible responses for this move
    Player.possible_responses = make_possible_responses()
    
    if Player.possible_responses[0][0]:
        bet_raise(Player.possible_responses[0][3])
    elif Player.possible_responses[5][0]:
        bet_raise(Player.possible_responses[5][3])
    elif Player.possible_responses[3][0]:
        discard_low()
    else:
        check()

##################################################

#### End Justin's work ####


class Player:
    #Class variables
    selectedCard1 = '0'
    selectedCard2 = '0'
    burnedCard_is = '0'
    holeCard1 = '0'
    holeCard2 = '0'
    holeCard3 = '0'
    bb = '0'
    lastActions = []
    legalActions = []
    button = 'false'
    possible_responses = []
    last_actions = []
    numBoardCards = '0'
    raise_counter = 0
    ######## keep_percent currently set to 50% #########
    keep_percent = 0.60
    def run(self, input_socket):
        # Get a file-object for reading packets from tde socket.
        # Using this ensures that you get exactly one packet per read.
        f_in = input_socket.makefile()
        
        
        while True:
            # Block until the engine sends us a packet.
            data = f_in.readline().strip()
            # if data is None, connection has closed.
            if not data:
                print "Gameover, engine disconnected."
                break
            
            # Here is where you should implement code to parse the packets from
            # the engine and act on it. We are just printing it instead.
            print data
            
            word = data.split()
            
            ### String Parsing
            if word[0] == "GETACTION":
                action = "GETACTION"
                potSize = word[1]
                
                Player.numBoardCards = word[2]
                tempBC=int(Player.numBoardCards)
                Player.boardCards=word[3:3+tempBC]
                Player.numLastActions=word[3+tempBC]
                tempLast=int(Player.numLastActions)
                Player.lastActions=word[4+tempBC:4+tempBC+tempLast]
                
                Player.numLegalActions=word[4+tempBC+tempLast]
                tempLegal=int(Player.numLegalActions)
                Player.legalActions=word[5+tempBC+tempLast:5+tempBC+tempLast+tempLegal]
                
                timeBank = word[-1]
            elif word[0] == "NEWHAND":
                action = "NEWHAND"
                handId = word[1]
                Player.button = word[2]
                Player.holeCard1 = word[3]
                Player.holeCard2 = word[4]
                Player.holeCard3 = word[5]
                yourBank = word[6]
                oppBank = word[7]
                timeBank = word[8]
            #preFlopHand(holeCard3,holeCard2,holeCard1)
            elif word[0] == "HANDOVER":
                action = "HANDOVER"
                yourBank= word[1]
                oppBank = word[2]
                
                Player.numBoardCards = word[3]
                tempBC = int(Player.numBoardCards)
                Player.boardCards = word[4:4+tempBC]
                
                Player.numLastActions = word[4+tempBC]
                tempLast = int(Player.numLastActions)
                Player.lastActions = word[5+tempBC:5+tempBC+tempLast]
                
                timeBank = word[-1]
            elif word[0] == "KEYVALUE":
                action = word[0]
                key = word[1]
                value = word[2]
            elif word[0] == "NEWGAME":
                action = word[0]
                yourName = word[1]
                oppName = word[2]
                stackSize = word[3]
                Player.bb = word[4]
                numHands = word[5]
                timeBank = word[6]
            elif word[0] == "REQUESTKEYVALUES":
                action = word[0]
                bytesLeft = word[1]
            ### End String Parsing
            
            if action == "GETACTION":
                simple_betting()
            #if(numBoardCards == 4):
            #   print last_possibilities(boardCards, holeCard1, holeCard2, holeCard3)
            elif action == "REQUESTKEYVALUES":
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")
        # Clean up the socket.
        s.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
    parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
    parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
    args = parser.parse_args()

    # Create a socket connection to the engine.
    print 'Connecting to %s:%d' % (args.host, args.port)
    try:
        s = socket.create_connection((args.host, args.port))
    except socket.error as e:
        print 'Error connecting! Aborting'
        exit()

    bot = Player()
    bot.run(s)




