#!/usr/bin/python
from optparse import OptionParser
import re

'''
Simple part-of-speech tagger which either tags analyses in a text file or
a single analyses on the command line.

    ----------------------------------------------------------------------
    Copyright (C) 2010  Sebastian Spiegler, spiegler@cs.bris.ac.uk

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    ----------------------------------------------------------------------

This is a prototype for a rule-based Zulu part-of-speech (POS) tagger. 
It is based on 34 hard-coded rules which assign a to a morphologically 
analysed Zulu word.

The POS-tagger can be used in 3 different ways:
1) assign POS-tags to a list of morphological analyses.
2) assign a POS-tag to a single morphological analysis in the console.
3) assign POS-tags to words in sentences for which a morphological analysis
   is given in a separate file.

For help use: "posTagger.py -h". 

@author: Sebastian Spiegler, University of Bristol, Bristol, U.K.
@contact: spiegler@cs.bris.ac.uk
@license: GNU GENERAL PUBLIC LICENSE, Version 3, 29 June 2007
@version: 1.0 (2010-07-17)
Created on Jul 17, 2010
'''

class PosTagger(object):
################################################################################
#
# Variables
#
################################################################################
    def add2DictList(self, _dict, _key, _element):
        if _dict.__contains__(_key):
            _list = _dict[_key]
            _list.append(_element)
            _dict[_key] = _list
        else:
            _list = list()
            _list.append(_element)
            _dict[_key] = _list
        return _dict
    
    def add2DictSet(self,_dict, _key, _element):
        if _dict.__contains__(_key):
            _set = _dict[_key]
            _set.add(_element)
            _dict[_key] = _set
        else:
            _set = set()
            _set.add(_element)
            _dict[_key] = _set
        return _dict
    
    def incDict(self, _dict, _key, _inc):
        if _dict.__contains__(_key):
            _value = _dict[_key]
            _value += _inc
            _dict[_key] = _value
        else:
            _dict[_key] = _inc
        return _dict


    def calcSets(self):
        #===========================================================================
        # Original sets
        #===========================================================================

        # 'X' stands for numbers 1-15, or '1s' or '2s' or '1p' or 2p'
        self._xSet = set()
        self._xSet = set(['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','1s','2s','1p','2p', '1pp', '2pp', '1ps', '2ps'])

        # 'J' stands for any of the following morphemes; <ar>, <adv>, <cj>, <locpf>, <mr>, <nY>, <nr>, <p>, <prZ>, <vr>, <qr>, <cj>, <intj>
        # 'J' stands for any of the following morphemes: <adv>, <advpf>, <fut>, <imp>, <locpf>, <mr>, <nr>, <nX>, <opt>, <p>, <prX>, <qr>, <r>, <vr>
        self._jSet = set()
        self._jSet = set(['<ar>', '<adv>', '<advpf>', '<d>', '<fut>', '<imp>', '<locpf>', '<mr>', '<nr>', '<opt>', '<p>', '<qr>', '<r>', '<vr>'])
        for x in self._xSet:
            self._jSet.add('<n' + x + '>')
            self._jSet.add('<pr' + x + '>')
            self._jSet.add('<d' + x + '>')

        #===========================================================================
        # Auxiliary sets
        #===========================================================================
        self._prXSet = set()
        self._pXSet = set()
        self._iXSet = set()
        self._dXSet = set()
        self._nXSet = set()
        self._iv_nXSet = set()
        self._zXSet = set()
        self._zX_ivSet = set()
        self._iX_vrSet = set()
        self._pX_vrSet = set()
        self._sXSet = set()
        self._oXSet = set()
        for x in self._xSet:
            self._prXSet.add('<pr' + x + '>')
            self._pXSet.add('<p' + x + '>')
            self._iXSet.add('<i' + x + '>')
            self._dXSet.add('<d' + x + '>')
            self._nXSet.add('<n' + x + '>')            
            self._iv_nXSet.add('<iv_n' + x + '>')
            self._zXSet.add('<z' + x + '>')
            self._zX_ivSet.add('<z' + x + '_iv')
            self._iX_vrSet.add('<i' + x + '_vr')
            self._pX_vrSet.add('<p' + x + '_vr')
            self._sXSet.add('<s' + x + '>')
            self._oXSet.add('<o' + x + '>')

    def getSegmentLabelSeq(self, line):
        pattern = "(\w+)(<\w+>)"
        found = re.findall(pattern, line)
        segmentation = list()
        labels = list()
        segLabelCombis = list()
        for (s,l) in found:
            segmentation.append(s)
            segLabelCombis.append(s + l)
            if not list(l).__contains__("_"):
                labels.append(l)
            else:
                l = re.sub("_", ">_<", l)
                labels.extend(l.split("_"))
        return (segmentation, labels, segLabelCombis)
    
    def processing(self, inFile, outFile, separate, printWord, multiLabel, sentenceInFile, debug):
        self.calcSets()
        #if debug:
        #    self.printDebug()
        #    exit()
        
        if not multiLabel and sentenceInFile == None:  
            self.doPosTagging(inFile, outFile, separate, printWord, debug)
        elif multiLabel and sentenceInFile == None:
            self.doPosTaggingMulti(inFile, outFile, debug)
        elif sentenceInFile != None:
            self.doSentenceTag(inFile, sentenceInFile, outFile, debug)
        else:
            print "Confusing parameters!"
            
    def doPosTagging(self, inFile, outFile, separate, printWord, debug):
        resultList = list()
        resultDictList = dict()
        for line in open(inFile,'r'):
            (segmentation, labels, segLabelCombis) = self.getSegmentLabelSeq(line)
            
            pos = self.getPosTag(line, labels, segLabelCombis, debug)
            
            if not separate:
                if not printWord:
                    resultList.append(pos + "\t" + line)
                else:
                    resultList.append("".join(segmentation) + "\t" + pos + "\t" + line)
            else:
                if not printWord:
                    resultDictList = self.add2DictList(resultDictList, pos, line)
                else:
                    line = "".join(segmentation) + "\t" + pos + "\t" + line
                    resultDictList = self.add2DictList(resultDictList, pos, line)
                    
        if not separate:
            f_out = open(outFile, 'w')
            f_out.writelines(resultList)
            f_out.close()
        else:
            for key in resultDictList:
                sublist = resultDictList[key]
                f_out = open(outFile + '.' + key, 'w')
                f_out.writelines(sorted(sublist))
                f_out.close()
                
    def doPosTaggingMulti(self, inFile, outFile, debug):
        wordDictSet = dict()
        for line in open(inFile,'r'):
            (segmentation, labels, segLabelCombis) = self.getSegmentLabelSeq(line)
            word = "".join(segmentation)
            pos = self.getPosTag(line, labels, segLabelCombis, debug)
            wordDictSet = self.add2DictSet(wordDictSet, word, pos)

        
        posStats = dict()
        f_out = open(outFile, 'w')
        for word in sorted(wordDictSet.keys()):
            posSet = sorted(wordDictSet[word])
            posStats = self.incDict(posStats, len(posSet), 1)
            result = word + "\t"
            for pos in posSet:
                result += pos + ", "
            result = result[0:len(result)-2] + "\n"
            f_out.write(result)
        f_out.close()
        
        print "POS statistics:", posStats

    def doSentenceTag(self, inFile, sentenceInFile, outFile, debug):
        wordDictSet = dict()
        for line in open(inFile,'r'):
            (segmentation, labels, segLabelCombis) = self.getSegmentLabelSeq(line)
            word = "".join(segmentation)
            pos = self.getPosTag(line, labels, segLabelCombis, debug)
            wordDictSet = self.add2DictSet(wordDictSet, word, pos)
        
        multiStats = dict()
        f_out = open(outFile, 'w')
        for line in open(sentenceInFile, 'r'):
            line = re.sub("\n$", "", line)
            words = line.split(" ")
            
            stopFlag = 0
            multiFlag = 0
            
            posList = list()
            for word in words:
                if wordDictSet.__contains__(word):
                    posSet = wordDictSet[word]
                    posList.append(list(posSet))
                    if len(posSet) > 1:
                        multiFlag += 1
                else:
                    stopFlag = 1
                
            if stopFlag == 0:
                result = str(posList)
                result = re.sub("'", "", result)
                result = re.sub(" ", "", result)
                result = line + "\t" + result
                f_out.write(result + "\n")
            if not stopFlag:
                multiStats = self.incDict(multiStats, multiFlag, 1)
        f_out.close()
        print "Sentence stats:", multiStats
            
           
    def getPosTag(self, line, labels, segLabelCombis, debug):
        firstMorpheme = labels[0]
        jMorphemes = list()
        for i in range(1, len(labels)):
            label = labels[i]
            if self._jSet.__contains__(label):
                jMorphemes.append(label)
        try:
            jMorpheme1 = jMorphemes[0]
        except IndexError:
            jMorpheme1 = None
            
        posTag = str()
        
        #adv rules
        # ADDED: adv    first morpheme <red>     J morpheme <adv>
        if firstMorpheme == "<red>" and jMorpheme1 == "<adv>":
            posTag = 'adv'
            if debug:  
                posTag += " 1"
  
        # cop rules
        elif (firstMorpheme == '<asp>' and (jMorpheme1 == '<adv>' or jMorpheme1 == '<advpf>' or jMorpheme1 == '<ar>' or jMorpheme1 == '<locpf>' or jMorpheme1 == '<nr>' or jMorpheme1 == '<p>' or self._prXSet.__contains__(jMorpheme1) or jMorpheme1 == '<r>' or self._pXSet.__contains__(jMorpheme1) or self._nXSet.__contains__(jMorpheme1))):
            posTag = 'cop'
            if debug:  
                posTag += " 2"
            
        # ADDED: cop    first morpheme <iX>     J morpheme <nX>
        # ADDED: cop    first morpheme <iX>     J morpheme <d>
        # ADDED: cop    first morpheme <iX>     J morpheme <dX>            
        elif (self._iXSet.__contains__(firstMorpheme) and (jMorpheme1 == '<adv>' or jMorpheme1 == '<advpf>' or jMorpheme1 == '<ar>' or self._dXSet.__contains__(jMorpheme1) or jMorpheme1 == '<in>' or jMorpheme1 == '<locpf>' or jMorpheme1 == '<nr>' or jMorpheme1 == '<p>' or self._prXSet.__contains__(jMorpheme1) or jMorpheme1 == '<r>' or self._nXSet.__contains__(jMorpheme1) or jMorpheme1 == '<d>' or self._dXSet.__contains__(jMorpheme1))): 
            posTag = 'cop'
            if debug:  
                posTag += " 3"
            
        # ADDED: cop    first morpheme <neg>     J morpheme <nX>            
        elif (firstMorpheme == '<neg>' and (jMorpheme1 == '<adv>' or jMorpheme1 == '<advpf>' or jMorpheme1 == '<ar>' or jMorpheme1 == '<locpf>' or jMorpheme1 == '<nr>' or jMorpheme1 == '<p>' or self._prXSet.__contains__(jMorpheme1) or jMorpheme1 == '<r>' or self._nXSet.__contains__(jMorpheme1))): 
            posTag = 'cop'
            if debug:  
                posTag += " 4"
            
        elif (firstMorpheme == '<past>' and (jMorpheme1 == '<adv>' or jMorpheme1 == '<advpf>' or jMorpheme1 == '<locpf>' or jMorpheme1 == '<nr>' or jMorpheme1 == '<p>' or self._prXSet.__contains__(jMorpheme1) or jMorpheme1 == '<r>')):
            posTag = 'cop'
            if debug:  
                posTag += " 5"
            
        # ADDED: cop    first morpheme <pX>     J morpheme <nX>
        # ADDED: cop    first morpheme <pX>     J morpheme <d>
        # ADDED: cop    first morpheme <pX>     J morpheme <dX>
        elif (self._pXSet.__contains__(firstMorpheme) and (jMorpheme1 == '<adv>' or jMorpheme1 == '<advpf>' or jMorpheme1 == '<ar>' or jMorpheme1 == '<locpf>' or jMorpheme1 == '<nr>' or jMorpheme1 == '<p>' or self._prXSet.__contains__(jMorpheme1) or jMorpheme1 == '<r>' or self._nXSet.__contains__(jMorpheme1) or jMorpheme1 == '<d>' or self._dXSet.__contains__(jMorpheme1))): 
            posTag = 'cop'
            if debug:  
                posTag += " 6"
            
        # ADDED: cop     first morpheme <st>     J morpheme <nX>
        elif (firstMorpheme == '<st>' and (jMorpheme1 == '<ar>' or self._nXSet.__contains__(jMorpheme1))):
            posTag = 'cop'
            if debug:  
                posTag += " 7"

        # m rules
        elif jMorpheme1 == "<mr>" and (firstMorpheme == '<asp>' or self._iXSet.__contains__(firstMorpheme) or firstMorpheme == '<neg>' or firstMorpheme == '<past>' or self._pXSet.__contains__(firstMorpheme)):
            posTag = 'm'
            if debug:  
                posTag += " 8"
            
        # n rules
        # ADDED: n    first morpheme <voc>
        elif firstMorpheme == '<d>' and (self._nXSet.__contains__(jMorpheme1) or jMorpheme1 == '<nr>'):
            posTag = 'n'
            if debug:  
                posTag += " 9"
            
        elif self._dXSet.__contains__(firstMorpheme) and (self._nXSet.__contains__(jMorpheme1) or jMorpheme1 == '<nr>'):
            posTag = 'n'
            if debug:  
                posTag += " 10"
            
        elif firstMorpheme == '<vr>' and jMorpheme1 == '<in>':
            posTag = 'n'
            if debug:  
                posTag += " 11"
            
        # ADDED: n    first morpheme <red>     J morpheme <nr>
        elif firstMorpheme == '<red>' and jMorpheme1 == '<nr>':
            posTag = 'n'
            if debug:  
                posTag += " 12"
            
        # ADDED: <prX> + <st> = pr 
        # pro rules
        elif self._prXSet.__contains__(firstMorpheme) or jMorpheme1 == '<st>':
            posTag = 'pron'
            if debug:  
                posTag += " 13"        

        # q rules
        elif self._prXSet.__contains__(firstMorpheme) and (jMorpheme1 == '<qr>' or self._nXSet.__containts__(jMorpheme1)):
            posTag = 'q'
            if debug:  
                posTag += " 14"

        # v rules
        elif (jMorpheme1 == '<vr>' or jMorpheme1 == '<fut>' or jMorpheme1 == '<opt>') and (firstMorpheme == '<asp>' or self._iXSet.__contains__(firstMorpheme) or firstMorpheme == '<neg>' or firstMorpheme == '<past>' or self._pXSet.__contains__(firstMorpheme)):
            posTag = 'v'
            if debug:  
                posTag += " 15"
        
        elif jMorpheme1 == '<imp>' and (self._oXSet.__contains__(firstMorpheme) or firstMorpheme == '<red>' or firstMorpheme == '<refl>' or firstMorpheme == '<st>' or firstMorpheme == '<vr>'):
            posTag = 'v'
            if debug:  
                posTag += " 16"

        elif firstMorpheme == '<vr>' and jMorpheme1 == '<pl>':
            posTag = 'v'
            if debug:  
                posTag += " 17"
         
        #ADDED: first morpheme <oX>     J morpheme <vr>     
        elif self._oXSet.__contains__(firstMorpheme) and jMorpheme1 == '<vr>':
            posTag = 'v'
            if debug:  
                posTag += " 18"
        
        # ADDED: first morpheme <red>    J morpheme <vr>
        # ADDED: first morpheme <refl>   J morpheme <vr>
        # ADDED: first morpheme <st>     J morpheme <vr>
        elif jMorpheme1 == '<vr>' and (firstMorpheme == '<red>' or firstMorpheme == '<refl>' or firstMorpheme == '<st>'):
            posTag = 'v'
            if debug:  
                posTag += " 19"

        #=======================================================================
        # FIRST MORPHEME
        #=======================================================================
        #a rules
        elif firstMorpheme == "<ar>":
            posTag = 'a'
            if debug:  
                posTag += " 20"
            
        # adv
        elif firstMorpheme == "<adv>" or firstMorpheme == "<advpf>":
            posTag = 'adv'
            if debug:  
                posTag += " 21"
  
        #conj rules
        elif firstMorpheme == "<cj>":
            posTag = 'conj'
            if debug:  
                posTag += " 22"

        # dem rules
        elif firstMorpheme == '<d>' or self._dXSet.__contains__(firstMorpheme):
            posTag = 'dem'  
            if debug:  
                posTag += " 23"
            
        # intj rule
        elif firstMorpheme == '<intj>':
            posTag = 'intj' 
            if debug:  
                posTag += " 24"
            
        # n rules
        elif firstMorpheme == '<iv>' or self._iv_nXSet.__contains__(firstMorpheme) or self._nXSet.__contains__(firstMorpheme) or firstMorpheme == '<nr>' or firstMorpheme == '<der>' or firstMorpheme == '<voc>':
            posTag = 'n'
            if debug:  
                posTag += " 25"
            
        # loc rule
        elif firstMorpheme == '<locpf>':
            posTag = 'loc' 
            if debug:  
                posTag += " 26"
            
        # p rule
        elif firstMorpheme == '<p>':
            posTag = 'p'
            if debug:  
                posTag += " 27"
            
        # pres rule
        elif firstMorpheme == '<pres>':
            posTag = 'pres'
            if debug:  
                posTag += " 28"
                
        # pron rule
        elif self._prXSet.__contains__(firstMorpheme):
            posTag = 'pron'
            if debug:  
                posTag += " 29"

        # pos rules
        elif self._zXSet.__contains__(firstMorpheme) or self._zX_ivSet.__contains__(firstMorpheme):
            posTag = 'pos'
            if debug:  
                posTag += " 30"
                
        # rel rule
        elif firstMorpheme == '<r>':
            posTag = 'rel'
            if debug:  
                posTag += " 31"
            
        elif (firstMorpheme == '<hort>' or self._iX_vrSet.__contains__(firstMorpheme) or self._pX_vrSet.__contains__(firstMorpheme) or self._sXSet.__contains__(firstMorpheme)):
            posTag = 'v'            
            if debug:  
                posTag += " 32"

        #=======================================================================
        # DEFAULT
        #=======================================================================
        #Label for unknown/non-Zulu words
        elif len(labels) == 1 and set(labels).__contains__('<w>'):
            posTag = 'w'
            if debug:  
                posTag += " 33"
        else:
            posTag = 'unknown'
            if debug:  
                posTag += " 34"
        
        return posTag


    def processingSingle(self, singleAnalysis, debug):
        self.calcSets()
        (segmentation, labels, segLabelCombis) = self.getSegmentLabelSeq(singleAnalysis)
        word = "".join(segmentation)
        pos = self.getPosTag(singleAnalysis, labels, segLabelCombis, debug)
        print word + "\t" + singleAnalysis  + ":\t" + pos 

        
