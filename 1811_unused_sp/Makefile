TARGETS = $(patsubst posts-%.shelf,stats-%.shelf,$(wildcard posts-*.shelf))

all: $(TARGETS)

clean:
	$(RM) $(TARGETS)

stats-%.shelf: posts-%.shelf daily_stats.py
	python daily_stats.py $<
