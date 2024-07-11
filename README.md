# Blood Pressure and Heart Rate Monitoring Software
## Overview
This project is a Python-based software application designed to collect and display blood pressure and heart rate data. The software interfaces with an Arduino connected to a blood pressure cuff and a heart rate sensor. Communication between the Arduino and the software is handled via serial connection over USB. The graphical user interface (GUI) is implemented using the Tkinter library, and the application utilizes multithreading to ensure continuous data collection and real-time graphing.

## Features
Serial Communication: Communicates with the Arduino via a USB serial connection.
GUI Interface: Easy-to-use GUI for selecting ports, subjects, and data parameters.
Measurement Control: Start, stop, and restart data measurements with ease.
Real-Time Graphing: Continuously graph the collected data during measurements.
Data Export: Save collected data in a .txt format after measurements are complete.
Multithreading: Ensures smooth and continuous data collection and graphing.
