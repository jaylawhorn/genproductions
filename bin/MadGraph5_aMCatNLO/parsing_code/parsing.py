#!/usr/bin/env python
import sys, re, os, os.path
import subprocess
import string
import os.path
import urllib, re



#print "Plese remove any comment inside the 'define' lines, if they are present "
#print "PDF from lhapdf here:", link_pdfset
print "-----------------------------------------------------------------------"
print "-----------------------------------------------------------------------"
print """___  ___            _                             _      ______                    _               
|  \/  |           | |                           | |     | ___ \                  (_)              
| .  . |  __ _   __| |  __ _  _ __   __ _  _ __  | |__   | |_/ /  __ _  _ __  ___  _  _ __    __ _ 
| |\/| | / _` | / _` | / _` || '__| / _` || '_ \ | '_ \  |  __/  / _` || '__|/ __|| || '_ \  / _` |
| |  | || (_| || (_| || (_| || |   | (_| || |_) || | | | | |    | (_| || |   \__ \| || | | || (_| |
\_|  |_/ \__,_| \__,_| \__, ||_|    \__,_|| .__/ |_| |_| \_|     \__,_||_|   |___/|_||_| |_| \__, |
                        __/ |             | |                                                 __/ |
                       |___/              |_|                                                |___/  """

print "-----------------------------------------------------------------------"

#Return the lhapdf ID number AND check if lhaid is present only one time in the run card: if double or more "lhaid" give a Warning.
def lhaid_finder(run):
  file_run = open(run, "r") 
  word=[]
  count=0
  for line in file_run: 
    #print line
    if 'lhaid' in line: 
      word=line.split()
      count+=1  

  file_run.close()
  if count>1: 
    word[0]=-999
    return word[0]
  else:  
    return word[0]


#Return the number of flavour (4 or 5) presents in the PDF 
def num_flavour(lhaid_num,link_pdfset):
  nf=0
  f = urllib.urlopen(link_pdfset)
  myfile = f.read()
  mylist = myfile.split("\n")
  for s in mylist:
    if lhaid_num in s and 'nf_5' in s: 
      #print '\n nf5', lhaid_num
      nf=5
    if lhaid_num in s and 'nf_4' in s: 
      #print '\n nf4', lhaid_num
      nf=4

  return nf

#Return a string for "generate" line
def generate_process(proc):

  myline=[]
  file_proc=open(proc,"r")
  for lines in file_proc: 
    my_generate=[] 
    my_generate=lines.split()
    if "generate" in lines and "#" not in list(my_generate[0]):
      myline=lines.split()
      myline.remove("generate")
      myline.remove("p")
      myline.remove("p")
      myline.remove(">")
      myline.remove("@0")
      #print  myline

  file_proc.close()
  return myline


def jet_proc_finder(proc):
  ctrl_j=0
  file_proc = open(proc, "r") 
  for lines in file_proc: 
    if 'process' in lines and 'p p' in lines and not 'j' in lines:  
      ctrl_j+=1

  file_proc.close()
  return ctrl_j

def finder(card, word):
 file_my= open(card, "r") 
 for lines in file_my: 
   if word in lines and not '#' in lines:
     #print lines
     return 1
  # else: return 0
 file_my.close()

