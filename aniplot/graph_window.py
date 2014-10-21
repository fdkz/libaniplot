import time

import draw
import copengl as gl


class GraphWindow:
    """
    handles keyboard/mouse navigation (zoom/drag), border drawing. delegates graph rendering to self.graph_renderer
    """
    def __init__(self, parent, font, graph_renderer, keys, x=0, y=0, w=100, h=50):
        """ TODO: w, h is with scrollbars and borders?
        :type graph_renderer: GraphRenderer
        """
        self.parent = parent
        self.font = font
        self.graph_renderer = graph_renderer
        self.keys = keys
        self.x, self.y = x, y
        self.w, self.h = w, h

        # render the legend window
        self.render_legend = True
        self.render_legend_pos = (50, 35)

        # graph is moving from right to left? newest sample is anchored to the right window edge.
        self.anchored = True

        num_visible_samples = int(5 * self.graph_renderer.channels[0].freq + 0.5)

        # TODO: make these private
        # also, create set_visible_samplespace() method

        # visible sample-space rectangle. x1, y1 is top-left on screen
        # so the top-left screen-pixel of the graph window should have the sample at coordinates (sx1, sy2)
        self.sx1 = -num_visible_samples
        self.sy1 = self.graph_renderer.channels[0].value_max
        self.sx2 = 0.
        self.sy2 = self.graph_renderer.channels[0].value_min
        # wanted visible sample-space rectangle. the visible sample-space rectangle is animated towards this rect.
        self.wsx1 = self.sx1
        self.wsy1 = self.sy1
        self.wsx2 = self.sx2
        self.wsy2 = self.sy2

        self.ax = 0.
        self.ay = 0.

        self._time = time.time
        self._smooth_movement = True

    def tick(self, dt=1./60):
        d = 0.4

        # turns out that it's better to not have separate values for left/right and top/bottom,
        # ie. it's better to have just ax, ay instead of ax1, ax2, ay1, ay2
        # smooth out the movement. trying to lower the initial speed.
        # TODO: only tuned for 60fps. could be TERRIBLE on lower fps
        if abs(self.wsx2 - self.wsx1) > 0.0001:
            self.ax += (abs(self.wsx1 - self.sx1) + abs(self.wsx2 - self.sx2)) / abs(self.wsx2 - self.wsx1) * .02
        self.ax *= 0.99
        ax = min(self.ax, 1.)

        if abs(self.wsy2 - self.wsy1) > 0.0001:
            self.ay += (abs(self.wsy1 - self.sy1) + abs(self.wsy2 - self.sy2)) / abs(self.wsy2 - self.wsy1) * .02
        self.ay *= 0.99
        ay = min(self.ay, 1.)

        #def move_towards(x1, x2, dt):
        #    speed = 1. ; dx = speed * dt
        #    if x1 < x2:
        #        if x1 + dx > x2: dx = x2 - x1
        #    else:
        #        dx = -dx;
        #        if x1 + dx < x2: dx = x1 - x2
        #    return x1 + dx
        if not self._smooth_movement:
            ax = ay = 1

        self.sx1 += (self.wsx1 - self.sx1) * d * ax
        self.sy1 += (self.wsy1 - self.sy1) * d * ay
        self.sx2 += (self.wsx2 - self.sx2) * d * ax
        self.sy2 += (self.wsy2 - self.sy2) * d * ay

        #self.sx1 += (self.wsx1 - self.sx1) * d * math.log(abs(self.wsx1 - self.sx1) + 1, 1.2)
        #self.sx2 += (self.wsx2 - self.sx2) * d * math.log(abs(self.wsx2 - self.sx2) + 1, 1.2)
        self._hold_bounds()

    def render(self):
        """ render everything. window edge, scrollbar, legend, and the graph itself. the graph object
         renders the grid, background, grid text and the graph line """
        draw.filled_rect(self.x, self.y, self.w, self.h, (0.0,0.0,0.0,1.))
        self._render_scrollbar(self.x, self.y + 1, self.w, 8)

        # render oscilloscope window edge
        gl.glPushMatrix()
        gl.glTranslatef(.5,.5,0.)
        gl.glLineWidth(1.)
        draw.rect(self.x, self.y, self.w, self.h, (0.6,0.6,0.6,1.))
        gl.glPopMatrix()

        gl.glPushMatrix()
        x, y, w, h = self._raw_graph_window_dim()
        xx, yy = self.parent.gl_coordinates(x, y)
        gl.glScissor(int(xx), int(yy - h), int(w), int(h))
        gl.glEnable(gl.GL_SCISSOR_TEST)
        #print "sy1 %.2f sy2 %.2f sy2 - sy1 %.2f" % (self.sy1, self.sy2, self.sy2 - self.sy1)
        self.graph_renderer.render(x, y, w, h, self.sx1, self.sy1, self.sx2 - self.sx1, self.sy2 - self.sy1)
        gl.glDisable(gl.GL_SCISSOR_TEST)
        gl.glPopMatrix()

        if self.render_legend:
            x, y = self.render_legend_pos
            self._render_legend(self.x + x, self.y + y)

    def set_smooth_movement(self, smooth):
        self._smooth_movement = smooth
        #if not smooth:
        #    self.wsx1 = self.sx1
        #    self.wsx2 = self.sx2

    def zoom_in(self, x_ratio, y_ratio):
        """ zoom in. exactly 'percent' fewer samples are visible. """
        n = (self.wsx2 - self.wsx1) * x_ratio
        self.wsx1 += n / 2.
        self.wsx2 -= n / 2.
        n = (self.wsy2 - self.wsy1) * y_ratio
        self.wsy1 += n / 2.
        self.wsy2 -= n / 2.

    def zoom_out(self, x_ratio, y_ratio):
        n = (self.wsx2 - self.wsx1) * (1. / (1. - x_ratio) - 1.)
        self.wsx1 -= n / 2.
        self.wsx2 += n / 2.
        n = (self.wsy2 - self.wsy1) * (1. / (1. - y_ratio) - 1.)
        self.wsy1 -= n / 2.
        self.wsy2 += n / 2.

    def move_by_pixels(self, dx, dy):
        """ move graph by pixels """
        wx, wy, w, h = self._raw_graph_window_dim()
        dwx = dx / w * (self.wsx2 - self.wsx1)
        dwy = dy / h * (self.wsy2 - self.wsy1)
        self.wsx1 -= dwx
        self.wsy1 -= dwy
        self.wsx2 -= dwx
        self.wsy2 -= dwy
        # moving the graph left releases anchoring
        if dx > 0:
            self.anchored = False
        self._hold_bounds()

    def move_by_ratio(self, dx, dy):
        d = (self.wsx2 - self.wsx1) * dx
        self.wsx1 += d
        self.wsx2 += d
        if d < 0.:
            self.anchored = False
        d = (self.wsy2 - self.wsy1) * dy
        self.wsy1 += d
        self.wsy2 += d
        self._hold_bounds()

    # THIS WILL BE REMOVED

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        k = self.keys
        if self._inside(x, y):
            if 1: # self.use_trackpad
                if not (k[key.LCTRL] or k[key.RCTRL] or k[key.LSHIFT] or k[key.RSHIFT]):
                    self.move_by_pixels(scroll_x*4., scroll_y*4.)
                # hmm. if shift is down, scroll_x and scroll_y are swapped for mouse wheel.
                # but not for apple trackpad.
                if not (k[key.LCTRL] or k[key.RCTRL]) and (k[key.LSHIFT] or k[key.RSHIFT]):
                    self._zoom_graph(x, y, scroll_x*4., scroll_y*4.)
            else: # use mouse wheel
                if not (k[key.LCTRL] or k[key.RCTRL] or k[key.LSHIFT] or k[key.RSHIFT]):
                    self._zoom_graph(x, y, -scroll_y*16., scroll_x*4.)
                if not (k[key.LCTRL] or k[key.RCTRL]) and (k[key.LSHIFT] or k[key.RSHIFT]):
                    self._zoom_graph(x, y, -scroll_x*16., scroll_y*4.)

                # a hybrid solution. hold down t to use the apple trackpad for navigation
                #if not (k[key.LCTRL] or k[key.RCTRL]) and (k[key.LSHIFT] or k[key.RSHIFT]):
                if not (k[key.LCTRL] or k[key.RCTRL]) and k[key.T]:
                    self.move_by_pixels(scroll_x*4., scroll_y*4.)

    def _inside(self, x, y):
        """ return True if coordinate x, y is inside the graph window (excludes window border) """
        wx, wy, w, h = self._raw_graph_window_dim()
        if wx <= x < wx + w and wy <= y < wy + h:
            return True
        return False

    def _raw_graph_window_dim(self):
        """ return graph window pos/size in parent window coordinate system, compensating for window border """
        # self.y + 10: 1 for border, 9 for scrollbar
        return self.x+1., self.y+1.+9., self.w-2., self.h-2.-9.

    def _zoom_graph(self, x, y, dx, dy):
        assert self._inside(x, y)
        wx, wy, w, h = self._raw_graph_window_dim()

        # zoom horizontally
        d = (x - wx) / w
        coef = 0.001
        num_samples = (self.wsx2 - self.wsx1) * dx * coef
        self.wsx1 -= d * num_samples
        self.wsx2 += (1. - d) * num_samples

        # zoom vertically
        d = float(y - wy) / h
        coef = 0.001
        num_values = (self.wsy2 - self.wsy1) * dy * coef
        self.wsy1 += (d) * num_values
        self.wsy2 -= (1. - d) * num_values

        self._hold_bounds()

    def _hold_bounds(self):
        """ anchores and releases right window edge to last sample. bounds zooms and movements. """
        adc_channel = self.graph_renderer.channels[0]
        if self.sx2 > adc_channel.size():
            self.anchored = True

        if self.anchored:
            # anchor right side of the window to the last graph sample. so the graph always animates, grows out from
            # the right side of the window. (anchor sx2 to adc_channel.size())
            dx = self.sx2 - adc_channel.size()
            dxw = self.wsx2 - adc_channel.size()
            self.sx1 -= dx
            self.sx2 -= dx
            self.wsx1 -= dxw
            self.wsx2 -= dxw

        # eliminate integer overflow problems. only allow indices smaller than a 32bit integer value. and then divide
        # it by four just to be sure.. maybe it's not necessary, but maybe there are some other tricks used in the
        # graph rendering..
        bound = 0xffffffff / 4
        # hmm. this allows only 12 days of data with ~960Hz. time to go 64bit?
        self.sx1 = max(self.sx1, -bound)
        self.sy1 = max(self.sy1, -bound)
        self.sx1 = min(self.sx1,  bound)
        self.sy1 = min(self.sy1,  bound)
        self.sx2 = max(self.sx2, -bound)
        self.sy2 = max(self.sy2, -bound)
        self.sx2 = min(self.sx2,  bound)
        self.sy2 = min(self.sy2,  bound)
        self.wsx1 = max(self.wsx1, -bound)
        self.wsy1 = max(self.wsy1, -bound)
        self.wsx1 = min(self.wsx1,  bound)
        self.wsy1 = min(self.wsy1,  bound)
        self.wsx2 = max(self.wsx2, -bound)
        self.wsy2 = max(self.wsy2, -bound)
        self.wsx2 = min(self.wsx2,  bound)
        self.wsy2 = min(self.wsy2,  bound)

        # limit horizontal zoom to 2 samples. can't zoom in anymore if less than one sample stays on screen.
        # don't have time to implement and test line segment cutting, if one sample is outside the window, and another
        # is inside.
        if self.wsx2 - self.wsx1 < 2.:
            self.wsx2 = self.wsx1 + 2.
        if self.sx2 - self.sx1 < 2.:
            self.sx2 = self.sx1 + 2.

        #
        # limit vertical movement and vertical zoom
        #

        val_min = adc_channel.value_min
        val_max = adc_channel.value_max

        # allow offset of this percent/100 of the screen
        overlap = .30

        # top of the screen has smaller sample values than bottom of the screen. inverted graph.
        # sy1 is top pixel, sy2 bottom. bottom-left coordinat is (0, 0)
        if self.sy1 < self.sy2:
            val_top    = val_min + (self.wsy1 - self.wsy2) * overlap
            val_bottom = val_max - (self.wsy1 - self.wsy2) * overlap
            if self.wsy1 < val_top:
                self.wsy2 -= self.wsy1 - val_top
                self.wsy1 = val_top
            if self.wsy2 > val_bottom:
                self.wsy1 += val_bottom - self.wsy2
                self.wsy2 = val_bottom
            if self.wsy1 < val_top:
                self.wsy1 = val_top
            if self.wsy2 > val_bottom:
                self.wsy2 = val_bottom
        else:
            val_bottom = val_min - (self.wsy1 - self.wsy2) * overlap
            val_top    = val_max + (self.wsy1 - self.wsy2) * overlap
            if self.wsy1 > val_top:
                self.wsy2 -= self.wsy1 - val_top
                self.wsy1 = val_top
            if self.wsy2 < val_bottom:
                self.wsy1 += val_bottom - self.wsy2
                self.wsy2 = val_bottom
            if self.wsy1 > val_top:
                self.wsy1 = val_top
            if self.wsy2 < val_bottom:
                self.wsy2 = val_bottom

    def _render_scrollbar(self, x, y, w, h):
        v = .6
        draw.line(x + 0.5, y+h + 0.5, x+w, y + h, (v,v,v,1.))

        adc_channel = self.graph_renderer.channels[0]
        if not adc_channel.size():
            return

        x1 = self.sx1 / (adc_channel.size()) * w
        x2 = self.sx2 / (adc_channel.size()) * w
        if x2 - x1 < 1.:
            x2 = x1 + 1.
        x1 = max(x1, 0.)
        x2 = max(x2, 0.)
        x1 = min(x1, w)
        x2 = min(x2, w)
        v = .8
        draw.filled_rect(x1+x, y + 1., x2-x1, h - 2., (v,v,v,1.))
        v = .7
        #draw.rect(x1, y, x2-x1, h, (v,v,v,1.))

    def _render_legend(self, x, y):
        # render oscilloscope window edge
        gl.glPushMatrix()
        gl.glTranslatef(.5,.5,0.)
        gl.glLineWidth(1.)
        gl.glDisable(gl.GL_LINE_SMOOTH)
        # calculate legend window size
        w = 0.
        h = self.font.height * len(self.graph_renderer.channels)
        for channel in self.graph_renderer.channels:
            w = max(w, self.font.width(channel.name))
        # draw legend window background and border
        draw.filled_rect(x, y, w+24, h+4, (0.3, 0.3, 0.3, 0.3))
        draw.rect(x, y, w+24, h+4, (0.4, 0.4, 0.4, .8))
        # draw legend window example linesegments
        dy = y + 2. + self.font.height / 2.
        gl.glEnable(gl.GL_LINE_SMOOTH)
        for channel in self.graph_renderer.channels:
            gl.glLineWidth(channel.f_linewidth)
            draw.line(x + 4, dy, x + 14, dy, channel.f_color_avg)
            dy += self.font.height
        # draw legend window text
        gl.glTranslatef(-.5, -.5, 0.)
        dy = y + 2.
        for channel in self.graph_renderer.channels:
            self.font.drawtl(channel.name, x + 20, dy, bgcolor=(0.,0.,0.,0.), fgcolor=(0.9, 0.9, 0.9, .8))
            dy += self.font.height
        gl.glPopMatrix()
