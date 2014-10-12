import sys
import math
import time
import os
import traceback

from PySide import QtCore, QtGui, QtOpenGL

sys.path.append("..")
from aniplot import graph_window
from aniplot import graph_renderer
from aniplot import graph_channel
import fps_counter

import gltext
import copengl as gl
import copenglconstants as glconst


class AniplotBase(QtOpenGL.QGLWidget):
    ''' Aniplot baseclass - this is not used directly in real application.
        Use AniplotWidget instead.
    '''

    def __init__(self, parent=None):
        super(AniplotBase, self).__init__(parent)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.tick)

        self.gltext = gltext.GLText(os.path.join(os.path.dirname(__file__), 'data', 'font_proggy_opti_small.txt'))

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus()
        self.setMouseTracking(True)

        # renders graphs, grids, legend, scrollbar, border.
        self.grapher = graph_renderer.GraphRenderer(self.gltext)
        self.channels = []
        self.graph_window = None

        self._fps_counter = fps_counter.FpsCounter()
        self._mouse_last_pos = None # event.pos()
        self._mouse_dragging = False
        self._last_tick_time = time.time()

    def _start(self):
        ''' begins drawing if all channels are setup '''
        self.grapher.setup(self.channels)
        # converts input events to smooth zoom/movement of the graph.
        self.graph_window = graph_window.GraphWindow(self, font=self.gltext, graph_renderer=self.grapher, keys=None, x=0, y=0, w=10, h=10)
        self.timer.start(1./60*1000)

    def __del__(self):
        self.makeCurrent()

    def initializeGL(self):
        gl.glDisable(glconst.GL_TEXTURE_2D)
        gl.glDisable(glconst.GL_DEPTH_TEST)
        gl.glDisable(glconst.GL_FOG)
        gl.glDisable(glconst.GL_DITHER)
        gl.glDisable(glconst.GL_LIGHTING)
        gl.glShadeModel(glconst.GL_FLAT)
        gl.glEnable(glconst.GL_BLEND)
        gl.glBlendFunc(glconst.GL_SRC_ALPHA, glconst.GL_ONE_MINUS_SRC_ALPHA)
        gl.glDisable(glconst.GL_LINE_SMOOTH)
        gl.glEnable(glconst.GL_POINT_SMOOTH)
        gl.glDisable(glconst.GL_LINE_STIPPLE)
        gl.glDisable(glconst.GL_LIGHT1)
        #glFrontFace(glconst.GL_CW)

        gl.glEnable(glconst.GL_NORMALIZE)
        gl.glHint(glconst.GL_PERSPECTIVE_CORRECTION_HINT, glconst.GL_NICEST)
        gl.glDisable(glconst.GL_CULL_FACE)
        #glCullFace(glconst.GL_BACK)
        gl.glPolygonMode(glconst.GL_FRONT_AND_BACK, glconst.GL_FILL)
        # wireframe view
        #glPolygonMode(glconst.GL_FRONT_AND_BACK, glconst.GL_LINE)

        self.gltext.init()

    def tick(self):
        t = time.time()
        self._fps_counter.tick(t - self._last_tick_time)
        self.updateGL()
        self._last_tick_time = t

    def gl_coordinates(self, x, y):
        return x, self.size().height() - y

    def paintGL(self):
        try:
            self.render()
        except:
            traceback.print_exc()
            sys.exit(1)

    def render(self):
        if self.graph_window:
            w = self.size().width()
            h = self.size().height()
            if w <= 0 or h <= 0:
                return

            self.grapher.tick()
            self.graph_window.tick()

            gl.glClearColor(0.2, 0.2, 0.2, 1.0)
            gl.glClear(glconst.GL_COLOR_BUFFER_BIT | glconst.GL_DEPTH_BUFFER_BIT)

            gl.glViewport(0, 0, w, h)

            gl.glMatrixMode(glconst.GL_PROJECTION)
            gl.glLoadIdentity()
            gl.glOrtho(0., w, h, 0., -100, 100)

            gl.glDisable(glconst.GL_DEPTH_TEST)
            gl.glDisable(glconst.GL_TEXTURE_2D)
            gl.glDisable(glconst.GL_LIGHTING)

            gl.glMatrixMode(glconst.GL_MODELVIEW)
            gl.glLoadIdentity()
            gl.glScalef(1.,1.,-1.)

            self.graph_window.x = -1
            self.graph_window.y = -1
            self.graph_window.w = w + 2
            self.graph_window.h = h + 2

            # render 2d objects
            gl.glDisable(glconst.GL_DEPTH_TEST)
            gl.glDisable(glconst.GL_TEXTURE_2D)
            self.graph_window.render()
            gl.glEnable(glconst.GL_TEXTURE_2D)
            self.gltext.drawbr("fps: %.0f" % (self._fps_counter.fps), w, h, fgcolor = (.9, .9, .9, 1.), bgcolor = (0.3, 0.3, 0.3, .0))
            self.gltext.drawbm("usage: arrows, shift, mouse", w/2, h-3, fgcolor = (.5, .5, .5, 1.), bgcolor = (0., 0., 0., .0))

    def resizeGL(self, width, height):
        pass

    @QtCore.Slot(QtGui.QKeyEvent)
    def keyPressEvent(self, event):
        key = event.key()
        if self.graph_window:
            # if shift is not pressed, move the graph.
            if not (event.modifiers() & QtCore.Qt.ShiftModifier):
                d = 1. / 3
                if key == QtCore.Qt.Key_Left:
                    self.graph_window.move_by_ratio(-d, 0.)
                if key == QtCore.Qt.Key_Right:
                    self.graph_window.move_by_ratio(d, 0.)
                if key == QtCore.Qt.Key_Up:
                    self.graph_window.move_by_ratio(0., -d)
                if key == QtCore.Qt.Key_Down:
                    self.graph_window.move_by_ratio(0., d)
            # shift was pressed. zoom the graph.
            else:
                d = 1. / 3
                if key == QtCore.Qt.Key_Left:
                    self.graph_window.zoom_out(d, 0.)
                if key == QtCore.Qt.Key_Right:
                    self.graph_window.zoom_in(d, 0.)
                if key == QtCore.Qt.Key_Up:
                    self.graph_window.zoom_in(0., d)
                if key == QtCore.Qt.Key_Down:
                    self.graph_window.zoom_out(0., d)

    @QtCore.Slot(QtGui.QKeyEvent)
    def keyReleaseEvent(self, event):
        pass

    @QtCore.Slot(QtGui.QMouseEvent)
    def mousePressEvent(self, event):
        if self.graph_window:
            self._mouse_last_pos = event.pos()
            if event.button() == QtCore.Qt.LeftButton:
                self._mouse_dragging = True
                self.graph_window.set_smooth_movement(False)

    @QtCore.Slot(QtGui.QMouseEvent)
    def mouseReleaseEvent(self, event):
        if self.graph_window:
            if event.button() == QtCore.Qt.LeftButton:
                self._mouse_dragging = False
                self.graph_window.set_smooth_movement(True)

    @QtCore.Slot(QtGui.QMouseEvent)
    def mouseMoveEvent(self, event):
        if self.graph_window:
            if not self._mouse_last_pos:
                self._mouse_last_pos = event.pos()
            dx = event.x() - self._mouse_last_pos.x()
            dy = event.y() - self._mouse_last_pos.y()
            if self._mouse_dragging:
                self.graph_window.move_by_pixels(dx, dy)
            self._mouse_last_pos = event.pos()


