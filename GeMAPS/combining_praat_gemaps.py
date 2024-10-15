# -*- coding: utf-8 -*-
"""
Run this file to combine the Praat and (e)GeMAPS features.

Input: folders with excel files containg Praat and openSMILE features
Output: excel file with combined features

Things to change depending on your data:
filenames, output_name, removeOutliers

@author: Loes van Bemmel
@date created: 20-4-2021
@data last adaptations: 7-7-2021
"""

#imports
import numpy as np
import pandas as pd
import os

filenames = ["results/praat_wordlevel_Reference.xlsx", 
            "results/eGeMAPS_wordlevel_Reference.xlsx"
            ]
            
output_name = "results/wordlevel_Reference.xlsx"
removeOutliers = True


def combineFeatureSets(filenames, removeOutliers):
    dftotal = None
    for filename in filenames:
        print("\n"+filename)
        df = pd.read_excel(filename)
        df.columns = list(df.columns)
        
        varname = 'name'
        if 'file_name' in df.columns:
            varname = 'file_name'
        
        newNameList = [] 
        for name in df[varname]:
            name = name.replace("_tier2_results", "")
            name = name.replace("_tier3_results", "")
            name = name.replace("-16khz", "")
            name = name.replace("_tier4_results", "")
            newNameList.append(name)

        df['file_name'] = newNameList

        #We already made 'file_name', so drop the 'name'
        if 'name' in list(df.columns):
            df = df.drop('name', axis=1)

        #drop all the silences/unknown words
        #since these are already dropped in the Praat features
        if 'word' in list(df.columns):
            outlierConditions = [
                    (df["word"].eq("<SIL>")), 
                    (df["word"].eq("SIL")), 
                    (df["word"].eq("<SPN>")), 
                    (df["word"].eq("SPN")),
                    (df["word"].eq("<UNK>")),
                    (df["word"].eq("UNK")),
                    (df["word"].eq("<SPK>")),
                    (df["word"].eq("UNK")),
                    (df["word"].eq("sil")),
                    (df["word"].eq("spn")),
                    (df["word"].eq("[SPN]")),
            ]
            df["outlier"] = np.select(outlierConditions, np.ones(len(outlierConditions)), default =0)
            df = df.drop(df[df.outlier == 1].index)
            df = df.drop(["outlier"], axis=1)
        
        if(dftotal is None):
            dftotal = df.copy()
        else:        
            newdfs = None
            for name in dftotal['file_name'].unique():
                subdf1 = df[df.file_name == name]
                subdf2 = dftotal[dftotal.file_name == name]
             
                if(len(subdf1) != 0 and len(subdf2) != 0):
                    #possible that the last few 'words' have to be deleted
                    #cause of a problem with generating the eGeMAPS
                    if(len(subdf1)>len(subdf2)): 
                        subdf1 = subdf1.drop(subdf1.tail(len(subdf1)-len(subdf2)).index)   
                    if(len(subdf2)>len(subdf1)): 
                        subdf2 = subdf2.drop(subdf2.tail(len(subdf2)-len(subdf1)).index) 
                        
                print(len(subdf1), " en ", len(subdf2))
                print(subdf1.head(5))
                print("en")
                print(subdf2.head(5))
                print("-------------")
                
                #resetting indexes so the concatenation goes well 
                subdf1.reset_index(drop=True, inplace=True)
                subdf2.reset_index(drop=True, inplace=True)
                newdf = pd.concat([subdf1, subdf2], axis=1)
                newdfs = pd.concat([newdfs, newdf])

            dftotal = newdfs
            
    dftotal = dftotal.reset_index()
    
    if(removeOutliers):
        print("Length before any outlier deletion: ", dftotal.shape[0])
        oldshape = dftotal.shape[0]
    
        if 'pitch_max' in list(dftotal.columns):
            outlierConditions2 = [
                (dftotal["pitch_max"] == 0), 
                (dftotal["dur"] == 0), 
                (dftotal["intensity_max"] == 0)
            ]
        else:
            outlierConditions2 = [
                (dftotal["pitch_max_mean"] == 0),
                (dftotal["dur_mean"] == 0), 
                (dftotal["intensity_max_mean"] == 0)
            ]

        dftotal["outlier"] = np.select(outlierConditions2, np.ones(len(outlierConditions2)), default =0)
        print('Amount of outliers = ', len(dftotal[dftotal.outlier==1]))
        dftotal = dftotal.drop(dftotal[dftotal.outlier == 1].index)
        dftotal = dftotal.drop(["outlier"], axis=1)
        
        print('Before drop of NaN values: ', dftotal.shape)

        #drop any rows containing any NaN/empty values
        dftotal = dftotal.dropna()
        print("Length after deletion of outliers and NaN: ", dftotal.shape[0])
        print("So ", oldshape - dftotal.shape[0], " datapoints were deleted.")
            
        
    print("-----------------------------------")
    print("New set created with ", len(list(dftotal.columns)), " features.")
    print("-----------------------------------")
            
    return dftotal
    
dftotal = combineFeatureSets(filenames, removeOutliers)
dftotal.to_excel(output_name, index=False)
print("The file "+ output_name + " is created.")