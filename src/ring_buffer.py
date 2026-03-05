# #! /bin/MicroPython
import array


class RingBuffer:
    """This class provides a circular buffer implementation optimized for
    MicroPython using array.array to minimize memory fragmentation and
    allocation during high-speed data acquisition.
    """

    def __init__(self, size: int, typecode: str = 'i'):
        """Initialize the queue with a fixed size and data type.

        :size: Maximum number of elements the queue can hold.
        :typecode: Type of the elements in the array (e.g., 'i' for signed int, 'f' for float).
        :returns: None

        """
        # We add 1 to size to distinguish between full and empty states
        self._max_size = size + 1
        self._buffer = array.array(typecode, [0] * self._max_size)
        self._head = 0
        self._tail = 0

    def init(self) -> None:
        """Resets the queue pointers to empty the buffer without reallocating memory.

        :returns: None

        """
        self._head = 0
        self._tail = 0

    def is_empty(self) -> bool:
        """Checks if the buffer contains no data.

        :returns: True if empty, False otherwise.

        """
        return self._head == self._tail

    def is_full(self) -> bool:
        """Checks if the buffer has reached its maximum capacity.

        :returns: True if full, False otherwise.

        """
        return ((self._head + 1) % self._max_size) == self._tail

    def write(self, item: int) -> bool:
        """Push a single item into the circular buffer.

        :item: Value to be stored in the buffer.
        :returns: True if successful, False if the buffer is full.

        """
        next_head = (self._head + 1) % self._max_size

        if next_head == self._tail:
            return False

        self._buffer[self._head] = item
        self._head = next_head
        return True

    def read(self) -> int | None:
        """Pop and return the oldest item from the buffer (FIFO).

        :returns: The stored value or None if the buffer is empty.

        """
        if self._head == self._tail:
            return None

        item = self._buffer[self._tail]
        self._tail = (self._tail + 1) % self._max_size
        return item
