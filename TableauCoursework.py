
class Node:
    def __init__(self,formula,parent):
        self.formula = formula
        self.children = []
        self.parent = parent
        self.closed = False
        self.ticked = False

        self.parseParts = []

    def isLeaf(self):
        return self.children == []

    def createNodes(self,parts):
        if len(parts)==0:
            return
        if self.isLeaf():
            if len(parts)==3:
                if (parts[1]=="^"):                 # Alpha formula
                    p = Node(parts[0],self)
                    self.children = [p]
                    p.closeBranch()
                    self.children[0].createNodes([parts[2]])
                elif (parts[1]=="v"):               # Beta formula
                    p1 = Node(parts[0],self)
                    p2 = Node(parts[2],self)
                    self.children = [p1,p2]
                    p1.closeBranch()
                    p2.closeBranch()
                    return
            elif len(parts)==1:
                p = Node(parts[0],self)
                self.children = [p]
                p.closeBranch()
                return
        else:
            for i in range(len(self.children)):
                if not (self.children[i].closed):
                    self.children[i].createNodes(parts)


    def findClosingNode(self):
        if (self.formula[0] == "-"):
            nFMLA = self.formula[1:]
        else:
            nFMLA = "-" + self.formula
        closingNode = self.FCNrecur(nFMLA)
        return closingNode
        
    def FCNrecur(self,f):
        if self.formula == f:
            return self
        else:
            if self.parent != None:
                return self.parent.FCNrecur(f)
            else:
                return None

    def closeBranch(self):
        closingNode = self.findClosingNode()
        if closingNode == None: return None
        current = self
        while current != None:
            nonClosedChildren = len(current.children)
            for i in range(len(current.children)):
                if (current.children[i].closed):
                    nonClosedChildren-=1
            if nonClosedChildren==0:
                current.closed = True
                current = current.parent
            else:
                break
        return closingNode



    def parseFMLA(self):
        PROP = ["p","q","r","s"]
        CON = ["^","v",">"]
        VAR = ["x","y","z","w","a","b","c","d","e","f","g","h","i","j"]
        PRED = ["P","Q","R","S"]
        fmla = self.formula

        isFO = False
        for i in range(len(PRED)):
            if PRED[i] in fmla:
                isFO = True
                break
        for i in range(len(VAR)):
            if VAR[i] in fmla:
                isFO = True
                break
            if isFO: break
        if "E" in fmla or "A" in fmla:
            isFO = True
        
        if (fmla=="") or (" " in fmla):
            if self.parseParts==[]:
                self.parseParts = [0]
            return

        if len(fmla)==1:                # PROP
            if fmla in PROP:
                if self.parseParts==[]:
                    self.parseParts = [6]
                return [] # make no new parts
            else:
                self.parseParts = [0]
                return
        if len(fmla)==2:                # -PROP
                if (fmla[0]=="-") and (fmla[1] in PROP):
                    if self.parseParts==[]:
                        self.parseParts = [7]
                    return []
                else:
                    self.parseParts = [0]
                    return

        if isFO and len(fmla)<6:
            self.parseParts = [0]
            return
        if isFO and len(fmla)==6:       # PRED(VAR,VAR)
            if ((fmla[0] in PRED) and (fmla[1]=="(") and (fmla[2] in VAR) and (fmla[3]==",") and
                (fmla[4] in VAR) and (fmla[5]==")")):
                if self.parseParts==[]:
                    self.parseParts = [1]
                return []
            else:
                self.parseParts = [0]
                return
        if isFO and len(fmla)==7:       # -PRED(VAR,VAR)
            if ((fmla[0]=="-") and (fmla[1] in PRED) and (fmla[2]=="(") and (fmla[3] in VAR) and
                (fmla[4]==",") and (fmla[5] in VAR) and (fmla[6]==")")):
                if self.parseParts==[]:
                    self.parseParts = [2]
                return []
            else:
                self.parseParts = [0]
                return
            
        truth = True
        if fmla[0]=="-":                # -FMLA
            if self.parseParts==[]:
                if isFO:
                    self.parseParts = [2]
                else:
                    self.parseParts = [7]
            i = 0
            while fmla[i]=="-":
                truth = not truth
                i+=1
            if i>=2:
                return ("-"*(i%2))+fmla[i:]
            else:
                fmla = fmla[1:]
        


        if fmla[0]=="E" or fmla[0]=="A":
            if fmla[1] in VAR:
                if self.parseParts==[]:
                    if fmla[0]=="E":    # EvarFMLA
                        self.parseParts = [4]
                    if fmla[0]=="A":    # AvarFMLA
                        self.parseParts = [3]
                if truth:
                    return [fmla[0],fmla[1],fmla[2:]]
                else:
                    if fmla[0]=="E":
                        return "A"+fmla[1]+"-",fmla[2:]
                    else:
                        return "E"+fmla[1]+"-",fmla[2:]
            else:
                if self.parseParts==[]:
                    self.parseParts = [0]

        parts = []
        if fmla[0]=="(" and fmla[-1]==")":
            fmla = fmla[1:-1]           # (FMLA * FMLA)
            brackets = 0
            subFMLA = ""
            for c in range(len(fmla)):
                if fmla[c]=="(": brackets+=1
                if fmla[c]==")": brackets-=1
                subFMLA += fmla[c]
                if (fmla[c] in CON) and (brackets==0):
                    if c > 0 and len(parts)==0:
                        parts.append(subFMLA[:-1])
                        parts.append(fmla[c])
                        subFMLA = ""
                    else:
                        if self.parseParts==[]:
                            self.parseParts = [0]
                        return
            if brackets==0:
                parts.append(subFMLA)
            else:
                if self.parseParts==[]:
                    self.parseParts = [0]
                return

            if len(parts) != 3:
                self.parseParts = [0]
                return

            if self.parseParts==[]:
                if isFO:
                    self.parseParts = [5,parts[0],parts[1],parts[2]]
                else:
                    self.parseParts = [8,parts[0],parts[1],parts[2]]
            if (truth and parts[1]==">"):
                parts[0] = "-"+parts[0]
                parts[1] = "v"
            elif (not truth and parts[1]==">"):
                parts[2] = "-"+parts[2]
                parts[1] = "^"
            elif (not truth and parts[1]=="^"):
                parts[0] = "-"+parts[0]
                parts[1] = "v"
                parts[2] = "-"+parts[2]
            elif (not truth and parts[1]=="v"):
                parts[0] = "-"+parts[0]
                parts[1] = "^"
                parts[2] = "-"+parts[2]
            return parts
        else:
            self.parseParts = [0]
            return

                        
                
        
            
            
