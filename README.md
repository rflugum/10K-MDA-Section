# 10K-MDA-Section
These programs (i.e., MDA Extractor.py and MDA Cleaner and Tone Calculator.py) will extract the Management Discussion and Analyses (MD&A) section from 10K Financial Statements and calculate the tone of these sections.  You must use the attached files that contain the list of 10K files paths on the SEC servers.  The program will output the sections that are potential MD&A sections and calculate the tone accordingly.  For details as to how this data is used, please refer to "Do Tone Changes in Financial Statements Predict Acquisition Behavior?" by John Berns, Patty Bick, Ryan Flugum and Reza Houston.  A detailed list of the included documents and programs in this repository are as follows:

## downloadindex.csv
This is a csv file that includes all of the SEC filings classified as '10-K','10-K/A','10-K405/A','10-K405','10-KSB', '10-KSB/A','10KSB','10KSB/A','10KSB40','10KSB40/A' from 2002 to 2016.  This data is obtained from the SEC archive located here https://www.sec.gov/Archives/edgar/full-index/.  Note that this dataset contains the number of each filing that I assign.  You will use this index throughout the process as 'filing' is the main identifier that I use for each filing.

## downloadlist.txt
This is the text file that includes the filing number and links to be used in the MDA Extractor.py program.  This text file is a subset of the downloadindex sas dataset and includes only the 'filing' and 'link' columns.

## Word Dictionary Files
This file includes the Positive and Negative word dictionaries that are used to calculate the tone of the MD&A sections.  Specifically, the POSITIVE.txt and NEGATIVE.txt files are used in the MDA Cleaner and Tone Calculator.py programs.  These dictionaries were contructed by Tim Loughran and Bill McDonald and are used in Loughran and McDonald (2011).  These dictionaries, as well as other word classifications, can be obtained at https://sraf.nd.edu/. 

## MDA_Tone.csv
This is the sas dataset that includes the final output of Managment Discussion and Analysis tone of each financial statement.  If you would not like to understand the attached programs and would just like the resulting output, use this dataset.  Also, please note that some filings have multiple possible MD&A sections - please evaluate the data carefully and make sure that each filing has only one tone measurement. 

## MDA Data Construction.sas
This is a sas program that constructs MDA_Tone.csv.  The program uses the SampleData.txt output from running the MDA Cleaner and Tone Calculator.py program.  Note that you must convert SampleData.txt to an excel document before using this program because I import data via excel into the sas program.

## MDA Extractor.py
This is the python program that extracts the possible Management Discussion and Analysis (MD&A) section/s from 10K financial statements.  The input file for this program is downloadlist.txt.  In order to identify possible MD&A sections, we search for combinations of "Item 7. Managements Discussion and Analysis" that include:

"item 7\. managements discussion and analysis"
"item 7\.managements discussion and analysis"
"item7\. managements discussion and analysis"
"item7\.managements discussion and analysis"
"item 7\. management discussion and analysis"
"item 7\.management discussion and analysis"
"item7\. management discussion and analysis"
"item7\.management discussion and analysis"
"item 7 managements discussion and analysis"
"item 7managements discussion and analysis"
"item7 managements discussion and analysis"
"item7managements discussion and analysis"
"item 7 management discussion and analysis"
"item 7management discussion and analysis"
"item7 management discussion and analysis"
"item7management discussion and analysis"
"item 7: managements discussion and analysis"
"item 7:managements discussion and analysis"
"item7: managements discussion and analysis"
"item7:managements discussion and analysis"
"item 7: management discussion and analysis"
"item 7:management discussion and analysis"
"item7: management discussion and analysis"
"item7:management discussion and analysis"

The program includes all sections of the financial statement that begin with one of the above phrases, copy each section of text into a new text document to be further cleaned and verified.

## MDA Cleaner and Tone Calculator.py
This is the python program that cleans the output text files from MDA Extractor.py.  The input files for this program are all of the output text files from MDA Extractor.py, the POSTIVE and NEGATIVE word dictionaries, and the downloadlog.txt file created from MDA Extractor.py.  The output is SampleData.txt which include the number of postive, negative, and total words, along with the tone, of a verified MD&A section.  In order to be classified as an MD&A section, the first 5 sentences of the respective section must include one of the following phrases:  "the following discussion", "this discussion and analysis", "should be read in conjunction", "should be read together with", "the following managements discussion and analysis".  Additionally, we identify possible acquisition terms that include: "Acquisition", "acquisition", "merger", "Merger", "Buyout", "buyout".  The tone of the respective section is the difference between the number of negative and positive words, scaled by the total number of words in the section.

