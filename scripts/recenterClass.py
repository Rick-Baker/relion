#!/usr/bin/python

# recenterClass.py is called by relion when the user selects "Recenter and save selected classes"
# It opens a new relion_display for each selected class in which the user selects a new center for the class image stack
# This script then creates a new particles.star file with the recentering applied 

import math
import sys
import os
from time import gmtime, strftime
import subprocess

def load_star_file(fileName):
    loadFile = open(fileName,'r')
    data = loadFile.readlines()
    loadFile.close()
    return data

# from https://stackoverflow.com/questions/1158076/implement-touch-using-python
def touch(fname, times=None):
    basedir = os.path.dirname(fname)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    fhandle = open(fname, 'a')
    try:
        os.utime(fname, times)
    finally:
        fhandle.close()
	
def write_star_file(data, particleCount, workingDir, fileName):
    writeFileName = workingDir+fileName[:-5]+strftime("-recenter-%Y-%m-%d--%H-%M-%S", gmtime())+".star"
    nodeWriteFileName = workingDir+".Nodes/3/"+fileName[:-5]+strftime("-recenter-%Y-%m-%d--%H-%M-%S", gmtime())+".star"
    writeFile = open(writeFileName,'w')
    for line in data:
        writeFile.write(line)

    writeFile.write("\n")
    writeFile.close()
    print "*********************************************************************************************"
    print "New Starfile created at "+ writeFileName
    print "*********************************************************************************************"
    print "A total of " + str(particleCount) + " particles were selected"
    touch(nodeWriteFileName)
	
# Arguments of the form:
# imageScale pathOfStarFile selectedClass1 selectedClass2 ... selectedClassN 
def load_arguements():
    if len(sys.argv) < 4:
        print "Error: too few arguments"
        exit()
    else:
        imageScale = sys.argv[1]
        fileName = sys.argv[2]
        workingDir = sys.argv[3]
        selectedClasses = []
        #for arg in range(3,len(sys.argv)-1):
        for arg in range(4,len(sys.argv)):
	    selectedClasses.append(sys.argv[arg])
    return fileName,imageScale,selectedClasses,workingDir

# Moves rlnCoordinateX rlnCoordinateY rlnOrigin1 rlnOrigin2 based on mouseVector 
def recenter_classes(data, mouseVectors, workingDir):
    # iterate through .star file and move all images in a class
    allData = []
    done = False
    scale = 1 
    #find the column number for Coordinate X, Coordinate Y, Origin X, Origin Y, Psi angle, and image class number
    columnValue = 0
    loadColumns = False
    loadData = False
    particleCount = 0
    class_column = originX_column = originY_column = coordX_column = coordY_column = psi_column = -1
    for line in data:
       # This gets the column numbers of the various parameters we must modify
        if(loadColumns):
            if '_rlnOriginX' in line: 
                originX_column = columnValue
            if '_rlnOriginY' in line:
                originY_column = columnValue
            if '_rlnCoordinateX' in line:
                coordX_column = columnValue
            if '_rlnCoordinateY' in line:
                coordY_column = columnValue
            if '_rlnAnglePsi' in line:
                psi_column = columnValue
            if '_rlnClassNumber' in line:
                class_column = columnValue
            columnValue += 1
            # If a line does not begin with '_' then start loading data
            if line[0] != '_':
                loadColumns = False
                loadData = True
        # This loads in the data of star file and then rotates it by the mouse click
        if(loadData):
            elements = line.split()
	    if len(elements) >= max(class_column,originX_column,originY_column,coordX_column,coordY_column):
            	psi = float(elements[psi_column])*math.pi/180.0
            	imageClass = int(elements[class_column])
            	originX = float(elements[originX_column])
            	originY = float(elements[originY_column])
            	coordX = float(elements[coordX_column])
            	coordY = float(elements[coordY_column])
            	if imageClass in mouseVectors:
		    particleCount += 1
                    mouseX = float(mouseVectors[imageClass][0])
                    mouseY = float(mouseVectors[imageClass][1])
                    # rotates the mouseX and mouseY coords to the image plane - see:
                    # https://en.wikipedia.org/wiki/Rotation_matrix#In_two_dimensions
                    mouseXRot = mouseX*math.cos(-psi)-mouseY*math.sin(-psi)
                    mouseYRot = mouseX*math.sin(-psi)+mouseY*math.cos(-psi)
                    # subtract the mouse and origin componets from the coordVector to recenter
                    newX = originX - mouseXRot
                    newY = originY - mouseYRot
                    elements[originX_column] = str(newX)
                    elements[originY_column] = str(newY)
                    line = "     "+"    ".join(elements)+"\n"
                    allData.append(line)
                else:
                    allData.append(line)
            else:
                allData.append(line)
        else:
            allData.append(line)
        # If the string 'loop_' is in line, start loading columns
        if 'loop_' in line:
            loadColumns = True
    return allData, particleCount

# Loops through each class in selectedClasses and creates a relion_display process
# After the user selects a new center the output of the mouseVector is stored and the process is closed
def spawn_relion_displays(selectedClasses):
    mouseVectors = {}
    for fileName in selectedClasses:
        # Create the relion_display processes and monitor their output
        proc = subprocess.Popen(["relion_display", "--i", str(fileName)], stdout=subprocess.PIPE)
        for output in iter(proc.stdout.readline, ''):
            # get the classNumber from the fileName
            classNumber = int(fileName.split("@")[0])
            output=output.split()
            # parse the output of relion_display to get the mouseVector
            output = output[5].split(")")[0].replace("(","").split(',')
            mouseVectors[classNumber] = output
            # kill the process so the next one can begin
            proc.kill()
    # mouseVector is set to ['0','0'] for processes where the window was closed
    for key in selectedClasses:
        classNumber = int(key.split("@")[0])
        if classNumber not in mouseVectors:
            mouseVectors[classNumber]=['0','0']
    return mouseVectors

# Gets the ratio between particle box size and scaled size to get scale
def get_scale(fileName, workingDir):
    newFileName = '/'.join(fileName.split('@')[1].split('/')[:2]) + "/run.job"
    loadFile = open(workingDir+newFileName,'r')
    data = loadFile.readlines()
    loadFile.close()
    for line in data:
        if "Particle box size (pix):" in line:
            boxSize = int(line.split('==')[1])
        if "-scaled size (pixels):" in line:
            scaleSize = int(line.split('==')[1])
    scale = boxSize/scaleSize
    return scale

# Load arguments & files -> spawn relion_displays -> recenter data based on output -> write out new .star file
def main():

    # To keep track of how many particles were affected
    fileName,imageScale,selectedClasses, workingDir = load_arguements()
    data = load_star_file(workingDir+fileName)
    mouseVectors = spawn_relion_displays(selectedClasses)
    recenteredData,particleCount = recenter_classes(data, mouseVectors, workingDir)
    write_star_file(recenteredData, particleCount, workingDir, fileName)

if __name__ == "__main__":
    main()
