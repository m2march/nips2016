import os
import logging
import glob

import plotting.onsets as po
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

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


def analyze_examples(analyzer):
    for example_file in glob.glob('examples/*.mid'):
        onsets = midi.midi_to_collapsed_onset_times(example_file) 
        hts = tracker(onsets)
        hts_at_time = tracking_overtime.OvertimeTracking(hts)

        analyzer(os.path.basename(example_file), hts, hts_at_time)


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


def output_hipothesis_conf_eval(file_name, hts, hts_at_time):
    hypothesis_count = [len(hats)
                        for time, hats in hts_at_time.hypothesis_by_time()]

    hat_sorted_by_conf = list(hts_at_time.hypothesis_sorted_by_conf())
    times, rel_top_conf = zip(*[
        (time, hats[0].conf / sum([x.conf for x in hats]))
        for time, hats in hat_sorted_by_conf])
    top_conf = [hats[0].conf for _, hats in hat_sorted_by_conf]

    changes = calculate_hypothesis_changes(hat_sorted_by_conf)

    print_hypothesis_evolution(file_name, times, hypothesis_count, changes)

    f = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=(2, 1))
    ax1 = plt.subplot(gs[0])
    ax1.plot(times, top_conf, color='green')
    ax1.set_ylabel('top confidence value')
    ax1.set_ylim(0, 1.1)
    ax1.set_xlim(0, times[-1]) 
    ax1.set_frame_on(False)
    plt.tick_params(bottom=False, left=False, top=False, right=False)
    plt.grid(which='both', lw=1, ls=':', color='grey', alpha=0.6)


    for idx, c in enumerate(changes):
        x = c.hts.onset_times[c.onset_idx]
        ax1.vlines(x=x, ymin=0, ymax=0.5, color='black', alpha=0.7)
        y = 0.4 + (.075 * (idx % 3))
        ax1.text(x=x + 10, y=y  , s=str(c.hts), va='center')

    ax2 = plt.subplot(gs[1])
    po.prepare_for_onsets(ax2)
    ax2.set_ylim(0, 1)
    ax2.vlines(x=hts_at_time.onset_times, ymin=0, ymax=0.7)
    for idx, time in enumerate(hts_at_time.onset_times):
        y = 0.75 + 0.05 * (idx % 2)
        ax2.text(time, y, str(idx), size=6, ha='center')

    plt.xlabel('Onset time (ms)')
    plt.savefig(os.path.join('visualizations', 
        file_name.replace('.mid', '_top_conf.pdf')))


def main():
    analyze_examples(output_hipothesis_conf_eval)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    main()
