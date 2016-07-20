from steemapi.steemclient import SteemClient
from steemexchange import SteemExchange
import pprint
import time
import os

#WALLET NEEDS TO BE IN AN UNLOCKED STATE

class Config():
  wallet_host           = "localhost"
  wallet_port           = 8091
  wallet_user           = ""
  wallet_password       = ""
  safe_mode             = False
  witness_url           = "wss://this.piston.rocks" #USE A LOCAL NODE IF YOU CAN
  account = "steem_user"


################################################
###############CONFIG SECTION ##################

steem   = SteemExchange(Config,safe_mode=True) #SET THIS TO FALSE TO START TRADING

balSteem = 0
balSbd   = 0

spread   = 0.03 #THIS IS EFFECTIVELY 6% SPREAD!
tolorance = 0.01 #HOW MUCH THE PRICE CAN MOVE BEFORE ORDERS ARE MOVED

################################################
################################################

#THE BOT LOOP
while True:

  os.system('clear')

  peg = float(steem.returnTicker()['STEEM:SBD']['latest'])

  balances = steem.returnBalances()
  print("\nLiquid: %s %s\n" % (balances['STEEM'], balances['SBD']))

  balSteem = float(balances['STEEM'].partition(' ')[0])
  balSbd   = float(balances['SBD'].partition(' ')[0])

  liqSteem = balSteem
  liqSbd   = balSbd

  print("Latest: %f \n" % peg)
  buy  = peg * (1 - spread)
  sell = peg * (1 + spread)

  openOrders = steem.returnOpenOrders()
  print("Open Orders:\nTYPE  Rewarded  STEEM   Price\n----+---------+--------------\n")

  for order in openOrders:
    #print("%s" % order)
    raw_price = order['sell_price']['base']
    base = raw_price.partition(' ')[2]
    price = float(order['real_price'])

    rewarded = order['rewarded']
    rewarded = True
    if (base == 'SBD'):

       quantity = float(order['sell_price']['quote'].partition(' ')[0])

       if (abs(price - buy) / price) >= tolorance:
         print("[BUY]  [%r] %f @ %f [CANCEL]" % (order['rewarded'], quantity, price))
         if rewarded: 
           result = steem.cancel(order['orderid'])
       else:
         print("[BUY]  [%r] %f @ %f" % (order['rewarded'], quantity, price))

       balSbd = balSbd + float(order['sell_price']['base'].partition(' ')[0])

    else:

       quantity = float(order['sell_price']['base'].partition(' ')[0])

       if (abs(price - sell ) / price) >= tolorance:
         print("[SELL] [%r] %f @ %f [CANCEL]" % (order['rewarded'], quantity, price))
         if rewarded:
           result = steem.cancel(order['orderid'])
       else:
         print("[SELL] [%r] %f @ %f" % (order['rewarded'], quantity, price))

       balSteem = balSteem + float(order['sell_price']['base'].partition(' ')[0])


  print("\n\nTotal Bot: %0.3f STEEM %0.3f SBD ($%0.2f)" % (balSteem, balSbd, (balSteem*peg) + balSbd))
  print ("\n=========================\n")

  if liqSbd >= 4:
    try:
      result = steem.buy(liqSbd/buy, 'STEEM', buy) 
      print("Buy  STEEM @ %f SBD/STEEM...\r" % (buy ))
      print("     Order placed!")
    except:
      pass

  if liqSteem >= 1:
    try:
      result = steem.sell(liqSteem, 'STEEM', sell)
      print("Sell STEEM @ %f SBD/STEEM...\r" % ( sell ))
      print("     Order placed!")
    except:
      pass
  
  time.sleep( 3 )

