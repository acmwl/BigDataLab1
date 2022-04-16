from ctypes import Union
from operator import index
import random
import time
import timeit
from math import floor

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█'): #Prints a simple progress bar to be used on for loops 
    #Taken from https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r %s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()
        print() 

def create_random_hash_function(p=2**33-355, m=2**32-1): #Returns Hash function to be used by MinHash and LSH
    a = random.randint(1,p-1)
    b = random.randint(0, p-1)
    return lambda x: 1 + (((a * x + b) % p) % m)

def MyReadDataRoutine(fileName, numDocuments): #Reads all words from input file and returns a list of sets containing all the words from each document
    input = open(fileName,"r") #open file
    output = list()
    numDocuments = int(numDocuments)

    if numDocuments>int(input.readline()) or numDocuments<0: #check if numDocuments is valid
        print("Wrong numDocuments input")
        return 0

    global dictSize
    dictSize = int(input.readline()) #initalise total number of possible words globaly
    input.readline() #skip 3rd line

    curLine = input.readline().split() # read current file number
    for i in range(1, numDocuments+1):  # and iterate until we reach next file num
        curSet = set()
        while ((int(curLine[0])) == i): # while we are in the same file num
            curSet.add(int(curLine[1]))
            curLine = input.readline().split()
            if not curLine: # edge case for last file
                break
        output.append(sorted(frozenset(curSet))) # save as frozen set to output list
    print("Successfully imported document data")
    return output 

def MyJacSimWithSets(docID1,docID2): # Returns Jaccard similarity using 2 for loops
    intersectionCounter = 0
    for i in docID1:
        for j in docID2:
            if i==j:
                intersectionCounter+=1
    return intersectionCounter/(len(docID1)+len(docID2)-intersectionCounter)

def MyJacSimWithOrderedLists(docID1, docID2): # Returns Jaccard similarity using an improved algorithm scanning ordered lists
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

def MyMinHash(docList, K): # Hashes all files into signatures to be compared later. Returns said list of signatures
    #random.seed(10)
    h = []
    print("Creating the Minhash Functions")
    total = 0.0
    start=time.process_time()
    for i in range(K): #creates K different hash functions
        randomHash = {i:create_random_hash_function()(i) for i in range(dictSize+1)}
        myHashKeysOrderedByValues = sorted(randomHash, key = randomHash.get)
        myHash = {myHashKeysOrderedByValues[x]:x for x in range(dictSize+1)}
        h.append(myHash)
        printProgressBar(i,K)
    print()

    total += time.process_time()-start 
    print("Hash functions creation time: ",time.process_time()-start," seconds") # calculate time taken to create hash functions
    
    start=time.process_time()
    sig = []
    print("Creating Signatures for each file")
    for col in range(len(docList)): # set values of signatures matrix to max (=dictSize=biggest possible word)
        sig.append([])
        for i in range(K):
            sig[col].append(dictSize)

    for col in range(len(docList)): # for each file
        for row in docList[col]: # for each word
            for i in range(K): # hash and select min possible value (thats why we used max above)
                if h[i].get(row) < sig[col][i]:
                    sig[col][i] = h[i].get(row)
        printProgressBar(col,len(docList))
    print()
    total += time.process_time()-start
    print("Signature creation time: ",time.process_time()-start, " seconds") # calculate time taken to hash documents
    print("MinHash execution time: ",total, " seconds")
    return sig

def MySigSim(docID1, docID2, numPermutations): # compares signatures and returns the similarity
    counter=0
    for i in range(numPermutations): #increase counter for each two same signature parts
        if(docID1[i]==docID2[i]):
            counter+=1
    return counter/numPermutations

def bruteForceJacNeighbors(docList, numDocuments, numNeighbors): # brute force calculation of similarities for select number of closest neighbors. Returns closest neighbor list
    print("Calculating brute force similarity using jacSim, for ",numDocuments," documents and keeping the closest ",numNeighbors, " neighbors")
    if(numDocuments>len(docList) or numNeighbors>len(docList)): #false input
        return
    
    simList = []
    start_time = time.time()
    for i in range(numDocuments): 
        myDict = {}
        for j in range(numDocuments): #for each possible document combination, calculate the distance
            if i==j: 
                continue
            myDict[j] = 1 - MyJacSimWithOrderedLists(docList[i],docList[j])
        myDict = {k: v for k, v in sorted(myDict.items(), key = lambda item:item[1])} #sort by distance
        counter = 0
        neighbors = {}
        for key in myDict: # keep select number of closest neighbors
            if counter>=numNeighbors:
                break
            neighbors[key] = 1 - myDict[key] #convert distance to similarity
            counter += 1
        simList.append(neighbors)
        printProgressBar(i,numDocuments)
    print()

    AvgSim = [] 
    Avg = 0
    for i in range(len(simList)): #calculate average similarity for each document
        avg = 0
        for key in simList[i]:
            avg += simList[i][key] # calculate total average similarity (of average similarities per document)
        AvgSim.append(avg/numNeighbors)
        Avg += AvgSim[i]
    Avg = Avg/numDocuments

    print("Average similarity of all averages for each document: ",Avg)
    #print("Average Similarity for each document :",AvgSim)
    print("Brute force jaccard similarity execution time: ",time.time() - start_time, " seconds")
    return simList #AvgSim #Avg

