#!/bin/bash

# Set base dir to the main data directory
basePath=/vol/bigdata3/datasets3/dutch_child_audio/dart/preposttest_final

# Audio directory
audioDir=$basePath/02_audio_renamed
audioExtension=.mp3

# TextGrid directory
textGridDir=$basePath/05_asr_experiments/whispert_dis_prompts/json-asr-results-as-tg # choose between whispert_dis_prompts or whispert_dis

# If textgrid is created from WhisperTimestamped json-asr-result (with script asr-results-to-textgrids):
# Tier 1: wordsDisTier
# Tier 2: wordsTier
# Tier 3: confTier
# Tier 4: segmentsTier
tierNumber=2

# Output directory
lsaFeatureTxtDir=$basePath/05_asr_experiments/whispert_dis_prompts/fluency-features/lsa-feature-files
lsaFeatureTotalFile=$basePath/05_asr_experiments/whispert_dis_prompts/fluency-features/lsa-features-total.tsv
calculateMean=false #if True, only the mean values per recording will be saved

python3 run_LabeledSegmentsAnalysis_v3.py --audioDir $audioDir --audioExtension '.mp3' --textGridDir $textGridDir --tierNumber $tierNumber --lsaFeatureTxtDir $lsaFeatureTxtDir
python3 organizing_PraatFeatures.py --lsaFeatureTxtDir $lsaFeatureTxtDir --lsaFeatureTotalFile $lsaFeatureTotalFile --calculateMean $calculateMean
