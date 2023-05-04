
PORT = /dev/ttyUSB0

all: rs run

run:
	ampy -p $(PORT) put module/ads1299.py
	ampy -p $(PORT) run app/main.py

list:
	ampy -p $(PORT) ls

flash:
	ampy -p $(PORT) put app/main.py

plot: rs
	rshell -p /dev/ttyUSB0 cp /pyboard/signals.json .
	python plot.py
	rm signals.json

repl:
	rshell -p $(PORT) repl

rs:
	ampy -p $(PORT) reset

clean:
	ampy -p $(PORT) rm main.py


