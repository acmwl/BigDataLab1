from ctypes import Union
from operator import index
import random
import time
from math import floor
from math import ceil
from time import sleep



def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r %s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()
        print() 

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
    start=time.process_time()
    intersectionCounter = 0
    for i in docID1:
        for j in docID2:
            if i==j:
                intersectionCounter+=1
    print("ExecTime : ",time.process_time() - start)
    return intersectionCounter/(len(docID1)+len(docID2)-intersectionCounter)

def MyJacSimWithOrderedLists(docID1, docID2):
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
    return intersectionCounter/(len1+len2-intersectionCounter)

def MyMinHash(docList, K):
    random.seed(10)
    h = []
    print("Creating the Minhash Functions")
    for i in range(K):
        randomHash = {i:create_random_hash_function()(i) for i in range(dictSize)}
        myHashKeysOrderedByValues = sorted(randomHash, key = randomHash.get)
        myHash = {myHashKeysOrderedByValues[x]:x for x in range(dictSize)}
        h.append(myHash)
        printProgressBar(i,K)
    
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

def bruteForceJacNeighbors(docList, numDocuments, numNeighbors):
    start_time=time.time()
    if(numDocuments>len(docList) or numNeighbors>len(docList)):
        return
    
    simList = []
    start_time = time.time()
    for i in range(numDocuments):
        myDict = {}
        for j in range(numDocuments):
            if i==j: 
                continue
            myDict[j] = 1 - MyJacSimWithOrderedLists(docList[i],docList[j])
        myDict = {k: v for k, v in sorted(myDict.items(), key = lambda item:item[1])}
        counter = 0
        neighbors = {}
        for key in myDict:
            if counter>=numNeighbors:
                break
            neighbors[key] = 1 - myDict[key]
            counter += 1
        simList.append(neighbors)

    AvgSim = []
    Avg = 0
    for i in range(len(simList)):
        avg = 0
        for key in simList[i]:
            avg += simList[i][key]
        AvgSim.append(avg/numNeighbors)
        Avg += AvgSim[i]
    Avg = Avg/numDocuments
    print("--- ExecTime--- : ",time.time() - start_time)
    return simList #AvgSim #Avg

def bruteForceSigNeighbors(sig, numDocuments, numNeighbors):
    start_time=time.time()
    if(numDocuments>len(sig) or numNeighbors>len(sig)):
        return

    simList = []
    for i in range(numDocuments):
        myDict = {}
        for j in range(numDocuments):
            if i==j: 
                continue
            myDict[j] = 1 - MySigSim(sig[i],sig[j],len(sig[i]))
        myDict = {k: v for k, v in sorted(myDict.items(), key = lambda item:item[1])}
        counter = 0
        neighbors = {}
        for key in myDict:
            if counter>=numNeighbors:
                break
            neighbors[key] = 1 - myDict[key]
            counter += 1
        simList.append(neighbors)

    AvgSim = []
    Avg = 0
    for i in range(len(simList)):
        avg = 0
        for key in simList[i]:
            avg += simList[i][key]
        AvgSim.append(avg/numNeighbors)
        Avg += AvgSim[i]
    Avg = Avg/numDocuments
    print("--- ExecTime of Brute Force Using SigSimilarity : ---" , time.time() - start_time)
    return simList #AvgSim #Avg

def LSH(sig, rowsPerBands):
    start_time=time.time()
    hashLSH = create_random_hash_function()
    numBands = floor(len(sig[0])/rowsPerBands)
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
        #print(keys)
        values = [val for val in band.values()]
        #print(values)
        for val in range(len(values)-1):
            if values[val]==values[val+1] and val<len(values)-2:
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
    print("The result in ExeTime(%s)" %(time.time()-start_time))
    print(pairs)
    return pairs

def LSHcount(numOfHashes):
    minr = numOfHashes  
    for r in range(1,numOfHashes):
        
        b = floor(numOfHashes/r)
        if 0.2<((1/b)**(1/r)) and ((1/b)**(1/r))<0.4:
            minr = r
    print("Recommended rowsPerBand for ",numOfHashes," permutations is ",minr)
    return minr

def main():  
    print("Scanning and analysing input document")
    #a
    print("\nSelect which document to use:\n1)Enron Dataset\n2)Nips dataset")
    documentSel=int(input("Input selection (input 1 or 2): "))
    if documentSel<1 or documentSel>2: 
        print("Wrong input")
    numberOfDucuments=int(input("How many documents shall be examined: "))
    inputDoc=MyReadDataRoutine("DATA_1-docword.enron.txt" if documentSel==1 else "DATA_2-docword.nips",numberOfDucuments)

    print()

    #b
    numNeighbors=int(input("Input a number of neighbors to check (input a number between 2 and 5): "))
    if (int(numNeighbors)>5) or (int(numNeighbors)<2):
        print("Wrong input, setting it to 3")
        numNeighbors=3

    print()

    #c
    numberOfHashes=int(input("Input the number of random permutations (i.e. hash functions to be used): "))
    sig=MyMinHash(inputDoc,numberOfHashes)
    
    print()

    #d
    simMethod=int(input("Select which similarity method to use (input 1 or 2): \n1)Jaccard Similarity using Ordered lists\n2)MinHash signature similarity\n"))
    if(simMethod<1 or simMethod >2):
        print("Wrong input, will use option 2")

    print()

    #e
    compMethod=int(input("Select which comparison method to use (input 1 or 2):\n1)Brute Force comparison\n2)Locality Sensitive Hashing\n"))
    if(compMethod<1 or compMethod >2):
        print("Wrong input, will use option 2")

    if compMethod==1:
        if simMethod==1:
            bruteForceJacNeighbors(inputDoc,numberOfDucuments,numNeighbors)
        else:
            bruteForceSigNeighbors(sig,numberOfDucuments,numNeighbors)
    else:
        #f
        print()
        
        number=0
        variable=8
        print("Now setting variables for LSH. Recommended threshold is around 0.3")

        r = LSHcount(numberOfHashes)

        rin = int(input("Select a number of rows to be used per band: "))
        print(rin," rows yield a threshold of ",(1/floor(numberOfHashes/r))**(1/r))
        ans = 'y'
        if rin>r+0.1 or rin<r-0.1:
            ans = input("Warning, inputted r yields a threshold far from the recommended. Continue with inputted value? (y/n)")
        r = rin if ans=='y' else r

        print("Using ",r," rows per band, with a total of ",floor(numberOfHashes/r)," bands")

        print("\n")
        LSH(sig,r)
        
    print("Database succesfully scanned\n")

    #3
    print("To verify above finds, you can check for similarity between two specific files\nSelect 1 or 2:\n1)Compare specific files\n2)Exit")

    while(int(input("How would you like to continue?\n1)Compare specific files\n2)Exit\n"))==1):
        inp = input("Input 2 specific document IDs seperated by space: ").split()
        docID1=int(inp[0])
        docID2=int(inp[1])

        numberOfK=int(input("Select a number of random permutations to be used from the signatures list: "))
        if numberOfK>len(sig[0]):
            numberOfK=len(sig[0]);

        print("Computing Jaccard similarity using Sets: ",MyJacSimWithSets(inputDoc[docID1-1],inputDoc[docID2-1]))
        print("Computing Jaccard similarity using Ordered Lists : ", MyJacSimWithOrderedLists(inputDoc[docID1-1],inputDoc[docID2-1]))
        print("Computing Signature similarity: ", MySigSim(sig[docID1-1],sig[docID2-1],numberOfK))
    
    print("Exiting")

main()

