# -*- coding: utf-8 -*-
"""
Run this file or extract_results.py to organize the Praat features 
extracted from LabeledSegementAnalysis.praat
('word', 'dur', 'pitch_min', 'pitch_max', 'pitch_mean', 'pitch_std','pitch_var', 'intensity_min', 'intensity_max', 'intensity_mean', 'intensity_std', 'f0', 'f1', 'f2','f3','grav_center')
Based on outlierDetection.py by Wieke Harmsen and extract_results.py by Maarten Vos

Input: folders with .txt files containing Praat features
Output: excel file with Praat features per segment

Things to change depending on your data:
resultsdir, dirforoutput,typeOfSpeech, featureset, calculate_mean.
Possibly add string logic to extract correct participant from datanames on line 170

@author: Loes van Bemmel
@date created: 20-4-2021
@data last adaptations: 7-7-2021
"""

#imports
import numpy as np
import os
import pandas as pd
import re
import argparse
import glob

def compute_average(df_list_clean, dataframe_info):       
    mean_columns = ['file_name', 'total_dur','total_intervals','dur_mean', 
               'pitch_min_mean', 'pitch_max_mean', 'pitch_mean_mean',
               'pitch_std_mean', 'pitch_var_mean', 'intensity_min_mean', 
               'intensity_max_mean','intensity_mean_mean', 'intensity_std_mean', 
               'f0_mean', 'f1_mean', 'f2_mean','f3_mean', 'grav_center_mean']
    
    means_matrix = []
    for df_idx in range(len(df_list_clean)):
        
        #select one dataframe
        df = df_list_clean[df_idx]
        
        #obtain the mean of all acoustic measures in this dataframe.
        file_name = dataframe_info[df_idx][0]
        total_dur = dataframe_info[df_idx][1]
        total_intervals = dataframe_info[df_idx][2]
        dur_mean = df["dur"].mean()
        pitch_min_mean = df['pitch_min'].mean()
        pitch_max_mean = df['pitch_max'].mean()
        pitch_mean_mean = df['pitch_mean'].mean()
        pitch_std_mean = df['pitch_std'].mean()
        pitch_var_mean = df['pitch_var'].mean()
        intensity_min_mean = df['intensity_min'].mean()
        intensity_max_mean = df['intensity_max'].mean()
        intensity_mean_mean = df['intensity_mean'].mean()
        intensity_std_mean = df['intensity_std'].mean()
        f0_mean = df['f0'].mean()
        f1_mean = df['f1'].mean()
        f2_mean = df['f2'].mean()
        f3_mean = df['f3'].mean()
        grav_center_mean = df['grav_center'].mean()
        
        #Save all means in a list
        row = [file_name, total_dur, total_intervals, dur_mean, pitch_min_mean, 
               pitch_max_mean, pitch_mean_mean, pitch_std_mean, pitch_var_mean,
               intensity_min_mean, intensity_max_mean, intensity_mean_mean,
               intensity_std_mean, f0_mean, f1_mean, f2_mean, f3_mean, grav_center_mean]
        
        #Append this list to another list (matrix)
        means_matrix.append(row)
    
    #Save the matrix as dataframe and return it
    df_means = pd.DataFrame(means_matrix, columns = mean_columns)
    
    return df_means
    
def fill_matrix(line_array):
    matrix = []
    for element in line_array:
        row = []
        row.append(element[0])
        
        for idx in [1,3,4,5,6,8,10,11,12,13,15,16,17,18,20]:
            try:
                row.append(float(element[idx])) 
            except ValueError:
                row.append(np.nan) 
        matrix.append(row)
    return matrix   
    
    
