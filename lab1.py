from ctypes import Union
from operator import index
import random
import time
from math import floor
from math import ceil
from unicodedata import name


def create_random_hash_function(p=2**33-355, m=2**32-1):
    a = random.randint(1,p-1)
    b = random.randint(0, p-1)
    return lambda x: 1 + (((a * x + b) % p) % m)

def MyReadDataRoutine(fileName, numDocuments):
    input = open(fileName,"r") #open file
    output = list()
    numDocuments = int(numDocuments)

    if numDocuments>int(input.readline()) or numDocuments<0: #check if numDocuments is valid
        print("Wrong numDocuments input")
        return 0

    global dictSize
    dictSize = int(input.readline())
    input.readline() #skip 3rd line

    curLine = input.readline().split() # read current file number
    for i in range(1,numDocuments+1):  # and iterate until we reach next file num
        curSet = set()
        while int(curLine[0]) == i:
            curSet.add(int(curLine[1]))
            curLine = input.readline().split()
        output.append(sorted(frozenset(curSet))) # save as frozen set to output list
    return output

def MyJacSimWithSets(docID1,docID2):
    start_time=time.time();
    
    intersectionCounter = 0
    for i in docID1:
        for j in docID2:
            if i==j:
                intersectionCounter+=1
    print("--------JacSimWithSets %s seconds------" %(time.time() - start_time))
    return intersectionCounter/(len(docID1)+len(docID2)-intersectionCounter)

def MyJacSimWithOrderedLists(docID1, docID2):
    start_time=time.time();
    docID1 = sorted(docID1)
    docID2 = sorted(docID2)
    pos1 = 0
    pos2 = 0
    intersectionCounter = 0
    len1 = len(docID1)
    len2 = len(docID2)
    while pos1<len1 and pos2<len2:
        if docID1[pos1]==docID2[pos2]:
            intersectionCounter +=1; pos1+=1; pos2+=1
        else:
            if docID1[pos1] < docID2[pos2]:
                pos1+=1
            else:
                pos2+=1
    print("--------JacSimWithOrderedLists %s seconds------" %(time.time() - start_time))
    return intersectionCounter/(len1+len2-intersectionCounter)

def MyMinHash(docList, K):
    random.seed(10)
    h = []
    for i in range(K):
        randomHash = {i:create_random_hash_function()(i) for i in range(dictSize)}
        myHashKeysOrderedByValues = sorted(randomHash, key = randomHash.get)
        myHash = {myHashKeysOrderedByValues[x]:x for x in range(dictSize)}
        h.append(myHash)
        print("Progress, ",i)
    
    sig = []
    for col in range(len(docList)):
        sig.append([])
        for i in range(K):
            sig[col].append(dictSize)

    for col in range(len(docList)):
        for row in docList[col]:
            for i in range(K):
                if h[i].get(row) < sig[col][i]:
                    sig[col][i] = h[i].get(row)
    return sig

def MySigSim(docID1, docID2, numPermutations):
    counter=0
    for i in range(numPermutations):
        if(docID1[i]==docID2[i]):
            counter+=1
    return counter/numPermutations

def bruteForceJacSim(docList, numDocuments, numNeighbors):

    if(numDocuments>len(docList) or numNeighbors>len(docList)):
        return
    
    simList = []
    start_time = time.time()
    for i in range(numDocuments):
        myDict = {}
        for j in range(numNeighbors):
            myDict[j] = 1 - MyJacSimWithSets(docList[i],docList[j])
        myDict = dict(sorted(myDict.items(), key=lambda x:x[1]))
        for key in myDict:
            myDict[key] = 1 - myDict[key]
        simList.append(myDict)
    
    print("Time cost: ",time.time()-start_time)
    AvgSim = []
    Avg = 0
    for i in range(len(simList)):
        avg = 0
        for key in simList[i]:
            avg += simList[i][key]
        AvgSim.append(avg/numNeighbors)
        Avg += AvgSim[i]
    Avg = Avg/numDocuments

    return Avg

