#!/usr/bin/env python
# encoding: utf-8
"""
Created by Olivier Bélanger on 2010-04-22.
"""
from pyo import *
from random import uniform

s = Server(sr=44100, nchnls=2, buffersize=512, duplex=0).boot()

a = FM(carrier=[uniform(197,203) for i in range(10)], 
       ratio=[uniform(0.49,0.51) for i in range(10)], 
       index=[uniform(8,12) for i in range(10)], mul=.1).out()

def go():
    a.set("carrier", [uniform(395,405) for i in range(10)], 20)
    a.set("ratio", [uniform(0.14,0.16) for i in range(10)], 18)
    a.set("index", [uniform(4,6) for i in range(10)], 23)
    
s.gui(locals())

