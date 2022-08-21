import tkinter
from tkinter import ttk
from tkinter import filedialog
from typing import List,Union,Tuple
from os import path
from numpy import sin, cos, tan, array, NaN, arctan
from numpy.linalg import norm
import numpy
from math import pi

deg:float = pi / 180.0

def dummyHook(draggedObj:Union[Tuple[int],None])->None:
    _ = draggedObj

class EntryVariable:
    def getInt(self)->int:
        return int(self.stringVar.get())

    def getFloat(self)->float:
        return float(self.stringVar.get())

    def __init__(self, parent:ttk.Frame, *args, **kwargs):
        self.stringVar = tkinter.StringVar()
        self.entry = ttk.Entry(parent, *args, textvariable=self.stringVar, **kwargs)
        self.pack = self.entry.pack


class PyFitMain:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('My First App')

        self.leftPane = ttk.Frame(self.root, padding=8)
        self.centerPane = ttk.Frame(self.root, padding=8)
        self.rightPane = ttk.Frame(self.root, padding=8)

        self.frame1 = ttk.Frame(self.leftPane, padding=8)
        self.label1 = ttk.Label(self.frame1, text='Filename:')
        self.fname = tkinter.StringVar()
        self.fnameEntry = ttk.Entry(self.frame1, textvariable=self.fname,)
        # self.fnameEntry.configure(state='readonly')
        self.fnameEntry.configure(state=tkinter.DISABLED)
        self.button1 = ttk.Button(
            self.frame1,
            text='Select File',
            command=self.selectImage
        )

        self.t2 = tkinter.StringVar(value='hoge')
        self.frame2 = ttk.Frame(self.leftPane, padding=8)
        self.img    = None
        self.canvas:Union[tkinter.Canvas,None] = None

        self.geomEntries:List[EntryVariable] =[]

        self.centerFrame = ttk.Frame(self.centerPane, padding=8)
        self.centerLabel = ttk.Label(self.centerFrame, text='Fuselage')
        self.centerXY = PyFitCenter('Center Line (XY)', self)
        self.centerXY.defCenterLine()
        self.geomEntries += self.centerXY.geomEntries

        self.centerYZ = PyFitCenter('Center Line (YZ)', self)
        self.centerYZ.defCenterLine()
        # self.geomEntries += self.centerYZ.geomEntries

        self.wing = PyFitWing('Wing', self)
        self.wing.defWing()
        self.geomEntries += self.wing.geomEntries

        self.hstab = PyFitWing('Horizontal Stabilizer', self)
        self.hstab.defWing()
        self.geomEntries += self.hstab.geomEntries

        self.vstab = PyFitWing('Vertical Stabilizer', self)
        self.vstab.defWing()
        self.geomEntries += self.hstab.geomEntries


        self.rightButtonFrame = ttk.Frame(self.centerPane, padding=8)
        self.geomUpdateButton = ttk.Button(
            self.rightButtonFrame,
            text='Update',
            command=self.updateGeom
        )

        # pack stuffs
        self.leftPane.pack(side=tkinter.LEFT)
        self.centerPane.pack(side=tkinter.LEFT)
        self.rightPane.pack(side=tkinter.RIGHT)
        self.results = PyFitResults(self)

        self.frame1.pack(anchor=tkinter.N)
        self.label1.pack( side=tkinter.LEFT)
        self.fnameEntry.pack( side=tkinter.LEFT)
        self.button1.pack(side=tkinter.LEFT)

        self.frame2.pack()

        self.centerFrame.pack(anchor=tkinter.N)
        self.centerXY.packCenterLine()
        self.centerYZ.packCenterLine()
        self.wing.packWing()
        self.hstab.packWing()
        self.vstab.packWing()

        self.rightButtonFrame.pack(anchor=tkinter.N)
        self.geomUpdateButton.pack(side=tkinter.LEFT)

        self.root.mainloop()

    def selectImage(self):
        fname:str = filedialog.askopenfilename(filetypes=[("Images", ('*.png', '*.jpg', '*.jpeg'))])
        if (type(fname) is str):
            self.fname.set(path.basename(fname))
            self.renderImg(fname)
        return

    def get_coordinates(self, event):
        assert(type(self.canvas) is tkinter.Canvas)
        self.canvas.itemconfigure(self.tag, text='({x}, {y})'.format(x=event.x, y=event.y))

    def renderImg(self, fname:str):
        self.img = tkinter.PhotoImage(file=fname)
        self.canvas = tkinter.Canvas(self.frame2, height=self.img.height(), width=self.img.width())
        self.canvas.create_image(0,0, image=self.img, anchor=tkinter.NW)

        self.canvas.pack( side=tkinter.TOP)

        self.canvas.bind('<Motion>', self.get_coordinates)
        self.canvas.bind('<Enter>',  self.get_coordinates)  # handle <Alt>+<Tab> switches between windows
        self.tag = self.canvas.create_text(10, 10, text='', anchor='nw')

        self.root.update()

        for entry in self.geomEntries:
            entry.stringVar.set('0')
            entry.entry.configure(state=tkinter.NORMAL)


    def updateResult(self):
        return


    def updateGeom(self):
        assert(type(self.canvas) is tkinter.Canvas)

        try:
            self.canvas.delete('overlay')
        except BaseException as e:
            print(e)

        self.scale=self.centerXY.VLengthEntry.getFloat() / self.centerXY.ALengthEntry.getFloat()

        self.line1=self.centerXY.renderLine()
        self.lineWing=self.wing.renderWing(self.centerXY)
        self.lineHstab=self.hstab.renderWing(self.centerXY)

        self.results.renderResult()


