from com.pnfsoftware.jeb.client.api import IScript,IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionCommentData, ActionRenameData
from java.lang import Runnable

from com.pnfsoftware.jeb.core.actions import ActionXrefsData
import re
import json


class JEBClasses(IScript):

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
        dexClasses = {}
        externalClasses = {}
        def getSimpleClass(item):
            address = item.getAddress()
            if item.isInternal():
                return dexClasses[address]
            else:
                if not externalClasses.has_key(address):
                    externalClasses[address] = SimpleClass(address)
                return externalClasses[address]

        for unit in units:
            classes = unit.getClasses()
            print('start parse class')
            for cls in classes:
                dexClasses[cls.getAddress()] = SimpleClass(cls.getAddress())
            
            print('start parse superType and interfaces')
            for key, sClass in dexClasses.items():
                cls = unit.getClass(key)
                supers = cls.getSupertypes()
                if supers != None and len(supers) > 0:
                    sClass.superType = getSimpleClass(supers[0])
                
                intrefaces = cls.getImplementedInterfaces ()
                if intrefaces != None and len(intrefaces) > 0:
                    for interface in intrefaces:
                        sClass.interfaces.append(getSimpleClass(interface))

                fields = cls.getFields()
                if fields != None and len(fields) > 0:
                    for field in fields:
                        sClass.fields.append(getSimpleClass(field.getClassType()))

            for key, sClass in dexClasses.items():
                print(sClass)

        self.dump(dexClasses)    

    def dump(self, classes):
        clss = map(lambda x: { 'signature': x.signature, 
                        'fields': [field.signature for field in x.fields],
                        'interfaces': [interface.signature for interface in x.interfaces],
                        'superType': x.superType.signature if x.superType != None else ''}, classes.values())
        js = json.dumps(clss)
        print(js)

        with open('E:\\Workstation\\classes.json', 'w') as f:
            f.write(js)


class SimpleClass(object):

    def __init__(self, signature):
        self.signature = signature
        self.fields = []
        self.interfaces = []
        self.superType = None

    def __str__(self):
        return self.signature + " -> " + ", ".join(map(lambda x: x.signature, self.interfaces)) if len(self.interfaces) > 0 else self.signature
    
    def __repr__(self):
        return self.__str__()