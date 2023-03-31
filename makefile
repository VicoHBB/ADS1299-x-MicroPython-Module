
PORT = /dev/ttyUSB0

all: rs run

run:
	ampy -p $(PORT) put app/ads1299.py
	ampy -p $(PORT) run app/main.py

list:
	ampy -p $(PORT) ls

flash:
	ampy -p $(PORT) put app/main.py

repl:
	rshell -p $(PORT) repl

rs:
	ampy -p $(PORT) reset

clean:
	ampy -p $(PORT) rm main.py


