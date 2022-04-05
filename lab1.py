from ctypes import Union
from operator import index
import random
import time
from math import floor

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
        output.append(frozenset(curSet)) # save as frozen set to output list

    return output

def MyJacSimWithSets(docID1,docID2):
    intersectionCounter = 0
    for i in docID1:
        for j in docID2:
            if i==j:
                intersectionCounter+=1
    return intersectionCounter/(len(docID1)+len(docID2)-intersectionCounter)

def MyJacSimWithOrderedLists(docID1, docID2):
    docID1 = sorted(docID1)
    docID2 = sorted(docID2)
    pos1 = 0; pos2 = 0; intersectionCounter = 0
    len1 = len(docID1);
    len2 = len(docID2);
    while pos1<len1 and len2<pos2:
        if docID1[pos1]==docID2[pos2]:
            intersecrtionCounter +=1; pos1+=1; pos2+=1
        else:
            if docID1[pos1] < docID2[pos2]:
                pos1+=1
            else:
                pos2+=1
    return intersectionCounter/(len1+len2-intersectionCounter)

def MyMinHash(docList, K):
    h = []
    for i in range(K):
        randomHash = {i:create_random_hash_function()(i) for i in range(dictSize)}
        myHashKeysOrderedByValues = sorted(randomHash, key = randomHash.get)
        myHash = {myHashKeysOrderedByValues[x]:x for x in range(dictSize)}
        h.append(myHash)


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
    return (len(frozenset(docID1[:numPermutations]).intersection(frozenset(docID2[:numPermutations]))))/numPermutations

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
    return

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
            curSig = tuple(sig[signature][band*rowsPerBands:((band+1)*rowsPerBands if band<(len(LSHdicts)-1) else len(sig[signature])-1)])
            LSHdicts[band][signature] = hashLSH(hash(curSig))
        LSHdicts[band] = {k: v for k, v in sorted(LSHdicts[band].items(), key=lambda item: item[1])}

    result = []

    for band in LSHdicts:
        result.append([])
        counter = 0
        keys = [key for key in band]
        for i in range(len(keys)-1):
            if(band[keys[i]]==band[keys[i+1]]):
                result[counter].append(keys[i])
                if i+1==len(keys)-1:
                    result[counter].append(keys[i+1])
            elif(band[keys[i-1]]!=band[keys[i]]):
                continue
            else:
                result.append([])
                counter+=1
    print(result)
    return result
        
        


list = MyReadDataRoutine("DATA_1-docword.enron.txt",10)

LSH(MyMinHash(list,10),10//4)


