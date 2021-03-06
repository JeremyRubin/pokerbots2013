import argparse
import socket
import sys
import random
import pprint
from datetime import datetime
import pbots_calc
from Stats import Stats
import Actions
import StatsStrategy
"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
class Player(object):
    def __init__(self):
        self.fields = {'selectedCard1':None, 'selectedCard2': None,
        'burnedCard_is' : None,
        'boardCards': None,
        'holeCard1' : None,
        'holeCard2' : None,
        'holeCard3' : None,
        'bb' : None,
        'lastActions' : None,
        'legalActions' : None,
        'button' : None,
        'possible_responses' : None,
        'last_actions' : None,
        'numBoardCards' : None,
        'raise_counter' : None,
        'action':None,
        'lastActionsSplit': None,
        'handHistory': None,
        'handHistorySplit': None,
        'handId': None,
        'yourName': None,
        'oppName': None,
        'stackSize':None,
        'potSize': None}
        
        self.respond = Actions.ActionResponder(s)
        self.parser = Actions.Parser(self.fields)
        self.stats = Stats() # load classes once
        self.strategy = StatsStrategy.Strategy(self.respond, self.fields,self.stats)
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
            print
            #################################
            #       PARSER BLOCK            #
            #################################
            self.fields = self.parser.parse(data)
            self.strategy.set_data(self.fields)
            #################################
            #       ACTIONS BLOCK           #
            #################################
            action = self.fields['action']

            
        #print self.fields, 'ffff'
            if action == "GETACTION":
                self.strategy.jeremy_betting()
                print 'Our current Aggro Strategy: '+str(self.strategy.aggro.AggroMod)
                print
                print 'Our current Loose Strategy: '+str(self.strategy.aggro.LooseMod)
                print
            if action == "HANDOVER":
                self.strategy.stats.endOfHandUpdate(self.fields)
                
                print 'Button Preflop Stats: '+str(self.strategy.stats.button.preFlop.read())
                print
                print 'Button Flop Stats: '+str(self.strategy.stats.button.postFlop.read())
                print 
                print 'Button Turn Stats: '+str(self.strategy.stats.button.turn.read())
                print 
                print 'Button River Stats: '+str(self.strategy.stats.button.river.read())
                print 
                print 'Non-Button Preflop Stats: '+str(self.strategy.stats.nobutton.preFlop.read())
                print
                print 'Non-Button Flop Stats: '+str(self.strategy.stats.nobutton.postFlop.read())
                print 
                print 'Non-Button Turn Stats: '+str(self.strategy.stats.nobutton.turn.read())
                print 
                print 'Non-Button River Stats: '+str(self.strategy.stats.nobutton.river.read())
                print 
                
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