class PyFitCenter:
    def dragHook(self, draggedObj:Union[Tuple[int],None]):
        assert self.parent.canvas is not None
        if draggedObj is None:
            return

        coords = self.parent.canvas.coords(draggedObj[-1])
        print(coords)
        self.parent.updateGeom()

    def defCenterLine(self):
        self.Frame = ttk.Frame(self.centerFrame, padding=8)
        self.Label = ttk.Label(self.Frame, text=self.name)

        self.BeginFrame = ttk.Frame(self.Frame, padding=8)
        self.BeginLabel = ttk.Label(self.BeginFrame, text='Begins(x,y): ')
        self.BeginXEntry = EntryVariable(self.BeginFrame, state=tkinter.DISABLED, width=8)
        self.BeginYEntry = EntryVariable(self.BeginFrame, state=tkinter.DISABLED, width=8)

        self.VLengthFrame = ttk.Frame(self.Frame, padding=8)
        self.VLengthLabel = ttk.Label(self.VLengthFrame, text='Length(visual): ')
        self.VLengthEntry = EntryVariable(self.VLengthFrame, state=tkinter.DISABLED)

        self.ALengthFrame = ttk.Frame(self.Frame, padding=8)
        self.ALengthLabel = ttk.Label(self.ALengthFrame, text='Length(actual): ')
        self.ALengthEntry = EntryVariable(self.ALengthFrame, state=tkinter.DISABLED)

        self.TiltFrame = ttk.Frame(self.Frame, padding=8)
        self.TiltLabel = ttk.Label(self.TiltFrame, text='Til[deg]: ')
        self.TiltEntry = EntryVariable(self.TiltFrame, state=tkinter.DISABLED)

        self.geomEntries=[self.BeginXEntry, self.BeginYEntry, self.VLengthEntry, self.ALengthEntry, self.TiltEntry]

    def packCenterLine(self):
        self.Frame.pack(anchor=tkinter.N)
        self.Label.pack(side=tkinter.TOP)

        self.BeginFrame.pack(anchor=tkinter.NE)
        self.BeginLabel.pack(side=tkinter.LEFT)
        self.BeginXEntry.pack(side=tkinter.LEFT)
        self.BeginYEntry.pack(side=tkinter.LEFT)

        self.VLengthFrame.pack(anchor=tkinter.NE)
        self.VLengthLabel.pack(side=tkinter.LEFT)
        self.VLengthEntry.pack(side=tkinter.LEFT)

        self.ALengthFrame.pack(anchor=tkinter.NE)
        self.ALengthLabel.pack(side=tkinter.LEFT)
        self.ALengthEntry.pack(side=tkinter.LEFT)

        self.TiltFrame.pack(anchor=tkinter.NE)
        self.TiltLabel.pack(side=tkinter.LEFT)
        self.TiltEntry.pack(side=tkinter.LEFT)

    def renderLine(self):
        assert(type(self.parent.canvas) is tkinter.Canvas)

        __x =  self.BeginXEntry.getInt()
        __y =  self.BeginYEntry.getInt()
        self.len = self.VLengthEntry.getInt()
        __tilt = self.TiltEntry.getFloat() * deg


        self.line1=self.parent.canvas.create_line(
            __x,__y,__x+self.len*cos(__tilt),__y+self.len*sin(__tilt),
            tags='overlay',
            fill = '#880000',
            arrow='both',
            # arrowshape=(10,0,10),
            width=2,
            smooth=True
        )

        # self.parent.canvas.tag_bind(self.line1, "<ButtonPress-1>", self.clickHandler.onClick)
        # self.parent.canvas.tag_bind(self.line1, "<Button1-Motion>", self.clickHandler.onDrag)
        # self.parent.canvas.tag_bind(self.line1, "<ButtonRelease-1>", self.clickHandler.onDrop)

        return (self.line1)

    def getXpos(self, xpos:float)->numpy.ndarray:
        __x =  self.BeginXEntry.getInt()
        __y =  self.BeginYEntry.getInt()
        __tilt = self.TiltEntry.getFloat() * deg
        __alen = self.ALengthEntry.getFloat()
        __vlen = self.VLengthEntry.getInt()
        return xpos/__alen*__vlen*array([cos(__tilt), sin(__tilt)], dtype=float) + array([__x, __y],dtype=float)

    def __init__(self, name:str, parent:PyFitMain):
        self.name = name
        self.centerFrame = parent.centerFrame
        self.parent=parent
        # self.clickHandler = DandDhandler(self.parent, onDrag=self.dragHook)
        # self.clickHandler = DandDhandler(self.parent)


