

libname MDA ". . . . filepath here. . . . "; /*This is the location of where you would like the MDA data to be stored, as well as the downloadindex file*/

*-----------------------------------------------------------------------------------------;
*MDA Postive Versus Negative;
*-----------------------------------------------------------------------------------------;
PROC IMPORT OUT= WORK.MDA_DATA 
            DATAFILE= ". . . . \SampleData_Master.xlsx" /*File path of the SampleData_Master excelfile*/
            DBMS=EXCEL REPLACE;
     RANGE="V5.0$"; 
     GETNAMES=NO;
     MIXED=NO;
     SCANTEXT=YES;
     USEDATE=YES;
     SCANTIME=YES;
RUN;

data MDA_DATA; set MDA_DATA;
ACQ=input(trim(substr(F1,find(F1,',',-length(F1))+1,length(F1))),12.);
F1=trim(substr(F1,1,find(F1,',',-length(F1))-1));
run;
data MDA_DATA; set MDA_DATA;
NEG=input(trim(substr(F1,find(F1,',',-length(F1))+1,length(F1))),12.);
F1=trim(substr(F1,1,find(F1,',',-length(F1))-1));
run;
data MDA_DATA; set MDA_DATA;
POS=input(trim(substr(F1,find(F1,',',-length(F1))+1,length(F1))),12.);
F1=trim(substr(F1,1,find(F1,',',-length(F1))-1));
run;
data MDA_DATA; set MDA_DATA;
TWORDS=input(trim(substr(F1,find(F1,',',-length(F1))+1,length(F1))),12.);
F1=trim(substr(F1,1,find(F1,',',-length(F1))-1));
run;
data MDA_DATA; set MDA_DATA;
SECTIONS=input(trim(substr(F1,find(F1,',',-length(F1))+1,length(F1))),12.);
F1=trim(substr(F1,1,find(F1,',',-length(F1))-1));
run;
data MDA_DATA; set MDA_DATA;
REPDATE=trim(substr(F1,find(F1,',',-length(F1))+1,length(F1)));
F1=trim(substr(F1,1,find(F1,',',-length(F1))-1));
run;
data MDA_DATA; set MDA_DATA;
SIC=input(trim(substr(F1,find(F1,',',-length(F1))+1,length(F1))),12.);
F1=trim(substr(F1,1,find(F1,',',-length(F1))-1));
run;
data MDA_DATA; set MDA_DATA;
CIK=input(trim(substr(F1,find(F1,',',-length(F1))+1,length(F1))),12.);
F1=trim(substr(F1,1,find(F1,',',-length(F1))-1));
run;
data MDA_DATA; set MDA_DATA;
FILING=input(trim(substr(F1,1,find(F1,',',1)-1)),12.);
COMNAM=trim(substr(F1,find(F1,',',1)+1,length(F1)));
run;

DATA mda_data; set mda_data;
	year=input(substr(strip(REPDATE),1,4),12.);
	month=input(substr(strip(REPDATE),5,2),12.);
	day=input(substr(strip(REPDATE),7,2),12.);
run;
data mda_data; set mda_data; 
	datadate=intnx('month',mdy(month,day,year), 0, 'e');
	format datadate date9.;
run;

/*Obtain filing date, filetype, link from the downloadindex file*/
Proc sql; 
	create table MDA_DATA as 
	select a.*, b.filingdate, b.link, b.filetype 
	from MDA_DATA a left outer join mergers.downloadindex b
		on a.filing=b.filing 
	order by filing; 
quit; 
Proc sql; 
	create table MDA_DATA_SIMPLE as 
	select filing, filetype label='File Type', cik, COMNAM, datadate, filingdate, NEG, POS, TWORDS, (POS-NEG)/TWORDS as TONE, ACQ, link
	from MDA_DATA 
	order by filing; 
quit; 

/*Word count restriction for valid MD&A sections*/
data mda_data_simple; set mda_data_simple; if TWORDS>250; run;

Proc means data=MDA_DATA_SIMPLE N mean Median min max std; var TONE ACQ TWORDS; run;

data MDA.mda_github; set MDA_DATA_SIMPLE; run;


