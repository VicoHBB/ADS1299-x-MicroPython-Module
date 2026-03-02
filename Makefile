PORT = /dev/ttyUSB0
FIRMWARE = ESP32_GENERIC-20251209-v1.27.0.bin # You need to downloand and update Firmware

all: rs prep run

run:
	uv run ampy -p $(PORT) put src/module/
	uv run ampy -p $(PORT) run src/main.py

prep:
	uv run ampy -p $(PORT) put src/module/

list:
	uv run ampy -p $(PORT) ls

flash: rs prep
	uv run ampy -p $(PORT) put src/app/main.py

test_1s: rs prep
	uv run ampy -p $(PORT) run tests/1_slave_test.py
	uv run rshell -p /dev/ttyUSB0 cp /pyboard/signals.json tests/
	uv run python tests/plot_channels.py
	uv run rm tests/signals.json

test_2s: rs prep
	uv run ampy -p $(PORT) run tests/2_slaves_test.py
	uv run rshell -p /dev/ttyUSB0 cp /pyboard/signals.json tests/
	uv run python tests/plot_channels.py
	uv run rm tests/signals.json

repl:
	uv run rshell -p $(PORT) repl

rs:
	uv run ampy -p $(PORT) reset

clean:
	uv run ampy -p $(PORT) rmdir module/
	uv run ampy -p $(PORT) rm main.py

esp_update: esp_erase esp_flash

esp_erase:
	uv run esptool --chip esp32 --port $(PORT) erase-flash

esp_flash:
	uv run esptool --chip esp32 --port $(PORT) --baud 460800 write_flash -z 0x1000 $(FIRMWARE)

help:
	@echo "### HELP ###"
	@echo "make all        -> Runs the rs and run recipes."
	@echo "make run        -> Just run main.py file to the Pyboard."
	@echo "make prep       -> Uploads the module/ dir and files that will be use to the Pyboard."
	@echo "make list       -> Lists all files on the Pyboard."
	@echo "make flash      -> Flash all files of the project to the Pyboard."
	@echo "make test_1s    -> Execute test for one slave."
	@echo "make test_2s    -> Execute test for two slaves."
	@echo "make repl       -> Connects to the Pyboard's REPL and start it."
	@echo "make rs         -> Resets the Pyboard."
	@echo "make clean      -> Removes project files from the Pyboard just leave boot.py."
	@echo "make esp_update -> Erase flashe and deploy firmware to the Pyboard"
	@echo "make esp_erase  -> Erase the entire flash of Pyboard"
	@echo "make esp_flash  -> Deploy the firmware to the Pyboard"