class PyFitWing:
    def renderWing(self, root:PyFitCenter):
        canvas = self.parent.canvas
        assert(canvas is not None)

        r_le = root.getXpos(self.LeXEntry.getFloat())
        r_te = root.getXpos(self.TeXEntry.getFloat())

        span = self.SpanEntry.getFloat() * self.parent.scale
        demispan = span /2
        tilt = root.TiltEntry.getFloat() * deg

        angle_le = self.LeSweepEntry.getFloat() * deg
        angle_te = self.TeSweepEntry.getFloat() * deg

        tiltMat = array([
            [ cos(tilt), -sin(tilt)],
            [ sin(tilt),  cos(tilt)],
        ])

        le_tip = tiltMat@array([demispan*tan(angle_le), demispan])
        te_tip = tiltMat@array([demispan*tan(angle_te), demispan])

        leCoords = (r_le[0], r_le[1], r_le[0]+le_tip[0], r_le[1]+le_tip[1],)
        teCoords = (r_te[0], r_le[1], r_te[0] + te_tip[0], r_te[1] + te_tip[1],)
        tipCoords = (leCoords[2], leCoords[3], teCoords[2], teCoords[3],)
        rootCoords = (leCoords[0], leCoords[1], teCoords[0], teCoords[1],)
        cordLen = lambda x: norm(array([x[0],x[1]], dtype=float)-array([x[2],x[3]], dtype=float))

        linestyle = {
            'tags': 'overlay',
            'fill': '#880000',
            'width': 2,
            'smooth': True
        }

        self.leLine=canvas.create_line(*leCoords, **linestyle)
        self.teLine=canvas.create_line(*teCoords, **linestyle)
        self.tipLine=canvas.create_line(*tipCoords, **linestyle)

        le_tip = tiltMat@array([demispan*tan(angle_le), -demispan])
        te_tip = tiltMat@array([demispan*tan(angle_te), -demispan])
        leCoordsMir = (r_le[0], r_le[1], r_le[0] + le_tip[0], r_le[1] + le_tip[1],)
        teCoordsMir = (r_te[0], r_le[1], r_te[0] + te_tip[0], r_te[1] + te_tip[1],)
        tipCoordsMir = (leCoordsMir[2], leCoordsMir[3], teCoordsMir[2], teCoordsMir[3],)

        self.leLineMir=canvas.create_line(*leCoordsMir, **linestyle)
        self.teLineMir=canvas.create_line(*teCoordsMir, **linestyle)
        self.tipLineMir=canvas.create_line(*tipCoordsMir, **linestyle)

        quarterLin = array(
            [
            (0.75*leCoords[0]+0.25*teCoords[0], 0.75*leCoords[1]+0.25*teCoords[1]),
            (0.75*leCoords[2]+0.25*teCoords[2], 0.75*leCoords[3]+0.25*teCoords[3]),
            ]
        )

        self.quarterLine=canvas.create_line(
            quarterLin[0,0],
            quarterLin[0,1],
            quarterLin[1,0],
            quarterLin[1,1],
            **linestyle)

        quarterVec = quarterLin[0] - quarterLin[1]
        print(quarterLin)

        self.quarterSweep = arctan(0.75*tan(angle_le) + 0.25*tan(angle_te)) /deg
        self.taper = cordLen(tipCoords)/cordLen(rootCoords)
        self.S = 0.5*(cordLen(tipCoords)+cordLen(rootCoords))*span
        self.AR = span**2 / self.S

        return (self.leLine, self.tipLine, self.teLine)


    def defWing(self):
        self.wingFrame = ttk.Frame(self.centerPane, padding=8)
        self.wingLabel = ttk.Label(self.wingFrame, text=f'{self.name}')

        self.SpanFrame = ttk.Frame(self.wingFrame, padding=8)
        self.SpanLabel = ttk.Label(self.SpanFrame, text=f'{self.name} Span:')
        self.SpanEntry = EntryVariable(self.SpanFrame, state=tkinter.DISABLED)

        self.LeFrame = ttk.Frame(self.wingFrame, padding=8)
        self.LeXFrame = ttk.Frame(self.LeFrame, padding=0)
        self.LeXLabel = ttk.Label(self.LeXFrame, text=f'{self.name} LE X:')

        self.LeXEntry = EntryVariable(self.LeXFrame, state=tkinter.DISABLED)
        self.LeSweepFrame = ttk.Frame(self.LeFrame, padding=0)
        self.LeSweepLabel = ttk.Label(self.LeSweepFrame, text=f'{self.name} LE Sweep[rad]:')

        self.LeSweepEntry = EntryVariable(self.LeSweepFrame, state=tkinter.DISABLED)

        self.TeFrame = ttk.Frame( self.wingFrame, padding=8)
        self.TeXFrame = ttk.Frame(self.TeFrame, padding=0)
        self.TeXLabel = ttk.Label(self.TeXFrame, text=f'{self.name} LE X:')

        self.TeXEntry = EntryVariable(self.TeXFrame, state=tkinter.DISABLED)
        self.TeSweepFrame = ttk.Frame(self.TeFrame, padding=0)
        self.TeSweepLabel = ttk.Label(self.TeSweepFrame, text=f'{self.name} TE Sweep[rad]:')

        self.TeSweepEntry = EntryVariable(self.TeSweepFrame, state=tkinter.DISABLED)

        self.geomEntries=[self.SpanEntry, self.LeXEntry, self.LeSweepEntry, self.TeXEntry, self.TeSweepEntry]

    def packWing(self):
        self.wingFrame.pack(anchor=tkinter.N)
        self.wingLabel.pack(side = tkinter.TOP)

        self.SpanFrame.pack(anchor=tkinter.NE)
        self.SpanLabel.pack(side=tkinter.LEFT)
        self.SpanEntry.pack(side=tkinter.LEFT)

        self.LeFrame.pack(anchor=tkinter.NE)

        self.LeXFrame.pack(anchor=tkinter.NE)
        self.LeXLabel.pack(side = tkinter.LEFT)
        self.LeXEntry.pack(side = tkinter.LEFT)

        self.LeSweepFrame.pack(anchor=tkinter.NE)
        self.LeSweepLabel.pack(side = tkinter.LEFT)
        self.LeSweepEntry.pack(side = tkinter.LEFT)

        self.TeFrame.pack(anchor=tkinter.NE)

        self.TeXFrame.pack(anchor=tkinter.NE)
        self.TeXLabel.pack(side = tkinter.LEFT)
        self.TeXEntry.pack(side = tkinter.LEFT)

        self.TeSweepFrame.pack(anchor=tkinter.NE)
        self.TeSweepLabel.pack(side = tkinter.LEFT)
        self.TeSweepEntry.pack(side = tkinter.LEFT)

    def __init__(self, name:str, parent:PyFitMain):
        self.name = name
        self.parent = parent
        self.centerPane = parent.centerPane


