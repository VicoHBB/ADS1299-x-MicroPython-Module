from utime import sleep_ms


def uint_to_int(unsigned_int, number_of_bits=24):
    """This funciton converts an unsigned integer to a signed integer
       by default it uses 24 bits.

    :unsigned_int: Number to is going to be converted.
    :number_of_bits: Number of bits to be used.
    :returns: Number converted to signed integer.

    """
    # check if the unsigned integer is negative
    if unsigned_int >> (number_of_bits - 1):
        # calculate the two's complement representation of the negative value
        signed_int = -((unsigned_int ^ ((1 << number_of_bits) - 1)) + 1)
    else:
        # unsigned integer is positive, so no need to convert
        signed_int = unsigned_int
    return signed_int


class ADS1299:
    """This class is used to control the ADS1299,
       the parame that need is the spi channel and
       chip select pin.
    """
    """
    Commands definitions
    """
    # Commands
    WAKEUP = 0x02
    STANDBY = 0x04
    RESET = 0x06
    START = 0x08
    STOP = 0x0A
    # Data Read Commands
    RDATAC = 0x10
    SDATAC = 0x11
    RDATA = 0x12
    # Register Read Commands -- n nnnn = number of registers to be read or
    # written – 1. For example, to read or write three registers,
    # set n nnnn = 0 (0010). r rrrr = starting register address for
    # read or write commands.
    RREG = 0x01 << 5
    WREG = 0x01 << 6
    """"""
    """
    Register maps
    """
    # Read Only ID Registers
    ID = 0x00
    # Global Settings Across Channels
    CONFIG1 = 0x01
    CONFIG2 = 0x02
    CONFIG3 = 0x03
    LOFF = 0x04
    # Channel-Specific Settings
    CH1SET = 0x05
    CH2SET = 0x06
    CH3SET = 0x07
    CH4SET = 0x08
    CH5SET = 0x09
    CH6SET = 0x0A
    CH7SET = 0x0B
    CH8SET = 0x0C
    BIAS_SENSP = 0x0D
    BIAS_SENSN = 0x0E
    LOFF_SENSP = 0x0F
    LOFF_SENSN = 0x10
    LOFF_FLIP = 0x11
    # Lead-Off Status Registers (Read-Only Registers)
    LOFF_STATP = 0x12
    LOFF_STATN = 0x13
    # GPIO and OTHER Registers
    GPIO = 0x14
    MISC1 = 0x15
    MISC2 = 0x16
    CONFIG4 = 0x17
    """"""

    def __init__(self, cs, spi_channel):
        self.cs = cs
        self.spi_channel = spi_channel

    def init(self, config1=0x96, config2=0xC0, config3=0xE0):
        """This method initializes the ADS1299, with 250 S/s, use internal
           reference and do not use the internal signal for testing. For change
           this configuration please check 9.6 Register Maps section of the
           datasheet.

        :config1: This register configures the DAISY_EN bit, clock, and data
                  rate.
        :config2: This register configures the test signal generation. See the
                  Input Multiplexer section for more details.
        :config3: Configuration register 3 configures either an internal or
                  exteral reference and BIAS operation.
        :returns: None

        """
        self.cs.on()
        self.send_command(ADS1299.SDATAC)
        self.send_command(ADS1299.SDATAC)
        self.send_command(ADS1299.STOP)
        # Set internal reference
        self.write_register(ADS1299.CONFIG3, 1, config3)
        # Set internal reference
        self.write_register(ADS1299.CONFIG1, 1, config1)
        # Set internal reference
        self.write_register(ADS1299.CONFIG2, 1, config2)
        # Set internal reference
        self.read_all_registers()
        sleep_ms(4)
        pass

    def send_command(self, command):
        """Send a unique command trowgh SPI channel

        :command: Command extractd from the data sheet to control ADS1299
        :returns: None

        """
        # self.spi_channel.write(chr(command))
        self.cs.off()
        self.spi_channel.write(chr(command))
        self.cs.on()
        pass

    def write_register(self, starting_register, number_of_registers,
                       data_to_write):
        """ Write data to a n registers

        :starting_register: Starting register address for read
        :number_of_registers: Number of registers to be read
        :data_to_write: Value of the register that is going to be write
        :returns: None

        code_editor = "alacritty -vvv -e nvim",
        """
        data = [(ADS1299.WREG | starting_register),
                (number_of_registers - 1), data_to_write]
        txdata = bytearray(data)
        rxdata = bytearray(len(txdata))
        self.cs.off()
        self.spi_channel.write_readinto(txdata, rxdata)
        self.cs.on()

        pass

    def read_register(self, starting_register, number_of_registers):
        """ Read date from a n registers, this fucntions send
            RREGr rrrr & 000n nnnn where n is number of registers to be read
            and r the starting register address

        :starting_register: Starting register address for read
        :number_of_registers: Number of registers to be read
        :returns: content of the n registers

        """
        data = [(ADS1299.RREG | starting_register),
                (number_of_registers - 1), 0x00]
        txdata = bytearray(data)
        rxdata = bytearray(len(txdata))
        self.cs.off()
        self.spi_channel.write_readinto(txdata, rxdata)
        self.cs.on()

        return rxdata[2]

    def read_all_registers(self):
        """Read all registers
        :returns: the content of each register

        """
        registers = []

        for i in range(22):
            registers.append(self.read_register(i, 1))

        return registers

    def config_channels(self, channels, gain, srb2, muxr):
        """Assuming all channels will be used, this method
           enables all channels, configuring gain, SRB2
           connection, and multiplexing.

        :channels: Number of channels to be used, starting from 0 to 7 (n+1)
        :gain: Gain value(None, 1, 2, 4, 6, 8 ,12, 24)
        :srb2: 0 SERB2 connection open, 1 closed
        :muxr: These bits determine the channel input selection
               (See the data sheet to know more)
        :returns: None

        """
        # Enable channels
        pdn_bits = []
        for i in range(8):
            if (i <= channels):
                pdn_bits.append(0)
            else:
                pdn_bits.append(1)

        # Set gain
        if gain == 1:
            pgain = 0b000
        elif gain == 2:
            pgain = 0b001
        elif gain == 4:
            pgain = 0b010
        elif gain == 6:
            pgain = 0b011
        elif gain == 8:
            pgain = 0b100
        elif gain == 12:
            pgain = 0b101
        elif gain == 24:
            pgain = 0b110
        else:
            pgain = 0b111

        settings_bits = (pgain << 4) | (srb2 << 3) | muxr

        for i in range(8):
            self.write_register(
                (0x05 + i), 1, ((pdn_bits[i] << 7) | settings_bits))

        pass

    def read_channels_once(self):
        """This method reads the data from all channels only one time,
        that includes 3 bytes from status
        :returns: A list of the data read from each channel

        """

        data = []
        channels = []

        data.append(ADS1299.RDATA)
        for i in range(27):
            data.append(0)

        txdata = bytearray(data)
        rxdata = bytearray(len(txdata))

        self.cs.off()
        self.spi_channel.write_readinto(txdata, rxdata)
        self.cs.on()

        for i in range(9):
            channels.append(uint_to_int(int.from_bytes(
                rxdata[(i * 3): ((i*3) + 3)], 'big'), 24))

        return channels[1:9]

    def enable_read_continuous(self):
        """ This method enables continuous reading of the data.
        :returns: None

        """
        self.send_command(ADS1299.START)
        self.send_command(ADS1299.RDATAC)
        # This delay is calculated from the datasheet correponding to
        # 4 t CLK cycles
        sleep_ms(16)

        pass

    def read_channels_continuous(self):
        """This method continuously reads the data from all
        channels without sending a command.
        :returns: A list of the data read from each channel
        in continuous mode.

        """
        data_rx = bytearray(27)
        channels = []

        self.cs.off()
        self.spi_channel.readinto(data_rx, 0x00)
        self.cs.on()

        for i in range(9):
            channels.append(uint_to_int(int.from_bytes(
                data_rx[(i*3):((i*3)+3)], 'big'), 24))

        return channels[1:9]

    def disable_read_continuous(self):
        """Disable continuous reading of the data.
        :returns: None

        """
        self.send_command(ADS1299.SDATAC)
        self.send_command(ADS1299.STOP)
        pass