def bruteForceSigSim(docList, numDocuments, numNeighbors):
    hashNumber = 50

    if(numDocuments>len(docList) or numNeighbors>len(docList)):
        return
    
    sig = MyMinHash(docList, hashNumber)
    simList = []
    start_time = time.time()
    for i in range(numDocuments):
        myDict = {}
        for j in range(numNeighbors):
            myDict[j] = 1 - MySigSim(sig[i],sig[j],hashNumber)
        myDict = dict(sorted(myDict.items(), key=lambda x:x[1]))
        for key in myDict:
            myDict[key] = 1 - myDict[key]
        simList.append(myDict)
    
    print("Time cost: ",time.time()-start_time)
    AvgSim = []
    Avg = 0
    for i in range(len(simList)):
        avg = 0
        for key in simList[i]:
            avg += simList[i][key]
        AvgSim.append(avg/numNeighbors)
        Avg += AvgSim[i]
    Avg = Avg/numDocuments

    return Avg
 
def LSH(sig, rowsPerBands):
    hashLSH = create_random_hash_function()
    numBands = floor(len(sig)/rowsPerBands)
    LSHdicts = [dict() for i in range(numBands)] #docID: hashLSH(SIG[bandRows:docID])
    for band in range(len(LSHdicts)):
        for signature in range(len(sig)):
            curSig = tuple(sig[signature][band*rowsPerBands:((band+1)*rowsPerBands if (band+1)*rowsPerBands<len(sig[signature]) else len(sig[signature]))])
            LSHdicts[band][signature] = hashLSH(hash(curSig))
        LSHdicts[band] = {k: v for k, v in sorted(LSHdicts[band].items(), key=lambda item: item[1])}

    pairs = set()
    for band in LSHdicts:
        cand = []
        keys = [key for key in band.keys()]
        print(keys)
        values = [val for val in band.values()]
        print(values)
        for val in range(len(values)-1):
            if values[val]==values[val+1]:
                cand.append(keys[val])
            else:
                cand.append(keys[val])
                if(len(cand)>1):
                    for i in range(len(cand)-1):
                        for j in range(i+1,len(cand)):
                            if cand[i]<cand[j]:
                                pairs.add((cand[i],cand[j]))
                            elif cand[i]>cand[j]:
                                pairs.add((cand[j],cand[i]))
                            else:
                                print('error')
                cand = []

    print(pairs)
    return pairs

def main():
    #a
    nameOFDucument=input("Enter the name of the document(name.txt) : ")
    numberOfDucuments=input("Give me the number of the documents you want to read : ")
    listData=MyReadDataRoutine(nameOFDucument,numberOfDucuments)
    
    #b
    numNeighbors=input("Give me the number of the neighbors you want: ")
    while (numNeighbors>5) or (numNeighbors<2):
        numNeighbors=input("Give me again the number of the neigbors you want (2,3..,5): ")
        
    #c
    numberOfK=input("Give me the number of random permutations : ")
    sig=MyMinHash(list,numberOfK)
    
    #d
    methods=input("Give me the method you want to use (JacSim or SigSim): ")
    
    #e
    mehtods1=input("Which method you want to use BruteForce or LSH: ")
    
    if methods1=="BruteForce":
        if methods=="JacSim":
            bruteForceJacSim(list,numberOfDucuments,numNeighbors)
        elif method=="SigSim":
            bruteForceSigSim(list,numberOfDucuments,numNeighbors)
    
    #elif methods1=="LSH":
        
    
    if(input("Do you want to give me specific docID :")=="Yes"):
        docID1=input("Give me the first DocID : ")
        docID2=input("Give me the second DocID : ")
        
        numberOfK=input("Give me the number of random permutations : ")
        
        print("Jac sim with Sets: ",MyJacSimWithSets(listData[docID1],listData[docID2]))
        print("Jac sim with Ordered List : ", MyJacSimWithOrderedLists(listData[docID1],listData[docID2]))
        print("Sig sim: ",MySigSim(sig[docID1],sig[docID2],numberOfK))
            
   
         
        
        
        
        
        
#list = MyReadDataRoutine("DATA_1-docword.enron.txt",90)

#sig = MyMinHash(list,32)

#LSH(sig, ceil(32/17))
#main()

#print("Jac sim: ",MyJacSimWithSets(list[5],list[18]))
#print("Sig sim: ",MySigSim(sig[5],sig[18],200))
