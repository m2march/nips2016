all: slow_tempo_change.mid duration_step_change.mid \
	varying_musical_patterns.mid \
	syncopation.mid

%.mid: %.abc
	abc2midi $< -o $@
