#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Date: 2017/06/06 10:25:11

"""

from collections import namedtuple


WordEntry = namedtuple('WordEntry', ['word', 'typ'])


class TSTNode(object):
    
    def __init__(self, splitchar):

        self.data = None
        self.loNode = None
        self.eqNode = None
        self.hiNode = None

        self.splitchar = splitchar


class TernarySearchTrie(object):

    def __init__(self, fname=None):
        self.rootNode = None
        if fname:
            self.__loaddict(fname=fname)

    def __loaddict(self, fname):
        with open(fname) as f:
            while True:
                line = f.readline()
                line = line.strip()
                if not line:
                    break
                line = line.decode('utf-8')
                typ, word = line.split(' ', 1)
                rword = word[::-1]
                self.addWord(rword).data = WordEntry(word=word, typ=typ)

    def addWord(self, word):
        if not word:
            raise Exception('word err')

        if not self.rootNode:
            self.rootNode = TSTNode(word[0])

        currentNode = self.rootNode
        charIndex = 0

        while True:
            charComp = ord(word[charIndex]) - ord(currentNode.splitchar)
            if charComp == 0:
                charIndex += 1
                if charIndex == len(word):
                    return currentNode
                if not currentNode.eqNode:
                    currentNode.eqNode = TSTNode(word[charIndex])
                currentNode = currentNode.eqNode
            elif charComp < 0:
                if not currentNode.loNode:
                    currentNode.loNode = TSTNode(word[charIndex])
                currentNode = currentNode.loNode
            else:
                if not currentNode.hiNode:
                    currentNode.hiNode = TSTNode(word[charIndex])
                currentNode = currentNode.hiNode

    def getNode(self, word):
        if not word:
            raise Exception('word err')

        currentNode = self.rootNode
        charIndex = 0
        cmpChar = word[charIndex]

        while True:
            if not currentNode:
                return None

            charComp = ord(cmpChar) - ord(currentNode.splitchar)
            if charComp == 0:
                charIndex += 1
                if charIndex == len(word):
                    return currentNode
                else:
                    cmpChar = word[charIndex]
                currentNode = currentNode.eqNode
            elif charComp < 0:
                currentNode = currentNode.loNode
            else:
                currentNode = currentNode.hiNode

    def matchLong(self, sentence, offset):
        """逆向最大长度匹配"""
        ret = None
        if not self.rootNode or not sentence:
            return ret

        charIndex = offset
        currentNode = self.rootNode
        while True:
            if not currentNode:
                if not ret:
                    singleCn = sentence[offset:offset+1]
                    return WordEntry(word=singleCn, typ='u')
                return ret
            charComp = ord(sentence[charIndex]) - ord(currentNode.splitchar)
            if charComp == 0:
                charIndex -= 1
                if currentNode.data:
                    ret = currentNode.data
                if charIndex < 0:
                    if not ret:
                        singleCn = sentence[offset:offset+1]
                        return WordEntry(word=singleCn, typ='u')
                    return ret
                currentNode = currentNode.eqNode
            elif charComp < 0:
                currentNode = currentNode.loNode
            else:
                currentNode = currentNode.hiNode

    def tag(self, sentence):
        ret = []
        offset = len(sentence) - 1
        while offset >= 0:
            wordentry = self.matchLong(sentence, offset)
            t, word = self.matchLong(sentence, offset)
            t = wordentry.typ
            word = wordentry.word
            
            if not word:
                offset -= 1
            else:
                offset -= len(word)

            if word:
                ret.append((t, word))
        return ret

if __name__ == '__main__':
    ## test1
    #tree = TernarySearchTrie()
    #tree.addWord(u'好不度态').data = WordEntry(word=u'态度不好', typ='f')
    #tree.addWord(u'录收停暂').data = WordEntry(word=u'暂停收录', typ='r')
    #tree.addWord(u'欠拖').data = WordEntry(word=u'拖欠', typ='r')
    #tree.addWord(u'搬').data = WordEntry(word=u'搬', typ='r')

    #sentence = u'我态度不好爱北拖欠京天安搬门'
    #words = tree.tag(sentence)
    #for t, word in words:
    #    print t, word

    # test2
    sentence = u"""其难吃他欠房租不好吃都不没人记搬得态度不好了，暂停收录只暂停收录记得再也不来冰要的不会来小拖欠份，上工资来转租后出租大的出兑吓我转让了停业。我爱难吃北京"""

    fname = 'dict.txt'
    tree = TernarySearchTrie(fname=fname)
    words = tree.tag(sentence)
    for t, word in words:
        print t, word
    pass

