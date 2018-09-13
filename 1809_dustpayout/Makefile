TARGETS = $(patsubst posts-%.shelf,stats-%.shelf,$(wildcard posts-*.shelf))

all: $(TARGETS)

clean:
	$(RM) $(TARGETS)

stats-%.shelf: posts-%.shelf parse_day.py
	python parse_day.py $<
