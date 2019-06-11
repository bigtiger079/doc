# -*- coding: utf-8 -*-
"""
Sample client script for PNF Software's JEB2.

More samples are available on our website and within the scripts/ folder.

Refer to SCRIPTS.TXT for more information.
"""

import string
import re, collections
from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionXrefsData
from com.pnfsoftware.jeb.core.events import JebEvent, J
from com.pnfsoftware.jeb.core.output import AbstractUnitRepresentation, UnitRepresentationAdapter
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, IJavaStaticField, IJavaNewArray, IJavaConstant, IJavaCall, IJavaField, IJavaMethod, IJavaClass, IJavaIdentifier
from com.pnfsoftware.jeb.core.actions import ActionTypeHierarchyData
from com.pnfsoftware.jeb.core.actions import ActionRenameData
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.core.output.text import ITextDocument
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from java.lang import Runnable


class JEB2AutoRenameByTypeInfo(IScript):

    def run(self, ctx):
        ctx.executeAsync("Running name detection...", JEBArgsRename(ctx))
        JEBUIInfo().run(ctx)
        print('Done')


class JEBUIInfo():

    def run(self, ctx):
        engctx = ctx.getEnginesContext()
        if not engctx:
            print('Back-end engines not initialized')
            return

        projects = engctx.getProjects()
        if not projects:
            print('There is no opened project')
            return

        if not isinstance(ctx, IGraphicalClientContext):
            print('This script must be run within a graphical client')
            return

        prj = projects[0]

        fragment = ctx.getFocusedView().getActiveFragment()
        address = fragment.getActiveAddress()
        item = fragment.getActiveItem()
        print("active address : %s    item: %s offset: %d" % (address, item.toString(), item.getOffset()))
        unit = fragment.getUnit()
        itemAtAddress = unit.getItemAtAddress(address)
        print(unit.getAddressOfItem(item.getItemId()))
        print(dir(item))


class JEBArgsRename(Runnable):

    def __init__(self, ctx):
        self.ctx = ctx

    def run(self):
        ctx = self.ctx
        engctx = ctx.getEnginesContext()
        if not engctx:
            print('Back-end engines not initialized')
            return

        projects = engctx.getProjects()
        if not projects:
            print('There is no opened project')
            return

        prj = projects[0]

        # units = RuntimeProjectUtil.getAllUnits(prj)
        # for unit in units:
        #     print(unit.getName())

        units = RuntimeProjectUtil.findUnitsByType(prj, IJavaSourceUnit, False)

        for unit in units:
            self.displayASTTree(unit.getClassElement())
        #     indetofiers = unit.getUnitProcessor().getUnitIdentifiers()
        #     for i in indetofiers:
        #         print(i.getFormatType(), i.getPluginInformation().getName(), i.getPluginInformation().getDescription())
        # decompiler = unit.getDecompiler()
        # codeUnit = decompiler.getCodeUnit()
        # print(decompiler.getFormatType())
        # methods = codeUnit.getMethods()
        # for mt in methods:
        #     print('parse ->'+mt.getClassType().getName(False) +"." + mt.getName(False))
        #     addr = mt.getAddress()
        #     if decompiler.canDecompile(addr):
        #         source = decompiler.decompile(addr)
        #         print(source)

        # cls = unit.getClassElement()
        # methods = cls.getMethods()
        # if len(methods) == 0:
        #     continue
        # for mt in methods:
        #     parameters = mt.getParameters()
        #     if len(parameters) == 0:
        #         continue
        #     for param in parameters:
        #         tags = param.getIdentifier().getTagMap()
        #         print(dir(param.getIdentifier()))

        # units = RuntimeProjectUtil.findUnitsByType(prj, IDexUnit, False)
        # for unit in units:
        #     # document = unit.getDisassemblyDocument()
        #     # for i in range(1, 10):
        #     #     print("line %d --------------------->" % i)
        #     #     documentPart = document.getDocumentPart(i, 1)
        #     #     lines = documentPart.getLines()
        #     #     for line in lines:
        #     #         print('        %s' % line.getText())
        #     # print('anchor count: %d' % document.getAnchorCount())
        #     classes = unit.getClasses()
        #     for cls in classes:
        #         print(cls.getName(True))
        #         if cls.getName(True) == 'UpdateDialogActivity':
        #             methods = cls.getMethods()
        #             for mt in methods:
        #                 itemId = mt.getItemId()
        #                 item = unit.getItemObject(itemId)
        #                 print(item)
        #                 address = mt.getAddress()
        #                 print("Method address: " + address)
        #                 instructions = mt.getData().getCodeItem().getInstructions()
        #                 for ins in instructions:
        #                     print(ins.getMnemonic(), ins.getOffset())

    def displayASTTree(self, e0, level=0):
        print('%s%s' % (level * '  ', e0.getElementType()))
        if e0:
            elts = e0.getSubElements()
            for e in elts:
                self.displayASTTree(e, level + 1)


class JEB2AutoRename(Runnable):

    def __init__(self, ctx):
        self.ctx = ctx

    def run(self):
        ctx = self.ctx
        engctx = ctx.getEnginesContext()

        if not engctx:
            print('Back-end engines not initialized')
            return

    def run(self):
        ctx = self.ctx
        engctx = ctx.getEnginesContext()

        if not engctx:
            print('Back-end engines not initialized')
            return

        projects = engctx.getProjects()
        if not projects:
            print('There is no opened project')
            return
