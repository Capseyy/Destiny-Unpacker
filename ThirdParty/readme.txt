The tool is used via the command line:

MontevenDynamicExtractor -p [packages path] -o [output path] -n [file name] -i [input hash] -t -b [package ID] -a [api hash]

The required arguments are -p and one of -i, -b, or -a. Backslashes will not work for file paths.

    -p [packages path]: package path for Destiny 2. An example might be I:/SteamLibrary/steamapps/common/Destiny 2/packages
    -o [output path]: the output path, by default is the current directory
    -n [file name]: the file name of the target folder and files, by default is the hash provided
    -i [input hash]: the input hash. To get hashes to extract, either use the batch command or the public sheets page
    -t: enable texture extraction
    -b [package ID]: will extract every dynamic model given for a package ID. For the package "w64_sr_combatants_01ba_4", the package ID would be "01ba"
	-c: extracts cbuffers

A batch file (run.bat) is provided for ease-of-use to users who may not be well versed with using the command line. 
The run.bat file can be edited to your preferences by "Right Click -> Edit" which will open the file in Notepad.
Double clicking the run.bat file will open the extractor.