#!/bin/sh python

from ASRRunner import ASRRunner
from AudioSplit import AudioSplit

import os

def main():
    dir_path = os.path.dirname(__file__)
    # folder should under dir_path
    folder_name = ''

    runner = ASRRunner(dir_path, folder_name)
    runner.run()

    # split = AudioSplit(folder_name, dir_path)
    # split.run()

if __name__ == "__main__":
    main()