def bruteForceSigNeighbors(sig, numDocuments, numNeighbors): # Same as above function, but uses Signature similarity instead of Jaccard. Returns similarity list
    print("Calculating brute force Signature similarity, for ",numDocuments," documents and keeping the closest ",numNeighbors, " neighbors")
    start_time=time.time()
    if(numDocuments>len(sig) or numNeighbors>len(sig)):
        return

    simList = []
    for i in range(numDocuments): #find closest neighbors using signatures. Check each possible combination of files
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
        printProgressBar(i,numDocuments)
    print()

    AvgSim = [] #calculate and print averages
    Avg = 0
    for i in range(len(simList)):
        avg = 0
        for key in simList[i]:
            avg += simList[i][key]
        AvgSim.append(avg/numNeighbors)
        Avg += AvgSim[i]
    Avg = Avg/numDocuments

    print("Average similarity of all averages for each document: ",Avg)
    #print("Average Similarity for each document :",AvgSim)
    print("Brute force Signature similarity execution time: ",time.time() - start_time, " seconds")
    return simList

def LSH(docList, sig, rowsPerBands, numNeighbors, simMethod): 
    random.seed(10)
    #Locality sensitive hashing to find file combinations with similarities over a threshold. Returns a list of said combinations
    start_time=time.time()
    hashLSH = create_random_hash_function()
    numBands = floor(len(sig[0])/rowsPerBands)
    LSHdicts = [dict() for i in range(numBands)] #docID: hashLSH(SIG[bandRows:docID])
    print("Hashing signatures for each band")
    for band in range(len(LSHdicts)): # hashing signature parts and assinging to hash-bins for each signature for each band
        for signature in range(len(sig)):
            curSig = tuple(sig[signature][band*rowsPerBands:((band+1)*rowsPerBands if (band+1)*rowsPerBands<len(sig[signature]) else len(sig[signature]))]) #create a tuple and hash a select part of a signature
            LSHdicts[band][signature] = hashLSH(hash(curSig)) # select part of above signature is determined by band number. Last band takes rest singnatures (else statement)
        LSHdicts[band] = {k: v for k, v in sorted(LSHdicts[band].items(), key=lambda item: item[1])}  # sort by value
        printProgressBar(band,len(LSHdicts))
    print()

    print("Calculating pairs from above hashes")
    pairs = set()
    progressCounter = 0
    for band in LSHdicts: # for each band extract pairs by inserting them into a list and then calculating all posible combinations
        cand = []
        keys = [key for key in band.keys()]
        #print(keys)
        values = [val for val in band.values()]
        #print(values)
        for val in range(len(values)-1): #found same bin element. Adding it to cand list
            if values[val]==values[val+1] and val<len(values)-2:
                cand.append(keys[val])
            else: #next element is in a different bin. Now we calculate all posible pairs from cand list
                cand.append(keys[val])
                if(len(cand)>1):
                    for i in range(len(cand)-1): #find pairs, save them to tuples, add them to a set
                        for j in range(i+1,len(cand)):
                            if cand[i]<cand[j]:
                                pairs.add((cand[i],cand[j]))
                            elif cand[i]>cand[j]:
                                pairs.add((cand[j],cand[i]))
                            else:
                                print('error')
                cand = []
    
    #now we have all the canditate pairs. Lets calculate average similarities for all documents, based on found pairs
    simList = [dict() for i in range(len(sig))] #exactly like brute force but now we only check the pairs set LSH made

    if simMethod==1: #check with jaccard similarity
        for pair in pairs:                          
            p1 = pair[0]
            p2 = pair[1]
            simList[p1][p2] = MyJacSimWithOrderedLists(docList[p1],docList[p2])
            simList[p2][p1] = MyJacSimWithOrderedLists(docList[p1],docList[p2])
    else: #check with signature similarity
        for pair in pairs:                          
            p1 = pair[0]
            p2 = pair[1]
            simList[p1][p2] = MySigSim(sig[p1],sig[p2], len(sig[0]))
            simList[p2][p1] = MySigSim(sig[p1],sig[p2], len(sig[0]))

    for i in range(len(simList)): #sort list by value (distance, by reverse sorting similarity)
        simList[i] = {k:v for k, v in sorted(simList[i].items(), key = lambda item:item[1],reverse=True)} #sort by distance
        neighbors = dict()
        counter = 0
        for j in simList[i].keys(): #only keep first numNeighbors found
            if counter>=numNeighbors:
                break
            neighbors[j] = simList[i][j]
            counter+=1
        simList[i] = neighbors #and save them to simlist

    print("Calculating average similarity of found pairs:")

    AvgSim = [] #calculate and print averages
    Avg = 0
    for i in range(len(simList)):
        avg = 0
        for key in simList[i]:
            avg += simList[i][key]
        AvgSim.append(avg/(len(simList[i]) if len(simList[i])>0 else 1))
        Avg += AvgSim[i]

    Avg = Avg/len(simList)

    print("Average similarity of all averages for each document: ",Avg)
    #print("Average Similarity for each document :",AvgSim)
    print("LSH similarity execution time: ",time.time() - start_time, " seconds")

    return simList

