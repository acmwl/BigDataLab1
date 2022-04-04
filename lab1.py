from ctypes import Union
from operator import index
import random

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


list = MyReadDataRoutine("DATA_1-docword.enron.txt",4)
sig = MyMinHash(list,5)

print(MySigSim(sig[0],sig[1],5))

print(MyJacSimWithSets(list[0],list[1]))