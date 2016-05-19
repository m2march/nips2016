'''Helper functions for plotting onsets.'''


def prepare_for_onsets(ax):
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(left='off', right='off', labelleft=False)