class AniplotWidget(AniplotBase):

    default_color = QtGui.QColor(30, 144, 255) # http://cloford.com/resources/colours/500col.htm dodgerblue 1

    def __init__(self):
        AniplotBase.__init__(self)

    def create_channel(self, frequency=1000, value_min=0., value_min_raw=0., value_max=5., value_max_raw=255., legend="graph", unit="V", color=default_color):
        ''' Returns GraphChannel object.

            "frequency"     : sampling frequency
            "value_min"     : is minimum real value, for example it can be in V
            "value_min_raw" : is minimum raw value from ADC that corresponds to real "value_min"
            "value_max"     : is maximum real value, for example it can be in V
            "value_max_raw" : is maximum raw value from ADC that corresponds to real "value_max"

            For example with 10 bit ADC with AREF of 3.3 V these values are: value_min=0., value_min_raw=0., value_max=3.3, value_max_raw=1023.

            Use case:
                plotter = AniplotWidget()
                ch1 = plotter.create_channel(frequency=1000, value_min=0., value_min_raw=0., value_max=5., value_max_raw=255.)
                ch2 = plotter.create_channel(frequency=500, value_min=0., value_min_raw=0., value_max=3.3, value_max_raw=1023.)
                plotter.start()

                while 1:
                    sample1 = some_source1.get()
                    sample2 = some_source2.get()
                    if sample1:
                        ch1.append(sample1)
                    if sample2:
                        ch2.append(sample2)

            Data can be appended also with custom timestamp: ch1.append(sample1, time.time())
        '''
        r, g, b, a = color.getRgb()
        channel = graph_channel.GraphChannel(frequency=frequency, legend=legend, unit=unit, color=(r/255., g/255., b/255., a/255.,))
        channel.set_mapping(value_min=value_min, value_min_raw=value_min_raw, value_max=value_max, value_max_raw=value_max_raw)
        self.channels.append(channel)
        return channel

    def start(self):
        ''' Start drawing.
            If channels are setup call this method to begin plotting.
        '''
        self._start()


