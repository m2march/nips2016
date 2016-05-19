'''Module with functions to operate with melisma and melisma results.'''
import re

import numpy as np


def tactus_times(nblines):
    return parse_nbfile(nblines)[2]


def parse_nbfile(nblines):
    beats = [[], [], [], [], []]
    for l in nblines:
        beat_re = re.compile('Beat\s+(\d+)\s+(\d).*')
        m = beat_re.match(l)
        if m:
            pip, level = m.groups()
            for i in xrange(int(level)):
                beats[i].append(pip)
    return [np.array(pips, dtype=np.float) for pips in beats]


def moving_average(a, n=5):
    '''Calculates the moving average of a list'''
    ret = np.convolve(a, np.ones((n,)) / n, mode='valid')
    return ret


def tactus_ma(beat_times):
    '''Given a list of beat times in ms, returns a list of tactus deltas
    calculated as a moving average of the inter-beat interval.'''
    deltas = beat_times[1:] - beat_times[:-1]
    ma = moving_average(deltas, n=5)
    return ma


def bpms_ma_over_nblines(nblines):
    beats = parse_nbfile(nblines)
    bpms = [60000.0 / tactus_ma(beat_times) for beat_times in beats
            if len(beat_times)]
    return bpms


def bpms_over_nblines(nblines):
    beats = parse_nbfile(nblines)
    bpms = 60000.0 / (beats[2][1:] - beats[2][:-1])
    return bpms
