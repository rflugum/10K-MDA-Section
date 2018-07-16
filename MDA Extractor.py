"""
This code extracts the MD&A sections from 10K financial statements.  The list of paths for the respective 10K's
are obtained from the SEC's master files giving paths to all of the public documents that are filed with the SEC
in each quarter.  The repository includes that actual download links (i.e. downloadindex.sas7bdat and downloadlist.txt) 
that we use in our study.  Our links include all filings classified as '10-K','10-K/A','10-K405/A','10-K405','10-KSB',
'10-KSB/A','10KSB','10KSB/A','10KSB40','10KSB40/A' from 2002 to 2016. 
"""

import csv
import requests
import re
import os

######################################################################################
######################################################################################
# This section is for functions that are used throughout the scrape
######################################################################################
######################################################################################

########################## Obtain file Information ###################################
def parse(file1, file2):
    hand=open(file1)
    IDENTITY=""
    for line in hand:
        line=line.strip()
        if re.findall('^COMPANY CONFORMED NAME:',line):
            k = line.find(':')
            comnam=line[k+1:]
            comnam=comnam.strip()
            IDENTITY='<HEADER>\nCOMPANY NAME: '+str(comnam)+'\n'                                         
            break
        
    hand=open(file1)
    for line in hand:
        line=line.strip()
        if re.findall('^CENTRAL INDEX KEY:',line):
            k = line.find(':')
            cik=line[k+1:]
            cik=cik.strip()
            #print cik
            IDENTITY=IDENTITY+'CIK: '+str(cik)+'\n'
            break
        
    hand=open(file1)
    for line in hand:
        line=line.strip()
        if re.findall('^STANDARD INDUSTRIAL CLASSIFICATION:',line):
            k = line.find(':')
            sic=line[k+1:]
            sic=sic.strip()
            siccode=[]
            for s in sic: 
                if s.isdigit():
                    siccode.append(s)    
            #print siccode
            IDENTITY=IDENTITY+'SIC: '+''.join(siccode)+'\n'
            break
        
    hand=open(file1)
    for line in hand:
        line=line.strip()
        if re.findall('^CONFORMED SUBMISSION TYPE:',line):
            k = line.find(':')
            subtype=line[k+1:]
            subtype=subtype.strip()
            #print subtype
            IDENTITY=IDENTITY+'FORM TYPE: '+str(subtype)+'\n'
            break
            
    hand=open(file1)
    for line in hand:
        line=line.strip()
        if re.findall('^CONFORMED PERIOD OF REPORT:',line):
            k = line.find(':')
            cper=line[k+1:]
            cper=cper.strip()
            #print cper
            IDENTITY=IDENTITY+'REPORT PERIOD END DATE: '+str(cper)+'\n'
            break
            
    hand=open(file1)
    for line in hand:
        line=line.strip()
        if re.findall('^FILED AS OF DATE:',line):
            k = line.find(':')
            fdate=line[k+1:]
            fdate=fdate.strip()
            #print fdate                                
            IDENTITY=IDENTITY+'FILE DATE: '+str(fdate)+'\n'+'</HEADER>\n'
            break
            
    with open(file2, 'a') as f:
        f.write(str(IDENTITY))
        f.close()
    hand.close()

###########################  DELETE HEADER INFORMATION  #######################################

def headerclean(temp, temp1):
    mark0=0
    strings1=['</SEC-HEADER>','</IMS-HEADER>']
    hand=open(temp)
    hand.seek(0)
    for x, line in enumerate(hand):
        line=line.strip()
        if any(s in line for s in strings1):
            mark0=x
            break
    hand.seek(0)
    
    newfile=open(temp1,'w')
    for x, line in enumerate(hand):
        if x>mark0:
            newfile.write(line)
    hand.close()
    newfile.close()
    
    newfile=open(temp1,'r')
    hand=open(temp,'w')        
    for line in newfile:
        if "END PRIVACY-ENHANCED MESSAGE" not in line:
            hand.write(line)                
    hand.close()                
    newfile.close()

###########################  XBRL Cleaner  ###################################################

def xbrl_clean(cond1, cond2, str0):
    locations=[0]
    #print locations
    placement1=[]
    str0=str0.lower()
    for m in re.finditer(cond1, str0):
        a=m.start()
        placement1.append(a)
    #print placement1
    
    if placement1!=[]:
        placement2=[]
        for m in re.finditer(cond2, str0):
            a=m.end()
            placement2.append(a)
    #    print placement2
        
        len1=len(placement1)
        placement1.append(len(str0))
        
        for i in range(len1):
            placement3=[]
            locations.append(placement1[i])
            for j in placement2:
                if (j>placement1[i] and j<placement1[i+1]):
                    placement3.append(j)
                    break
            if placement3!=[]:
                locations.append(placement3[0])
            else:
                locations.append(placement1[i])
    
    #print locations
    return locations

