# pico-lte-message-printer

## Summary

Using the cellular connectivity of the Sixfab daughterboard, reach out and grab a string from a given endpoint, then print it via the attached thermal printer.

## Hardware

 - Raspberry Pi Pico W + Sixfab LTE
   - [Product Page](https://sixfab.com/product/sixfab-pico-lte/)
   - [SDK Docs](https://docs.sixfab.com/docs/sixfab-pico-lte-introduction)
   - [SDK](https://github.com/sixfab/pico_lte_micropython-sdk)
 - Thermal Printer (CSN-A2)
   - [Product Page (Discontinued)](https://www.adafruit.com/product/597)
   - [Random Implementation Example](https://github.com/onlyskin/thermal-printer)

## Notes

**Use the `dev` branch of the Sixfab SDK**. It [has changes](https://github.com/sixfab/pico_lte_micropython-sdk/commit/b8b6b4d34f5cc4817c25f16f6f17bb15f7e1cbe0) to the modem buffer so that a (somewhat) decent amount of data can be received from a web request.
