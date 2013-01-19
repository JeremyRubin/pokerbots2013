class Cards():

    def __init__(self):
        self.holeCard1 = '0'
        self.holeCard2 = '0'
        self.holeCard3 = '0'
        self.boardCards = []
        self.handList = []

    def setHand(self,holeCard1,holeCard2,holeCard3):
        self.holeCard1 = holeCard1
        self.holeCard2 = holeCard2
        self.holeCard3 = holeCard3
        self.handList = [self.holeCard1, self.holeCard2, self.holeCard3)

    def setBoard(self,boardCards):
        for card in boardCards:
            self.boardCards.append(card)

    def getHand(self):
        return self.handList

    def getHoleCard1(self):
        return self.holeCard1

    def getHoleCard2(self):
        return self.holeCard2

    def getHoleCard3(self):
        return self.holeCard3

    def getBoardCards(self):
        return self.boardCards
