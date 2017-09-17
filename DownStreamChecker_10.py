import sys
from Bio import SeqIO
import os
import subprocess
import glob
import sys
from Bio.Blast.Applications import NcbiblastnCommandline
from io import StringIO
from Bio.Blast import NCBIXML
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
from Bio.Blast import NCBIXML
import subprocess
import glob
from os.path import basename
import operator


def FindTE(file):
    with open(file,"r",encoding='utf-8',errors='ignore') as f:
        lines = f.readlines()
        setlist = []
        for i in range(len(lines) - 2):
            columns = lines[i].split()
            nextcolumns=lines[i+1].split()
            if (columns[0]!="#"):
                plist=[]
                firststart = int(columns[6])
                firstend = int(columns[7])
                secondstart = int(nextcolumns[6])
                secondend = int(nextcolumns[7])
                fisrtFam = columns[1]
                secondFam = nextcolumns[1]
                if (firststart!=secondstart and secondstart-firststart<=50000 and fisrtFam[0:5]==secondFam[0:5]and firstend<secondstart):
                    plist.append(firststart)
                    plist.append(firstend)
                    plist.append(secondstart)
                    plist.append(secondend)
                    setlist.append(plist)
    return setlist

# print(FindTE("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/TEVSRice.tsv"))
# list=FindTE("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/TEVSRice.tsv")
# print(len(list))

def getFile(file):
    mkout="touch DupTE.tsv"
    os.system(mkout)
    Output=open("DupTE.tsv", 'r+')
    with open(file,"r",encoding='utf-8',errors='ignore') as f:
        lines = f.readlines()
        for i in range(len(lines) - 2):
            columns = lines[i].split()
            nextcolumns=lines[i+1].split()
            if (columns[0]!="#"):
                firststart=int(columns[6])
                firstend=int(columns[7])
                secondstart=int(nextcolumns[6])
                secondend=int(nextcolumns[7])
                fisrtFam=columns[1]
                secondFam=nextcolumns[1]
                if (firststart!=secondstart and secondstart-firststart<=50000 and fisrtFam[0:5]==secondFam[0:5] and firstend<secondstart):
                    Output.write(lines[i])
                    Output.write(lines[i+1])
                    Output.write("\n")

    Output.close()
    return Output

# getFile("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/TEVSRice.tsv")

###get the length of duplication(single Copy)
def getInter(file):
    list=FindTE(file)
    Interlist=[]
    for i in range(0,len(list)):
        ele=list[i]
        inter=ele[2]-ele[1]
        Interlist.append(inter)
    return Interlist

# list=getInter("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/TEVSRice.tsv")
# print(list)
# print(max(list))

def get_seq(seq):
    out = ''
    split = seq.split('\n')
    for sp in split:
        if any([i.isdigit() for i in sp]):
            continue
        out += sp
    return out

###Get seq by Blastcmd according to positions
def getseq(start, end, db, entry,name):
    seq1 = subprocess.check_output("blastdbcmd -db '%s' -entry '%s' -range '%s'-'%s'" % (db,int(entry),int(start), int(end)), shell=True)
    seq1 = seq1.decode("utf-8")
    seq1=get_seq(seq1)
    seq1 = SeqRecord(Seq(seq1))
    SeqIO.write(seq1, "%s.fasta"%(name), "fasta")

getseq(21824667,21830252,"/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Arabidopsis/Genome/Ara_ncbi/Arabidopsis.fa",1,"Araseq2")

###Select 1HSP candidates
def get1HSP(infile, outfile):
    mkfile="touch %s"%(outfile)
    os.system(mkfile)
    output=open(outfile,"r+")
    for line in open(infile):
        columns=line.split()
        if(columns[4]=="1"):
            output.write(line)

    output.close()
#
# get1HSP("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/Rice_1.fa.selfd.dds2.selfd.sort","/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1HSP")


### DDS2 output Duplications blast with TE database
def DupBlastTE(Dupfile, db, entry, BlastFile, Folder):
    os.chdir(Folder)
    for line in open(Dupfile):
        columns=line.split()
        firststart=columns[1]
        firstend=columns[2]
        secondstart=columns[5]
        secondend=columns[6]
        getseq(firststart,firstend,db,entry,"firstSeq")
        Output1=NcbiblastnCommandline(query="firstSeq.fasta",subject=BlastFile,out="%s-u"%(firststart), outfmt=7)()
        getseq(secondstart,secondend,db,entry,"secondSeq")
        Output2=NcbiblastnCommandline(query="secondSeq.fasta",subject=BlastFile,out="%s-u"%(secondstart), outfmt=7)()
        catfile="cat %s-u %s-u > %s-c"%(firststart,secondstart,firststart)
        os.system(catfile)
        os.remove('firstSeq.fasta')
        os.remove('secondSeq.fasta')
        os.remove('%s-u' % (firststart))
        os.remove('%s-u' % (secondstart))
