from com.pnfsoftware.jeb.client.api import IScript,IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionCommentData, ActionRenameData
from java.lang import Runnable

from com.pnfsoftware.jeb.core.actions import ActionXrefsData
import re
import sys

sys.setrecursionlimit(100000)


class JEBTrace(IScript):

    def run(self, ctx):
        # self.ctx = ctx
        #ctx.executeAsync("Running deobscure class ...", AsyncTask(ctx, self))
        engctx = ctx.getEnginesContext()
        if not engctx:
            print('Back-end engines not initialized')
            return

        projects = engctx.getProjects()
        if not projects:
            print('There is no opened project')
            return

        prj = projects[0]

        units = RuntimeProjectUtil.findUnitsByType(prj, IDexUnit, False)
        for unit in units:
            cls = unit.getClass('Lcom/jingdong/aura/wrapper/AuraInitializer;')
            
            if cls != None:
                print('getClassTypeIndex -> %d' % cls.getClassTypeIndex())
                for m in cls.getMethods():
                    if m.getName(False) == 'update':
                        # print(m.getSignature(True), m.getAddress(), m.getAddress())
                        refs = DataReference(DataReferenceNode(m.getItemId(), m.getAddress()))
                        self.findMethodXRef(units, m.getItemId(), m.getAddress(), refs)
                        print(refs.getNodes())
                        print(refs.getLeafNodes())
                        lines = []
                        for leaf in refs.getLeafNodes():
                            lines.extend(refs.getLineToRoot(XrefLine(leaf)))

                        print(lines)


    def findMethodXRef(self, units, itemId, itemAddress, refs):
        preNode = refs.getCurrentNode()
        refs.setCurrentNodeById(itemId)
        sub_address = []
        total = 0
        for unit in units:
            data = ActionXrefsData()
            if unit.prepareExecution(ActionContext(unit, Actions.QUERY_XREFS, itemId, itemAddress), data):
                if len(data.getAddresses()) > 0 :
                    sub_address.append((unit, data.getAddresses()))
                    total += len(data.getAddresses())
                else:
                    row_m = unit.getMethod(itemAddress)
                    impl_class = row_m.getClassType().getImplementingClass()
                    if re.search(r'(\$\d+?)+;$', impl_class.getAddress()) != None:
                        # sub_address.append((unit, impl_class.getAddress()))
                        clxXref = self.findClassXRef(units, impl_class.getItemId(), impl_class.getAddress())
                        sub_address.extend(clxXref)
                        for (unit, addresses) in clxXref:
                            total += len(addresses)

        refs.getCurrentNode().setXrefCount(total)
        for (unit, addresses) in sub_address:
            for xref_addr in addresses:
                indexObj = re.search(r'\+[0-9A-F]+?h$', xref_addr)
                if indexObj != None:
                    index = indexObj.group()
                    last_index = 0-len(index)
                    method = unit.getMethod(xref_addr[0:last_index])
                    node = refs.buildNode(method.getItemId(), method.getAddress())
                    if node == None:
                        refs.setCurrentNodeById(preNode.itemId)
                        return
                    else:
                        self.findMethodXRef(units,method.getItemId(), method.getAddress(),refs)
                else:
                    method = unit.getMethod(xref_addr)
                    node = refs.buildNode(method.getItemId(), method.getAddress())
                    if node == None:
                        refs.setCurrentNodeById(preNode.itemId)
                        return
                    else:
                        self.findMethodXRef(units,method.getItemId(), method.getAddress(),refs)
        refs.setCurrentNodeById(preNode.itemId)
        return

    def findClassXRef(self, units, itemId, itemAddress):
        refs = []
        for unit in units:
            data = ActionXrefsData()
            if unit.prepareExecution(ActionContext(unit, Actions.QUERY_XREFS, itemId, itemAddress), data):
                if len(data.getAddresses()) > 0 :
                    refs.append((unit, data.getAddresses()))
        return refs

class DataReference:

    def __init__(self, head_node):
        self.nodes = [head_node]
        self.head_node = head_node
        self.current_node = self.head_node
        self.current_node.is_on_parsing = True

    def getNodes(self):
        return self.nodes
    
    def addNodes(self, nodes):
        for node in nodes:
            self.current_node.addNextNode(node)

    def setCurrentNodeById(self, nodeId):
        for node in self.nodes:
            if node.itemId == nodeId:
                self.current_node = node
                self.current_node.is_on_parsing = True
                return True
        print('ERROR -> setCurrentNodeById: no such id %s' %nodeId)
        return False

    def setCurrentNodeByAddress(self, address):
        for node in self.nodes:
            if node.itemAddress == address:
                self.current_node = node
                self.current_node.is_on_parsing = True
                break

    def getCurrentNode(self):
        return self.current_node

    def isParsed(self, itemId):
        for node in self.nodes:
            if node.itemId == itemId:
                return node.isParsed()
        
        return False
    
    def addSubNode(self, node):
        if node.itemAddress != self.current_node.itemAddress:
            self.current_node.addNextNode(node)

    def buildNode(self, itemId, itemAddress):

        for node in self.nodes:
            if node.itemId == itemId:
                self.addSubNode(node)
                return None
        newNode = DataReferenceNode(itemId, itemAddress)
        self.nodes.append(newNode)
        self.addSubNode(newNode)
        return newNode

    def getPreNodes(self, node):
        # if not node.isParsed():
        #     print('node %s is not parsed yet' % node.itemAddress)
        #     return None
        if node.itemId == self.head_node.itemId:
            return []
        else:
            pre_nodes = []
            for n in self.nodes:
                if n.hasSubNode(node):
                    pre_nodes.append(n)

            return pre_nodes

    def getLeafNodes(self):
        leaf = []
        for n in self.nodes:
            if n.isLeafNode():
                leaf.append(n)

        return leaf

    def isHeadNode(self, node):
        return node.itemId == self.head_node.itemId
            

    def getLineToRoot(self, line):
        node = line.getLast()
        print('on parse node: %s' % node.itemAddress)
        if self.isHeadNode(node):
            return [line]

        lines = []
        preNodes = self.getPreNodes(node)
        for n in preNodes:
            if not line.hasNode(n):
                copyLine = XrefLine.copyFrom(line)
                copyLine.addNode(n)
                if self.isHeadNode(n):
                    lines.append(copyLine)
                else:
                    subLines = self.getLineToRoot(copyLine)
                    lines.extend(subLines)
        return lines


