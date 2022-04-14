# dssSliceAndDice
DSS Utility Script to move data between HEC-DSS files in a programmatic manner.  Original code by Evan Heisman and improved by Reyn Aoki and Ross Wickham

# files
- `dssSliceAndDice.py` Jython script that parses the .csv file to search for and copy data in blocks from one file to another
- `dssSliceAndDice.bat` .bat file that calls `setupJython.bat` and launches Jython script
- `sliceAndDicePaths.csv` example showing how to break a single DSS file into a historical and synthetic files for HEC-WAT bootstrap monte carlo (FRA compute mode) inputs.