###########################  Table Cleaner  ###################################################

def table_clean(cond1, cond2, str1):
    Items0=["item 7", "item7", "item8", "item 8"]
    Items1=["item 1", "item 2","item 3","item 4","item 5","item 6","item 9", "item 10", "item1", "item2","item3","item4","item5","item6","item9", "item10"]
    
    str2=str1.lower()
    placement1=[]
    for m in re.finditer(cond1, str2):
        a=m.start()
        placement1.append(a)
    n=len(placement1)
    placement1.append(len(str2))
    
    placement2=[]
    for m in re.finditer(cond2, str2):
        a=m.end()
        placement2.append(a)
        
    if (placement1!=[] and placement2!=[]):
        current=str1[0:placement1[0]]
        
        for i in range(n):
            begin=placement1[i]
            for j in placement2:
                if j>begin:
                    end=j
                    break
            
            if end=="":
                current=current+str1[begin:placement1[i+1]]
            else:
                str2=""
                str2=str1[begin:end].lower()
                str2=str2.replace("&nbsp;"," ")
                str2=str2.replace("&NBSP;"," ")
                p = re.compile(r'&#\d{1,5};')
                str2=p.sub("",str2)
                p = re.compile(r'&#.{1,5};')
                str2=p.sub("",str2)
                if any(s in str2 for s in Items0):
                    if not any(s in str2 for s in Items1):
                        current=current+str2
                    
                current=current+str1[end:placement1[i+1]]
                end=""
    else:
        current=str1
    return current
    
###############################################################################################
###############################################################################################
# This section is the actual program
###############################################################################################
###############################################################################################
'''
This is the filepath of where you would like the text files of possible MD&A sections to be saved.  It is also the location of the downloadlist.txt file
that includes all of the filing links.
'''
filepath="C:\\Users\\rdf0969\\Documents\\Financial Statement Data"   

###############################################################################
#This is the master download file that include all of the links to SEC filings.
###############################################################################
download=os.path.join(filepath,"downloadlist.txt")


#############################################################################################################
#The are just hosting text files that can be ignored.  You need them to recored the data as the program runs.
#############################################################################################################
temp=os.path.join(filepath,"temp.txt")
temp1=os.path.join(filepath,"newfile.txt")

#################################################################################
#This is the file that records the number of sections for each respective filing.
#################################################################################
LOG=os.path.join(filepath,"DOWNLOADLOG.txt")
with open(LOG,'w') as f:
    f.write("Filer\tSECTIONS\n")
    f.close()

######## Download the filing ############
with open(download, 'r') as txtfile:
    reader = csv.reader(txtfile, delimiter=',')
    for line in reader:
        #print line
        FileNUM=line[0].strip()
        Filer=os.path.join(filepath, str(line[0].strip())+".txt")
        url = 'https://www.sec.gov/Archives/' + line[1].strip()
        with open(temp, 'w') as f:
            f.write(requests.get('%s' % url).content)
        f.close()
        
##### Obtain Header Information on Filing ######################        
        
        parse(temp, Filer)
        headerclean(temp, temp1)
        
##### ASCII Section ######################        
    
        with open(temp,'r') as f:
            str1=f.read()
            output=str1
            locations_xbrlbig=xbrl_clean("<type>zip", "</document>", output)
            locations_xbrlbig.append(len(output))
            
            if locations_xbrlbig!=[]:
                str1=""
                if len(locations_xbrlbig)%2==0:
                    for i in xrange(0,len(locations_xbrlbig),2):
                        str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]

        f.close
        output=str1
        locations_xbrlbig=xbrl_clean("<type>graphic", "</document>", output)
        locations_xbrlbig.append(len(output))
        
        if locations_xbrlbig!=[0]:
            str1=""
            if len(locations_xbrlbig)%2==0:
                for i in xrange(0,len(locations_xbrlbig),2):
                    str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]
        
        output=str1
        locations_xbrlbig=xbrl_clean("<type>excel", "</document>", output)
        locations_xbrlbig.append(len(output))
        
        if locations_xbrlbig!=[0]:
            str1=""
            if len(locations_xbrlbig)%2==0:
                for i in xrange(0,len(locations_xbrlbig),2):
                    str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]
                    
        output=str1
        locations_xbrlbig=xbrl_clean("<type>pdf", "</document>", output)
        locations_xbrlbig.append(len(output))
        
        if locations_xbrlbig!=[0]:
            str1=""
            if len(locations_xbrlbig)%2==0:
                for i in xrange(0,len(locations_xbrlbig),2):
                    str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]
        
        output=str1
        locations_xbrlbig=xbrl_clean("<type>xml", "</document>", output)
        locations_xbrlbig.append(len(output))
        
        if locations_xbrlbig!=[0]:
            str1=""
            if len(locations_xbrlbig)%2==0:
                for i in xrange(0,len(locations_xbrlbig),2):
                    str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]

        output=str1
        locations_xbrlbig=xbrl_clean("<type>ex", "</document>", output)
        locations_xbrlbig.append(len(output))
        
        if locations_xbrlbig!=[0]:
            str1=""
            if len(locations_xbrlbig)%2==0:
                for i in xrange(0,len(locations_xbrlbig),2):
                    str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]
                    
