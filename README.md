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

Before you can compile the sketch you must add the appropriate library dependencies. To do this, click on the icon that looks like a set of books on the left hand side of the IDE, to make the "Library Manager" appear, then in the search box, search for, and then add, each of the following libraries:

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

Format microSD card to FAT32 filesystem
Add MP3 file to: /MP3/0001.mp3
Insert SD Card into player

#### Wire the ESP32 to the DFPlayer

```
                                    DFPlayerMini
                                     TOP VIEW
                   
                                 USB-C connector here
                                          ↑
           
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

```
Nano ESP32 5V/VBUS/VIN-side  → DFPlayer VCC
Nano ESP32 GND               → DFPlayer GND
Nano A2 pin                  → 1 kΩ resistor → DFPlayer RX
Nano A1 pin                  → DFPlayer TX
```

Note: The 0.1 µF ceramic across the speaker pins helped reduce high frequency noise.

#### Wire the DFPlayer to the Speaker

Note that polarity to the speaker terminals does not matter.

```
DFPlayer SPK_1           → speaker terminal 1
DFPlayer SPK_2           → speaker terminal 2
```

[![Playing an MP3 Upon Photon Detection](https://img.youtube.com/vi/wpQJMHlid0s/0.jpg)](https://www.youtube.com/watch?v=wpQJMHlid0s)

## Collecting and Analyzing Data

Two scripts built in. One to log, another to analyze.
Describe how to connect a computer to the microcontroller to log data.

## Collecting Data


### Analyzing Data

Detail how 

Usage:

```bash
python3 analyze_geiger_run_enhanced.py run.csv \
  --out-prefix run_P1_perpendicular \
  --run-id P1 \
  --half-window-us 3 \
  --center-us 0 \
  --orientation perpendicular \
  --geometry "Al blocks, 90-degree scatter" \
  --detector-separation "..." \
  --source-position "centered" \
  --shielding "none" \
  --aluminum present \
  --notes "overnight run, no bumps observed"
```

```
<prefix>_signed_delta_histogram.png
<prefix>_window_scan.png
<prefix>_window_scan_summary.csv
<prefix>_run_log.csv
<prefix>_run_log.json
<prefix>_run_log.txt
```

```
Raw CSV filename
Host start/end time, if host_time_utc exists
Board timestamp start/end
Duration in seconds/minutes/hours
Left total counts
Right total counts
Left CPM
Right CPM
Prompt coincidence count
Average lagged coincidence count
Lag counts by each lag offset
Net coincidence count = prompt - average lag
Prompt CPM
Lag CPM
Net CPM
Simple significance: net / sqrt(prompt + avg_lag)
Li & Ma on/off significance
One-sided and two-sided normal-equivalent p-values
Expected accidental coincidence rate from singles rates
Arduino final summary values, if present
Max droppedEvents, if present
```


## Experimental Configurations

Describe each run, how to get baselines of environmental noise.
How to position each detector for each run.
How to analyze data to demonstrate results.

### Phase 0: Validation

0A: Detectors close, no source present (estimate background radiation, validate equipment and electronics working)
0B: Detectors horizontally separated, no source present (expect lower cosmic ray coincident effect)
0C: Detectors vertically stacked, no source present (expect high cosmic ray coincidences, crude cosmic ray telescope)

### Phase 1: Annihilation Pair Detection

1A: Detectors in demonstration position, no source (establish baseline environmental background radiation and coincidences)
1B: Positron source is added centered and inline with axis between the detectors (measure increase in singles counts and coincidences)
1C: Positron source is moved off-axis from the line between the detectors (expect small drop in singles detections, but large drop in coincidences)

### Phase 2: Compton Polarimetry in Parallel Configuration

2A: Detectors in Parallel Geometry Positions, no source present (establish baseline background radiation)
2B: Detectors in Parallel Geometry Positions, source present without aluminum blocks (establish baseline coincidences without effect of scattered photons)
2C: Detectors in Parallel Geometry Positions, source present with aluminum blocks (establish additional coincidences from scattered photons in parallel case)

### Phase 3: Compton Polarimetry in Perpendicular Configuration

3A: Detectors in Perpendicular Geometry Positions, no source present (establish baseline background radiation)
3B: Detectors in Perpendicular Geometry Positions, source present without aluminum blocks (establish baseline coincidences without effect of scattered photons)
3C: Detectors in Perpendicular Geometry Positions, source present with aluminum blocks (establish additional coincidences from scattered photons in perpendicular case)

## Results

Show histograms, summary of data runs, analysis, and evidence of entanglement compared to theoretical expectations.
