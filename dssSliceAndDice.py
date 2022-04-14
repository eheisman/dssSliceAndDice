# EVAN HEISMAN, NWW
# November 2015
# SliceAndDice.py
# Used to create synthetic year files required by the FRA hydrologic sampler
# These are the files stored in $WATERSHED/shared/fra/CRT_(Forecasts|Inflows)_$SYNTHETIC_NAME.dss
# Input is a CSV file.
# Columns:
#   IN_FILE - file that data is read in from
#   OUT_FILE - file that output is written to
#   WATERYEAR - Water years to read, may list single year (e.g. 1948) or a range (e.g. 1929-1948) 
#   OFFSET - Move output by this string.
#            See HecMath.shiftInTime in DSSVue Manual, Chapter 8: Scripting
#   PATH_FILTER - filters input pathnames to only those that match this filter.
#                 See getCatalogedPathnames in DSSVue Manual, Chapter 8: Scripting
#   FPART_REPLACE - replace the F part with this, if not blank.
#   SKIP
#   COMMENT
#   START_DATE / END_DATE - define window to copy if not 01OCT - 30SEP for a water year.
#                           Use this option if you need a lookback window to be copied as well.
#   All other columns are ignored.
#
# Run with execfile jython interpreter or paste into a DSSVue script.
# >>> execfile("D:/crt/hydrology/scripts/dssSliceAndDice.py")

# needs to be imported first, using "newer" feature in Python to safely handle files
from __future__ import with_statement

# From HEC libraries
from hec.heclib.dss import HecDss
from hec.heclib.util import Heclib
from hec.hecmath import TimeSeriesMath
from hec.hecmath import HecMathException

# From Python
from csv import DictReader
import os

# From Java
from java.lang import Float
from java.lang import Double
from java.lang import String
from javax.swing import JFileChooser
from javax.swing.filechooser import FileNameExtensionFilter
from java.io import File

def fileDialog(startPath=None, filter=None, title="Select file...", multiple=True, extensions=["json"]):
    """
    Returns the filename of the file selected.
    
    Pulled from Geoff Walter's Batch_Regulated_Peaks.py script
    """
    if startPath is None:
        startPath = ""
    JC = JFileChooser()
    JC.setCurrentDirectory(File(startPath))
    #JC.setSelectedFile(File(startPath))
    JC.setDialogTitle(title)
    JC.setMultiSelectionEnabled(multiple)
    JC.setDragEnabled(True)

    if filter is None:
        exFilter = FileNameExtensionFilter('Text Files', extensions)
    else:
        extensions = tuple(filter["extensions"])
        exFilter = FileNameExtensionFilter(filter["type"], extensions)
    JC.setFileFilter(exFilter)
    JC.setAcceptAllFileFilterUsed(False)
    
    if JC.showOpenDialog( JC ) == JC.APPROVE_OPTION:
        txtDirectory = JC.getCurrentDirectory()
        if JC.isMultiSelectionEnabled():
            txtPath = JC.getSelectedFiles()
        else:
            txtPath = JC.getSelectedFile()
        return txtPath.toString()
    return ""

def formatTimeString(wy, startTime="0001", wyStartDate="01Oct", wyEndDate="30Sep"):
    startWY = wy
    endWY = wy
    if "-" in str(wy):
        startWY, endWY = wy.split("-")
    return ("%s%d %s" % (wyStartDate, (int(startWY)-1), startTime), "%s%d 2400" % (wyEndDate, int(endWY)))

def copyBlock(inFilename, outFilename, WY, paths, newFPart=None, offset=None, wyStartDate="01Oct", wyEndDate="30Sep"):
    Heclib.zset("DssVersion", "", 6)
    Heclib.zset("MLVL", "", 2)
    outFile = HecDss.open(outFilename)
    #print(sd, ed)
    inFile = HecDss.open(inFilename)
    for path in paths:
        pathParts = path.split("/")[1:-1]
        startTime = "0001" # 0001 to make sure we capture the first value of the forecast OBSV paths.
        if pathParts[4].upper() == "1HOUR":   # If record is hourly, don't start until
            startTime = "2400"                # 2400 of the first day.
        sd, ed = formatTimeString(WY, startTime, wyStartDate, wyEndDate)
        try:
          data = inFile.read(path, "%s %s" % (sd, ed))
        except HecMathException:
          msg = "Unable to read HecMath object %s from file %s for %s to %s" % (path, inFilename, sd, ed)
          print(msg)
          with open(inFilename + ".log", 'a') as logFile:
            logFile.write(msg + "\n")
        if newFPart:
            data.setVersion(newFPart)
            #data.fullName = replacePart(data.fullName, "F", newFPart)
        if offset and offset != "":
            #dataHM = TimeSeriesMath()
            #dataHM.setData(data)
            data = data.shiftInTime(offset)
            #data = dataHM.getData()
        sp =  simplePaths([data.getData().fullName])[0] 
        if not (newFPart is None or newFPart.strip() == ""): #sp in simplePaths(outFile.getCatalogedPathnames()):
            data.setVersion(newFPart) #"%s_%s" % (WY, newFPart))
        if isinstance(data, TimeSeriesMath):
            tsc = data.getContainer()
            storedDoubles = False
            for v in tsc.values:
                #Figure out if data is in single or double precision
                #Should be able to use HEC storedAsdoubles parameter, but the API doesn't grab it when TimeSeriesContainers are created right now
                if abs(v-float(String.format("%.20f", Float(v)))) > abs(v-float(String.format("%.20f", Double(v)))):
                    print("storing pathname as doubles: %s" %(path))
                    storedDoubles = True
                    break
            if storedDoubles:
                tsc.storedAsdoubles = True
                tsc.fileName = outFilename
                outFile.write(tsc)
                storedDoubles = False
                continue
        outFile.write(data)
    inFile.done()
    outFile.close()

