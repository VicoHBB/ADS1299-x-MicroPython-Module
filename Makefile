
PORT = /dev/ttyUSB0

all: rs run

run:
	ampy -p $(PORT) put module/ads1299.py
	ampy -p $(PORT) run app/main.py

list:
	ampy -p $(PORT) ls

flash: rs
	ampy -p $(PORT) put module/ads1299.py
	ampy -p $(PORT) put app/main.py

test1: rs
	ampy -p $(PORT) put module/ads1299.py
	ampy -p $(PORT) run tests/1_slave_test.py
	rshell -p /dev/ttyUSB0 cp /pyboard/signals.json tests/
	python tests/plot.py
	rm tests/signals.json

test2: rs
	ampy -p $(PORT) put module/ads1299.py
	ampy -p $(PORT) run tests/2_slaves_test.py
	rshell -p /dev/ttyUSB0 cp /pyboard/signals.json tests/
	python tests/plot.py
	rm tests/signals.json

repl:
	rshell -p $(PORT) repl

rs:
	ampy -p $(PORT) reset

clean:
	ampy -p $(PORT) rm main.py
	ampy -p $(PORT) rm ads1299.py

help:
	@echo "### HELP ###"
	@echo "make all   -> Runs the rs and run recipes."
	@echo "make run   -> Uploads the ads1299.py and just run main.py file to the Pyboard.py script."
	@echo "make list  -> Lists all files on the Pyboard."
	@echo "make flash -> Resets the Pyboard and uploads the ads1299.py and main.py files."
	@echo "make test1 -> Execute test for one slave."
	@echo "make test2 -> Execute test for two slaves."
	@echo "make repl  -> Connects to the Pyboard's REPL and start it."
	@echo "make rs    -> Resets the Pyboard."
	@echo "make clean -> Removes the main.py and ads1299.py files from the Pyboard."