#Main function that do the parsing code...
def parsing (name, link_pdfset):
  proc=name+"_proc_card.dat"
  run=name+"_run_card.dat"

  proc_card = open(proc, "r") 
  run_card = open(run, "r") 

  #Check if only one lhaid is present 
  if lhaid_finder(run)==-999: 
    print "ERROR: define lhaid in the 'run' card ONLY one time!"
    return None
  else:  
    nf_pdf= num_flavour( lhaid_finder(run), link_pdfset )

     #----Inside PROC-CARD-----
    definedp=0
    nf_pfd_b=0
    myline=[] 
    count=0
    outputline=0
    model=0
    jet_def=0
    for line in proc_card: 
      myline=line.split()
     
      # Check if No duble definition of the proton in the proc card and Check on the right pdf has nf=5 if b/b~ in proton 
      if  'define p' in line and '#' not in  list(myline[0]):   
        myline.append(line)
        definedp+=1
        if  'b' in line  and nf_pdf !=5:
          nf_pfd_b+=1
          #print 'WARNING: plese use the correct pdf with b quark (nf==5)' 
          

      #Check if add process has correct definition (same of generate process)         
      if 'add process' in line:
        my_line=[] 
        my_line=line.split()
        myline=line.split()
        myline.remove("add")
        myline.remove("process")
        myline.remove("p")
        myline.remove("p")
        myline.remove(">")
        del myline[-1]
        if 'j' in line:
           jet_def= finder(proc,"define j")

        while 'j' in myline:
          myline.remove("j")       
        if myline!= generate_process(proc):
          count+=1
          #print '!=', myline, generate_process(proc)

      #Check if output line in in the card
      if 'output' in line and  name  in line and '-nojpeg' in line  and not '#' in line:
        outputline+=1       
      
      #Check if import model is in the card
      if 'import' in line and 'model' in line and not '#' in line: 
        model+=1


    #----Inside RUN-CARD----
    energy1=0
    energy2=0
    nevents=0
    ickkw=0
    for line in run_card: 

      if '6500' in line and '=' in line and 'ebeam1'  in line and not '#' in line: 
        energy1+=1
      if '6500' in line and '=' in line and 'ebeam2'  in line and not '#' in line:
        energy2+=1
      if '=' in line and  'nevents' in line  and not '#' in line:
        nevents+=1
      if   'ickkw' in line and '1' in line:
       if jet_proc_finder(proc)>0:
         ickkw+=1

  #---------------------------------------------------------------------------
  #Error List
  print 'Parsing for '+name+' process'
  print "-----------------------------------------------------------------------"
  print 'WARNINGS LIST  (if empty no warnings/errors in the cards)'
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  print "\n \n"

  #----Error in Proc Card----
  if definedp>1: 
    print "WARNING in Proc Card: double 'define p'. Plese define the proton only one time!"
  elif definedp<1: 
    print "WARNING in Proc Card: none proton definition. Plese add define proton process: 'define p = g u c d s u~ c~ d~ s~ b b~' "
  else: 
    print ""
    
  if nf_pfd_b>0: print 'WARNING in Proc/Run Card: plese use the correct pdf with b quark (nf==5)' 
  if count>0: print "WARNING in Proc Card: in 'add process line' NO same definition of the process that is in 'generate' line. "
  if  jet_def<1:  print "WARNING in Proc Card: no jet definition. Plese define the jat as: 'j = g u c d s u~ c~ d~ s~'  with or w/o 'b b~' "

  if outputline<1: print "WARNING in Proc Card: no/wrong output line in the proc card. Plese add this line at the END of card: 'output name_of_process -nojpeg'   "
  #else: print "GOOD"

  if model<1: print "WARNING in Proc Card: no model difined. Plese define the model as 'import model my_model' "
  #else: print "GOOD 3"



  #----Error in Run Card----
  if (energy1<1 or energy2<1): print "WARNING in Run Card: the sum of beams energy is different from 13 TeV"
  #else: print "GOOD 4"

  if  nevents<1: print "WARNING in Run Card: no 'nvents' declaration. Plese add the Number of unweighted events requested as: '1000	=  nevents' "
  #else: print "GOOD 5"

  if ickkw>0: print "WARNING in Proc/Run Card: in run card is set 'ickkw=1' but in the proc card there is NO Jet definition in 'process' line"
  #else: print "GOOD 6"

  print "\n"
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  print 'END of Parsing'
  print "-----------------------------------------------------------------------"

  proc_card.close() 
  run_card.close() 


#-------------------Run the function-----------------

#link_pdfset = "https://lhapdf.hepforge.org/pdfsets.html"
#proc = "tt012j_5f_ckm_NLO_FXFX_proc_card.dat"
#run = "tt012j_5f_ckm_NLO_FXFX_run_card.dat"

#parsing(run, proc,  link_pdfset)

#parsing("tt012j_5f_ckm_NLO_FXFX_run_card.dat","tt012j_5f_ckm_NLO_FXFX_proc_card.dat", "https://lhapdf.hepforge.org/pdfsets.html" )
#parsing("dyellell012j_5f_NLO_FXFX", "https://lhapdf.hepforge.org/pdfsets.html" )

#print sys.argv[0]
parsing(sys.argv[1], "https://lhapdf.hepforge.org/pdfsets.html" )



