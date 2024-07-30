# A Study of Network Performance through SRv6 and MPTCP Integration
This study investigates the integration of SRv6 (Segment Routing over IPv6) with MPTCP (Multipath TCP) to enable he concurrent use of multiple network routes. SRv6 provides a flexible and scalable routing architecture, while MPTCP allows for the distribution of traffic across multiple paths. By combining these technologies, this study aim to demonstrate improvement in network performance. This study is part of an internship at NAIST SDLab.

This repository provides a framework for integrating MPTCP and SRv6, demonstrating improvements in network performance.The integration uses Mininet for simulate the network, FRR and OSPF for dynamic routing protocol, with performance measurements conducted using iperf3.

## Prerequisite
- ```Linux Kernel``` version 6.8.0 or greater
- ```Python``` version 3.12 or greater
- ```Mininet``` version 2.3 or greater
- ```FRRouting``` version 10.0 or greater
- ```Iperf3``` version 3.17 or greater

## Installation
1. Make sure that you have all the prerequisite
2. Clone the repository:
    ```sh
    git clone https://github.com/RyukungG/Integration-of-MPTCP-and-SRv6.git
    cd Integration-of-MPTCP-and-SRv6
    ```
3. Go to the directory where you cloned the repository, and create a virtual environment using:
    ```sh
    python -m venv env
    ```
4. then run to activate a virtual environment.
    ```sh
    source env/bin/activate  
    ```
5. Install Python dependencies:
    ```sh
    pip install -r requirements.txt
    ```
- To Then exit the environment then use the command:
    ```sh
    deactivate
    ```

## Run the application
Go to the repository directory and you can run these file:
- ```main.py```: This file for run the mininet of small-scale topology that allows for easy controlled, and detailed analysis.
    - You can config you own topology here

- ```os3e_mininet.py```: This file for run the mininet of the OS3E topology.
    - You can config your own experiments in OS3E topology here.

- ```os3e_map.py```: This file for creating a visual representation of the OS3E topology.

## Project Structure
- ```base_node.py```:  Base class for network nodes.
- ```FRR.py```: Base class for FRR nodes.
- ```os3e.py```: Class for get OS3E topology data from OS3E.txt
- ```topology.py```: Class with function for creating network topology.

