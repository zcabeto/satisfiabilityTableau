
class Node:
    def __init__(self,formula,parent):
        self.formula = formula
        self.children = []
        self.parent = parent
        self.closed = False

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
                    self.children[0].createNodes([parts[2]])
                    p.closeBranch()
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
        while current != closingNode:
            current.closed = True
            current = current.parent
        while current != None:
            openChildren = len(current.children)
            for i in range(len(current.children)):
                if (current.children[i].closed):
                    openChildren-=1
            if openChildren==0:
                current.closed = True
                current = current.parent
            else:
                break
        return closingNode

        
        

    def evaluate(self):
        fmla = self.formula

        # if overload of -, reduce down
        truth = True
        negationCount = 0
        for i in range(len(fmla)):
            if (fmla[i] == "-"):
                negationCount+=1
                truth = not truth
            if (fmla[i] != "-"):
                fmla = fmla[i:]
                break
        if (negationCount>1):
            return [("-"*(negationCount%2))+fmla]

        if len(fmla)<=2:
            return []
        if (len(fmla)==6):              # case of PRED(var, var)
            if fmla[1]=="(" and fmla[3]=="," and fmla[5]==")":
                return []

        # check for E and A outside of brackets
        quantifier = ["E","A"]
        for i in range(2):
            if fmla[0]==quantifier[i]:
                if truth:
                    return [fmla[0],fmla[1],fmla[2:]]
                else:
                    return [quantifier[i-1]+fmla[1] + "-" + fmla[2:]]
                
        # check remaining in overall brackets        
        if (fmla[0]=="(" and fmla[-1]==")"):
            fmla = fmla[1:-1]
        else:
            return

        otherChars = ["-","E","A"]
        brackets = 0
        subForm = ""
        parts = []
        # inside overall brackets
##        for i in range(len(fmla)):
##            letter = fmla[i]
##            if (letter=="("): brackets+=1
##            elif (letter==")"): brackets-=1
##            if (brackets > 0 or letter=="-"):
##                subForm += letter
##            elif (brackets == 0 and letter!="-"):
##                subForm += fmla[i]
##                parts.append(subForm)
##                if (i!=len(fmla)-1):
##                    i+=2
##                    subForm = ""
##                else:
##                    break
##            else:
##                return
        started = False
        operations = ["^","v",">"]
        for i in range(len(fmla)):
            letter = fmla[i]
            if (letter in operations):
                started = True
            if (letter=="("):
                brackets+=1
                subForm += letter
            elif (letter==")"):
                brackets-=1
                subForm += letter
            elif (brackets==0 and started):
                parts.append(subForm)
                parts.append(letter)
                subForm = ""
                started = False
            else:
                subForm += letter
        if (brackets==0):
            parts.append(subForm)
        else:
            return
        print(parts)
            
        # check operation validity
        if (len(parts) != 3):
            return
        op = parts[1]
        if not (op in operations):
            return

        # do any switches required so only ^,v used for alpha, beta
        if (truth and op==">"):
            parts[0] = "-"+parts[0]
            parts[1] = "v"
        elif (not truth and op==">"):
            parts[2] = "-"+parts[2]
            parts[1] = "^"
        elif (not truth and op=="^"):
            parts[0] = "-"+parts[0]
            parts[1] = "v"
            parts[2] = "-"+parts[2]
        elif (not truth and op=="v"):
            parts[0] = "-"+parts[0]
            parts[1] = "^"
            parts[2] = "-"+parts[2]
        
        return parts
        
            
            
class Tableau:
    def __init__(self,formula):
        self.root = Node(formula,None)
        #self.prop = ["a","b","c","d","e","f","g","h","i","j"]
        self.prop = ["p","q"]
        #self.propUsed = [False,False,False,False,False,False,False,False,False,False]
        self.propUsed = [False,False]
        self.queue = PQ()

    def isSatisfiable(self):
        msg = self.addBranches(self.root)
        # somehow msg = None now???
        if msg==None:
            return "satisfiable"
        else:
            return msg

    def addBranches(self,current):
        parts = current.evaluate()
        self.queue.add(parts,([False]*10))      # prioritise anything but gamma formula
        parts = self.queue.next()
        # parts = None so below if statement used
        if parts==None:
            return "not a formula"
        if len(parts)>=3:
            if parts[0]=="E":
                for i in range(len(self.prop)):
                    if not self.propUsed[i]:
                        self.propUsed[i] = True
                        parts = self.changeConst(parts,self.prop[i])
                        break
            elif parts[0]=="A":
                for i in range(len(self.prop)):      # check gamma's used vars so far
                    if (parts[3][i]==False and self.propUsed[i]==True):
                        parts[3][i] = True
                        if i<len(parts[3])-1:       # more iterations to run
                            self.queue.add(parts[0:2],parts[3])
                        parts = self.changeConst(parts,self.prop[i])
                        break

        if parts==None:
            return "not a formula"
        current.createNodes(parts)
        for i in range(len(current.children)):
            self.addBranches(current.children[i])
            if (self.root.closed):
                return "not satisfiable"

    def changeConst(self,parts,char):
        new_parts = ""
        for c in range(len(parts[2])):
            if parts[2][c]==parts[1]:
                new_parts += char
            else:
                new_parts += parts[2][c]
        return [new_parts]

class PQ:
    def __init__(self):
        self.abd = []
        self.gamma = []
    def add(self,parts,propUsed):
        if parts==None:
            return None
        if parts==[]:
            self.abd.append([])
        elif parts[0]=="A":
            parts.append(propUsed)
            self.gamma.append(parts)
        else:
            self.abd.append(parts)
    def next(self):
        if self.abd==[]:
            if self.gamma==[]:
                return
            rVal = self.gamma[0]
            if len(self.gamma)>1:
                self.gamma = self.gamma[1:]
            else:
                self.gamma = []
            return rVal
        else:
            rVal = self.abd[0]
            if len(self.abd)>1:
                self.abd = self.abd[1:]
            else:
                self.abd = []
            return rVal
        

            
##formulasProp = ["-(p>(q>p))","(-(p>q)^q)","(---pv(q^-q))","(p>p)","-(p>p)","((pvq)^","(p-q)",
##            "((pvq)^(-pv-q))","(q^-(pv-p))","p","((pvq)^((p>-p)^(-p>p)))","-----------q"]
##for i in range(len(formulasProp)):
##    x = Tableau(formulasProp[i])
##    print(x.isSatisfiable())
##
##print("\n")
##
##formulasFO = ["(ExP(x,x)^Ax(-P(x,x)>P(x,x)))","-Ax(P(x,x)^-P(x,x))","-Ax-Ey-P(x,y)",
##              "ExAx(P(x,x)^-P(x,x))","ExAy(Q(x,x)>P(y,y))","(Q(x,x)-(P(y,y))",
##              "ExEy((Q(x,x)^Q(y,y))v-P(y,y))","ExEy((Q(x,x)^Q(y,y))v","Ex-P(x,x)",
##              "(AxEyP(x,y)^EzQ(z,z))","(Ax(P(x,x)^-P(x,x))^ExQ(x,x))","ExEy(P(x,y)^Ex-P(x,y))"]
##for i in range(len(formulasFO)):
##    x = Tableau(formulasFO[i])
##    print(formulasFO[i], x.isSatisfiable())

x = Tableau("ExEy((Q(x,x)^Q(y,y))v")
print(x.isSatisfiable())
