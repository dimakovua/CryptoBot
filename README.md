# CryptoBot

![CryptoBot Logo](logo.png)

CryptoBot is a cryptocurrency trading bot built with Python. It utilizes various trading strategies and technical analysis indicators to make automated trading decisions in the cryptocurrency market.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)


## Introduction

CryptoBot is a powerful tool for cryptocurrency traders who want to automate their trading strategies. It provides a flexible and extensible framework for developing and executing trading algorithms. By leveraging historical and real-time market data, CryptoBot aims to help traders maximize their profits while minimizing risks.

## Features

- Support for cryptocurrency exchanges (Binance).
- Real-time market data streaming and candlestick charting.
- Selling/buying features.
- Web-based user interface for monitoring and controlling the bot.
- Extensible architecture allowing users to add their own trading strategies and indicators.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/dimakovua/CryptoBot.git
2. Change to the project directory:

    ```bash
    cd CryptoBot
3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
4. Configure the bot by updating the config.py file with your API keys, trading parameters, and other settings (see [Configuration](#configuration) section for details).

## Usage

To run CryptoBot, execute the following:
```bash
python3 main.py
```
CryptoBot will start executing the configured trading strategies and monitoring the cryptocurrency market. You can monitor the bot's performance and make adjustments using the web-based user interface.

## Configuration

The configuration of CryptoBot is done through the config.yaml file. It allows you to specify various settings, including:

API keys for cryptocurrency exchanges
Trading parameters such as order size, stop-loss, and take-profit levels
Selected trading strategies and their parameters
Logging and notification settings



