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

### Library Dependencies

In the Arduino IDA go to Library Manager, search for and add the following dependencies:

1. Adafruit SSD1306
2. Adafruit GFX Library
3. DFRobotDFPlayerMini

## Wiring the Breadboard

Show detailed wiring diagram.

```
                                 Arduino Nano ESP32
                                  TOP VIEW
                
                              USB-C connector here
                                       ↑
        
                        LEFT HEADER                    RIGHT HEADER
                        ───────────                    ────────────
                        D13                            D12
 OLED, buzzer VCCs →    3V3                            D11
                        B0                             D10
                        A0                             D9
                        A1                             D8
                        A2                             D7
                        A3                             D6        ← buzzer signal
          OLED SDA →    A4 / SDA                       D5        ← 330 Ω → LED anode
          OLED SCL →    A5 / SCL                       D4
                        A6                             D3        ← 1kΩ → Geiger RIGHT J6 pulse
                        A7                             D2        ← 1kΩ → Geiger LEFT J6 pulse
                        VUSB                           GND       ← Geiger J6 GNDs, LED cathode, buzzer GND
                        B1                             RESET
          OLED GND →    GND                            D0 / RX0
                        VIN                            D1 / TX0


```

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
