class Analyzer(object):
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