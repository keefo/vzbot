
# WS2814 RGBW LED Strip Controller

This script controls WS2814 24V LED strip lights, which are advanced 4-in-1 addressable LEDs featuring RGBW (Red, Green, Blue, White) color channels. The WS2814 is an evolution of the popular WS2812 series with several key improvements.

https://www.aliexpress.com/item/1005004794429155.html?spm=a2g0o.order_list.order_list_main.314.73061802A57OPl#nav-specification

## 📋 LED Specifications

| Parameter | Value |
|-----------|-------|
| **Type** | WS2814 RGBW (4-in-1) |
| **Voltage** | 24V DC |
| **Form Factor** | 5050 SMD package |
| **Colors** | RGB + dedicated white channel |
| **Protocol** | Single-wire digital control (similar to WS2812) |
| **Connector** | 3-pin (Data, VCC, GND) |
| **Waterproofing** | IP30 (indoor), IP65 (water-resistant), IP67 (waterproof) |

## ⚡ Advantages of WS2814 vs WS2812

1. **Higher Voltage**: 24V operation reduces voltage drop and power loss over long runs
2. **True White**: Dedicated white channel produces pure white light (not RGB mixed white)
3. **Better Performance**: Improved color accuracy and brightness
4. **Efficiency**: Fewer power injection points needed for long strips
5. **Lower Current**: Reduced current draw per meter

## 🎯 Strip Layout (21 LEDs Total)

```
        Back (0-4)
           █████
Left    █          █    Right
(15-19) █          █    (5-9)
        █          █
           █████
        Front (10-14)
     
     Additional LED: 20
```

### Section Breakdown:
- **Back section**: LEDs 0-4 (5 LEDs)
  - Back Left: 0-1
  - Back Middle: 2
  - Back Right: 3-4
- **Right section**: LEDs 5-9 (5 LEDs)
- **Front section**: LEDs 10-14 (5 LEDs)
- **Left section**: LEDs 15-19 (5 LEDs)
- **Additional**: LED 20 (1 LED)

## ✨ Features

- 🎨 Individual LED control with RGBW color mixing
- 🌈 Predefined color patterns and animations
- 📍 Section-based lighting (back, front, left, right)
- 🎄 Rainbow and Christmas light animations
- 🔆 Configurable brightness control
- 📝 Comprehensive logging to file and console

## 🔧 Hardware Setup

### Requirements:
- **Controller**: Raspberry Pi
- **Data Signal**: GPIO 10 (MOSI/SPI)
- **Power Supply**: 24V DC for LED strip
- **Level Shifter**: Recommended for 3.3V Pi to 5V LED data signal
- **Grounding**: Common ground between Pi and LED power supply

### Wiring Diagram:
```
Raspberry Pi          Level Shifter          WS2814 Strip
GPIO 10 (3.3V) -----> LV Input               
3.3V Power     -----> LV Power               
GND            -----> GND            -----> GND (Data)
                      HV Power      <------ 24V Power Supply
                      HV Output     -----> Data In
                                    -----> VCC (24V Power Supply)
```