def LSHcount(numOfHashes):
    minr = numOfHashes  
    for r in range(1,numOfHashes):
        
        b = floor(numOfHashes/r)
        if 0.4<((1/b)**(1/r)) and ((1/b)**(1/r))<0.6:
            minr = r
    print("Recommended rowsPerBand for ",numOfHashes," permutations is ",minr ,
    "and with threshold :" , (1/floor(numOfHashes/minr))**(1/minr))
    return minr

def main():  
    print("Scanning and analysing input document")
    #a
    print("\nSelect which document to use:\n1)Enron Dataset\n2)Nips dataset")
    documentSel=int(input("Input selection (input 1 or 2): "))
    if documentSel<1 or documentSel>2: 
        print("Wrong input")
    numberOfDucuments=int(input("How many documents shall be examined: "))
    inputDoc=MyReadDataRoutine("DATA_1-docword.enron.txt" if documentSel==1 else "DATA_2-docword.nips.txt",numberOfDucuments)

    print()

    #b
    numNeighbors=int(input("Input a number of neighbors to check (input a number between 2 and 5): "))
    if (int(numNeighbors)>5) or (int(numNeighbors)<2):
        print("Wrong input, setting it to 2")
        numNeighbors=2

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
    print("All resulting pairs and lists show documents as their respective counters, but reducted by 1. This means that document i translates to the document with index i+1 in the input file")
    if(compMethod<1 or compMethod >2):
        print("Wrong input, will use option 2")

    if compMethod==1:
        if simMethod==1:
            pairs = bruteForceJacNeighbors(inputDoc,numberOfDucuments,numNeighbors)
            print(pairs if input("print similarity list? (y/n)")=='y' else '')
        else:
            pairs = bruteForceSigNeighbors(sig,numberOfDucuments,numNeighbors)
            print(pairs if input("print similarity list? (y/n)")=='y' else '')
    else:
        #f
        print()
        print("Now setting variables for LSH. Recommended threshold is around 0.5")

        r = LSHcount(numberOfHashes)

        rin = int(input("Select a number of rows to be used per band: "))
        print(rin," rows yield a threshold of ",(1/floor(numberOfHashes/rin))**(1/rin))
        ans = 'y'
        if rin>r+0.1 or rin<r-0.1:
            ans = input("Warning, inputted r yields a threshold far from the recommended. Continue with inputted value? (y/n)")
        r = rin if ans=='y' else r

        print("Using ",r," rows per band, with a total of ",floor(numberOfHashes/r)," bands")

        print("\n")
        pairs = LSH(inputDoc,sig,r,numNeighbors,simMethod)
        print(pairs if input("print found pairs? (y/n)")=='y' else '')

        
    print("Database succesfully scanned\n")

    #3
    print("To verify above finds, you can check for similarity between two specific files")

    while(int(input("How would you like to continue?\n1)Compare specific files\n2)Exit\n"))==1):
        inp = input("Input 2 specific document IDs seperated by space: ").split()
        docID1=int(inp[0])
        docID2=int(inp[1])

        numberOfK=int(input("Select a number of random permutations to be used from the signatures list: "))
        if numberOfK>len(sig[0]):
            numberOfK=len(sig[0])
        print("Computed similarities:\n")

        start = timeit.default_timer()
        jacSimSets = MyJacSimWithSets(inputDoc[docID1-1],inputDoc[docID2-1])
        print("Jaccard similarity using sets: ",jacSimSets," with exec time: ",timeit.default_timer()-start)

        start = timeit.default_timer()
        jacSimLists = MyJacSimWithOrderedLists(inputDoc[docID1-1],inputDoc[docID2-1])
        print("Jaccard similarity using ordered lists: ",jacSimLists," with exec time: ",timeit.default_timer()-start)

        start = timeit.default_timer()
        sigSim = MySigSim(sig[docID1-1],sig[docID2-1],numberOfK)
        print("Signature similarity using minHash signatures: ",sigSim," with exec time: ",timeit.default_timer()-start)
    
    print("Exiting")

def test(simMethod = 1, numOfPermutations = 64, neighborsMethod = 1, numOfNeighbors = 2, file = 1, docNum = 15000):
    inputData = 0
    if file == 2:
        inputData = MyReadDataRoutine("DATA_2-docword.nips.txt",docNum)
    else:
        inputData = MyReadDataRoutine("DATA_1-docword.enron.txt",docNum)
    sig = 0
    if simMethod==2 or neighborsMethod==2:
        sig = MyMinHash(inputData,numOfPermutations)
    if neighborsMethod == 2:
        LSH(inputData, sig, LSHcount(numOfPermutations),numOfNeighbors, simMethod)
    else:
        if simMethod == 2:
            bruteForceSigNeighbors(sig, docNum, numOfNeighbors)
        else:
            bruteForceJacNeighbors(inputData, docNum, numOfNeighbors)
 
test(2,64,2,2,1,15000)

#main()