######Remove <DIV>, <TR>, <TD>, and <FONT>###########################
                   
        p = re.compile(r'(<DIV.*?>)|(<DIV\n.*?>)|(<DIV\n\r.*?>)|(<DIV\r\n.*?>)|(<DIV.*?\n.*?>)|(<DIV.*?\n\r.*?>)|(<DIV.*?\r\n.*?>)')
        str1=p.sub("",str1)
        p = re.compile(r'(<div.*?>)|(<div\n.*?>)|(<div\n\r.*?>)|(<div\r\n.*?>)|(<div.*?\n.*?>)|(<div.*?\n\r.*?>)|(<div.*?\r\n.*?>)')
        str1=p.sub("",str1)
        p = re.compile(r'(<TD.*?>)|(<TD\n.*?>)|(<TD\n\r.*?>)|(<TD\r\n.*?>)|(<TD.*?\n.*?>)|(<TD.*?\n\r.*?>)|(<TD.*?\r\n.*?>)')
        str1=p.sub("",str1)
        p = re.compile(r'(<td.*?>)|(<td\n.*?>)|(<td\n\r.*?>)|(<td\r\n.*?>)|(<td.*?\n.*?>)|(<td.*?\n\r.*?>)|(<td.*?\r\n.*?>)')
        str1=p.sub("",str1)
        p = re.compile(r'(<TR.*?>)|(<TR\n.*?>)|(<TR\n\r.*?>)|(<TR\r\n.*?>)|(<TR.*?\n.*?>)|(<TR.*?\n\r.*?>)|(<TR.*?\r\n.*?>)')
        str1=p.sub("",str1)
        p = re.compile(r'(<tr.*?>)|(<tr\n.*?>)|(<tr\n\r.*?>)|(<tr\r\n.*?>)|(<tr.*?\n.*?>)|(<tr.*?\n\r.*?>)|(<tr.*?\r\n.*?>)')
        str1=p.sub("",str1)
        p = re.compile(r'(<FONT.*?>)|(<FONT\n.*?>)|(<FONT\n\r.*?>)|(<FONT\r\n.*?>)|(<FONT.*?\n.*?>)|(<FONT.*?\n\r.*?>)|(<FONT.*?\r\n.*?>)')
        str1=p.sub("",str1)
        p = re.compile(r'(<font.*?>)|(<font\n.*?>)|(<font\n\r.*?>)|(<font\r\n.*?>)|(<font.*?\n.*?>)|(<font.*?\n\r.*?>)|(<font.*?\r\n.*?>)')
        str1=p.sub("",str1)
        p = re.compile(r'(<P.*?>)|(<P\n.*?>)|(<P\n\r.*?>)|(<P\r\n.*?>)|(<P.*?\n.*?>)|(<P.*?\n\r.*?>)|(<P.*?\r\n.*?>)')
        str1=p.sub("",str1)
        p = re.compile(r'(<p.*?>)|(<p\n.*?>)|(<p\n\r.*?>)|(<p\r\n.*?>)|(<p.*?\n.*?>)|(<p.*?\n\r.*?>)|(<p.*?\r\n.*?>)')
        str1=p.sub("",str1)
        str1=str1.replace("</DIV>","")
        str1=str1.replace("</div>","")
        str1=str1.replace("</TR>","")
        str1=str1.replace("</tr>","")
        str1=str1.replace("</TD>","")
        str1=str1.replace("</td>","")
        str1=str1.replace("</FONT>","")
        str1=str1.replace("</font>","")
        str1=str1.replace("</P>","")
        str1=str1.replace("</p>","")
        
