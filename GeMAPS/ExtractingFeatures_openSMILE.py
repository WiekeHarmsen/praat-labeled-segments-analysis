# -*- coding: utf-8 -*-
"""
Run this file to extract eGeMAPS features using openSMILE.
Recommended to run on Ponyland, see ExtractingFeatures_openSMILE_instructions.txt

Input: folder with .wav files and folder with TextGrid files
Output: excel file with all features

Things to change depending on your data:
indir, outdir, opensmiledir, opensmile, tier, typeOfSpeech, textgriddir, textgridextensions, config, featureset

@author: Loes van Bemmel
@date created: 11-10-2020
@data last adaptations: 7-7-2021
"""

#Imports
from praatio import tgio 
import subprocess
import os
import arff #see instructions if it gives an error here 
import numpy as np 
import pandas as pd

#THINGS THAT POSSIBLY NEED TO CHANGE
#Directories: change these if necessary
indir = "audio/"
outdir = "results/"
textgriddir = "TextGrids/"
textgridextensions = ["_annotated.tg", "_checked_annotated.tg"]

opensmiledir = "opensmile-2.3.0/" #this is the standard directory, see instructions.txt
tier = 'word'
typeOfSpeech = 'Reference' 
opensmile = opensmiledir+"./SMILExtract" #change this according to your location of SMILExtract file in opensmile directory

#This should be correct: do not change
frameModeFunctionals = opensmiledir+"config/shared/FrameModeFunctionals.conf.inc"

#The configuration file of openSMILE used to extract features
#Feel free to add different configurations, you can find them in opensmile-2.3.0/config/
#Please also add a string to notate the featureset that you will use.

#config = opensmiledir+"config/gemaps/GeMAPSv01a.conf" #GeMAPS
#featureset = "GeMAPS"
config = opensmiledir+"config/gemaps/eGeMAPSv01a.conf" #eGeMAPS, might need to be changed, check your own opensmile directory!
featureset = "eGeMAPS"


"""
createFrameModeFunctionals 
    input: 
        file_name = the name of the .wav and corresponding textgrid file
            please ensure that the extension above is correct
        tier = either 'phoneme' or 'word'
        
    output:
        a new FrameModeFunctionals.conf.inc file that uses the force aligned intervals to calculate 
        openSMILE features rather than a pre-set sliding window

"""
def createFrameModeFunctionals(file_name, tier): 
    if(tier == 'full'): #standard FrameModeFunctionals file
        framemodefile = open(frameModeFunctionals, "w")
        framemodefile.write("frameMode = full \nframeSize = 0 \nframeStep = 0\nframeCenterSpecial = left")
        framemodefile.close()
        return [] 
    else:
        #Check if this is correct in your TextGrid files
        if(tier == 'word'):
            index = 1
        if(tier == 'phoneme'):
            index = 2
            
        #Check if file exists 
        file = ""
        for extension in textgridextensions:
            fileoption = textgriddir+file_name+extension
            if(os.path.exists(fileoption)):
                file = fileoption 
                break 
        if(file == ""):
            print("The textgrid for ", file_name, " does not exist in the given directory! Please add it!")
            return []

        tg = tgio.openTextgrid(file)
        tierList = tg.tierDict[tg.tierNameList[index]]

        intervalstring = ""
        labellist = []
        
        for start, stop, label in tierList.entryList:
            intervalstring += str(start)+"s-"+str(stop)+"s,"
            labellist.append(label)
            
        intervalstring = intervalstring[0:-1] #not the last comma
        framemodefile = open(frameModeFunctionals, "w")
        framemodefile.write("frameMode = list \nframeList = "+str(intervalstring)+" \nframeCenterSpecial = left")
        framemodefile.close()
    
    return labellist
    
def getFiles(indir, outdir):
    #Getting files from indir and creating the outdir
    filenames=[]
    for filename in os.listdir(indir):
        filenames.append(filename)
    
    if(not os.path.isdir(outdir)):
        os.makedirs(outdir)
        print("Created output directory ", outdir,".")

    print("\nExtracting features from ", len(os.listdir(indir))," files.") 
    return filenames
    
#Generating and running the commands
def createFeatures(filenames):
    finaldf = None
    for file in filenames: #for each input file
        resultname = file[0:-4]+"_openSMILE_"+featureset+"_"+tier+"tier_results"
        resultname = outdir+resultname
        command = opensmile + " -C " + config +" -I " +indir+file + " -O " + resultname

        print(command)
        labellist = createFrameModeFunctionals(file[0:-4], tier) #creating the FrameModeFunctionals file to ensure correct timeframes
        if((len(labellist) == 0) and (tier != "full")):
            print("Something went wrong with the labellist in createFeatures. Please ensure that the textgrid files are correct.")
            continue #if somehow it doesn't work; skip! 
        
        #Delete the file if it already exists
        if(os.path.exists(resultname)):
            os.remove(resultname)

        subprocess.run(command, shell=True)

        #load the arff dataset
        dataset = arff.load(open(resultname))
        data = np.array(dataset['data'])
        df = pd.DataFrame(data)
        df.columns = dataset['attributes']    
        df.columns = list([c[0] for c in list(df.columns)])
        df['name'] = file[0:-4]

        #The words/phonemes are only if you do not use the entire file; of course.
        if(tier != "full"):
            #Sometimes openSMILE doesn't calculate features for the last few milliseconds
            #So delete those last utterances from the labellist as well 
            if(len(labellist) > len(data)):
                difference = len(data) - len(labellist) #usually just 1! But could be more 
                labellist = labellist[0:difference] 

            df['word'] = labellist

        df['class'] = typeOfSpeech
        finaldf = pd.concat([finaldf, df])
    
    return finaldf 
    
    
filenames = getFiles(indir, outdir)
dataframe = createFeatures(filenames)
#Save to disk as excel file
output_name = outdir+featureset+"_"+tier+"level_"+typeOfSpeech+".xlsx"
dataframe.to_excel(output_name, index=False)
print("The file "+ output_name + " is created.")
print("--------------------------------------------------------------------------------")  