################################################################################
#
# Main
#
################################################################################
usage = "\nRule-based part-of-speech tagger for Zulu which uses morphological information\n"
usage +="\nusage 1: %prog -a singleAnalysis, e.g. posTagger.py -a 'a<hort>k<s1>enz<vr>e<vs>'\n"
usage +="\nusage 2: %prog -i inFile -o outFile [-s flag for separate files for each POS] [-w print word at beginning of line] [-m multiLabel (word + all labels)]\n"
usage +="\nusage 3: %prog -i inFile -o outFile -t sentenceInFile\n"
usage +="\nPOS tags:\ta (adjective)\n\t\tadv (adverb)\n\t\tconj (conjunction)\n\t\tcop (copulative)\n\t\tdem (demonstrative)\n\t\tintj (interjection)\n\t\tloc (locative)\n\t\tm (modal)\n\t\tn (noun)\n\t\tp (prepositional)\n\t\tpos (possessive)\n\t\tpres (presentative)\n\t\tpron (pronoun)\n\t\tq (quantifier)\n\t\trel (relative)\n\t\tv (verb)\n"
parser = OptionParser(usage=usage, version="%prog 1.0")
parser.add_option("-i", "--inFile", action="store", type="string", dest="inFile", help="input file")
parser.add_option("-o", "--outFile", action="store", type="string", dest="outFile", help="output file")
parser.add_option("-s", "--separate", action="store_true", dest="separate", help="separate file")
parser.add_option("-w", "--printWord", action="store_true", dest="printWord", help="print word")
parser.add_option("-m", "--multiLabel", action="store_true", dest="multiLabel", help="give word and all labels")
parser.add_option("-d", "--debug", action="store_true", dest="debug", help="debug")
parser.add_option("-t", "--sentenceInFile", action="store", type="string", dest="sentenceInFile", help="sentence input file")
parser.add_option("-a", "--singleAnalysis", action="store", type="string", dest="singleAnalysis", help="single analysis will be analysed")

(options, args) = parser.parse_args()
if options.inFile and options.outFile:
    inFile=options.inFile
    outFile=options.outFile
    separate=options.separate
    printWord=options.printWord
    debug=options.debug
    multiLabel=options.multiLabel
    sentenceInFile=options.sentenceInFile

    pt = PosTagger()
    pt.processing(inFile, outFile, separate, printWord, multiLabel, sentenceInFile, debug)
    
elif options.singleAnalysis:
    singleAnalysis=options.singleAnalysis
    debug=options.debug
    
    pt = PosTagger()
    pt.processingSingle(singleAnalysis, debug)

else:
    print usage