def convert_txt_to_dataframes(lines):
    dataframe_list = []
    dataframe_info = []
    #Convert txt file to separate dataframe for every audio+TextGrid file
    
    indx = 2
    if(len(lines) == 2):
        indx = 1
    
    for i, line in enumerate(lines[indx:]):
        # Split the line into an easy to use list
        if "\x00" in line:
            line = line.replace("\x00", "") #encoding issue, this is a workaround 
        line = re.sub("\s\s+", " ", line) #replace any amount of spaces with a single space

        line_list = line.split(" ")

        info = []
        name_file = line_list[0]
        info.append(name_file)
        
        tot_dur = int(line_list[-1].replace("\n",""))
        info.append(tot_dur)
        
        tot_int = int(line_list[-3])
        info.append(tot_int)
        
        dataframe_info.append(info)
        
        #Take repetitive part of line_list
        line_list = line_list[1:-4]
        
        #Reshape list to list in list, such that each word is separate sublist
        length = len(line_list)
        nr_rows = int(length/21) 
        line_array = np.asarray(line_list)
        line_array = line_array.reshape((nr_rows,21))

        matrix = fill_matrix(line_array)
        columns = ['word', 'dur', 'pitch_min', 'pitch_max', 'pitch_mean', 'pitch_std','pitch_var', 'intensity_min', 'intensity_max',
                                   'intensity_mean', 'intensity_std', 'f0', 'f1', 'f2','f3','grav_center']
        
        df = pd.DataFrame(matrix,columns=columns)
        dataframe_list.append(df)
        
    return dataframe_list, dataframe_info
    
def organize(directory, typeOfSpeech, calculate_mean):
    dffinal = None

    txt_result_files = glob.glob(os.path.join(directory, '*.txt'))

    for filename in txt_result_files:
        dataset = open(os.path.join(directory,filename))

        with open(filename, errors='ignore') as f:
            lines = f.readlines()
            dataframe_list, dataframe_info = convert_txt_to_dataframes(lines)
            

        for df_idx in range(len(dataframe_list)):
                #Select dataframe & corresponding dataframe info
                df = dataframe_list[df_idx]
                df_info = dataframe_info[df_idx]
                
                #Compute average of every acoustic measure
                if(calculate_mean):
                    df_mean = compute_average(dataframe_list, dataframe_info) 
                    df = df_mean
                    
                df['class'] = typeOfSpeech
                    
                #Add your own files' participants strings if needed
                #these should work for COPD, ISLA, and CHASING data 
                #if none of them match, take the filename as participant 
                if(filename.split('_')[0][0:10] == "Participant"):
                    df['participant'] = filename.split('_')[0]
                elif(filename.split('_')[0][0:2] == "PP"):
                    df['participant'] = filename.split('_')[0]
                elif(filename.split('_')[0][0:3] == "nds"):
                    df['participant'] = filename.split('_')[0]
                elif(filename.split('_')[0][0:2] == "s0"):
                    df['participant'] = filename.split('_')[0]
                else:
                    df['participant'] = "".join(filename.split('_')[0:-2]) #don't include "_tierx_results.txt" in the participants name
                
                    
                df['file_name'] = os.path.basename(filename).replace('.txt', '') #filename[0:-4] #without the .txt
                dffinal = pd.concat([dffinal, df]) 
    return dffinal
    


def run(args):
    #specify the input directories and some booleans
    lsaFeatureTxtDir = args.lsaFeatureTxtDir
    lsaFeatureTotalFile = args.lsaFeatureTotalFile
    typeOfSpeech = "lsa_features" #'class' label for excel file, e.g. Reference

    calculate_mean = args.calculateMean #if True, only the mean values per recording will be saved

    resultdf = organize(lsaFeatureTxtDir, typeOfSpeech, calculate_mean)
    
    mean = ""
    if(calculate_mean):
        mean = "_mean"

    resultdf.to_csv(lsaFeatureTotalFile, index=False, sep='\t')
    print("The file "+ os.path.basename(lsaFeatureTotalFile) + " is created.")
    

def main():
    parser = argparse.ArgumentParser("Message")
    parser.add_argument("--lsaFeatureTxtDir", type=str, help = "Path to fluency-features-dir directory.")
    parser.add_argument("--lsaFeatureTotalFile", type=str, help = "Path to fluency-features-dir directory.")
    parser.add_argument("--calculateMean", type=str, help = "Calculate only mean values.")

    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()