class PyFitResults:
    def __init__(self, parent:PyFitMain):
        self.parent = parent
        self.pane = parent.rightPane
        self.label = ttk.Label(self.pane, text='')
        self.label.pack()

    def updateResult(self):
        self.results = {
            'Wing': {
                '.25 sweep': NaN,
                'Taper': NaN,
                'AR': NaN,
                'S': NaN,
            },
            'HStab': {
                '.25 sweep': NaN,
                'Taper': NaN,
                'AR': NaN,
                'S': NaN,
            },
        }

        if self.parent.canvas is None:
            return

        self.results['Wing'][ '.25 sweep'] = self.parent.wing.quarterSweep
        self.results['HStab']['.25 sweep'] = self.parent.hstab.quarterSweep
        self.results['Wing']['Taper'] = self.parent.wing.taper
        self.results['HStab']['Taper'] = self.parent.hstab.taper
        self.results['Wing']['S'] = self.parent.wing.S
        self.results['HStab']['S'] = self.parent.hstab.S
        self.results['Wing']['AR'] = self.parent.wing.AR
        self.results['HStab']['AR'] = self.parent.hstab.AR


    def renderResult(self):
        self.updateResult()
        resultStr = ''
        for key in self.results:
            resultStr += f'{key}:\n'
            for subkey in self.results[key]:
                resultStr += f'    {subkey}: {self.results[key][subkey]}\n'

        self.label.configure(text=resultStr)
        return

class DandDhandler:
    def onClick(self,event):
        assert self.parent.canvas is not None

        x = event.x
        y = event.y

        # クリックされた位置に一番近い図形のID取得
        self.GrabbedObj = self.parent.canvas.find_closest(x, y)

        # マウスの座標を記憶
        self.before_x = x
        self.before_y = y

        self.clickHook(self.GrabbedObj)

    def onDrag(self,event):
        assert self.parent.canvas is not None
        global before_x, before_y

        x = event.x
        y = event.y

        # 前回からのマウスの移動量の分だけ図形も移動
        self.parent.canvas.move(
            self.GrabbedObj,
            x - self.before_x, y - self.before_y
        )

        # マウスの座標を記憶
        self.before_x = x
        self.before_y = y

        self.dragHook(self.GrabbedObj)

    def onDrop(self, event):
        _=event
        self.GrabbedObj = None

        self.dropHook(self.GrabbedObj)

    def __init__(
            self,
            parent:PyFitMain,
            onClick=dummyHook,
            onDrag=dummyHook,
            onDrop=dummyHook
    ):
        self.parent = parent
        self.clickHook = onClick
        self.dragHook = onDrag
        self.dropHook = onDrop
