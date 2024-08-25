
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