############# Remove XBRL Sections #########################
                
        output=str1
        locations_xbrlsmall=xbrl_clean("<xbrl", "</xbrl.*>", output)
        locations_xbrlsmall.append(len(output))
        
        if locations_xbrlsmall!=[0]:
            str1=""
            if len(locations_xbrlsmall)%2==0:
                for i in xrange(0,len(locations_xbrlsmall),2):
                    str1=str1+output[locations_xbrlsmall[i]:locations_xbrlsmall[i+1]]
        
############# Remove Teble Sections #########################

        output1=table_clean('<table','</table>',str1)
        
############# Remove Newlines and Carriage Returns #########################

        str1=str1.replace("\r\n"," ")
        p = re.compile(r'<.*?>')
        str1=p.sub("",str1)
        
############# Remove '<a' and '<hr' and <sup Sections #########################        
        
        str1=str1.replace("&nbsp;"," ")
        str1=str1.replace("&NBSP;"," ")
        str1=str1.replace("&LT;","LT")
        str1=str1.replace("&#60;","LT")
        str1=str1.replace("&#160;"," ")
        str1=str1.replace("&AMP;","&")
        str1=str1.replace("&amp;","&")
        str1=str1.replace("&#38;","&")
        str1=str1.replace("&APOS;","'")
        str1=str1.replace("&apos;","'")
        str1=str1.replace("&#39;","'")
        str1=str1.replace('&QUOT;','"')
        str1=str1.replace('&quot;','"')
        str1=str1.replace('&#34;','"')
        str1=str1.replace("\t"," ")
        str1=str1.replace("\v","")
        str1=str1.replace("&#149;"," ")
        str1=str1.replace("&#224;","")
        str1=str1.replace("&#145;","")
        str1=str1.replace("&#146;","")
        str1=str1.replace("&#147;","")
        str1=str1.replace("&#148;","")
        str1=str1.replace("&#151;"," ")
        str1=str1.replace("&#153;","") 
        str1=str1.replace("&#111;","")
        str1=str1.replace("&#153;","")
        str1=str1.replace("&#253;","")
        str1=str1.replace("&#8217;","")
        str1=str1.replace("&#32;"," ")
        str1=str1.replace("&#174;","")
        str1=str1.replace("&#167;","")
        str1=str1.replace("&#169;","")
        str1=str1.replace("&#8220;","")
        str1=str1.replace("&#8221;","")
        str1=str1.replace("&rsquo;","")
        str1=str1.replace("&lsquo;","")
        str1=str1.replace("&sbquo;","")
        str1=str1.replace("&bdquo;","")
        str1=str1.replace("&ldquo;","")
        str1=str1.replace("&rdquo;","")
        str1=str1.replace("\'","")
        p = re.compile(r'&#\d{1,5};')
        str1=p.sub("",str1)
        p = re.compile(r'&#.{1,5};')
        str1=p.sub("",str1)
        str1=str1.replace("_"," ")
        str1=str1.replace("and/or","and or")
        str1=str1.replace("-\n"," ")
        p = re.compile(r'\s*-\s*')
        str1=p.sub(" ",str1)
        p = re.compile(r'(-|=)\s*')
        str1=p.sub(" ",str1)
        p = re.compile(r'\s\s*')
        str1=p.sub(" ",str1)
        p = re.compile(r'(\n\s*){3,}')
        str1=p.sub("\n\n",str1)
        p = re.compile(r'<.*?>')
        str1=p.sub("",str1)

