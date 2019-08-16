# -*- coding: utf-8 -*-

class CnToken(object):

    def __init__(self, start=-1, end=-1, word=''):
        self.start = start
        self.end = end
        self.word = word

    def __str__(self):
        line = 'word:%s start:%s end:%s' % (self.word, self.start, self.end)
        if isinstance(line, unicode):
            return line.encode('utf-8')
        return line


class Node(object):

    def __init__(self, cnToken):
        self.item = cnToken
        self.next = None


class CnTokenLinkedList(object):

    def __init__(self):
        self.head = None
        self.tail = None

    def put(self, item):
        """ 
        item: CnToken
        往tail上追加节点
            
        """

        t = self.tail
        self.tail = Node(item)
        if not self.head:
            self.head = self.tail
        else:
            t.next = self.tail

    def __str__(self):
        buf = ''
        cur = self.head
        while cur:
            buf += str(cur.item)
            buf += '\t'
            cur = cur.next
        return buf


class AdjList(object):
    
    def __init__(self, verticesNum):
        self.verticesNum = verticesNum
        self.arr = [CnTokenLinkedList() for _ in range(verticesNum)]


    def addEdge(self, edge):
        self.arr[edge.end].put(edge)


    def __str__(self):
        buf = ''
        for i in range(self.verticesNum):
            if not self.arr[i]:
                continue

            buf += 'node:%s:%s\n' % (i, self.arr[i])
        buf = buf.strip()
        return buf


class WordEntry(object):

    def __init__(self, word, categories):
        self.word = word
        self.types = []
        self.types.append(categories)

    def appendTopicType(self, categories):
        self.types.append(categories)

    def __str__(self):
        line = '%s pos:%s' % (self.word, self.types)
        return line.encode('utf-8')


class TSTNode(object):

    def __init__(self, key):
        self.splitChar = key

        self.loNode = None
        self.eqNode = None
        self.hiNode = None

        self.data = None

    def __str__(self):
        return 'data [%s] spliter [%s]' % (self.data, self.splitChar.encode('utf-8'))



class TernarySearchTrie(object):

    def __init__(self, path='./dict.txt'):

        self.rootNode = None
        self.nodeId = 1
        self.path = path
        self.loadDict(self.path)

    def loadDict(self, path):
        # 统一都定为色情, 之后可以细分
        typ = 'porn'

        with open(path) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                try:
                    word = line.strip().decode('utf-8')
                except:
                    continue

                if not word:
                    continue

                if not self.rootNode:
                    self.rootNode = TSTNode(word[-1])

                currentNode = self.getOrCreateNode(word)
                if not currentNode.data:
                    we = WordEntry(word, typ)
                    currentNode.data = we
                else:
                    currentNode.data.appendTopicType(typ)


    def getNode(self, key):
        """
        查找词对应的节点
        """
        if not key:
            raise Exception('key is null')

        charIndex = len(key) - 1
        currentNode = self.rootNode

        while True:
            if not currentNode:
                return None
            compa = ord(key[charIndex]) - ord(currentNode.splitChar)
            if compa == 0:
                if charIndex <= 0:
                    return currentNode
                charIndex -= 1
                currentNode = currentNode.eqNode
            elif compa < 0:
                currentNode = currentNode.loNode
            else:
                currentNode = currentNode.hiNode

    def getOrCreateNode(self, key):
        """
        创建节点
        """
        if not key:
            raise Exception('key is null')

        charIndex = len(key) - 1
        currentNode = self.rootNode
        if not self.rootNode:
            self.rootNode = TSTNode(key[charIndex])
            self.nodeId += 1

        while True:
            compa = ord(key[charIndex]) - ord(currentNode.splitChar)

            if compa == 0:
                if charIndex <= 0:
                    return currentNode
                charIndex -= 1
                if not currentNode.eqNode:
                    currentNode.eqNode = TSTNode(key[charIndex])
                    self.nodeId += 1
                currentNode = currentNode.eqNode
            elif compa < 0:
                if not currentNode.loNode:
                    currentNode.loNode = TSTNode(key[charIndex])
                    self.nodeId += 1
                currentNode = currentNode.loNode
            else:
                if not currentNode.hiNode:
                    currentNode.hiNode = TSTNode(key[charIndex])
                currentNode = currentNode.hiNode

    def matchAll(self, sentence, offset, ret):
        if not sentence or not self.rootNode:
            return False

        currentNode = self.rootNode
        charIndex = offset
        while True:
            if not currentNode:
                if len(ret) > 0:
                    return True
                return False
            
            charComp = ord(sentence[charIndex]) - ord(currentNode.splitChar)
            #charComp =  ord(currentNode.splitChar) - ord(sentence[charIndex])
            if charComp == 0:
                if currentNode.data:
                    ret.append(currentNode.data)

                if charIndex <= 0:
                    if len(ret) > 0:
                        return True
                    return False
                charIndex -= 1
                currentNode = currentNode.eqNode
            elif charComp < 0:
                currentNode = currentNode.loNode
            else:
                currentNode = currentNode.hiNode

    def filter(self, sentence):
        # true kill


        tokens = []

        sLen = len(sentence) + 1

        for i in range(1, sLen):
            words = []
            match = self.matchAll(sentence, i-1, words)
            if match:
                for word in words:
                    start = i - len(word.word)
                    tok = CnToken(start, i, word)
                    tokens.append(tok)
            else:
                start = i - 1
        return tokens


    def split(self, sentence):
        #print u'输入:', sentence
        #print u'全切分结果:'
        sLen = len(sentence) + 1
        g = AdjList(sLen + 1)

        startNode = CnToken(-1, 0, u'start')
        g.addEdge(startNode)

        endNode = CnToken(sLen-1, sLen, u'end')
        g.addEdge(endNode)

        for i in range(1, sLen):
            words = []
            match = self.matchAll(sentence, i-1, words)
            if match:
                for word in words:
                    start = i - len(word.word)
                    tok = CnToken(start, i, word)
                    #print 'match ', tok
                    g.addEdge(tok)
            else:
                start = i - 1
                we = WordEntry(sentence[start: i], ['unknown'])
                tok = CnToken(start, i, we)
                g.addEdge(tok)

        return g


SensitiveFilter=TernarySearchTrie



if __name__ == '__main__':


    client = SensitiveFilter('dict_1.txt')
    import time
    start = time.time()
    input = u"两三百度的眼镜``黄海刺胡，色情，恐怖分子，刺杀，谋杀好好学习天天上上，天眼查是个公司"
    print client.split(input)

    end = time.time()
    print end - start