#
# DupBlastTE("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DDS2/chr1_100k",
#            "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/Oryza_sativa_ncbi/Oryza_sativa.fa",
#            1,"/Users/weijiasu/Downloads/26_nipponbare_seed_noTSD.fa",
#            "/Users/weijiasu/Downloads/Rice_chr1_noTSD")


### Blast
def Blast(query, subject, OutName):
    NcbiblastnCommandline(query=query, subject=subject, out=OutName, outfmt=7)()


### Class of Duplications don't associate with TE

def No_TE(Folder):

    os.chdir(Folder)

    mk="mkdir noTE"
    os.system(mk)
    for files in os.listdir(Folder):
        path = os.path.join(Folder,files)
        if os.path.isdir(path):
            # skip directories
            continue

        path= os.path.join(Folder, files)
        with open(files, "r", encoding='utf-8', errors='ignore') as f:

            lines = f.readlines()
            if(len(lines)<3):
                continue
            line = lines[3]
            line1 = lines[len(lines) - 2]
            if (lines[3] == "# 0 hits found\n" and lines[len(lines) - 2] == "# 0 hits found\n"):
                move = "mv %s noTE/" % (files)
                os.system(move)


# No_TE("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_100k_DupTE/Rice_chr1")

### Class of Duplications associated with one or two TE
def OneTwo_TE(Folder):

    os.chdir(Folder)
    mk = "mkdir 2TE"
    os.system(mk)

    for files in os.listdir(Folder):
        path= os.path.join(Folder, files)
        if os.path.isdir(path):
            # skip directories
            continue
        with open(files, "r", encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            if(len(lines)<3):
                continue
            line = lines[3]
            line1 = lines[len(lines) - 2]
            if (lines[3] != "# 0 hits found\n" and lines[len(lines) - 2] != "# 0 hits found\n"):
                move = "mv %s 2TE/" % (files)
                os.system(move)

    mk = "mkdir 1TE"
    os.system(mk)
    moveTwo="mv *-c 1TE/"
    os.system(moveTwo)

# OneTwo_TE("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_100k_DupTE/Rice_chr1")

### Get the blast result set, two list of matched TE for two copies of duplications
def getTwoTeList(File):
    with open(File, "r", encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        set1 =[]
        set2 =[]
        for i in range(len(lines) ):
            columns = lines[i].split()
            if (columns[0] == "#"):
                continue
            if (columns[0] != "#"):
                for j in range(i, len(lines)):
                    columnsj = lines[j].split()
                    if (columnsj[0] != "#"):
                        set1.append(columnsj[1])
                        i = i + 1
                    if (columnsj[0] == "#"):
                        i = i + 1
                        break
                for k in range(i, len(lines)):
                    columns = lines[i].split()
                    if (columns[0] == "#"):
                        i = i + 1
                        continue
                    else:
                        columnsk = lines[k].split()
                        if (columnsk[0] != "#"):
                            set2.append(columnsk[1])
                            i = i + 1
                        if (columnsk[0] == "#"):
                            i = i + 1
                            break

                break
            break

    return set1,set2
# set1, set2= getTwoTeList("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/TE_Terminal/12496162-c")
# # print(getTwoTeList("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/TE_Terminal/12496162-c"))
# print(set1)
# print(set2)
# print(len(set1))
# print(len(set2))

### Move same TE files
def SameTE(Folder):
    os.chdir(Folder)
    folder = Folder
    os.system("mkdir SameTE")
    for files in os.listdir(folder):
        path = os.path.join(folder, files)
        if os.path.isdir(path):
            # skip directories
            continue
        if os.path.isfile(".DS_Store"):
            os.remove(".DS_Store")
            continue
        set1,set2=getTwoTeList(files)
        for e in set1:
            if (e in set2):
                move = "mv %s sameTE/" % (files)
                os.system(move)
                break

# SameTE("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Arabidopsis/chr1_100k_all/2TE")

#### Get TE length from TE database

def GetTeLength(TeLengthFile):
    TeLength = open(TeLengthFile, 'r+')
    Te = TeLength.readlines()
    d={}
    for i in range(len(Te)):
        teL=Te[i].split()
        Name=teL[0]
        length=teL[1]
        d[Name]=length
    return d

# dic=GetTeLength("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/TElength")
# print(dic)
# print(len(dic))
def TID_position(Folder):
    os.chdir(Folder)
    folder = Folder
    list=[]
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        Name = basename(file)
        FirstStart = Name[:-2]
        if os.path.isdir(path):
            continue
        if (os.path.isfile(".DS_Store")):
            os.remove(".DS_Store")
            continue
        list.append(FirstStart)
    return list
list=TID_position("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/chr12_DupBlastTE/2TE/SameTE/TE_Terminal")
for i in range(len(list)):
    print(list[i])
### Get first Match TE, return position: TEname
def GetFirSameTe(file):
    File = open(file, "r+")
    Filename = basename(file)
    d = {}
    set1, set2 = getTwoTeList(file)
    for e in set1:
        if (e in set2):
            d[Filename]=e

            break
    return d

def GetFirSameTeFamily(file):
    d={}
    File = open(file, "r+")
    Filename = basename(file)
    d=GetFirSameTe(file)
    TEname=d[Filename]
    FamilyCode=TEname[:5]
    if(FamilyCode=="SQ261"):
        d[Filename]="Tc1/Mariner"
    if (FamilyCode == "SQ262"):
        d[Filename] = "Mutator"
    if (FamilyCode == "SQ263"):
        d[Filename] = "hAT"
    if (FamilyCode == "SQ264"):
        d[Filename] = "CACTA"
    if (FamilyCode == "SQ265"):
        d[Filename] = "PIF/Harbinger"
    if (FamilyCode == "SQ266"):
        d[Filename] = "MiM_group"
    return d

def checkFamily(Folder):
    os.chdir(Folder)
    folder = Folder
    nMariner=0
    nMutator=0
    nhAT=0
    nCACTA=0
    nHar=0
    nMiM=0
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        Name = basename(file)
        FirstStart = Name[:-2]
        if os.path.isdir(path):
            continue
        if (os.path.isfile(".DS_Store")):
            os.remove(".DS_Store")
            continue
        d=GetFirSameTeFamily(file)
        FamilyName=d[Name]

        if(FamilyName=="Tc1/Mariner"):
            nMariner+=1
        if (FamilyName == "Mutator"):
            nMutator += 1
        if (FamilyName == "hAT"):
            nhAT += 1
        if (FamilyName == "CACTA"):
            nCACTA += 1
        if (FamilyName == "PIF/Harbinger"):
            nHar += 1
        if (FamilyName == "MiM_group"):
            nMiM += 1
    return nMariner,nMutator,nhAT,nCACTA,nHar,nMiM

# nMariner,nMutator,nhAT,nCACTA,nHar,nMiM\
#     =checkFamily("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/chr12_DupBlastTE/2TE/SameTE/TE_Terminal")
# print("Mariner:"+" "+str(nMariner)+"\n"+"Mutator:"+" "+str(nMutator)+"\n"+"hAT:"+" "+str(nhAT)+"\n"+"CACTA:"+" "+str(nCACTA)+"\n"
#       +"PIF/Harbinger:"+" "+str(nHar)+"\n"+"MiM_group:"+" "+str(nMiM)+"\n")
# print( GetFirSameTe("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/TE_Terminal_1/6619056-c"))
####  Out put two sets of blast results
def getTwosetLines(file):
   f=open(file, "r", encoding='utf-8', errors='ignore')
   lines = f.readlines()
   set1 =[]
   set2 =[]
   for i in range(len(lines)):
       columns = lines[i].split()
       if (columns[0] == "#"):
           continue
       if (columns[0] != "#"):
           for j in range(i, len(lines)):
               columnsj = lines[j].split()
               if (columnsj[0] != "#"):
                   set1.append(columnsj)
                   i = i + 1
               if (columnsj[0] == "#"):
                   i = i + 1
                   break
           for k in range(i, len(lines)):
                   columns = lines[i].split()
                   if(columns[0]=="#"):
                       i=i+1
                       continue
                   else:
                       columnsk = lines[k].split()
                       if (columnsk[0] != "#"):
                           set2.append(columnsk)
                           i = i + 1
                       if (columnsk[0] == "#"):
                           i = i + 1
                           break

           break
       break

   return set1,set2


# set1, set2 = getTwosetLines("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/TE_Terminal/7300826-c")
# print(set1)
# print(len(set1))
# print(set2)
# print(len(set2))


#### Get dupLength from DDS2 file
def getDupLength(file):
    d1={}
    d2={}
    with open(file, "r", encoding='utf-8', errors='ignore') as f:
        lines=f.readlines()
        for i in range(len(lines)):
            columns=lines[i].split()
            FirstStart=columns[1]
            FirstEnd=columns[2]
            length1=int(FirstEnd)-int(FirstStart)+1
            d1[FirstStart]=length1
            SecondStart = columns[5]
            SecondEnd = columns[6]
            length2 = int(SecondEnd) - int(SecondStart) + 1
            d2[FirstStart] = length2

    return d1,d2

# d1,d2=getDupLength("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Arabidopsis/Ara_TIDList")
# v=list(d1.values())
# k=list(d1.keys())
# print(k[v.index(max(v))])
# print(max(v))

# print(getDupLength("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1_1HSP"))
# print(len(getDupLength("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1_1HSP")))
def CheckTETerminal(Blastfile,TeLengthFile,DDSfile ):
    d1 = {}
    d2 = {}
    TElength = GetTeLength(TeLengthFile)
    Duplength1, Duplength2 = getDupLength(DDSfile)
    Name = basename(Blastfile)
    FirstStart = Name[:-2]
    Key1=FirstStart+"_1"
    Key2=FirstStart+"_2"
    linelist1, linelist2 = getTwosetLines(Blastfile)
    CommenTE = GetFirSameTe(Blastfile)
    FirstComTE = CommenTE[Name]
    for line in linelist1:
        columns = line
        if (columns[1] == FirstComTE):
            aligLength = columns[3]
            TeName = columns[1]
            realTELength = TElength[TeName]
            realDuplength = Duplength1[FirstStart]
            if (abs(int(realDuplength) - int(aligLength)) < 21):
                d1[Key1]="TE_Only"
                break
            elif ((int(columns[8]) < int(realTELength)/2 or int(columns[9]) > int(realTELength)/2 )or int(columns[8]) > int(
                    realTELength)/2 or int(columns[9]) < int(realTELength)/2):
                d1[Key1]="TE_Terminal"
                break
            else:
                d1[Key1] = "TE_Middle/"
                break

    for line in linelist2:
        columns = line
        if (columns[1] == FirstComTE):
            aligLength = columns[3]
            TeName = columns[1]
            realTELength = TElength[TeName]
            realDuplength = Duplength1[FirstStart]
            if (abs(int(realDuplength) - int(aligLength)) < 21):
                d2[Key2] = "TE_Only"
                break
            elif ((int(columns[8]) == 1) or int(columns[9]) == int(realTELength) or int(columns[8]) == int(
                realTELength) or int(columns[9]) == 1):
                d2[Key2] = "TE_Terminal"
                break
            else:
                d2[Key2] = "TE_Middle/"
                break
    return d1,d2


### rule out duplicated TE cases, and the cases that TE in the middle  of the duplication

def ClassByTE(Folder,TeLengthFile,DDSfile):
    os.chdir(Folder)
    folder = Folder
    os.system("mkdir TE_Only")
    os.system("mkdir TE_Terminal")
    os.system("mkdir TE_Middle")
    os.system("mkdir Exception")
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        Name=basename(file)
        FirstStart = Name[:-2]
        Key1 = FirstStart + "_1"
        Key2 = FirstStart + "_2"
        if os.path.isdir(path):
            continue
        if (os.path.isfile(".DS_Store")):
            os.remove(".DS_Store")
            continue
        else:
            d1,d2=CheckTETerminal(file,TeLengthFile,DDSfile )
            if(d1[Key1]!=d2[Key2]):
                mv="mv %s Exception/"% (file)
                os.system(mv)
                continue
            elif(d1[Key1]=="TE_Only" and d2[Key2]=="TE_Only"):
                mv= "mv %s TE_Only/" % (file)
                os.system(mv)
                continue
            elif(d1[Key1]=="TE_Terminal" and d2[Key2]=="TE_Terminal"):
                move = "mv %s TE_Terminal/" % (file)
                os.system(move)
                continue
            else:
                move = "mv %s TE_Middle/" % (file)
                os.system(move)
                continue




#
# ClassByTE(
#                 "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Arabidopsis/chr1_100k_all/2TE/SameTE/",
#                 "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Arabidopsis/TElength",
#                 "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Arabidopsis/DDS2/Ara_chr1_noDup")
#
#



#



### Check if the TE is located in the begining or in the end
def checkTEPosition(Blastfile, DDSfile):
    Duplength1,Duplength2 = getDupLength(DDSfile)


    d1={}
    d2={}
    Name=basename(Blastfile)
    FirstStart=Name[:-2]
    Lineset1,Lineset2=getTwosetLines(Blastfile)
    firstTE=GetFirSameTe(Blastfile)
    firstTE=firstTE[Name]
    for line in Lineset1:
        if (line[1]==firstTE):
            pstart=int(line[6])
            pend=int(line[7])
            if(pstart<30):
                d1[Name]="begin"
                break
            else:
                realDuplength = Duplength1[FirstStart]
                if(pend>int(realDuplength)-30):
                    d1[Name]="end"
                    break
                else:
                    d1[Name] = "Middle"
                    break
    for line in Lineset2:
        if (line[1]==firstTE):
            pstart=int(line[6])
            pend=int(line[7])
            if(pstart==1):
                d2[Name]="begin"
            else:
                realDuplength = Duplength2[FirstStart]
                if(pend==int(realDuplength)):
                    d2[Name]="end"
                else:
                    d2[Name] = "Middle"
                    break
        else:
            continue
    return d1,d2
# print(checkTEPosition("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/test/TE_Terminal/nonTID/33165135-c"
#                 ,"/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1_1HSP" ))

#### Rule out nonTID
def KeepTDD(Folder, DDSfile):
    os.chdir(Folder)
    folder = Folder
    os.system("mkdir nonTID")
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        Name = basename(file)
        if os.path.isdir(path):
            # skip directories
            continue
        if (os.path.isfile(".DS_Store")):
            os.remove(".DS_Store")
            continue
        d1,d2=checkTEPosition(file, DDSfile)
        if(d1[Name]!=d2[Name] or d1[Name]=="Middle" or d2[Name]=="Middle"):
            move = "mv %s nonTID/" % (file)
            os.system(move)
#
# KeepTDD("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_100k_DupTEAll/ALL/2TE/SameTE/TE_Terminal",
# "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_100k_DupTEAll/Rice_chr1_noDup")


### rule out nonTID

def ClassByTePosition(Folder, DDSfile):
    os.chdir(Folder)
    folder = Folder
    os.system("mkdir begin")
    os.system("mkdir end")
    os.system("mkdir Middle")
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isdir(path):
            # skip directories
            continue
        if (os.path.isfile(".DS_Store")):
            os.remove(".DS_Store")
            continue
        Name=basename(file)
        TePosition=checkTEPosition(file,DDSfile)
        # if (TePosition[Name]=="begin"):
        #     move = "mv %s begin/" % (file)
        #     os.system(move)
        # if (TePosition[Name]=="end"):
        #     move = "mv %s end/" % (file)
        #     os.system(move)
        if (TePosition[Name]=="Middle"):
            move = "mv %s Middle/" % (file)
            os.system(move)
# ClassByTePosition("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/TE_Terminal",
#                   "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1_1HSP")



def GetWholeDupSeq(DupFile, Blastfile, db, entry):
    seq1=""
    seq2=""
    Position=basename(Blastfile)[:-2]
    f=open(DupFile,'r+')
    lines=f.readlines()
    for i in range(len(lines)):
        columns=lines[i].split()
        if (columns[1]==Position):
            FirstStart=int(columns[1])
            FirstEnd=int(columns[2])
            SecondStart=int(columns[5])
            SecondEnd=int(columns[6])
            FirstName=columns[1]+"_1"
            SecondName = columns[1] + "_2"
            if(FirstStart-FirstEnd<0 and SecondStart<SecondEnd<0):
                seq1 = subprocess.check_output("blastdbcmd -db '%s' -entry '%s' -range '%s'-'%s'" % (db, int(entry), int(FirstStart), int(FirstEnd)), shell = True)
                seq1 = seq1.decode("utf-8")
                seq1 = get_seq(seq1)
                seq2 = subprocess.check_output("blastdbcmd -db '%s' -entry '%s' -range '%s'-'%s'" % (db, int(entry), int(SecondStart), int(SecondEnd)),
                shell=True)
                seq2 = seq2.decode("utf-8")
                seq2 = get_seq(seq2)
                getseq(FirstStart, FirstEnd, db, entry, FirstName)
                getseq(SecondStart, SecondEnd, db, entry, SecondName)

    return seq1,seq2



# WD1, WD2=GetWholeDupSeq("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1_1HSP",
#                   "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/TE_Terminal/33165135-c"
#                   , "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/Oryza_sativa_ncbi/Oryza_sativa.fa",
#                   1)
#
# print(WD1)
# print(WD2)

def GetTwoTESeq(DupFile, Blastfile, db, entry):
    seq1=""
    seq2=""
    Position = basename(Blastfile)[:-2]



    f = open(DupFile, 'r+')
    FirstStart=0
    FirstEnd=0
    SecondStart=0
    SecondEnd=0
    lines = f.readlines()
    for i in range(len(lines)):
        columns = lines[i].split()
        if (columns[1] == Position):
            FirstStart = int(columns[1])
            FirstEnd = int(columns[2])
            SecondStart = int(columns[5])
            SecondEnd = int(columns[6])
            break

    firstTE = GetFirSameTe(Blastfile)[basename(Blastfile)]
    firstTEstart = 0
    firstTEend = 0
    SecondTEstart=0
    SecondTEend=0

    set1,set2=getTwosetLines(Blastfile)

    for i in range (len(set1)):
        if (set1[i][1] == firstTE):
            firstTEstart = FirstStart + int(set1[i][6]) - 1
            firstTEend= FirstStart  + int(set1[i][7])-1
            break
    if(firstTEstart<firstTEend and SecondTEstart<SecondTEend):
        seq1 = subprocess.check_output(
            "blastdbcmd -db '%s' -entry '%s' -range '%s'-'%s'" % (db, int(entry), int(firstTEstart), int(firstTEend)),
            shell=True)
        seq1 = seq1.decode("utf-8")
        seq1 = get_seq(seq1)
        FirstName = Position + "_TE1"

        getseq(firstTEstart, firstTEend, db, entry, FirstName)
        for line in set2:
            if (line[1] == firstTE):
                SecondTEstart = SecondStart + int(line[6]) - 1
                SecondTEend = SecondStart + int(line[7]) - 1
                break
        seq2 = subprocess.check_output(
            "blastdbcmd -db '%s' -entry '%s' -range '%s'-'%s'" % (db, int(entry), int(SecondTEstart), int(SecondTEend)),
            shell=True)
        seq2 = seq2.decode("utf-8")
        seq2 = get_seq(seq2)
        SecondName = Position + "_TE2"

        getseq(SecondTEstart, SecondTEend, db, entry, SecondName)

    return seq1, seq2

# TE1, TE2=GetTwoTESeq("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1_1HSP",
#                   "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/TE_Terminal/33165135-c"
#                   , "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/Oryza_sativa_ncbi/Oryza_sativa.fa",
#                   1)
#
# print(TE1)
# print(TE2)

def getTwodupSeq(DupFile, Blastfile, db, entry):
    seq1=""
    seq2=""
    
    Name=basename(Blastfile)
    Position = basename(Blastfile)[:-2]
    f = open(DupFile, 'r+')
    FirstStart = 0
    FirstEnd = 0
    SecondStart = 0
    SecondEnd = 0
    lines = f.readlines()
    for i in range(len(lines)):
        columns = lines[i].split()
        if (columns[1] == Position):
            FirstStart = int(columns[1])
            FirstEnd = int(columns[2])
            SecondStart = int(columns[5])
            SecondEnd = int(columns[6])
            break

    firstTE = GetFirSameTe(Blastfile)[basename(Blastfile)]
    firstDupstart = 0
    firstDupend = 0
    SecondDupstart = 0
    SecondDupend = 0

    set1, set2 = getTwosetLines(Blastfile)

    for i in range(len(set1)):
        if (set1[i][1] == firstTE):
            d1,d2=checkTEPosition(Blastfile, DupFile)
            if(d1[Name]=="begin"):
                firstDupstart = FirstStart + int(set1[i][7])
                firstDupend = FirstEnd
            if (d1[Name] == "end"):
                firstDupstart = FirstStart
                firstDupend = FirstStart+int(set1[i][6])-2

            break
    if(int(firstDupstart)<int(firstDupend)and int(SecondDupstart)and int(SecondDupend)):
        seq1 = subprocess.check_output(
            "blastdbcmd -db '%s' -entry '%s' -range '%s'-'%s'" % (db, int(entry), int(firstDupstart), int(firstDupend)),
            shell=True)
        seq1 = seq1.decode("utf-8")
        seq1 = get_seq(seq1)
        FirstName = Position + "_Dup1"
        getseq(firstDupstart, firstDupend, db, entry, FirstName)
        for line in set2:
            if (line[1] == firstTE):
                d1, d2 = checkTEPosition(Blastfile, DupFile)
                if (d1[Name] == "begin"):
                    SecondDupstart = SecondStart + int(line[7])
                    SecondDupend = SecondEnd
                if (d1[Name] == "end"):
                    SecondDupstart = SecondStart
                    SecondDupend = SecondStart + int(line[6]) - 2
                break
        seq2 = subprocess.check_output(
            "blastdbcmd -db '%s' -entry '%s' -range '%s'-'%s'" % (
            db, int(entry), int(SecondDupstart), int(SecondDupend)),
            shell=True)
        seq2 = seq2.decode("utf-8")
        seq2 = get_seq(seq2)
        SecondName = Position + "_Dup2"

        getseq(SecondDupstart, SecondDupend, db, entry, SecondName)

    return seq1, seq2



# seq1, seq2=getTwodupSeq("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr2_1HSP",
#                   "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr2_DupBlastTE/2TE/SameTE/TE_Terminal/7395685-c"
#                   , "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/Oryza_sativa_ncbi/Oryza_sativa.fa",
#                   1)
# print(seq1)
# print(seq2)


def getWhole(DupFile, Blastfile, db, entry):
    seq1=""
    Name = basename(Blastfile)
    Position = basename(Blastfile)[:-2]
    f = open(DupFile, 'r+')
    Start = 0
    End = 0
    lines = f.readlines()
    for i in range(len(lines)):
        columns = lines[i].split()
        if (columns[1] == Position):
            Start = int(columns[1])
            End = int(columns[6])
            break
    if(int(Start)<int(End)):
        seq1 = subprocess.check_output(
            "blastdbcmd -db '%s' -entry '%s' -range '%s'-'%s'" % (db, int(entry), int(Start), int(End)),
            shell=True)
        seq1 = seq1.decode("utf-8")
        seq1 = get_seq(seq1)
        FirstName = Position + "_whole"
        getseq(Start, End, db, entry, FirstName)

    return seq1
#
# whole= getWhole(
#     "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1_1HSP",
#     "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/TE_Terminal/33165135-c"
#     , "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/Oryza_sativa_ncbi/Oryza_sativa.fa",
#     1)
# print(whole)
# Folder="/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/TE_Terminal/"
# os.chdir(Folder)
# folder = Folder
# for file in os.listdir(folder):
#     path = os.path.join(folder, file)
#     Name = basename(file)
#
#     if os.path.isdir(path):
#         # skip directories
#         continue
#     if (os.path.isfile(".DS_Store")):
#         os.remove(".DS_Store")
#         continue
#     if (Name[-2:] == "-c"):
#         getWhole("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1_1HSP", file,
#                  "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/Oryza_sativa_ncbi/Oryza_sativa.fa", 1)


def CompareIdentity(Folder,DupFile, Blastfile, db, entry):
    Name = basename(Blastfile)
    Position=Name[:-2]
    TE1, TE2 = GetTwoTESeq(DupFile, Blastfile, db, entry)
    Dup1,Dup2=getTwodupSeq(DupFile, Blastfile, db, entry)
    WD1,WD2=GetWholeDupSeq(DupFile, Blastfile, db, entry)
    TE1_Name = Position + "_TE_Ind"
    Dup1_Name = Position + "_Dup_Ind"
    Whole1_Name = Position + "_WD_Ind"
    FinalName="C"+Position+"_Ind"

    TE1_A=Folder+"/"+Position+"_TE1.fasta"
    TE2_A = Folder + "/" + Position + "_TE2.fasta"
    Dup1_A=Folder + "/" + Position + "_Dup1.fasta"
    Dup2_A = Folder + "/" + Position + "_Dup2.fasta"
    WD1_A=Folder + "/" + Position + "_1.fasta"
    WD2_A = Folder + "/" + Position + "_2.fasta"
    Blast(TE1_A,TE2_A,TE1_Name)
    Blast(Dup1_A,Dup2_A,Dup1_Name)
    Blast(WD1_A,WD2_A,Whole1_Name)

    catfile = "cat %s %s %s> %s" % (TE1_Name, Dup1_Name,Whole1_Name, FinalName)
    os.system(catfile)

# CompareIdentity("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Code",
#      "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1_1HSP",
#      "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/TE_Terminal/33165135-c"
#      , "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/Oryza_sativa_ncbi/Oryza_sativa.fa",
#      1)
#

def FinalCheck(Folder, DDSfile, db, entry):
    os.chdir(Folder)
    folder = Folder
    # KeepTDD(Folder,DDSfile)
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        Name = basename(file)
        name=Name[:-2]
        if os.path.isdir(path):
             # skip directories
            continue
        if (os.path.isfile(".DS_Store")):
            os.remove(".DS_Store")
            continue
        elif (Name[-2:] == "-c"):
            CompareIdentity(Folder, DDSfile, file, db, entry)
            Start=int(basename(file)[:-2])
            End=0
            for line in open(DDSfile,'r+'):
                columns=line.split()
                if(int(columns[1])==Start):
                    End=columns[6]
            getseq(Start, End, db, entry,name)
#            seq1 = subprocess.check_output("blastdbcmd -db '%s' -entry '%s' -range '%s'-'%s'" % (db, int(entry), int(Start), int(End)),shell=True)
#            seq1 = seq1.decode("utf-8")
#            seq1 = get_seq(seq1)
#            FirstName = Position + "_whole"
#            getseq(Start, End, db, entry, FirstName)


def organize(folder):
    os.chdir(folder)
    os.system("mkdir fasta")
    os.system("mv *.fasta fasta/")
    os.system("mkdir finalresult")
    os.system("mv C* finalresult/")
    os.system("mkdir Identity")
    os.system("mv *_Ind Identity/")
#
# FinalCheck("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DupBlastTE/2TE/SameTE/test/TE_Terminal",
#            "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_1_1HSP",
#       "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/Oryza_sativa_ncbi/Oryza_sativa.fa",
#       1)

# "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_mHSP_blast/2TE/SameTE/",

# FinalCheck("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/Rice_DupBlastTE_mHSP/2TE/SameTE/TE_Terminal",
#            "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/chr1_mHSP",
#            "/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/Oryza_sativa_ncbi/Oryza_sativa.fa",
#            1)
#
# organize("/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/Rice_DupBlastTE_mHSP/2TE/SameTE/TE_Terminal")


def DownStreamChecker (DDSfile, db, entry, TEdatabase, Folder,TElengthfile,chr):

    os.chdir(Folder)

    BlastFolder=chr+"_"+"DupBlastTE"
    mk="mkdir %s"%(BlastFolder)
    os.system(mk)
    s=BlastFolder+"/"
    BlastFolder = Folder + "/" + BlastFolder
    cd="cd %s"%(BlastFolder)
    os.system(cd)
    DupBlastTE(DDSfile, db, entry, TEdatabase, BlastFolder)
    # mv="mv *-c %s" %(s)
    # os.system(mv)

    No_TE(BlastFolder)
    OneTwo_TE(BlastFolder)
    TwoTEFolder=BlastFolder+"/"+"2TE"
    SameTE(TwoTEFolder)
    SameTEFolder=TwoTEFolder+"/"+"SameTE"
    ClassByTE(SameTEFolder,TElengthfile,DDSfile)
    TETeminalFolder=SameTEFolder+"/"+"TE_Terminal"
    KeepTDD(TETeminalFolder, DDSfile)
    FinalCheck(TETeminalFolder,DDSfile,db,entry)
    organize(TETeminalFolder)


#for i in range(9,13):
# chr="chr"+str(12)
# entry=12
# DDSfile="/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/DDS2_0812/DDS2/"+chr
# DB="/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/Oryza_sativa_ncbi/Oryza_sativa.fa"
# TEDB="/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/26_nipponbare_mite_seq.fa"
# Folder="/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/Oryza_sativa/"
# TElength="/Users/weijiasu/Dropbox/Research/BioinformaticsProject/Rice/TElength"
#
# DownStreamChecker(DDSfile,DB,entry, TEDB,Folder,TElength, chr)
#
#