# def expandWYs(wys):
    # newList = []
    # for WY in wys:
        # #if "-" in WY:
        # #    #startWY, endWY = WY.split("-")
        # #    #newList += range(int(startWY.strip()), int(endWY.strip())+1)
        # #    newList += WY
        # #else:
        # #    newList += int(WY)
    # return newList

def replacePart(p, part, newValue=""):
    p = p.split("/")
    p[" ABCDEF".find(part.upper())] = newValue
    p = "/".join(p)
    return p
            
def simplePaths(paths):
    return list(set([replacePart(p, "D") for p in paths]))

scriptDirectory = os.path.dirname(__file__)
print(scriptDirectory)
CONFIG_FILENAME = fileDialog(startPath = scriptDirectory, title = "Select input CSV file...", multiple = False, extensions=["csv"])
#-mapBaseToSynthetics -80yr+Synthetics
#CONFIG_FILENAME = os.path.join("D:\\", "Tasks", "Preferred Alternative into CRT watershed", "CRT_HS_generation", "sliceAndDicePaths-80yr+Synthetics.csv")

Heclib.zset("DssVersion", "", 6)
Heclib.zset("MLVL", "", 2)

#Use relative file names for input/output files
relativeFilenames = True

with open(CONFIG_FILENAME, 'r') as configFile:
    inFilename = ""
    outFilename = ""
    wyString = ""
    WYs = None
    newFPart = None
    offset = None
    pathFilter = "NONE"
    wyStartDate = "01Oct"
    wyEndDate = "30Sep"
    for configLine in DictReader(configFile):
        if configLine["SKIP"].strip() != "":
            continue
        if configLine["IN_FILE"].strip() != inFilename and configLine["IN_FILE"].strip() != "":
            inFilename = configLine["IN_FILE"].strip()
            if relativeFilenames:
                inFilename = os.path.join(scriptDirectory, inFilename)
                print(inFilename)
        if configLine["OUT_FILE"].strip() != outFilename and configLine["OUT_FILE"].strip() != "":
            outFilename = configLine["OUT_FILE"].strip()
            if relativeFilenames:
                outFilename = os.path.join(scriptDirectory, outFilename)
                print(outFilename)
        if configLine["WATERYEARS"].strip() != wyString and configLine["WATERYEARS"].strip() != "":
            wyString = configLine["WATERYEARS"].strip()
            WYs = [wy.strip() for wy in wyString.split(",")]
        if configLine["OFFSET"].strip() != offset and configLine["OFFSET"].strip() != "":
            offset = configLine["OFFSET"].strip()
            if offset in ["0", ""]:
                offset = None
        if configLine["FPART_REPLACE"].strip() != newFPart:
            newFPart = configLine["FPART_REPLACE"].strip()
        if configLine["PATH_FILTER"].strip() != pathFilter and configLine["PATH_FILTER"].strip() != "":
            pathFilter = configLine["PATH_FILTER"].strip()
        if configLine["START_DATE"].strip() != wyStartDate and configLine["START_DATE"].strip() != "":
            wyStartDate =  configLine["START_DATE"].strip()
        if configLine["END_DATE"].strip() != wyEndDate and configLine["END_DATE"].strip() != "":
            wyEndDate =  configLine["END_DATE"].strip()
        inFile = HecDss.open(inFilename)
        paths = inFile.getCatalogedPathnames()
        if pathFilter != "NONE":
            paths = simplePaths(inFile.getCatalogedPathnames(pathFilter))
        inFile.done()
        for wy in WYs:
            copyBlock(inFilename, outFilename, wy, paths, newFPart, offset, wyStartDate, wyEndDate)
