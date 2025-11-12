#!/bin/bash


sudo apt update && sudo apt upgrade -y


sudo apt install -y python3-pip python3-venv python3-full openjdk-17-jdk git zip unzip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev


python3 -m venv kivy_venv
source kivy_venv/bin/activate


pip install --upgrade pip
pip install buildozer

echo "✅ Установка завершена! Запусти: buildozer android debug"