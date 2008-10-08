TALKS="StateOfZope3-PC08 Z3CForms"
REST2S5="./rst2s5.py"
THEME_URL="../s5-themes/zope"
STYLESHEET_PATH="./s5-themes/zope/reference.css"

all: build

build:
	for talk in "$(TALKS)"; do \
	    echo "Generating $$talk"; \
	    $(REST2S5) --stylesheet $(STYLESHEET_PATH) \
	        --theme-url $(THEME_URL) \
	        ./$$talk/$$talk.txt \
	        ./$$talk/$$talk.html; \
	done; \
	echo

single:
	echo "Generating $$talk"; \
	$(REST2S5) --stylesheet $(STYLESHEET_PATH) \
	   --theme-url $(THEME_URL) \
	   ./$$talk/$$talk.txt \
	   ./$$talk/$$talk.html; \


clean:
	for talk in "$(TALKS)"; do \
	    rm ./$$talk/$$talk.html; \
	    rm -rf ./$$talk/ui; \
	done; \
	echo