class XrefLine(object):
    
    def __init__(self, node=None):
        self.line = []
        if node != None:
            self.line.append(node)

    def hasNode(self, node):
        for n in self.line:
            if n.itemId == node.itemId:
                return True

        return False

    def addNode(self, node):
        if self.hasNode(node):
            return False

        self.line.append(node)
        return True

    def getLine(self):
        return self.line

    def getLast(self):
        return self.line[-1]

    def __str__(self):
        nodeInfo = ''
        for node in self.line:
            nodeInfo += '    ' +node.itemAddress + '\n'
        return '''
        XrefLine [ 
        %s
        ]
        ''' % nodeInfo

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def copyFrom(xline):
        newLine = XrefLine()
        for node in xline.getLine():
            newLine.addNode(node)
        return newLine

class DataReferenceNode:

    def __init__(self, itemId, itemAddress):
        self.itemId = itemId
        self.itemAddress = itemAddress
        self.pre_nodes = []
        self.next_nodes = []
        self.is_on_parsing = False
        self.xref_count = -1

    def addPreNode(self, node):
        for pnode in self.pre_nodes:
            if pnode.itemId == node.itemId:
                return False
        self.pre_nodes.append(node)
        return True
    
    def addNextNode(self, node):
        for nnode in self.next_nodes:
            if nnode.itemId == node.itemId:
                return False
        self.next_nodes.append(node)
        return True

    def isParsed(self):
        return len(self.next_nodes) == self.xref_count

    def setXrefCount(self, count):
        self.xref_count = count
    
    def hasSubNode(self, node):
        for n in self.next_nodes:
            if n.itemId == node.itemId:
                return True
        
        return False

    def isLeafNode(self):
        return self.isParsed() and len(self.next_nodes) == 0

    def __str__(self):
        return "str:" + self.itemAddress

    def __repr__(self):
        sub = ''
        for node in self.next_nodes:
            sub += node.itemAddress + '   '
        return '''
        %s
             subs: [ %s ]
        ''' % (self.itemAddress, sub)
    

        

# class AsyncTask(Runnable):
#     def __init__(self, ctx, main_thread):
#         self.ctx = ctx
#         self.main_thread = main_thread

#     def run(self):

#         ctx = self.ctx
#         engctx = ctx.getEnginesContext()
#         if not engctx:
#             print('Back-end engines not initialized')
#             return

#         projects = engctx.getProjects()
#         if not projects:
#             print('There is no opened project')
#             return

#         prj = projects[0]

#         units = RuntimeProjectUtil.findUnitsByType(prj, IDexUnit, False)
#         for unit in units:
#             print('unit formatType: %s' % unit.getFormatType())
#             cls = unit.getClass('Lmain/home/HomeFragment;')
            
#             if cls != None:
#                 self.main_thread.open(unit)
#                 print('getClassTypeIndex -> %d' % cls.getClassTypeIndex())
#                 for m in cls.getMethods():
#                     if m.getName(False) == 'getPlunginLists':
#                         print(m.getSignature(True))

#                         data = ActionXrefsData()
#                         if unit.prepareExecution(ActionContext(unit, Actions.QUERY_XREFS, m.getItemId(), m.getAddress()), data):
#                             for xref_addr in data.getAddresses():
#                                 print(xref_addr)
            # else:
                #print('no class in unit' )
            # for m in unit.getMethods():
            #     print m.getSignature(True)


        # unit = self.ctx.getActiveView().getUnit()
        # print(unit.getFormatType())

        # current_addr = self.ctx.getActiveView().getActiveFragment().getActiveAddress()
        # print(current_addr)
        # current_item = self.ctx.getActiveView().getActiveFragment().getActiveItem()
        # print(current_item)

        # data = ActionXrefsData()
        # if unit.prepareExecution(ActionContext(unit, Actions.QUERY_XREFS, current_item.getItemId(), current_addr), data):
        #     for xref_addr in data.getAddresses():
        #         print(xref_addr)