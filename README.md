# Low-Cost Plantain Row-Following Robot

This repository documents a low-cost autonomous robotic platform for plantain crop row-following under canopy conditions.

The system integrates an ESP32-based low-level controller, ROS 2 nodes for perception and decision-making, LiDAR-based lateral distance estimation, BNO055-assisted geometric yaw compensation, and a fuzzy controller for steering commands.

## Related Work

This repository is associated with an ongoing manuscript on low-cost autonomous navigation for plantain crop environments.

Original student repository:

- [Celenaxz/Robot-el-chino-de-los-mandados](https://github.com/Celenaxz/Robot-el-chino-de-los-mandados)

This curated repository reorganizes the material to improve readability, documentation, reproducibility, and research presentation.

## System Overview

The robotic platform follows plantain crop rows using low-cost embedded hardware and ROS 2-based processing.

Main system components:

- **ESP32 firmware:** low-level control, encoder reading, BNO055 IMU acquisition, serial communication, and actuator command handling.
- **ROS 2 processing layer:** serial communication, LiDAR processing, lateral distance estimation, image logging, and fuzzy steering control.
- **LiDAR sensing:** lateral distance estimation using a selected measurement cone.
- **BNO055 IMU:** geometric auxiliary used to orient or correct the LiDAR measurement cone.
- **Fuzzy control:** high-level steering command generation for row-following behavior.
- **Experimental logs:** CSV files with robot measurements and trial data.

## Repository Structure

```text
firmware/
└── esp32/                  ESP32 PlatformIO firmware

ros2_ws/
└── hinf/                   ROS 2 package and nodes

data/
└── experimental_trials/    Experimental CSV logs

figures/
└── experimental_results/   Plots and figures related to experiments

media/
└── images/                 Robot images and visual material

docs/                       Technical documentation