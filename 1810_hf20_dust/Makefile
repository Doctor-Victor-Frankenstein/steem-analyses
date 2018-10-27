TARGETS = $(patsubst posts-%.shelf,stats-%.shelf,$(wildcard posts-*.shelf))

all: $(TARGETS)

clean:
	$(RM) $(TARGETS)

stats-%.shelf: posts-%.shelf parse_posts.py
	python parse_posts.py $<