class SignalGenerator(object):
        ''' This can be used for testing purposes '''
        seed = 0

        def __init__(self):
            SignalGenerator.seed += 1
            self.i = self.seed

        def get(self):
            if 1:
                s = math.sin(time.time()*(self.i+1)*30+self.i*2) * 1.
                s += math.sin(time.time()*(self.i+1)*32.3+self.i*2) * 2.
                s += math.sin(time.time()*(self.i+1)*33.3+self.i*2) * 1.
                s += math.sin(time.time()*(self.i+1)*55.3+self.i*2) * 1.
                s += math.sin(time.time()*(self.i+1)*1.1+self.i*2) * 20.
                s += math.sin(time.time()*(self.i+1)*1.3+self.i*2) * 20.
                s += math.sin(time.time()*(self.i+1)*.2124+self.i*2) * 40.
                s += math.sin(time.time()*(self.i+1)*.0824+self.i*2) * 40.
                s += math.sin(time.time()*(self.i+1)*.0324+self.i*2) * 40.
                s += 127.
            else:
                s = math.sin(time.time()*(self.i+1)*.5+self.i*2) * 133.
                s += 127.
            s = min(s, 255.)
            s = max(s, 0.)

            return s


if __name__ == '__main__':

    class MainWindow(QtGui.QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            # setup GUI
            centralWidget = QtGui.QWidget()
            self.setCentralWidget(centralWidget)

            self.aniplot = AniplotWidget()

            self.glWidgetArea = QtGui.QScrollArea()
            self.glWidgetArea.setWidget(self.aniplot)
            self.glWidgetArea.setWidgetResizable(True)
            self.glWidgetArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.glWidgetArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.glWidgetArea.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
            self.glWidgetArea.setMinimumSize(50, 50)

            centralLayout = QtGui.QGridLayout()
            centralLayout.addWidget(self.glWidgetArea, 0, 0)
            centralWidget.setLayout(centralLayout)

            self.setWindowTitle("QAniplotTest")
            self.resize(400, 300)

            # setup data source
            self.source1 = SignalGenerator()
            self.source2 = SignalGenerator()
            # interestingly, every frequency larger than screen refresh rate results in incorrect speed and jerkyness.
            self.ch1 = self.aniplot.create_channel(frequency=60, value_min=0., value_min_raw=0., value_max=5., value_max_raw=255., legend="fast data")
            self.ch2 = self.aniplot.create_channel(frequency=5, value_min=0., value_min_raw=0., value_max=3.3, value_max_raw=255., legend="slow data", color=QtGui.QColor(0, 238, 0))

            self.timer1 = QtCore.QTimer(self)
            self.timer1.timeout.connect(self.timer1_fired)
            self.timer2 = QtCore.QTimer(self)
            self.timer2.timeout.connect(self.timer2_fired)

            self.aniplot.start()
            # NB! still NEVER use timers for this in real life. timers can skip updates, and
            # the graphs will lose their sync and it could be invisible. always update the slowest
            # graph at every tenth fastest graph update or something like that.. only the fastest
            # graph can use timers.
            self.timer1.start(1. / self.ch1.freq * 1000.)
            self.timer2.start(1. / self.ch2.freq * 1000.)

        def timer1_fired(self):
            self.ch1.append(self.source1.get())

        def timer2_fired(self):
            self.ch2.append(self.source2.get())

    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    if sys.platform == "darwin":
        # this line is here because on macosx the main window always starts below the terminal that opened the app.
        # the reason for getattr is that myapp.raise() caused a syntax error.
        getattr(mainWin, "raise")()

    sys.exit(app.exec_())
