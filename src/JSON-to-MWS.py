#!/usr/bin/env python
"""
JSON-to-MWS.py
    Given a mtgjson set array converts it into mws spoiler format and ouputs
    into a txt file
    
Author: Rui Miranda

Usage:
    python JSON-to-MWS.py http://mtgjson/seturlexample [output]
"""

from __future__ import print_function
import requests
import re
import os
import sys

#_______________________________________________________________________________

class MTGJSONCARD:
    def __init__(self, card):
        self.name = card['name']
        self.type = card['type']
        self.artist = card['artist']
        self.rarity = card['rarity']
        self.number = card['number']
        self.types = card['types']
        self.colors = []
        self.manaCost = ''
        self.power = ''
        self.toughness = ''
        self.text = ''
        self.flavor = ''
        if 'colors' in card:
            self.colors = card['colors']
        if 'manaCost' in card:
            self.manaCost = card['manaCost']
        if 'power' in card:
            self.power = card['power']
        if 'toughness' in card:
            self.toughness = card['toughness']
        if 'text' in card:
            self.text = card['text']
        if 'flavor' in card:
            self.flavor = card['flavor']


#_______________________________________________________________________________

def _(text):
    text = str(text).replace('•','')
    text = str(text).replace('-','')
    text = str(text).replace('−','')
    return str(text).replace('—','')
    #return str(text).replace('—','-')
    #return str(text).replace('−','—')

def get_create_pow_tou(types, power, toughness):
    pow_tou = ''
    if 'Creature' in types:
        pow_tou = power + '/' + toughness
    return pow_tou
      
def get_color(colors, types):
    color = None
    if colors:
        if(len(colors)>1):
            color = 'Gld'
        else:
            color = color_code[colors[0]]
    else:
        if 'Land' in types:
            color = 'Lnd'
        else:
            color = 'Art'
    return color

def get_manacost(manaCost, regex_curved_brackets):
    manaCost1 = manaCost.replace('}{',',')
    manaCost2 = regex_curved_brackets.sub('', manaCost1)
    manaCosts = manaCost2.split(',')
    cost = ''
    for manaCost3 in manaCosts:
        if '/' in manaCost3:#TODO TRANSFORMERS
            cost = cost + cost_splits[manaCost3]
        else:
            cost = cost + manaCost3
    return cost
    #return regex_curved_brackets.sub('', self.manaCost)

cost_splits = {'W/U': '%D','R/W': '%P','B/R': '%K','G/U': '%S','G/W': '%A','W/B': '%O','U/R': '%I','R/G': '%L','U/B': '%V','B/G': '%Q','2/W': '%E','2/U': '%F','2/B': '%H','2/R': '%J','2/G': '%M'}
color_code = {'Black': 'B', 'White': 'W', 'Green': 'G', 'Red': 'R', 'Blue': 'U'}
rarity_code = {'Mythic Rare': 'R','Rare': 'R', 'Uncommon': 'U', 'Common': 'C', 'Basic Land': 'C'}
class MTGJSONCARD2MWS(MTGJSONCARD):
    def __init__(self, card, regex_curved_brackets,cards_total):
        super().__init__(card)
        self.name = _(self.name)
        self.type = _(self.type)
        self.artist = _(self.artist)
        self.rarity = rarity_code[_(self.rarity)]
        self.number = _(self.number)+'/'+cards_total
        if self.manaCost:
            self.manaCost = get_manacost(self.manaCost, regex_curved_brackets)
        if self.power:
            self.power = _(self.power)
        if self.toughness in card:
            self.toughness = _(self.toughness)
        if self.text:
            self.text = _(self.text).replace('{T}','Tap')
        if self.flavor:
            self.flavor = _(self.flavor)
            
        self.color = get_color(self.colors, self.types)   
        self.pow_tou = get_create_pow_tou(self.types, self.power, self.toughness)
        
#_______________________________________________________________________________

def output_mws_file(dict_json, filepath=''):
    code = dict_json['code']
    cards = dict_json['cards']
    cards_total = str(len(cards))
    fname = os.path.join(filepath,code+'.txt')
    regex_curved_brackets = re.compile(r'([{|}]*)', re.IGNORECASE)
    f = open(fname, 'w', encoding='utf-8')
    for card in cards:
        mtgjsoncard2mws = MTGJSONCARD2MWS(card,regex_curved_brackets,cards_total)
        
        print('Card Name:        '+mtgjsoncard2mws.name, file=f)
        print('Card Color:        '+mtgjsoncard2mws.color, file=f)
        print('Mana Cost:        '+mtgjsoncard2mws.manaCost, file=f)
        print('Type & Class:         '+mtgjsoncard2mws.type, file=f)
        print('Pow/Tou:        '+mtgjsoncard2mws.pow_tou, file=f)
        print('Card Text:        '+mtgjsoncard2mws.text, file=f)
        print('Flavor Text:        '+mtgjsoncard2mws.flavor, file=f)
        print('Artist:                '+mtgjsoncard2mws.artist, file=f)
        print('Rarity:                '+mtgjsoncard2mws.rarity, file=f)
        print('Card #:                '+mtgjsoncard2mws.number, file=f)

        print('', file=f)
        del mtgjsoncard2mws
    f.close()
    return fname

#_______________________________________________________________________________
    

def main(url, out_folder=''): 
    r = requests.get(url)
    dict_json = r.json()
    return output_mws_file(dict_json, out_folder)
    
def _usage():
    print("python JSON-to-MWS.py http://mtgjson/seturlexample [output]")
    
if __name__ == "__main__":
    url = sys.argv[-1]
    out_folder = ''
    if not url.lower().startswith("http"):
        out_folder = sys.argv[-1]
        url = sys.argv[-2]
        if not url.lower().startswith("http"):
            _usage()
            sys.exit(-1)
    fname = main(url, out_folder)
    print('CONVERTION COMPLETE TO: '+fname)