################################## MD&A Section #####################################################
        
        item7={}
        item7[1]="item 7\. managements discussion and analysis"
        item7[2]="item 7\.managements discussion and analysis"
        item7[3]="item7\. managements discussion and analysis"
        item7[4]="item7\.managements discussion and analysis"
        item7[5]="item 7\. management discussion and analysis"
        item7[6]="item 7\.management discussion and analysis"
        item7[7]="item7\. management discussion and analysis"
        item7[8]="item7\.management discussion and analysis"
        item7[9]="item 7 managements discussion and analysis"
        item7[10]="item 7managements discussion and analysis"
        item7[11]="item7 managements discussion and analysis"
        item7[12]="item7managements discussion and analysis"
        item7[13]="item 7 management discussion and analysis"
        item7[14]="item 7management discussion and analysis"
        item7[15]="item7 management discussion and analysis"
        item7[16]="item7management discussion and analysis"
        item7[17]="item 7: managements discussion and analysis"
        item7[18]="item 7:managements discussion and analysis"
        item7[19]="item7: managements discussion and analysis"
        item7[20]="item7:managements discussion and analysis"
        item7[21]="item 7: management discussion and analysis"
        item7[22]="item 7:management discussion and analysis"
        item7[23]="item7: management discussion and analysis"
        item7[24]="item7:management discussion and analysis"
        
        
        item8={}
        item8[1]="item 8\. financial statements"
        item8[2]="item 8\.financial statements"
        item8[3]="item8\. financial statements"
        item8[4]="item8\.financial statements"
        item8[5]="item 8 financial statements"
        item8[6]="item 8financial statements"
        item8[7]="item8 financial statements"
        item8[8]="item8financial statements"
        item8[9]="item 8a\. financial statements"
        item8[10]="item 8a\.financial statements"
        item8[11]="item8a\. financial statements"
        item8[12]="item8a\.financial statements"
        item8[13]="item 8a financial statements"
        item8[14]="item 8afinancial statements"
        item8[15]="item8a financial statements"
        item8[16]="item8afinancial statements"
        item8[17]="item 8\. consolidated financial statements"
        item8[18]="item 8\.consolidated financial statements"
        item8[19]="item8\. consolidated financial statements"
        item8[20]="item8\.consolidated financial statements"
        item8[21]="item 8 consolidated  financial statements"
        item8[22]="item 8consolidated financial statements"
        item8[23]="item8 consolidated  financial statements"
        item8[24]="item8consolidated financial statements"
        item8[25]="item 8a\. consolidated financial statements"
        item8[26]="item 8a\.consolidated financial statements"
        item8[27]="item8a\. consolidated financial statements"
        item8[28]="item8a\.consolidated financial statements"
        item8[29]="item 8a consolidated financial statements"
        item8[30]="item 8aconsolidated financial statements"
        item8[31]="item8a consolidated financial statements"
        item8[32]="item8aconsolidated financial statements"
        item8[33]="item 8\. audited financial statements"
        item8[34]="item 8\.audited financial statements"
        item8[35]="item8\. audited financial statements"
        item8[36]="item8\.audited financial statements"
        item8[37]="item 8 audited financial statements"
        item8[38]="item 8audited financial statements"
        item8[39]="item8 audited financial statements"
        item8[40]="item8audited financial statements"
        item8[41]="item 8: financial statements"
        item8[42]="item 8:financial statements"
        item8[43]="item8: financial statements"
        item8[44]="item8:financial statements"
        item8[45]="item 8: consolidated financial statements"
        item8[46]="item 8:consolidated financial statements"
        item8[47]="item8: consolidated financial statements"
        item8[48]="item8:consolidated financial statements"
        
        look={" see ", " refer to ", " included in "," contained in "}
        
        a={}
        c={}
       
        lstr1=str1.lower()
        for j in range(1,25):
            a[j]=[]
            for m in re.finditer(item7[j], lstr1):
                if not m:
                    break
                else:
                    substr1=lstr1[m.start()-20:m.start()]
                    if not any(s in substr1 for s in look):   
                        #print substr1
                        b=m.start()
                        a[j].append(b)
        #print i
    
        list1=[]
        for value in a.values():
            for thing1 in value:
                list1.append(thing1)
        list1.sort()
        list1.append(len(lstr1))
        #print list1
               
        for j in range(1,49):
            c[j]=[]
            for m in re.finditer(item8[j], lstr1):
                if not m:
                    break
                else:
                    substr1=lstr1[m.start()-20:m.start()]
                    if not any(s in substr1 for s in look):   
                        #print substr1
                        b=m.start()
                        c[j].append(b)
        list2=[]
        for value in c.values():
            for thing2 in value:
                list2.append(thing2)
        list2.sort()
        
        locations={}
        if list2==[]:
            print "NO MD&A"
        else:
            if list1==[]:
                print "NO MD&A"
            else:
                for k0 in range(len(list1)):
                    locations[k0]=[]
                    locations[k0].append(list1[k0])
                for k0 in range(len(locations)):
                    for item in range(len(list2)):
                        if locations[k0][0]<=list2[item]:
                            locations[k0].append(list2[item])
                            break
                    if len(locations[k0])==1:
                        del locations[k0]
        
        if locations=={}:
            with open(LOG,'a') as f:
                f.write(str(FileNUM)+"\t"+"0\n")
                f.close()
        else:
            sections=0
            for k0 in range(len(locations)): 
                substring2=str1[locations[k0][0]:locations[k0][1]]
                substring3=substring2.split()
                if len(substring3)>250:
                    sections=sections+1
                    with open(Filer,'a') as f:
                        f.write("<SECTION>\n")
                        f.write(substring2+"\n")
                        f.write("</SECTION>\n")
                        f.close()
            with open(LOG,'a') as f:
                    f.write(str(FileNUM)+"\t"+str(sections)+"\n")
                    f.close()
        print FileNUM
     
        
