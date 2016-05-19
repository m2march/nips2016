Here we have the code that performs the beat induction evaluation used to
verify that the THT model works reasonably on this task, even if compared with
another system. 

`tactus_evaluation.py` uses the THT model's output (
[https://github.com/m2march/tht/tree/nips2016](https://github.com/m2march/tht/tree/nips2016))
to estimate the bpms of each passage in each dataset in `../datasets`. It also
uses the output of Melisma for the same task. Finally it outputs a table with
the accuracy on each dataset.

The `melisma` module contains scripts for analyzing the melisma system output
as `.nb` files.
