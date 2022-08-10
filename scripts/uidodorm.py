#26 July 2022. This is the version of this code as of this date. We continue to update this code at: https://github.com/rbailes/DORM-UIDO/blob/master/uidodorm.p

#there is a better library for this - pycontractions, but install is failing for dependency reasons
#we can probably make it work in a final version - it does some context detection to distinguish e.g., he's (he is) tired from he's (he has) gone home
from wordfreq import word_frequency
from nltk.tokenize import word_tokenize
from itertools import permutations
import pandas as pd
import numpy as np
import string,re
import contractions
import collections, math




def infovec(senString):
  #PART I: cleaning
  #first, clean the string: expand contractions, strip punctuation and capitalisation
  #Fix bad quotes that cause tokenization probs
  s = re.sub("[“”]","\"",senString)
  s = re.sub("[‘’]","\'",s)
  s = s.replace("—","--")
  s = s.replace("–","-")
  #s=contractions.fix(senString) #2022: trying with contractions, since they have different freqs and the word_tokenizer can deal with them. Note that it can also deal with trailing punctuation on words, though it uses intraword punctuation

  #2022: this was removing important information for the tokenizer, so instead, we let the tokenizer use punctuation, but then remove punctuation-only tokens later because word_frequency doesn't process them, though it does process intraword punctuation.
  #s=s.translate(str.maketrans('', '', string.punctuation)).lower()

  #split into an array; changed to nltk tokenizer 1Aug2022
  #s=s.split() #JCW: this used to be 'split(" ")', but I'm pretty sure it should split on all whitespace and we were losing words before...12May2020
  s = word_tokenize(s)
  
  #PART II: the information content vector
  orderedIC=[]
  for w in s:
    #the minimum here is veeery low (could proabbly be higher) and is mainly to prevent zero division errors
    #prevents punctuation-only tokens from ending up in the final list
    if re.match("^[%s]+$" % string.punctuation,w) == None:
      f=word_frequency(w,'en', minimum=0.000000000000000001)
      orderedIC.append(1/f)

  numberOfWords = len(orderedIC)
  logvec=np.log2(orderedIC)
  meanInfo = np.mean(logvec)
  
  return(logvec,numberOfWords,meanInfo)




def dorm(logvec, correct=False):
  #PART III: The DORM
  if len(logvec) <= 2: #changing this to return 0 for 1- and 2-word cases, so that we can used unbiased sample variance as estimator as per Ferrer i Cancho's suggestion
    dorm = 0 #JCW: changed this from "return 0" so that the length correction will still apply
  else:
    logvec_df=pd.DataFrame(logvec)
    rmeans=logvec_df.rolling(2).mean()
    rmeans=rmeans.dropna()
    dorm=  np.var(rmeans.to_numpy(),ddof=1) #Changed to unbiased sample variance 23Nov2020, as estimator as per Ferrer i Cancho's suggestion; old code: np.std(rmeans.to_numpy(),ddof=0) 
    #Notes: by default, ddof = 0, which gives lower dorms than "sd()" and "var()" in R, 
    #which has equivalent of ddof=1. np.std(...,ddof=1) yields identical results to "sd()" in R, and likewise for np.var(). 
    #Note also that ddof=1 fails when there is only 1 mean in the list, since std is computed by dividing by N-ddof observations. ddof=1 provides an unbiased estimator.
    if correct:
      #old way, brute force
      #uniquePerms=list(set(permutations(logvec)))
      #penalty=1/len(uniquePerms)
      
      #new way:
      
      #get dictionary containing the num of occurrences of every item
      itemCount = collections.Counter(logvec)
      repeats = []

      #get a list of repeat words
      for thing in itemCount:
        if itemCount[thing] > 1:
          repeats.append(thing)

      denominator = 1

      for rep in repeats:
        denominator = denominator*math.factorial(itemCount[rep])

      numberUniquePerms = math.factorial(len(logvec))/denominator
    
      penaltyProb=(1/numberUniquePerms)
      #This penalty is too small, and it is a probability, which is not the same units as dorm. So we can log it, which converts to bits, and then take the inverse, making sure there's a larger penalty for higher probabilities of a chance uido.
      #Except penaltyProb can't be 1, or else the log is undefined, so we arbitrarily set it to 0.95 in that case.
      if penaltyProb == 1:
        penaltyProb = 0.95
      penalty=(1/-np.log2(penaltyProb))
      #print(penalty)
      dorm+=penalty
  return(dorm)



def getDORM(senString,lenCorrect=False):
  #PARTs I and II: cleaning and logging
  logvec,numberOfWords,meanInfo = infovec(senString) #Note: infovec now also returns sent length
  
  #PART III: The DORM
  thisDorm = dorm(logvec, correct=lenCorrect)
  
  return thisDorm,numberOfWords,meanInfo
  
  
def uido(senString, lenCorrect = False):
  
  logvec = infovec(senString)[0]
  
  #midpoint = (len(logvec)-1)/2
  #print(midpoint)#debug
  #I've modified this to do decreasing because it might be better for head-initial langs
  newlist = sorted(logvec,reverse=True)
  
  mm = 0 
  jj = len(newlist)-1
  
  while (jj > mm):
    #starting from both ends of the array, swaps every other pair of numbers, which gets us very close to optimized
    cup = newlist[mm]
    newlist[mm] = newlist[jj]
    newlist[jj] = cup
    mm = mm+2
    jj = jj-2
  
  #Check to make sure the dorm of newlist isn't actually worse than the original dorm of logvec.
  
  if dorm(logvec, correct=lenCorrect) < dorm(newlist, correct=lenCorrect):
    swaplist = logvec
  else:
    swaplist = newlist
  
  #Gets the sd of the rolling pairwise means, the DORM, which we want to minimize, using the dorm function.

  prevsd = dorm(swaplist, correct = lenCorrect)
  currentsd = prevsd #initialize currentsd
  #print(prevsd)#debug
  
  #Now, see if swapping any pair of numbers gets us a lower sd for pairmeanlist. If any swap does, then do it, otherwise don't. Repeat till no swap helps.
  ll = 0
  #do the swap
  while((ll+1) < len(swaplist)):
    hyplist = []
    if (ll == 0): #when we are at the beginning of the list
      hyplist.append(swaplist[ll+1])
      hyplist.append(swaplist[ll])
      hyplist.extend(swaplist[(ll+2):len(swaplist)]) #CAVEAT: for lists in Python, unlike in R, slice syntax list[i:j] returns a list that does not include list[j]
      
    elif ((ll+1) == (len(swaplist)-1)): #when counter is at the penultimate place in the list and ll+1 is the end of the list
      hyplist.extend(swaplist[0:ll])
      hyplist.append(swaplist[ll+1])
      hyplist.append(swaplist[ll])
      
    else: #when we are in the middle of the list
      hyplist.extend(swaplist[0:ll])
      hyplist.append(swaplist[ll+1])
      hyplist.append(swaplist[ll])
      hyplist.extend(swaplist[(ll+2):len(swaplist)])
    
    currentsd = dorm(hyplist, correct = lenCorrect)
    
    
    #if the swap helped, then save that version of the list, and start the process over again, starting the counter at 1 again
    if (currentsd < prevsd):
      #print((prevsd-currentsd)) #debug
      swaplist = hyplist
      prevsd = currentsd
      ll = 0
      #print("we improved") #debug
    
    else:
      ll = ll+1
  
  #print("and here is new dorm") #debug
  #print(prevsd)#debug
  
  return(swaplist)
