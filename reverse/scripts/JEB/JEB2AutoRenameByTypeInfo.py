import string  
import re,collections  
from com.pnfsoftware.jeb.client.api import IScript  
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext  
from com.pnfsoftware.jeb.core import RuntimeProjectUtil  
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionXrefsData  
from com.pnfsoftware.jeb.core.events import JebEvent, J  
from com.pnfsoftware.jeb.core.output import AbstractUnitRepresentation, UnitRepresentationAdapter  
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem  
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit, IJavaStaticField, IJavaNewArray, IJavaConstant, IJavaCall, IJavaField, IJavaMethod, IJavaClass  
from com.pnfsoftware.jeb.core.actions import ActionTypeHierarchyData  
from com.pnfsoftware.jeb.core.actions import ActionRenameData  
from com.pnfsoftware.jeb.core.util import DecompilerHelper  
from com.pnfsoftware.jeb.core.output.text import ITextDocument  
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit  
from java.lang import Runnable
import sys
import platform


class JEB2AutoRenameByTypeInfo(IScript):  
    def run(self, ctx):
        print(sys.modules.keys())
        print(platform.python_version())
        ctx.executeAsync("Running name detection...", JEB2AutoRename(ctx))
        print('Done')


class JEB2AutoRename(Runnable):  
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