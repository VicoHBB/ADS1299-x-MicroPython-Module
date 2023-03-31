# ADS1999-MicroPython-Module

<!--toc:start-->
- [ToDo](#todo)
- [References](#references)
<!--toc:end-->

This is a small Micropython module for configuring and using the Texas Instruments ADS1299 8-channel, 24-bit, low-noise analog-to-digital converter for biopotential measurements. This module has been developed with an ESP32 board as a master device.

This module is under development, so some functions will be added soon.

# ToDo
- Modify the start up method `inti()` to configure data rate
- Implement the function of writing multiple records in one command 
- Complete the documentation

# References
- [MicroPython ESP32](https://micropython.org/download/esp32/)
- [MicroPython documentation](https://docs.micropython.org/en/latest/)
- [Getting started with MicroPython on the ESP32](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html?highlight=esp32)
- [ADS1299 TI](https://www.ti.com/product/ADS1299?ds_k=ADS1299&DCM=yes)
- [ADS1299-x Datasheet](https://www.ti.com/lit/ds/symlink/ads1299.pdf?ts=1680289538117&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FADS1299%253Futm_source%253Dgoogle%2526utm_medium%253Dcpc%2526utm_campaign%253Dasc-null-null-GPN_EN-cpc-pf-google-wwe%2526utm_content%253DADS1299%2526ds_k%253DADS1299%2526DCM%253Dyes%2526gclsrc%253Dds%2526gclsrc%253Dds)
- [EEG Front-End Performance Demonstration Kit](https://www.ti.com/lit/ug/slau443b/slau443b.pdf?ts=1680289719540&ref_url=https%253A%252F%252Fwww.google.com%252F)
