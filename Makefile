ADDON_VERSION ?= $(shell grep 'version=' addon.xml | grep -v -e '?xml' -e 'import' | grep -o -P '[\d\.]+')
ADDON_NAME ?= $(shell grep -o -P 'id="[^"]+' addon.xml | sed 's/id="//')
ADDON_FILES ?= $(shell cat addon_files.list)
ADDON_CHANNELS_FILE ?= tv.json

all: $(ADDON_NAME).$(ADDON_VERSION).zip

$(ADDON_NAME).$(ADDON_VERSION).zip: ${ADDON_FILES}
	mkdir -p build/$(ADDON_NAME)
	cp -rv $(ADDON_FILES) build/$(ADDON_NAME)/
	cd build/ && zip -r $(ADDON_NAME).$(ADDON_VERSION).zip ./$(ADDON_NAME)/
	cp -v build/$(ADDON_NAME).$(ADDON_VERSION).zip $(HOME)/

tv.json: update_channel_list.py
	python update_channel_list.py

clean:
	rm -rf build/
	rm $(ADDON_CHANNELS_FILE)
