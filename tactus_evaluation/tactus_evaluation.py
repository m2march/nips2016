'''This script performs the evaluation and comparison of the THT and Melisma
systems on the task of infering the correct beat for the song for the KP,
KP-Perf and Tap datasets.'''

import glob
import os
import melisma
import collections
import pandas
import numpy as np

from tht import midi
from tht.tht import tracking_overtime
from tht.tht import tactus_hypothesis_tracker

CORRECTNESS_EPSILON = 1.5

tht = tactus_hypothesis_tracker.default_tht()

def get_dataset(dataset_name, bpm_f):
    '''Returns the parameter dataset information generator.
    
    The expected bpm is extracted with the parametric function.
    
    Args:
        dataset_name: folder on which to look for the dataset cases
        bpm_f: (midi, midi_path) -> float function to extract bpm

    Returns:
        A generator of (name :: string, onsets :: [ms], expected_bpm :: float, 
            melisma_bpm :: float).
    '''
    for midi_file in glob.glob('../datasets/{}/*.mid'.format(dataset_name)):
        m = midi.MidiPlayback(midi_file)
        nb_file = midi_file.replace('.mid', '.nb')
        with open(nb_file, 'r') as f:
            melisma_bpm = np.mean(melisma.bpms_over_nblines(f.readlines()))
        m.collapse_onset_times()
        yield (os.path.basename(midi_file),
               m.onset_times_in_ms(), bpm_f(m, midi_file), 
               melisma_bpm)

def get_tap_dataset():
    'Returns the tap dataset (name, onsets, expected_bpm, melisma_bpm) list'
    def bpm_f(m, midi_file):
        bpm_name = os.path.join(midi_file.replace('mid', 'bpm'))
        if os.path.exists(bpm_name):
            with open(bpm_name, 'r') as f:
                return float(f.readlines()[0])
        else:
            return m.bpm
    return list(get_dataset('tap', bpm_f))

def get_kp_dataset():
    'Returns the kp dataset (name, onsets, expected_bpm, melisma_bpm) list'
    def bpm_f(m, midi_file):
        return m.bpm
    return list(get_dataset('kp', bpm_f))

def get_kp_perf_dataset():
    'Returns the kp-perf dataset (name, onsets, expected_bpm, melisma_bpm) list'
    expected_bpms = {}
    with open('../datasets/kp-perf/bpms.txt', 'r') as f:
        expected_bpms = dict([l.split(' ') for l in f.readlines()])

    def bpm_f(m, midi_file):
        key = os.path.splitext(os.path.basename(midi_file))[0]
        return float(expected_bpms[key])

    return list(get_dataset('kp-perf', bpm_f))


def is_correct_tactus(bpm, expected_bpm):
    'Returns 1 if the bpm is considered correct against expected_bpm'
    both = np.array([bpm, expected_bpm])
    m = both.min()
    mm = both.max()
    remain = np.array([m - (mm % m), mm % m]).min()
    return remain < CORRECTNESS_EPSILON


def scores_for_dataset(dataset):
    'Returns the percentage of correct answers on the dataset for tht'
    tht_results = []
    melisma_results = []
    for name, onsets, expected_bpm, melisma_bpm in dataset:
        hts = tht(onsets)
        hats = tracking_overtime.OvertimeTracking(hts)
        top_hyp = [hs[1][0].hts for hs in hats.hypothesis_sorted_by_conf()]
        c = collections.Counter(sorted(top_hyp, key=lambda ht: ht.name))
        tht_bpm = max(c.items(), key=lambda x: c[1])[0].bpm()

        tht_results.append(is_correct_tactus(tht_bpm, expected_bpm))
        melisma_results.append(is_correct_tactus(melisma_bpm, expected_bpm))
    return {'tht': np.mean(tht_results), 'melisma': np.mean(melisma_results)}



datasets = {
    'kp': get_kp_dataset(),
    'kp-perf': get_kp_perf_dataset(),
    'tap': get_tap_dataset()
}


def main():
    results = {}
    for dataset_name, cases in datasets.items():
        results[dataset_name] = scores_for_dataset(cases[:5])

    df = pandas.DataFrame.from_dict(results, orient='index')
    print df.to_latex(
            column_format='| l | c | c |', 
            float_format=lambda f: '%.2f' % f,
            index_names=True)


if __name__ == '__main__':
    main()
