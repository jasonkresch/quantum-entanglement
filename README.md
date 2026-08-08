# At Home Quantum Entanglement Demo

This repository features documentation, code, and instructions to perform an at-home demonstration of [quantum entanglement](https://en.wikipedia.org/wiki/Quantum_entanglement). It works by detecting statistical anti-correlations in the [Compton scattering](https://en.wikipedia.org/wiki/Compton_scattering) of high-energy entangled photons produced fro an electron positron matter-antimatter [annihilation](https://en.wikipedia.org/wiki/Annihilation) event.

This experimental design is based on an experiment performed and described by [George Musser](https://en.wikipedia.org/wiki/George_Musser) on his [blog](https://www.criticalopalescence.com/p/how-to-build-your-own-quantum-entanglement-experiment-part-1-of-2) and as featured in a 2013 [article](https://www.scientificamerican.com/blog/critical-opalescence/how-to-build-your-own-quantum-entanglement-experiment-part-1-of-2/) in [Scientific American](https://www.scientificamerican.com/).

This experiment has been updated to take advantage of more recent tools and technology:
* It uses two [MightyOhm](https://mightyohm.com/blog/) [Geiger Counter Kit](https://mightyohm.com/blog/products/geiger-counter/) which enable easy wiring to an [Arduino](https://www.arduino.cc/) microcontroller.
* It uses an Arduino-based ESP32 with headers, which enables easy wiring to the Geiger counters for coincident detection, as well as data logging by connecting to a computer over USB.
* It uses LEGO-compatible blocks to make the positioning of detectors, the positron source, and aluminum scattering blocks both flexible and repeatable.

## Shopping List

In total, the experiment can be put together for a total cost of around 500 USD.

Link to the shopping list document.

## Programming the Microcontroller

How to install Arduino IDA, setup dependencies, configure for sound, and install code.

## Wiring the Breadboard

Show detailed wiring diagram.

## Recording Data

Describe how to connect a computer to the microcontroller to log data.

## Experimental Configurations

Describe each run, how to get baselines of environmental noise.
How to position each detector for each run.
How to analyze data to demonstrate results.