class Tableau:
    def __init__(self,formula,theories=[]):
        self.root = Node(formula,None)
        self.prop = ["a","b","c","d","e","f","g","h","i","j"]
        self.propUsed = [False,False,False,False,False,False,False,False,False,False]
        self.gammaQueue = []
        self.theories = theories
        self.satisfiable = None
        for c in range(len(formula)):
            if formula[c] in ["E","A"]:
                if c==len(formula)-1: self.satisfiable = 4
                else:
                    if not (formula[c+1] in ["x","y","z","w"]):
                        self.satisfiable = 4

    def isSatisfiable(self):
        if self.satisfiable==4: return
        for t in range(len(self.theories)):
            self.root.createNodes([self.theories[t]])
        if (self.root.closed):
            self.root.parseFMLA()
        self.addBranches(self.root)
        if self.satisfiable==None:
            self.satisfiable = 1


    def addBranches(self,current):
        if self.root.closed:
            if self.satisfiable != 4:
                self.satisfiable = 0
            return
        if not current.ticked:
            parts = current.parseFMLA()
            current.ticked = True
            if parts==None:
                self.satisfiable = 4
                return
            elif parts==[]:
                if len(current.children)==0 and len(self.gammaQueue)>0:
                    gQ = len(self.gammaQueue)
                    countTrue = 0
                    countSame = 0
                    allPropsUsed = [True]*len(self.prop)
                    for i in range(gQ):
                        if self.gammaQueue[i][1] == allPropsUsed: countTrue+=1
                        if self.gammaQueue[i][1] == self.propUsed: countSame+=1
                    if countTrue==gQ:
                        if self.satisfiable==None:
                            self.satisfiable = 2
                        return
                    if countSame==gQ:
                        if self.satisfiable==None:
                            self.satisfiable = 1
                        return
                    self.addBranches(self.gammaQueue[0][0])
            elif parts[0]=="E":
                if self.propUsed == ([True]*len(self.prop)):
                    if self.satisfiable==None:
                        self.satisfiable = 2
                    return
                for i in range(len(self.prop)):
                    if self.propUsed[i]==False:
                        self.propUsed[i] = True
                        parts = self.changeConst(parts,self.prop[i])
                        break
            elif parts[0]=="A":
                current.ticked = False
                runYet = True   # run a,b,d first
                for i in range(len(current.children)):
                    if not current.children[i].ticked:
                        self.gammaQueue.append([current,([False]*len(self.prop))])
                        parts = []
                        runYet = False
                        break
                if runYet:      # come back for it
                    if len(self.gammaQueue)==0: self.gammaQueue.append([self,[False]*len(self.prop)])
                    gProp = self.gammaQueue[0][1]   # props used in gamma formula
                    self.dequeue()
                    for i in range(len(self.prop)):
                        if gProp[i]==False and self.propUsed[i]==True:
                            gProp[i] = True
                            parts = self.changeConst(parts,self.prop[i])
                            break
                        if gProp[i]==False and self.propUsed[i]==False:
                            gProp[i] = True
                            self.propUsed[i] = True
                            parts = self.changeConst(parts,self.prop[i])
                            break
                    self.gammaQueue.append([current,gProp])

            current.createNodes(parts)
        for i in range(len(current.children)):
            self.addBranches(current.children[i])
            if (self.root.closed):
                if self.satisfiable != 4:
                    self.satisfiable = 0
                

    def dequeue(self):
        if len(self.gammaQueue)>1:
            self.gammaQueue = self.gammaQueue[1:]
        else:
            self.gammaQueue = []
                
        
    def changeConst(self,parts,char):
        new_parts = ""
        for c in range(len(parts[2])):
            if parts[2][c]==parts[1]:
                new_parts += char
            else:
                new_parts += parts[2][c]
        return [new_parts]


