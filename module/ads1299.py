from utime import sleep_ms, sleep_us


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
    """ This class is used to control the ADS1299, the parame that need is the
    spi channel and chip select pin.

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
    """
    CNFIG1 SAMPLE RATE
    """
    SAMPLE_RATE_16K = 0b000
    SAMPLE_RATE_8K = 0b001
    SAMPLE_RATE_4K = 0b010
    SAMPLE_RATE_2K = 0b011
    SAMPLE_RATE_1K = 0b100
    SAMPLE_RATE_500 = 0b101
    SAMPLE_RATE_250 = 0b110
    """"""
    """
    CNFIG2 PARAMETERS Signal frequency

    """
    PULSED_1 = 0x00
    PULSED_2 = 0x01
    NOT_USE = 0x10
    DC = 0x11
    """"""
    """
    LOFF Values
    """
    # Lead-off comparator threshold
    COMP_95P_5N = 0b000
    COMP_92_5P_7_5N = 0b001
    COMP_90P_10N = 0b010
    COMP_87_5P_12_5N = 0b011
    COMP_85P_15N = 0b100
    COMP_80N_20N = 0b101
    COMP_75P_25N = 0b110
    COMP_70P_30N = 0b111
    # Lead-off current magnitude
    I_6NA = 0b00
    I_24NA = 0b01
    I_6UA = 0b10
    I_24UA = 0b11
    # Lead-off frequency
    DC_LOFF = 0b00
    AC_LOFF_7_8HZ = 0b01
    AC_LOFF_31_2HZ = 0b10
    AC_LOFF_FDR_BY_4 = 0b11
    """"""
    """
    CHnSET PARAMETERS
    """
    # Gain Values
    GAIN_1 = 0b000
    GAIN_2 = 0b001
    GAIN_4 = 0b010
    GAIN_6 = 0b011
    GAIN_8 = 0b100
    GAIN_12 = 0b101
    GAIN_24 = 0b110
    NO_GAIN = 0b111
    # MUXr Values
    NORMAL = 0b000  # Normal electrode input.
    SHORTED = 0b001  # Input shorted (for offset or noise measurement).
    BIAS_MEAS = 0b010  # Used in conjunction with BIAS_MEAS bit for BIAS meas.
    MVDD = 0b011  # MVDD for supply measurement.
    TEMP = 0b100  # Temperature sensor.
    TEST = 0b101  # Test signal.
    BIAS_DRP = 0b110  # Positive electrode is the driver
    BIAS_DRN = 0b111  # Negative electrode is the driver
    """"""

    def __init__(self, cs, spi_channel):
        self.cs = cs
        self.spi_channel = spi_channel

    def init(self, config1=0x96, config2=0xC0, config3=0x60):
        """ This method initializes the ADS1299, with 250 S/s, use internal
        reference and do not use the internal signal for testing. For change
        this configuration please check 9.6 Register Maps section of the
        datasheet.

        :config1: This register configures the DAISY_EN bit, clock, and data
                  rate. By default it is 0x96, as indicated in the datasheet.
        :config2: This register configures the test signal generation. See the
                  Input Multiplexer section for more details. By default it is
                  0xC0, as indicated in the datasheet.
        :config3: Configuration register 3 configures either an internal or
                  exteral reference and BIAS operation. By default it is 0x60.
        :returns: None

        """
        self.cs.on()
        self.send_command(ADS1299.RESET)
        self.send_command(ADS1299.SDATAC)
        self.send_command(ADS1299.SDATAC)
        self.send_command(ADS1299.STOP)
        # Set reference
        self.write_reg(ADS1299.CONFIG3, config3)
        # Set other cofing registers, sample rate & test signals
        self.write_registers(ADS1299.CONFIG1, [config1, config2])
        sleep_ms(4)
        pass

    def send_command(self, command):
        """ Send a unique command trowgh SPI channel.

        :command: Command extractd from the data sheet to control ADS1299.
        :returns: None

        """
        self.cs.off()
        self.spi_channel.write(chr(command))
        self.cs.on()
        pass

    def write_reg(self, register, data_to_write):
        """ This method write data to a single register.

        :register: Register to be written.
        :data_to_write: Value of the register that is going to be write.
        :returns: None

        """
        data = [(ADS1299.WREG | register), 0, data_to_write]
        txdata = bytearray(data)
        rxdata = bytearray(len(txdata))
        self.cs.off()
        self.spi_channel.write_readinto(txdata, rxdata)
        self.cs.on()

        pass

    def write_registers(self, starting_register, data_to_write=[]):
        """ This method write data to multiple registers one by one.

        :starting_register: Register to be reading from.
        :data_to_write: A list that contains the data to be written.
        :returns: None

        """
        for i in data_to_write:
            self.write_reg(starting_register, i)
            starting_register += 1
            sleep_us(1)    # Wait a little for the data to be written.

        pass

    def read_reg(self, register):
        """ This method read a single register.

        :register: Register to be read.
        :returns: Content of the n registers.

        """
        data = [(ADS1299.RREG | register), 0, 0x00]
        txdata = bytearray(data)
        rxdata = bytearray(len(txdata))
        self.cs.off()
        self.spi_channel.write_readinto(txdata, rxdata)
        self.cs.on()

        return rxdata[2]

    def read_registers(self, starting_register, number_of_registers):
        """ This method read data from multiple registers one by one.

        :starting_register: Register to be reading from.
        :number_of_registers: Number of registers to be read.
        :returns: A list with the value of each register.

        """
        registers_list = []
        for i in range(number_of_registers):
            registers_list.append(self.read_reg(starting_register+i))

        return registers_list

    def read_all_registers(self):
        """ This method read all the register values from the starting of the
        ADS1299

        :returns: A list with the value of all registers of ADS1299.

        """

        registers_list = self.read_registers(0, 24)

        return registers_list

    def config_all_channels(self, channels_active=8, gain=GAIN_24,
                            srb2_connection=False,
                            channel_input=SHORTED):
        """ Assuming all channels will be seted, this method enables all
        channels, configuring gain, SRB2 connection, and multiplexing.

        :channels: Number of channels to be used, you can set 1 to 8 if you set
                   0, all will be disabled.
        :gain: This determine the PGA gain setting could be:
            GAIN_1  -> 1
            GAIN_2  -> 2
            GAIN_4  -> 4
            GAIN_8  -> 8
            GAIN_12 -> 12
            GAIN_24 -> 24
            NO_GAIN -> Do not use
        :srb2_connection: This bit defines the SRB2 connection selection
              channels. Can be OPEN or CLOSED.
        :channel_input: These bits determine the channel input selection
                        NORMAL  -> Normal electrode input.
                        SHORTED -> Input shorted (for offset or noise
                                  measurement).
                        BIAS_MEAS -> Used in conjunction with BIAS_MEAS bit for
                                    BIAS measurement.
                        MVDD      -> MVDD for supply measurement.
                        TEMP      -> Temperature sensor.
                        TEST      -> Test signal.
                        BIAS_DRP  -> Positive electrode is the driver.
                        BIAS_DRN  -> Negative electrode is the driver.
        :returns: None

        """

        chnset = (0 << 7) \
            | (gain << 4) \
            | (srb2_connection << 3) \
            | channel_input

        self.write_registers(ADS1299.CH1SET, [chnset] * channels_active)

        self.write_registers(ADS1299.CH1SET + channels_active,
                             [(0x01 << 7)] * (8 - channels_active))

        pass

    def read_channels_once(self):
        """ This method reads the data from all channels only one time

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
        """ This method continuously reads the data from all
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
        """ Disable continuous reading of the data.
        :returns: None

        """
        self.send_command(ADS1299.SDATAC)
        self.send_command(ADS1299.STOP)
        pass


def make_config1(daisy_en=False, clock_en=False,
                 data_rate=ADS1299.SAMPLE_RATE_250):
    """ This register configures the DAISY_EN bit, clock, and data rate.

    This function creates the value to be written in the CONFIG1 register of
    the ADS1299, it only generates the value, this must be assigned in the
    init() method of the ADS1299 class. By default the register value is 0x96,
    as indicated in the datasheet.

    :daisy_en: Daisy-chain or multiple readback mode, False is
               Daisy-chain mode, True is multiple readback mode.
    :clock_en: Osilator clock output, could be Fase(disable), or True(enable).
    :data_rate: Output data rate of the device(SPS) are defined inside the
                ADS1299 class as constants and this could be:
                    SAMPLE_RATE_16k -> 16KSPS
                    SAMPLE_RATE_8K  -> 8KSPS
                    SAMPLE_RATE_4K  -> 4KSPS
                    SAMPLE_RATE_2K  -> 2KSPS
                    SAMPLE_RATE_1K  -> 1KSPS
                    SAMPLE_RATE_500 -> 500SPS
                    SAMPLE_RATE_250 -> 250SPS
    :returns: The value that is going to be written in the CONFIG1.

    """

    return (0x1 << 7) \
        | (daisy_en << 6) \
        | (clock_en << 5) \
        | (0x2 << 3) \
        | data_rate


def make_config2(self, test_source=False, signal_amp=1,
                 signal_freq=ADS1299.PULSED_1):
    """ This register configures the test signal generation. See the Input
    Multiplexer section of datasheet for more details.

    This function creates the value to be written in the CONFIG2 register of
    the ADS1299, it only generates the value, this must be assigned in the
    init() method of the ADS1299 class. By default the register value is 0xC0,
    as indicated in the datasheet.

    :test_source: This determines the source of the test signal. Could be
                  False(external), or True(Internal).
    :signal_amp: This determines the calibration of signal amplitude. Could
                 be:
                     1 -> 1 * – (VREFP – VREFN) / 2400
                     2 -> 2 * - (VREFP – VREFN) / 2400
    :signal_freq: These determines the calibration of signal frequency. this
                  values are defined inside the ADS1299 class as constants
                  and could be:
                  Could be:
                      PULSED_1 -> Pulsed at f_clk / 2**21
                      PULSED_2 -> Pulsed at f_clk / 2**20
                      NOT_USE  -> Do not used
                      DC       -> At DC
    :returns: The value that is going to be written in the CONFIG2.

    """

    return (0x06 << 5) \
        | (test_source << 4) \
        | (0x00 << 3) \
        | ((signal_amp - 1) << 2) \
        | signal_freq


def make_config3(pwr_down_refbuf=False, bias_meas=False, biasref_signal=False,
                 bias_buf_pwr=False, bias_sense_func=False,
                 bias_lead_off_status=False):
    """ Configuration register 3 configures either an internal or exteral
    reference and BIAS operation.

    This function creates the value to be written in the CONFIG3 register of
    ADS1299, it only generates the value, this must be assigned in the init()
    method of the ADS1299 class. By default the register value is 0x96, as
    indicated in the datasheet.

    :pwr_down_refbuf: This determines the power-down reference buffer state.
                      Could be:
                          False -> Power-down internal reference buffer.
                          True  -> Enable internal reference buffer.
    :bias_meas: This enables BIAS measurement. The BIAS signal may be
                measured with any channel. Could be:
                    False -> Open.
                    True  -> BIAS_IN signal is routed to the channel that
                              has the MUX_Setting 010(V_ref).
    :biasref_signal: This determines the BIASREF signal source. Could be:
        False -> BIASREF signal fed externally.
        True  -> BIASREF signal (AVDD + AVSS) / 2 generated internally.
    :bias_buf_pwr: This determines the BIAS buffer power state. Could be:
        False -> BIAS buffer is powered down.
        True  -> BIAS buffer is enabled.
    :bias_sense_func: This enables the bias sense function. Could be:
        False -> BIAS sense is disabled.
        True  -> BIAS sense is enabled.
    :bias_lead_off_status: This determiens the BIAS status. Could be:
        False    -> BIAS is connected.
        True -> BIAS is not connected.
    :returns: The value that is going to be written in the CONFIG3

    """

    return (pwr_down_refbuf << 7) \
        | (0x03 << 5) \
        | (bias_meas << 4) \
        | (biasref_signal << 3) \
        | (bias_buf_pwr << 2) \
        | (bias_sense_func << 1) \
        | bias_lead_off_status


def make_loff(comp_th=ADS1299.COMP_95P_5N, ilead_off=ADS1299.I_6NA,
              flead_off=ADS1299.DC_LOFF):
    """ The lead-off control register configures the lead-off detection
    operation.

    This function creates the value to be written in the LOFF register of
    ADS1299, it only generates the value, this must be assigned using
    wirte_reg() method of the ADS1299 class. By default the register value is
    0x00, as indicated in the datasheet.

    :comp_th: Lead-off comparator threshold, that means the value of the
              comparator in positive side and negative side, this values
              are defined inside the ADS1299 class as constants and could be:
                  COMP_95P_5N      -> Positive side 95%, Negative side 5%.
                  COMP_92_5P_7_5N  -> Positive side 92.5%, Negative side 7.5%.
                  COMP_90P_10N     -> Positive side 90%, Negative side 10%.
                  COMP_87_5P_12_5N -> Positive side 87.5%, Negative side 12.5%.
                  COMP_85P_15N     -> Positive side 85%, Negative side 15%.
                  COMP_80N_20N     -> Positive side 80%, Negative side 20%.
                  COMP_75P_25N     -> Positive side 75%, Negative side 25%.
                  COMP_70P_30N     -> Positive side 70%, Negative side 30%.
    :ilead_off: Lead-off current magnitude, These bits determine the
                magnitude of current for the current, this values are defined
                inside the ADS1299 class as constants and could be:
                    I_6NA  -> Set 6nA.
                    I_24NA -> Set 24nA.
                    I_6UA  -> Set 6uA.
                    I_24UA -> Set 24uA.
    :flead_off: Lead-off frequency, These bits determine the frequency of
                lead-off detect for each channel. this values are defined
                inside the ADS1299 class as constants and could be:
                    DC_LOFF          -> DC lead-off detection.
                    AC_LOFF_7_8HZ    -> AC lead-off detection at 7.8Hz.
                    AC_LOFF_31_2HZ   -> AC lead-off detection at 31.2Hz.
                    AC_LOFF_FDR_BY_4 -> AC lead-off detection at F_DR / 4.
    :returns: The value that is going to be written in the LOFF register.

    """

    return (comp_th << 5) \
        | (ilead_off << 2) \
        | (flead_off)


def make_chnset(power_down=False, gain=ADS1299.GAIN_24, srb2_connection=False,
                channel_input=ADS1299.SHORTED):
    """ The CH[1:8]SET control register configures the power mode, PGA gain,
    and multiplexer settings channels. See the Input Multiplexer section for
    details of datasheet. CH[2:8]SET are similar to CH1SET, corresponding to
    the respective channels.

    This function creates the value to be written in the CHnSET register of
    ADS1299, it only generates the value, this must be assigned, this must be
    assigned using wirte_reg() method of the ADS1299 class.
    By default the register value is 0x61, as indicated in the datasheet.

    :power_down: This bit determines the channel power mode for the
                 corresponding channel. This could be False(Normal operation)
                 or True(Power down).
                 When powering down a channel, TI recommends that the
                 channel be set to input short by setting the appropriate
                 MUXn[2:0] = 001(SHORTED) of the CHnSET register.
    :gain: This determine the PGA gain setting could be:
        GAIN_1  -> 1
        GAIN_2  -> 2
        GAIN_4  -> 4
        GAIN_8  -> 8
        GAIN_12 -> 12
        GAIN_24 -> 24
        NO_GAIN -> Do not use
    :srb2_connection: This bit defines the SRB2 connection selection
          channels. Can be OPEN or CLOSED.
    :channel_input: These bits determine the channel input selection
                    NORMAL  -> Normal electrode input.
                    SHORTED -> Input shorted (for offset or noise
                              measurement).
                    BIAS_MEAS -> Used in conjunction with BIAS_MEAS bit for
                                BIAS measurement.
                    MVDD      -> MVDD for supply measurement.
                    TEMP      -> Temperature sensor.
                    TEST      -> Test signal.
                    BIAS_DRP  -> Positive electrode is the driver.
                    BIAS_DRN  -> Negative electrode is the driver.
    :returns: The value that is going to be written in the CHnSET register

    """

    return ((power_down) << 7) \
        | (gain << 4) \
        | (srb2_connection << 3) \
        | channel_input


def make_bias_sensp(biasp8_bit=False, biasp7_bit=False, biasp6_bit=False,
                    biasp5_bit=False, biasp4_bit=False, biasp3_bit=False,
                    biasp2_bit=False, biasp1_bit=False):
    """ This register controls the selection of the positive signals from each
    channel for bias voltage (BIAS) derivation. See the Bias Drive
    (DC Bias Circuit) section of datasheet for details.

    This function creates the value to be written in the BIAS_SENSP register
    of ADS1299, it only generates the value, this must be assigned using
    wirte_reg() method of the ADS1299 class.
    By default the register value is 0x00, as indicated in the datasheet.

    For this function False is Disabled and True is Enabled.
    :biasp8_bit: Route channel 8 positive signal into BIAS derivation
    :biasp7_bit: Route channel 7 positive signal into BIAS derivation
    :biasp6_bit: Route channel 6 positive signal into BIAS derivation
    :biasp5_bit: Route channel 5 positive signal into BIAS derivation
    :biasp4_bit: Route channel 4 positive signal into BIAS derivation
    :biasp3_bit: Route channel 3 positive signal into BIAS derivation
    :biasp2_bit: Route channel 2 positive signal into BIAS derivation
    :biasp1_bit: Route channel 1 positive signal into BIAS derivation
    :returns: The value that is going to be written in the BIAS_SENSP register

    """

    return (biasp8_bit << 7) \
        | (biasp7_bit << 6) \
        | (biasp6_bit << 5) \
        | (biasp5_bit << 4) \
        | (biasp4_bit << 3) \
        | (biasp3_bit << 2) \
        | (biasp2_bit << 1) \
        | (biasp1_bit << 0)


def make_bias_sensn(biasn8_bit=False, biasn7_bit=False, biasn6_bit=False,
                    biasn5_bit=False, biasn4_bit=False, biasn3_bit=False,
                    biasn2_bit=False, biasn1_bit=False):
    """ This register controls the selection of the negative signals from each
    channel for bias voltage (BIAS) derivation. See the Bias Drive
    (DC Bias Circuit) section of datasheet for details.

    This function creates the value to be written in the BIAS_SENSN register
    of ADS1299, it only generates the value, this must be assigned using
    wirte_reg() method of the ADS1299 class.
    By default the register value is 0x00, as indicated in the datasheet.

    For this function False is Disabled and True is Enabled.
    :biasn8_bit: Route channel 8 negative signal into BIAS derivation
    :biasn7_bit: Route channel 7 negative signal into BIAS derivation
    :biasn6_bit: Route channel 6 negative signal into BIAS derivation
    :biasn5_bit: Route channel 5 negative signal into BIAS derivation
    :biasn4_bit: Route channel 4 negative signal into BIAS derivation
    :biasn3_bit: Route channel 3 negative signal into BIAS derivation
    :biasn2_bit: Route channel 2 negative signal into BIAS derivation
    :biasn1_bit: Route channel 1 negative signal into BIAS derivation
    :returns: The value that is going to be written in the BIAS_SENSN register

    """

    return (biasn8_bit << 7) \
        | (biasn7_bit << 6) \
        | (biasn6_bit << 5) \
        | (biasn5_bit << 4) \
        | (biasn4_bit << 3) \
        | (biasn3_bit << 2) \
        | (biasn2_bit << 1) \
        | (biasn1_bit << 0)


def make_loff_sensp(loffp8_bit=False, loffp7_bit=False, loffp6_bit=False,
                    loffp5_bit=False, loffp4_bit=False, loffp3_bit=False,
                    loffp2_bit=False, loffp1_bit=False):
    """ This register selects the positive side from each channel for lead-off
    detection. See the Lead-Off Detection section for details. The LOFF_STATP
    register bits are only valid if the corresponding LOFF_SENSP bits are set
    to 1.

    This function creates the value to be written in the LOFF_SENSP register
    of ADS1299, it only generates the value, this must be assigned using
    wirte_reg() method of the ADS1299 class.
    By default the register value is 0x00, as indicated in the datasheet.

    For this function False is Disabled and True is Enabled.
    :loffp8_bit: Enable lead-off detection on IN8P
    :loffp7_bit: Enable lead-off detection on IN7P
    :loffp6_bit: Enable lead-off detection on IN6P
    :loffp5_bit: Enable lead-off detection on IN5P
    :loffp4_bit: Enable lead-off detection on IN4P
    :loffp3_bit: Enable lead-off detection on IN3P
    :loffp2_bit: Enable lead-off detection on IN2P
    :loffp1_bit: Enable lead-off detection on IN1P
    :returns: The value that is going to be written in the LOFF_SENSP register

    """

    return (loffp8_bit << 7) \
        | (loffp7_bit << 6) \
        | (loffp6_bit << 5) \
        | (loffp5_bit << 4) \
        | (loffp4_bit << 3) \
        | (loffp3_bit << 2) \
        | (loffp2_bit << 1) \
        | (loffp1_bit << 0)


def make_loff_sensn(loffn8_bit=False, loffn7_bit=False, loffn6_bit=False,
                    loffn5_bit=False, loffn4_bit=False, loffn3_bit=False,
                    loffn2_bit=False, loffn1_bit=False):
    """ This register selects the negative side from each channel for lead-off
    detection. See the Lead-Off Detection section for details. The LOFF_STATN
    register bits are only valid if the corresponding LOFF_SENSN bits are set
    to 1.

    This function creates the value to be written in the LOFF_SENSN register
    of ADS1299, it only generates the value, this must be assigned using
    wirte_reg() method of the ADS1299 class.
    By default the register value is 0x00, as indicated in the datasheet.

    For this function False is Disabled and True is Enabled.
    :loffn8_bit: Enable lead-off detection on IN8N
    :loffn7_bit: Enable lead-off detection on IN7N
    :loffn6_bit: Enable lead-off detection on IN6N
    :loffn5_bit: Enable lead-off detection on IN5N
    :loffn4_bit: Enable lead-off detection on IN4N
    :loffn3_bit: Enable lead-off detection on IN3N
    :loffn2_bit: Enable lead-off detection on IN2N
    :loffn1_bit: Enable lead-off detection on IN1N
    :returns: The value that is going to be written in the LOFF_SENSN register

    """

    return (loffn8_bit << 7) \
        | (loffn7_bit << 6) \
        | (loffn6_bit << 5) \
        | (loffn5_bit << 4) \
        | (loffn4_bit << 3) \
        | (loffn3_bit << 2) \
        | (loffn2_bit << 1) \
        | (loffn1_bit << 0)


def make_loff_flip(loff_flip8_bit=False, loff_flip7_bit=False,
                   loff_flip6_bit=False, loff_flip5_bit=False,
                   loff_flip4_bit=False, loff_flip3_bit=False,
                   loff_flip2_bit=False, loff_flip1_bit=False):
    """ This register controls the direction of the current used for lead-off
    derivation. See the Lead-Off Detection section for details.

    This function creates the value to be written in the LOFF_SENSN register
    of ADS1299, it only generates the value, this must be assigned using
    wirte_reg() method of the ADS1299 class.
    By default the register value is 0x00, as indicated in the datasheet.

    :loff_flip8_bit:
        False -> No flip = IN8P is pulled to AVDD and IN8N pulled to AVSS
        True  -> Flipped = IN8P is pulled to AVSS and IN8N pulled to AVDD
    :loff_flip7_bit:
        False -> No flip = IN7P is pulled to AVDD and IN7N pulled to AVSS
        True  -> Flipped = IN7P is pulled to AVSS and IN7N pulled to AVDD
    :loff_flip6_bit:
        False -> No flip = IN6P is pulled to AVDD and IN6N pulled to AVSS
        True  -> Flipped = IN6P is pulled to AVSS and IN6N pulled to AVSS
    :loff_flip5_bit:
        False -> No flip = IN5P is pulled to AVDD and IN5N pulled to AVSS
        True  -> Flipped = IN5P is pulled to AVSS and IN5N pulled to AVSS
    :loff_flip4_bit:
        False -> No flip = IN4P is pulled to AVDD and IN4N pulled to AVSS
        True  -> Flipped = IN4P is pulled to AVSS and IN4N pulled to AVSS
    :loff_flip3_bit:
        False -> No flip = IN3P is pulled to AVDD and IN3N pulled to AVSS
        True  -> Flipped = IN3P is pulled to AVSS and IN3N pulled to AVSS
    :loff_flip2_bit:
        False -> No flip = IN2P is pulled to AVDD and IN2N pulled to AVSS
        True  -> Flipped = IN2P is pulled to AVSS and IN2N pulled to AVSS
    :loff_flip1_bit:
        False -> No flip = IN1P is pulled to AVDD and IN1N pulled to AVSS
        True  -> Flipped = IN1P is pulled to AVSS and IN1N pulled to AVSS
    :returns: The value that is going to be written in the LOFF_SENSN register

    """

    return (loff_flip8_bit << 7) \
        | (loff_flip7_bit << 6) \
        | (loff_flip6_bit << 5) \
        | (loff_flip5_bit << 4) \
        | (loff_flip4_bit << 3) \
        | (loff_flip3_bit << 2) \
        | (loff_flip2_bit << 1) \
        | (loff_flip1_bit << 0)


def make_gpio(gpio3=True, gpio2=True, gpio1=True, gpio0=True):
    """ The general-purpose I/O register controls the action of the three GPIO
    pins. When RESP_CTRL[1:0] is in mode 01 and 11, the GPIO2, GPIO3, and GPIO4
    pins are not available for use.

    The bits [7:4] are GPIO data; These bits are used to read and write data to
    the GPIO ports. When reading the register, the data returned correspond to
    the state of the GPIO external pins, whether they are programmed as inputs
    or as outputs. As outputs, a write to the GPIOD sets the output value. As
    inputs, a write to the GPIOD has no effect. GPIO is not available in
    certain respiration modes.

    The bits [3:0] are GPIO control(corresponding GPIOD), These bits determine
    if the corresponding GPIOD pin is an input or output.

    This function creates the value to be written in the GPIO register
    of ADS1299, it only generates the value, this must be assigned using
    wirte_reg() method of the ADS1299 class.
    By default the register value is 0x0F, as indicated in the datasheet.

    :gpio3: Set False for use as Output or True for use as Input.
    :gpio2: Set False for use as Output or True for use as Input.
    :gpio1: Set False for use as Output or True for use as Input.
    :gpio0: Set False for use as Output or True for use as Input.
    :returns: The value that is going to be written in the GPIO register.

    """

    return (gpio3 << 3) | (gpio2 << 2) | (gpio1 << 1) | (gpio0)


def make_misc1(srb1=False):
    """ This register provides the control to route the SRB1 pin to all
    inverting inputs of the four, six, or eight channels (ADS1299-4,
    ADS1299-6, or ADS1299).

    This function creates the value to be written in the MISC1 register of
    ADS1299, it only generates the value, this must be assigned using
    write_reg() method of the ADS1299 class.
    By default the register value is 0x00, as indicated in the datasheet.

    :srb1: This bit connects the SRB1 to all 4, 6, or 8 channels inverting
    inputs is set False switches open if True switches closed.
    :returns: The value that is going to be written in the MISC1 register.

    """

    return (srb1 << 5)


def make_config4(single_shot=False, pd_loff_comp=False):
    """ This register configures the conversion mode and enables the lead-off
    comparators.

    This function creates the value to be written in the CONFIG4 register of
    ADS1299, it only generates the value, this must be assigned using
    write_reg() method of the ADS1299 class.
    By default the register value is 0x00, as indicated in the datasheet.

    :single_shot: This bit sets the conversion mode if set False will be
    continuous conversion mode if set True will be single shot conversion mode.
    :pd_loff_comp: This bit powers down the lead-off comparators, if set False
    Lead-off comparators will be disabled or if set True Lead-off comparators
    will be enabled.
    :returns: The value that is going to be written in the CONFIG4 register.

    """

    return (single_shot << 3) | (pd_loff_comp << 1)
