from com.pnfsoftware.jeb.client.api import IScript,IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionCommentData, ActionRenameData
from java.lang import Runnable

from com.pnfsoftware.jeb.core.actions import ActionXrefsData
import re
import os
import sys

sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/numpy/')

import numpy

class JEBClasses(IScript):

    def run(self, ctx):
        print(sys.path)
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
            classes = unit.getClasses()
            print('Classes in unit %s in %d' %(unit.getName(), len(classes)))
            # for cls in classes:
            #     print(cls.getAddress())