def getTheories(fmla):
    endBracket = fmla[1:].index("]")+1
    theories = fmla[1:endBracket].split(",")
    fmla = fmla[endBracket+1:].strip()
    return (theories,fmla)

def parse(fmla):
    global y
    if fmla[0]=="[":
        theories, fmla = getTheories(fmla)
        y = Tableau(fmla,theories)
    else:
        y = Tableau(fmla)
    y.isSatisfiable()
    if y.satisfiable == 4:
        return 0
    return y.root.parseParts[0]

def lhs(fmla):
    return y.root.parseParts[1]
def rhs(fmla):
    return y.root.parseParts[3]
def con(fmla):
    return y.root.parseParts[2]

def theory(line):
    return

def sat(tab):
    return y.satisfiable


#DO NOT MODIFY THE CODE BELOW
parseOutputs = ['not a formula',
                'an atom',
                'a negation of a first order logic formula',
                'a universally quantified formula',
                'an existentially quantified formula',
                'a binary connective first order formula',
                'a proposition',
                'a negation of a propositional formula',
                'a binary connective propositional formula']

satOutput = ['is not satisfiable', 'is satisfiable', 'may or may not be satisfiable']

f = open('input.txt')
firstline = f.readline()


PARSE = False
if 'PARSE' in firstline:
    PARSE = True

SAT = False
if 'SAT' in firstline:
    SAT = True

for line in f:
    if line[-1] == '\n':
        line = line[:-1]
    parsed = parse(line)

    if PARSE:
        output = "%s is %s." % (line, parseOutputs[parsed])
        if parsed in [5,8]:
            output += " Its left hand side is %s, its connective is %s, and its right hand side is %s." % (lhs(line), con(line) ,rhs(line))
        print(output)

    if SAT:
        if parsed:
            tableau = [theory(line)]
            print('%s %s.' % (line, satOutput[sat(tableau)]))
        else:
            print('%s is not a formula.' % line)
