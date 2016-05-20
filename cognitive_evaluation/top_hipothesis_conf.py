import os
import logging
import glob

import plotting.onsets as po
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import collections

from tht import midi
from tht.tht import tactus_hypothesis_tracker
from tht.tht import confidence, similarity, correction, defaults
from tht.tht import tracking_overtime


tracker = tactus_hypothesis_tracker.TactusHypothesisTracker(
    eval_f=confidence.OnsetRestrictedEval(8),
    corr_f=correction.lin_r_corr_opt,
    sim_f=defaults.sim_f,
    similarity_epsilon=defaults.similarity_epsilon,
    min_delta=defaults.min_delta,
    max_delta=defaults.max_delta,
    max_hypotheses=defaults.max_hypotheses)


examples = collections.OrderedDict([
    ['Sudden tempo change', 'examples/duration_step_change.mid'],
    ['Slow tempo change', 'examples/slow_tempo_change.mid'],
    ['Syncopation', 'examples/syncopation.mid'],
    ['Varying musical patterns', 'examples/varying_musical_patterns.mid']
])    

def analyze_examples(analyzer):
    analysis = {}
    for title, example_file in examples.items():
        onsets = midi.midi_to_collapsed_onset_times(example_file) 
        hts = tracker(onsets)
        hts_at_time = tracking_overtime.OvertimeTracking(hts)
        analysis[title] = {
            'hts': hts,
            'hat': hts_at_time,
            'file_name': os.path.basename(example_file)
        }
    return analysis


def calculate_hypothesis_changes(hat_sorted_by_conf):
    '''
    Returns the hypothesis at time of the times when the top hypothesis
    changed.
    '''
    top_confs = [hats[0] for _, hats in hat_sorted_by_conf]
    changes = [top_confs[0]]

    for idx in xrange(1, len(top_confs)):
        if top_confs[idx].hts != top_confs[idx - 1].hts:
            changes.append(top_confs[idx])

    return changes


def print_hypothesis_evolution(file_name, times, hypothesis_count, changes):
    with open(os.path.join('visualizations',
              file_name.replace('mid', 'txt')), 'w') as f:
        print >> f, '# Hypothesis evolution'
        if len(changes):
            print len(times), [c.onset_idx for c in changes]
            changes_at_time = dict([(times[c.onset_idx], c)
                                    for c in changes
                                    if c.onset_idx < len(times)]) #TODO(march): should not be needed
            for time, count in zip(times, hypothesis_count):
                if time in changes_at_time:
                    print >> f, '%d (%d) : %s' % (time, count, 
                                                  changes_at_time[time])
                else:
                    print >> f, '%d (%d)' % (time, count)


def print_conf_per_hypothesis(hts):
    print >> f,  '# Conf per hypothesis'
    sorted_keys = sorted(hts.keys())
    for name in sorted_keys :
        ht = hts[name]
        cs = [c[1] for c in ht.confs]
        print >> f, '%s (%s): %s' % (name, len(cs), 
                ['%.2f' % c for c in cs])


def plot_hipothesis_conf_eval(ax, file_name, hts, hts_at_time):
    hypothesis_count = [len(hats)
                        for time, hats in hts_at_time.hypothesis_by_time()]

    hat_sorted_by_conf = list(hts_at_time.hypothesis_sorted_by_conf())

    times, top_conf = zip(*[
        (time, hats[0].conf)
        for time, hats in hat_sorted_by_conf
    ])

    changes = calculate_hypothesis_changes(hat_sorted_by_conf)
    c_times, c_conf  = zip(*[
        (c.hts.onset_times[c.onset_idx], c.conf)
        for c in changes
    ])

    print_hypothesis_evolution(file_name, times, hypothesis_count, changes)

    ax.plot(times, top_conf, color='forestgreen', lw=1.5)
    ax.plot(c_times, c_conf, ls=' ', marker='|', ms=12, markeredgewidth=2,
            color='darkred')
    ax.set_ylim(0, 1.1)
    ax.set_xlim(0, times[-1]) 
    ax.set_yticks([0, 1])
    ax.set_yticks(np.arange(0, 1, 0.2), minor=True)
    ax.set_frame_on(False)
    plt.tick_params(bottom=False, left=False, top=False, right=False,
            labelbottom=False)
    plt.grid(which='both', lw=1, ls=':', color='grey', alpha=0.6)

    ax.vlines(x=hts_at_time.onset_times, ymin=0, ymax=0.3, lw=2)


def main():
    analysis = analyze_examples(plot_hipothesis_conf_eval)
    for idx, (title, d) in enumerate(analysis.items()):
        plt.figure(figsize=(4,2))
        hts = d['hts']
        hat = d['hat']
        file_name = d['file_name'].replace('.mid', '_top_conf.pdf')
        ax = plt.gca()
        plot_hipothesis_conf_eval(ax, title, hts, hat)
        plt.tight_layout()
        plt.savefig('visualizations/' + file_name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    main()
