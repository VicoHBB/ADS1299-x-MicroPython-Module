import sys
import socket
import json
import queue
from collections import deque
import numpy as np
from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg

# ==========================================
# ADS1299 Constants (Adjusted for 250 SPS & Gain 1)
# ==========================================
V_REF = 4.5
GAIN = 1
# Formula: V = (Raw_Int * V_REF) / (GAIN * (2**23 - 1))
LSB_TO_VOLTS = V_REF / (GAIN * ((1 << 23) - 1))

class TelemetryReceiver(QtCore.QThread):
    """
    Dedicated thread for high-speed TCP reception.
    Acts as the 'Producer' in the decoupled architecture.
    """
    status_msg = QtCore.pyqtSignal(str)

    def __init__(self, data_queue, host='0.0.0.0', port=5005):
        super().__init__()
        self.data_queue = data_queue
        self.host = host
        self.port = port
        self.running = True

    def run(self):
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((self.host, self.port))
                    s.listen(1)
                    self.status_msg.emit(f"Server Active: Listening on port {self.port}...")

                    conn, addr = s.accept()
                    with conn:
                        self.status_msg.emit(f"Streaming established with ESP32: {addr}")
                        buffer = ""
                        while self.running:
                            try:
                                data = conn.recv(4096).decode('utf-8')
                                if not data:
                                    break

                                buffer += data
                                # Extract complete JSON objects from stream
                                while "}" in buffer:
                                    end_pos = buffer.find("}") + 1
                                    json_part = buffer[:end_pos]
                                    buffer = buffer[end_pos:]

                                    try:
                                        payload = json.loads(json_part)
                                        self.data_queue.put(payload)
                                    except json.JSONDecodeError:
                                        continue
                            except socket.error:
                                break
                        self.status_msg.emit("Connection lost. Waiting for reconnect...")
            except Exception as e:
                self.status_msg.emit(f"Receiver Error: {e}. Retrying...")
                QtCore.QThread.msleep(1000)


class Dashboard(QtWidgets.QMainWindow):
    """
    Real-Time Monitor.
    Acts as the 'Consumer', buffering and plotting smoothly.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADS1299 Monitor - 250 SPS Synchronized")
        self.resize(1200, 900)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.win = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.win)

        self.win_size = 500
        self.buffers = [deque([0.0] * self.win_size, maxlen=self.win_size) for _ in range(8)]
        self.curves = []

        # Subplots initialization
        for i in range(8):
            p = self.win.addPlot(row=i, col=0)
            p.showGrid(x=True, y=True, alpha=0.3)
            p.setLabel('left', f'Ch{i}', units='V')

            # Dynamic Y scaling, fixed X range
            p.enableAutoRange('y', True)
            p.enableAutoRange('x', False)
            p.setXRange(0, self.win_size)

            curve = p.plot(pen=pg.mkPen(color=(0, 255, 127), width=1.2))
            self.curves.append(curve)
            if i < 7:
                self.win.nextRow()

        self.raw_queue = queue.Queue()
        self.playback_queues = [queue.Queue() for _ in range(8)]

        self.receiver = TelemetryReceiver(self.raw_queue)
        self.receiver.status_msg.connect(self.statusBar().showMessage)
        self.receiver.start()

        # Rendering timer: 30 FPS -> ~33ms frame rate
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.consume_and_render)
        self.timer.start(33)

    def consume_and_render(self):
        """
        Drains network queue and pulls ~8 samples per tick (250 SPS / 30 FPS) for smooth playback.
        """
        # 1. Drain network queue into playback queues
        while not self.raw_queue.empty():
            try:
                payload = self.raw_queue.get_nowait()
                for i in range(8):
                    key = f'Ch{i}'
                    if key in payload:
                        raw_data = payload[key]
                        values = raw_data if isinstance(raw_data, list) else [raw_data]

                        for val in values:
                            # Convert raw value to voltage
                            volts = val * LSB_TO_VOLTS
                            self.playback_queues[i].put(volts)
            except queue.Empty:
                break

        # 2. Smooth playback: ~8 samples per frame
        samples_per_tick = 8
        rendered = False

        for i in range(8):
            count = 0
            # Pull samples only if a small buffer exists to avoid stuttering
            while self.playback_queues[i].qsize() > 2 and count < samples_per_tick:
                volts = self.playback_queues[i].get_nowait()
                self.buffers[i].append(volts)
                count += 1

            if count > 0:
                rendered = True

        # 3. Plot and remove DC Offset (center at 0)
        if rendered:
            for i in range(8):
                data_array = np.array(self.buffers[i])

                # Subtract mean to center the wave
                if len(data_array) > 0:
                    data_array = data_array - np.mean(data_array)

                self.curves[i].setData(data_array)

    def closeEvent(self, event):
        """Ensure proper thread and socket closure on exit"""
        self.receiver.running = False
        self.receiver.wait()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    pg.setConfigOption('background', 'k')
    pg.setConfigOption('foreground', 'w')
    pg.setConfigOptions(antialias=False)

    window = Dashboard()
    window.show()
    sys.exit(app.exec())
