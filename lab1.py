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
    print("ExecTime : "+time.process_time() - start)
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

def count(variable,numOfHashes):
    r = int(numOfHashes/variable)
    b = floor(numOfHashes/r)
    s = (1/b)**(1/r)
    print("The number of bands : ",b, "\nThe number of Rows : ", r , "\nThe number of Threshold : ",s)
    return r

def main():
    
    
    while True:
        #a
        nameOfDucument=input("Enter the name of the document(name.txt) : ")
        numberOfDucuments=int(input("Give me the number of the documents you want to read : "))
        listData=MyReadDataRoutine(nameOfDucument,numberOfDucuments)

        #b
        numNeighbors=int(input("Give me the number of the neighbors you want: "))
        while (int(numNeighbors)>5) or (int(numNeighbors)<2):
            numNeighbors=input("Give me again the number of the neigbors you want (2,3..,5): ")

        #c
        numberOfK=int(input("Give me the number of random permutations (we suggest that the number is a power of 2) : "))
        sig=MyMinHash(listData,numberOfK)
        

        #d
        method=input("Give me which similarity method you want to use (JacSim or SigSim): ")

        #e
        method1=input("Which method you want to use BruteForce or LSH: ")

        if method1=="BruteForce":
            if method=="JacSim":
                bruteForceJacNeighbors(listData,numberOfDucuments,numNeighbors)
            elif method=="SigSim":
                bruteForceSigNeighbors(sig,numberOfDucuments,numNeighbors)
        elif method1=="LSH":
            number=0
            variable=8
            
            while True:
                print("We recommend :\n")
                number=count(variable,numberOfK)
                answer=input("\n If you want to increase the threshold type (increase) else type (decrease) or enter for continue: ")
                if(answer=="increase"):variable=variable/2
                elif(answer=="decrease"):variable=variable*2
                else: break
            print("\n")
            LSH(sig,number)
            
        print("\n")
        if(input("Do you want to give me specific docID (Yes or No) :")=="Yes"):
            docID1=int(input("Give me the first DocID : "))
            docID2=int(input("Give me the second DocID : "))

            numberOfK=int(input("Give me the number of random permutations : "))

            print("Jac sim with Sets: ",MyJacSimWithSets(listData[docID1-1],listData[docID2-1]))
            print("Jac sim with Ordered List : ", MyJacSimWithOrderedLists(listData[docID1-1],listData[docID2-1]))
            print("Sig sim: ", MySigSim(sig[docID1-1],sig[docID2-1],numberOfK))
    
        if(input("Do you want to start again (Yes or No) :")!="Yes"):break



#variable = 32



#numOfFilesRead = 90
#numOfHashes = 1024
#r = int(numOfHashes/variable)
#b = floor(numOfHashes/r)
#s = (1/b)**(1/r)


#list = MyReadDataRoutine("DATA_1-docword.enron.txt",numOfFilesRead)

#sig = MyMinHash(list,numOfHashes)
#simList = bruteForceSigNeighbors(sig,90,1)
#print(simList[27],simList[48],simList[36],simList[45])

main()

#LSH(sig, r)
#print("Bands: ",b,"\nRows: ",r,"\nThreshold: ",s)


#print("Jac sim: ",MyJacSimWithSets(list[5],list[18]))
#print("Sig sim: ",MySigSim(sig[5],sig[18],200))
