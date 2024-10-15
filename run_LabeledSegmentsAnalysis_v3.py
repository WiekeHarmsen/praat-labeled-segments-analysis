"""
This script loops through the .TextGrid files in the input, 
searches for each file the corresponding audio file, 
and computes audio features over the labeled segments in the specified tier.

Author: Wieke Harmsen
Date created: 15 October 2024
"""


import parselmouth
from parselmouth.praat import call, run_file
import os
import glob
import argparse



def run(args):
    # DART preposttest
    audioDir = args.audioDir
    textgridDir = args.textGridDir
    outputDir = args.lsaFeatureTxtDir
    audioExtension = args.audioExtension

    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    audio_dir = audioDir
    textgrid_dir = textgridDir
    output_dir = outputDir
    audio_extension = '*' + audioExtension

    result_file = '.txt'
    suffix_tg_file_names = ''
    tg_extension = '.TextGrid'

    # If textgrid is created from WhisperTimestamped json-asr-result (with script asr-results-to-textgrids):
    # Tier 1: wordsDisTier
    # Tier 2: wordsTier
    # Tier 3: confTier
    # Tier 4: segmentsTier
    tier_number = 2 # wordsTier
    match_label = '*'
    begin_end_labels = 'SIL'

    try:
        run_file('./LabeledSegmentsAnalysis_v3.praat', audio_dir, textgrid_dir, output_dir, audio_extension, result_file, suffix_tg_file_names, tg_extension, 2, '*', 'SIL', True, True, True, True, True, True, 0.0, 75, 600, 5, 5500, 0.025, 50)
    except Exception as e:
        print(f'Error encountered: {e}')

def main():
    parser = argparse.ArgumentParser("Message")
    parser.add_argument("--audioDir", type=str, help = "Path to audio directory.")
    parser.add_argument("--audioExtension", type=str, help = "Audio extension")
    parser.add_argument("--textGridDir", type=str, help = "Dir to TextGrids that are created from json-asr-results.")
    parser.add_argument("--tierNumber", type=str, help = "Tier number of tier with segments that should be analysed")
    parser.add_argument("--lsaFeatureTxtDir", type=str, help = "Output dir")
    
    
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()