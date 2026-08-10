# At Home Quantum Entanglement Demo

This repository features documentation, code, and instructions to perform an at-home demonstration of [quantum entanglement](https://en.wikipedia.org/wiki/Quantum_entanglement). It works by detecting statistical anti-correlations in the [Compton scattering](https://en.wikipedia.org/wiki/Compton_scattering) of high-energy entangled photons produced fro an electron positron matter-antimatter [annihilation](https://en.wikipedia.org/wiki/Annihilation) event.

This experimental design is based on an experiment performed and described by [George Musser](https://en.wikipedia.org/wiki/George_Musser) on his [blog](https://www.criticalopalescence.com/p/how-to-build-your-own-quantum-entanglement-experiment-part-1-of-2) and as featured in a 2013 [article](https://www.scientificamerican.com/blog/critical-opalescence/how-to-build-your-own-quantum-entanglement-experiment-part-1-of-2/) in [Scientific American](https://www.scientificamerican.com/).

This experiment has been updated to take advantage of more recent tools and technology:
* It uses two [MightyOhm](https://mightyohm.com/blog/) [Geiger Counter Kit](https://mightyohm.com/blog/products/geiger-counter/) which enable easy wiring to an [Arduino](https://www.arduino.cc/) microcontroller.
* It uses an Arduino-based ESP32 with headers, which enables easy wiring to the Geiger counters for coincident detection, as well as data logging by connecting to a computer over USB.
* It uses LEGO-compatible blocks to make the positioning of detectors, the positron source, and aluminum scattering blocks both flexible and repeatable.

![Logging Geiger coincidences to a computer](media/computer-logging.jpg)

Above is an image of the assembled kits, both wired into an Arduino, and connected to a computer via USB for logging and analysis. 

## Shopping List

In total, the experiment can be put together for a total cost of around 500 USD (pricing information as of mid 2026).

Here is a link to the [parts list](related-docs/Entanglement-Demo-Shopping-List.pdf).

### Assembling the Geiger Counters

This experiment uses a kit to make each of the two Geiger counters. This requires some soldering. The kits arrive with the following parts:

![MightyOhm Kit Pre-Assembly](media/geiger-kit-pre-assembly.jpg)

After soldering and attaching some screws, the assembled Geiger counters look like this:

![MightyOhm Kit Pre-Assembly](media/geiger-kit-post-assembly.jpg)

The instructions for assembling the Geiger Counter kits can be found at [this link](related-docs/MightyOhm-Geiger-Counter-Assembly-Instructions.pdf).

Conveniently, each Geiger Counter has [pin headers](https://en.wikipedia.org/wiki/Pin_header) which send a 100 microsecond pulse which can be interpreted by an Arduino device with headers. Using a [breadboard](https://en.wikipedia.org/wiki/Breadboard) together with and male-to-female [jumper wires](https://en.wikipedia.org/wiki/Jump_wire), the Geiger counters can be directly wired to the Arduino device without soldering.

### Testing the Geiger Counters

The Geiger counters are sensitive to beta and gamma radiation, and any significant source of these can trigger the counter. The counters will also detect background radiation at a level of around 20 counts per minute at sea level. By arranging the detectors vertically, simultaneous detections will trigger several times a minute due to [cosmic-ray-generated](https://en.wikipedia.org/wiki/Cosmic_ray) [muons](https://en.wikipedia.org/wiki/Muon) passing from the upper atmosphere down to earth and passing through both detectors.

Below is a link to a video demonstrating testing of the two detectors with a 1 μCi test source of Na-22. A source of positrons, such as Na-22, is required in order to perform some of the entangled photon pair experiments detailed later in this document. Check all applicable laws in your area and familiarize yourself with safe practices before obtaining, handling, or disposing of any radioactive sources. 

[![Testing the Geiger Counters with Na-22 Source](https://img.youtube.com/vi/xobj9LGZI20/0.jpg)](https://www.youtube.com/watch?v=xobj9LGZI20)

## Programming the Microcontroller

Before the Arduino device will work as intended for this project, it must be loaded with software. To do this, you must have the Arduino IDE installed.

You may download the Arduino IDE for your operating system from [this link](https://www.arduino.cc/en/software/).

Once it is installed, connect the Arduino device to your computer via a USB-C cable, make sure the cable supports data (sone USB cables are for power only).

Then open the Arduino IDE by opening the micro-controller source code (known as a [sketch](https://en.wikipedia.org/wiki/Arduino#Sketch)) located in the [microcontroller-code](microcontroller-code) directory.

Then select the board from the drop down list at the top of the interface:

![Arduino IDE](media/arduino-ide.png)

### Adding Library Dependencies

Before you can compile the sketch you must add the appropriate library dependencies. To do this, click on the icon that looks like a set of books on the left hand side of the IDE, to make the `Library Manager` appear, then in the search box, search for, and then add, each of the following libraries:

1. Adafruit BusIO
2. Adafruit GFX Library
3. Adafruit SSD1306
4. DFRobotDFPlayerMini

### Compiling and Uploading the Code

Once each of the library dependencies have been added, you can compile and upload the code to the Arduino device. To do this, click the icon at the top left which looks like a right-ward facing arrow. Note that it may take a few minutes to compile and transfer the code. Once it does, you will see lights flicker on the Arduino device and then it should simply show a solid blue LED light up. This indicates the sketch has been successfully compiled and transferred to the device and it is now running.

## Wiring the Breadboard

The following represents the pin diagram for the Nano ESP32 with headers:

![Arduino IDE](related-docs/esp32-pin-diagram.png)

To wire the ESP32 to the two Geiger counters, a LED, a buzzer, and an optional speaker output, connect the wires to the pins as shown below:

```

                                 Arduino Nano ESP32
                                     TOP VIEW

                    USB-C connection to Computer or Power Supply
                                        ↑
       
                       LEFT HEADER          RIGHT HEADER
                       ───────────          ────────────
                       D13                  D12
OLED, buzzer VCCs →    3V3                  D11
                       B0                   D10
                       A0                   D9
                       A1                   D8
                       A2                   D7
                       A3                   D6        ← buzzer signal
         OLED SDA →    A4 / SDA             D5        ← 330 Ω → LED anode
         OLED SCL →    A5 / SCL             D4
                       A6                   D3        ← 1kΩ → Geiger RIGHT J6 pulse
                       A7                   D2        ← 1kΩ → Geiger LEFT J6 pulse
                       VUSB                 GND       ← Geiger GNDs, LED cathode, buzzer GND
                       B1                   RESET
         OLED GND →    GND                  D0 / RX0
                       VIN                  D1 / TX0


```

The end result should look something like the following when all wired up:

![Breadboard Wiring](media/bread-board-wiring.jpg)

To verify operation, you can test with either a positron source placed between the detectors as shown in this video:

[![Detecting Simultaneous Entangled Photons](https://img.youtube.com/vi/ERMolkiLw2E/0.jpg)](https://www.youtube.com/watch?v=ERMolkiLw2E)

Or alternatively, you can stack the detectors one on top of the other, as is shown here:

![Cosmic Ray Telescope](media/vertical-cosmic-ray-telescope.jpg)

And wait for a cosmic ray muon to trigger simultaneous detection. A simultaneous detection event should trigger a flash and beep, as well as the OLED display to update the count of the number of simultaneous detections.

### Setting up DFRobot DFPlayer Mini

For playback of an arbitrary sound file as an audio alert upon detection of a photon pair, the following:

#### Load MP3 File

First, obtain a microSD card and make sure it is formatted with the [FAT32 filesystem](https://en.wikipedia.org/wiki/File_Allocation_Table#FAT32). If it is not already formatted with this file system, you will need to reformat it. The size should be 16 GB or less.

Add the desired MP3 file to be played to the following path on that microSD card: `/MP3/0001.mp3`

That is, first create a directory named `MP3` at the root level of the microSD card's filesystem, then place the MP3 file in that directory, and rename it to `0001.mp3`. This file will then play at the moment of any simultaneous detection by the Geiger counters.

#### Connecting the ESP32 to the DFPlayer

All wiring between the ESP32 and the DFPlayer is done on the left-side of the DFPlayer:

![Arduino IDE](related-docs/dfplayer-mini-pin-layout.png)

Connect via jumper wires the following four pins from the EST32 to the DFPlayer:

```
Nano ESP32 5V/VBUS/VIN-side  → DFPlayer VCC
Nano ESP32 GND               → DFPlayer GND
Nano ESP32 A2 pin            → 1 kΩ resistor → DFPlayer RX
Nano ESP32 A1 pin            → DFPlayer TX
```

In the end, the DFPlayer Mini should appear like this:

```
                                       DFPlayer Mini
                                         TOP VIEW

           
                           LEFT HEADER                    RIGHT HEADER
                           ───────────                    ────────────
                ESP VIN →  VCC                            BUSY
 ESP A2 → 1 kΩ resistor →  RX                             USB-
                 ESP A1 →  TX                             USB+
                           DAC_R                          ADKEY_2
                           DAC_I                          ADKEY_1
     speaker terminal 1 →  SPK_1  ←|                      IO_2
                ESP GND →  GND     | 0.1 µF capacitor     GND
     speaker terminal 2 →  SPK_2  ←|                      IO_1
```

Note: The 0.1 µF ceramic across the speaker pins is optional but can help reduce high frequency noise.

#### Wire the DFPlayer to the Speaker

Note that polarity to the speaker terminals does not matter.

```
DFPlayer SPK_1           → speaker terminal 1
DFPlayer SPK_2           → speaker terminal 2
```

The speakers should be 3 Watt, 8 Ohm speakers. Note that `JST-PH 2.0mm 2 Pin Male Connectors` may simplify the connection of speakers to a breadboard, especially if the speakers come with `JST-PH 2.0` connectors.

Once the speakers are wired correctly to the DFPlayer, you can verify that the MP3 file plays correctly upon a coincidence detection, as shown in this video:

[![Playing an MP3 Upon Photon Detection](https://img.youtube.com/vi/wpQJMHlid0s/0.jpg)](https://www.youtube.com/watch?v=wpQJMHlid0s)

## Collecting and Analyzing Data

This project comes with scripts to collect and analyze data, and even comes with a number of pre-set experiments to peform. These scripts, and experiments, can be found in the [experiments](experiments) directory. The two scripts are:

```
log_geiger.py
analyze_geiger_run.py
```

These are [python](https://en.wikipedia.org/wiki/Python_(programming_language)) scripts and require `python3` in order to run.

## Collecting Data

When the Arduino device is connected to a computer via USB, the `log_geiger` script will connect to it and start outputting data to the screen. Each time either the left or right detector registers a detection event, it will output which detector sent the signal, and a microsecond-accurate timestamp of when it occurred. Periodically, the script will also report summary data.

The detection event lines are prefaced with `E` while the summary report lines are prefaced with `S`:

![Logging Events](media/log_geiger_screenshot.png)

When you have collected sufficient data, you can end the logging script by sending an exit command (generally `Ctrl+C` on most systems).

Note that running this script requires specification of the USB port to which the Arduino device is attached, this can vary from system to system, below are some examples:

### Windows Devices

```bash
# Windows
python3 log_geiger.py --port COM5 --out --out output_file.csv
```

### Linux Devices

```bash
# Linux
python3 log_geiger.py --port /dev/ttyACM0 --out --out output_file.csv
```

### MacOS Devices
```bash
# macOS
python3 log_geiger.py --port /dev/cu.usbmodem206EF13166CC2 --out output_file.csv
```

Note that the particular USB device name will change from system to system. The Arduino IDE displays the exact device name to use for logging.

### Analyzing Data

After collecting data and storing it to an output file, for example `output_file.csv` the analyze script can be run to report various statistics:


```bash
python3 analyze_geiger_run.py output_file.csv \
  --out-prefix run_perpendicular_geometry \
  --run-id R1 \
  --half-window-us 3 \
  --center-us 0 \
  --orientation perpendicular \
  --geometry "Al blocks, 90-degree scatter" \
  --detector-separation "100mm" \
  --source-position "centered" \
  --shielding "none" \
  --aluminum "present" \
  --notes "overnight run, no bumps observed"
```

This will result in the following output to the screen:

![Logging Events](media/analyze_geiger_run_screenshot.png)

The output information includes the run duration, total number of left and right events, as well as counts per minute for both detectors. It then reports, for various time windows ranging from 1 microsecond to 1000 microseconds, how many coincident events were observed within each of those windows. Generally 3 microseconds is the most robust, as it is narrow enough to register all genuine coincidences, without being so wide that it includes spurious events that occur near the same time but are not genuinely correlated.

The rate of these spurious events are continuously estimated by looking for coincident events if the right or left detector's reported events are time-shifted by a significant period (say half a second). These are reported as `lag counts` and should be subtracted from the raw observed counts to yield a more accurate net count.

In addition, it will also generate the following files:

```
<out-prefix>_signed_delta_histogram.png
<out-prefix>_window_scan.png
<out-prefix>_window_scan_summary.csv
<out-prefix>_run_log.csv
<out-prefix>_run_log.json
<out-prefix>_run_log.txt
```

Where `<out-prefix>` was the parameter supplied to the script under `--out-prefix`.

Here is an example of a generated histogram. It shows a genuine signal within the ±5 microseconds bucket, indicating a true excess of correlated events not observed for any of the other greater time-difference buckets:

![Signed Histogram](media/run_signed_delta_histogram.png)


## Experimental Configurations

The minimum experiments required to demonstrate quantum entanglement are defined below. Note that for each of these experiments, a sub-directory has already been setup within the [experiments](experiments) directory, which contains a [bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell)) script to log and analyze data for that run.

### Phase 0: Validation

Phase 0 tests are meant to validate the equipment, establish a baseline for environmental background radiation, and verify detection of coincidences. These tests are not strictly required to prove quantum entanglement, but are important to run before proceeding to ensure the equipment is working as expected.

- 0A: Detectors close, no source present (estimate background radiation, validate equipment and electronics working)
- 0B: Detectors horizontally separated, no source present (expect lower cosmic ray coincident effect)
- 0C: Detectors vertically stacked, no source present (expect high cosmic ray coincidences, crude cosmic ray telescope)

![0C Vertically Stacked Detectors](media/vertical-cosmic-ray-telescope-2.jpg)

The expected results are that general CPM rates should be more or less consistent regardless of placement, but that coincident event detection rates should drop when the detectors are separated by a larger horizontal difference in test `0B` and should sharply increase when the detectors are stacked vertically in `0C`.

### Phase 1: Annihilation Pair Detection

The next phase is meant to demonstrate that entangled photon pairs are emitted in directions that are 180° off from one another, heading in opposite directions along the same axis.

- 1A: Detectors in demonstration position, no source (establish baseline environmental background radiation and coincidences)
- 1B: Positron source is added centered and inline with axis between the detectors (measure increase in singles counts and coincidences)
- 1C: Positron source is moved off-axis from the line between the detectors (expect small drop in singles detections, but large drop in coincidences)

![1B Positron source directly between detectors](media/direct-geometry-detections.jpg)

The expected result is that coincident detections sharply increase from `1A` to `1B` when the positron source is placed exactly between the two directors, but that the coincident rate drops when the source is raised relative to the detectors (taking it off-axis) and making it unlikely for two entangled photons traveling in opposite directions to reach both detectors.

### Phase 2: Compton Polarimetry in Parallel Configuration

- 2A: Detectors in Parallel Geometry Positions, no source present (establish baseline background radiation)
- 2B: Detectors in Parallel Geometry Positions, source present without aluminum blocks (establish baseline coincidences without effect of scattered photons)
- 2C: Detectors in Parallel Geometry Positions, source present with aluminum blocks (establish additional coincidences from scattered photons in parallel case)

### Phase 3: Compton Polarimetry in Perpendicular Configuration

- 3A: Detectors in Perpendicular Geometry Positions, no source present (establish baseline background radiation)
- 3B: Detectors in Perpendicular Geometry Positions, source present without aluminum blocks (establish baseline coincidences without effect of scattered photons)
- 3C: Detectors in Perpendicular Geometry Positions, source present with aluminum blocks (establish additional coincidences from scattered photons in perpendicular case)

## Results

Show histograms, summary of data runs, analysis, and evidence of entanglement compared to theoretical expectations.
