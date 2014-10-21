import sys
import math
import time

import copengl as gl


class GraphRenderer:
    """
    renders graphs (graph_channel objects) and grid/grid-text with the selected zoom level and position.
    """

    def __init__(self, font):
        self.font = font
        # graph_channel objects that are filled with data from the outside world
        self.channels = []

        if sys.platform == "win32":
            self._time = time.clock
        else:
            self._time = time.time

    def setup(self, channels):
        """ channels - list of graph_channel objects
        :type channels: list(GraphChannel)
        TODO: this type format seems that doesn't work

        NB! if rendering multiple channels:
          1. make sure the channels never get out of sync. first sample has to mark the same point in time,
             and channel.size() / channel.freq has to.. mean something-something..
          2. channels[0] has to be the fastest channel.
        """
        self.channels = channels[:]

    def tick(self):
        pass

    def _pixel_to_sample(self, y_pixel, h_pixels, y2, h2):
        """ return sample val of a pixel at height y_pixel (0 is top). pixel center coordinates.
        y_pixel : 0..h_pixels
        """
        return y2 + h2 / (h_pixels - 1) * y_pixel

    def _sample_to_pixel(self, y_sample, y2, h2, h_pixels):
        """ return pixel coord of sample at val y_sample """
        return (h_pixels - 1.) / h2 * (y_sample - y2)

    def _samplenum_to_pixel(self, samplenum, x2, w2, w_pixels):
        return (samplenum - x2) / w2 * w_pixels

    def _render_grid_hortext(self, w, h, x2, y2, w2, h2, channel, left=False, min_div_hpix=50.):
        """
        render text for the horizontal lines. value legend.
        min_div_hpix : minimum division height (grid line distance) in pixels
        """
        assert  h > 1.
        ch = channel
        if abs(h2) < 0.000001:
            return

        v1 = y2
        v2 = y2 + h2
        # swap begin/end if necessary to make following calculations much more convenient
        if v2 < v1:
            v1, v2 = v2, v1

        volts_per_min_div = (v2 - v1) / (h - 1.) * min_div_hpix
        pixels_per_volt = (h - 1.) / (v2 - v1)
        v_step = math.pow(2, math.ceil(math.log(volts_per_min_div, 2)))
        v_font_height = 1. / pixels_per_volt * self.font.height
        v_begin = math.floor((v1 - v_font_height / 2.) / v_step) * v_step + v_step
        v_end   = v2 + v_font_height / 2.
        v_num   = math.floor((v_end - v_begin) / v_step)

        c = 0.2
        v = v_begin
        while v < v_end:
            px = self._sample_to_pixel(v, y2, h2, h)
            #if ch == self.temperature_channel:
            #    txt = "%.1f%s" % (tempc.convertTemp(ch.value_for_volt(v)), ch.si_unit)
            txt = "%.2f%s" % (v, ch.si_unit)
            if left:
                xcoord = w - self.font.width(txt) - 1
            else:
                xcoord = 1
            self.font.drawtl(txt, xcoord, px - self.font.height / 2., bgcolor = (c, c, c, .8), fgcolor = (1.9, 1.9, 1.9, .8))

            v += v_step

    def _render_grid_vertext(self, w, h, x2, y2, w2, h2, min_div_hpix=100.):
        assert w > 0.
        ch = self.channels[0]
        if abs(w2) < 0.000001:
            return

        sn1 = x2 # sample num
        sn2 = x2 + w2
        st1 = ch.sample_to_time(sn1) # sv - sample time
        st2 = ch.sample_to_time(sn2)
        # swap begin/end if necessary to make following calculations much more convenient
        if st2 < st1:
            st1, st2 = st2, st1
            sn1, sn2 = sn2, sn1

        #volts_per_min_div = (v2 - v1) / (h - 1.) * min_div_hpix
        seconds_per_min_div = (st2 - st1) / w * min_div_hpix
        #pixels_per_volt = (h - 1.) / (v2 - v1)
        pixels_per_second = float(w) / w2 * ch.freq
        st_text_maxwidth = 1. / pixels_per_second * self.font.height * 15 / 2. # assume our text is max 15 characters wide and font width is the same as font height
        st_step  = math.pow(2, math.ceil(math.log(seconds_per_min_div, 2)))
        st_begin = math.floor((st1 - st_text_maxwidth) / st_step) * st_step + st_step
        st_end   = st2 + st_text_maxwidth / 2.

        c = 0.2
        st = st_begin
        while st < st_end:
            px = self._samplenum_to_pixel(st * ch.freq, x2, w2, w)
            txt = self._grid_timestr(st, st_step)
            self.font.drawtl(txt, px - self.font.width(txt) / 2. - 0.5, 1, bgcolor = (c, c, c, .8), fgcolor = (1.9, 1.9, 1.9, .8))
            st += st_step

    def _grid_timestr(self, seconds, step):
        s = abs(seconds)
        days     = s // (60*60*24)
        hours    = s // (60*60) % 24
        minutes  = s // 60 % 60
        seconds2 = s % 60
        # TODO: use the step parameter for seconds comma?
        if s < 60.:
            t = "%.2fs" % s
        elif s < 60. * 60.:
            t = "%im%.2fs" % (minutes, seconds2)
        elif s < 60. * 60. * 24:
            t = "%ih%im%.2fs" % (hours, minutes, seconds2)
        else:
            t = "%id%ih%im%.2fs" % (days, hours, minutes, seconds2)

        if seconds < 0.:
            return "-" + t
        else:
            return t

    def _render_grid_horlines(self, w, h, x2, y2, w2, h2, min_div_hpix=50.):
        """
        min_div_hpix : minimum division height (grid line distance) in pixels
        """
        assert  h > 1.
        ch = self.channels[0]
        if abs(h2) < 0.000001:
            return

        v1 = y2
        v2 = y2 + h2
        # swap begin/end if necessary to make following calculations much more convenient
        if v2 < v1:
            v1, v2 = v2, v1

        volts_per_min_div = (v2 - v1) / (h - 1.) * min_div_hpix
        pixels_per_volt = (h - 1.) / (v2 - v1)
        v_step = math.pow(2, math.ceil(math.log(volts_per_min_div, 2)))

        # volt begin
        v_begin = math.floor(v1 / v_step) * v_step + v_step
        px_begin = self._sample_to_pixel(v_begin, y2, h2, h)
        px_end   = self._sample_to_pixel(v2, y2, h2, h) # overshooting is intentional
        sign = 1 if px_end > px_begin else -1
        px_step  = pixels_per_volt * v_step * sign

        gl.glBegin(gl.GL_LINES)

        px = px_begin
        while px * sign < px_end:
            gl.glVertex3f( 0., px, 0. )
            gl.glVertex3f(  w, px, 0. )
            px += px_step

        gl.glEnd()

    def _render_grid_verlines(self, w, h, x2, y2, w2, h2, min_div_hpix=100.):
        """
        min_div_hpix : minimum division height (grid line distance) in pixels
        """
        assert w > 0.
        ch = self.channels[0]
        if abs(w2) < 0.000001:
            return

        sn1 = x2 # sample num
        sn2 = x2 + w2
        st1 = ch.sample_to_time(sn1) # sv - sample time
        st2 = ch.sample_to_time(sn2)
        # swap begin/end if necessary to make following calculations much more convenient
        if st2 < st1:
            st1, st2 = st2, st1
            sn1, sn2 = sn2, sn1

        #volts_per_min_div = (v2 - v1) / (h - 1.) * min_div_hpix
        seconds_per_min_div = (st2 - st1) / w * min_div_hpix
        #pixels_per_volt = (h - 1.) / (v2 - v1)
        pixels_per_second = float(w) / w2 * ch.freq
        st_step  = math.pow(2, math.ceil(math.log(seconds_per_min_div, 2)))
        st_begin = math.floor(st1 / st_step) * st_step + st_step

        px_begin = self._samplenum_to_pixel(ch.time_to_sample(st_begin), x2, w2, w)
        px_end   = self._samplenum_to_pixel(sn2, x2, w2, w) # overshooting is intentional
        sign = 1 if px_end > px_begin else -1
        px_step  = pixels_per_second * st_step * sign

        gl.glBegin(gl.GL_LINES)

        px = px_begin
        while px * sign < px_end:
            gl.glVertex3f( px, 0., 0. )
            gl.glVertex3f( px,  h, 0. )
            px += px_step

        gl.glEnd()

    def _render_grid_text(self, w, h, x2, y2, w2, h2):
        self._render_grid_hortext(w, h, x2, y2, w2, h2, self.channels[0])
        #if self.temperature_channel:
        #    self._render_grid_hortext(w, h, x2, y2, w2, h2, self.temperature_channel, left=True)
        self._render_grid_vertext(w, h, x2, y2, w2, h2)

    def _render_grid_lines(self, w, h, x2, y2, w2, h2):
        """ render grid in screenspace. render gridlines and grid legend """
        # 1. find sample value of top/bottom pixel coordinate
        # 2. calc sample values that need a line and draw them using pixel-coordinates
        # 3. find time values of left/right pixel coordinate
        # 2. calc time values that need a line and draw them using pixel-coordinates
        gl.glLineWidth(1.)
        gl.glColor4f(0.15, 0.15, 0.15, 1.)

        self._render_grid_horlines(w, h, x2, y2, w2, h2)
        self._render_grid_verlines(w, h, x2, y2, w2, h2)

    # TODO: make another version with timebased x2, w2?
    def _render_graphs(self, x, y, w, h, x2, y2, w2, h2):
        """
        x,  y,  w,  h : pos and dimensions inside parent window
        x2, y2, w2, h2: pos and dimensions of visible sample-space. (0..1 is first sample)
        """
        if -0.0001 < h2 < 0.0001: return

        gl.glPushMatrix()
        gl.glTranslatef(x, y, 0.)

        # top-left pixel of the graph shows sample x2 valued y2
        gl.glTranslatef(0., 0.5, 0.)

        if 1:
            # draw sensor value limit boxes in sample-space
            gl.glPushMatrix()
            gl.glScalef(1., float(h - 1.) / h2, 1.)
            gl.glTranslatef(0., -y2, 0.)

            gl.glEnable(gl.GL_LINE_SMOOTH)
            gl.glScalef(w / w2, 1., 1.)

            ch = self.channels[0]
            hh = (ch.value_max - ch.value_min) * 10.
            gl.glColor4f(.13, 0.13, 0.13 ,1.)
            gl.glBegin(gl.GL_QUADS)
            gl.glVertex3f( 0., ch.value_min - hh, 0. )
            gl.glVertex3f( w2, ch.value_min - hh, 0. )
            gl.glVertex3f( w2, ch.value_min, 0. )
            gl.glVertex3f( 0., ch.value_min, 0. )
            gl.glVertex3f( 0., ch.value_max, 0. )
            gl.glVertex3f( w2, ch.value_max, 0. )
            gl.glVertex3f( w2, ch.value_max + hh, 0. )
            gl.glVertex3f( 0., ch.value_max + hh, 0. )
            gl.glEnd()

            gl.glDisable(gl.GL_LINE_SMOOTH)
            gl.glPopMatrix()

        gl.glDisable(gl.GL_LINE_SMOOTH)
        self._render_grid_lines(w, h, x2, y2, w2, h2)
        gl.glEnable(gl.GL_LINE_SMOOTH)

        gl.glPushMatrix()
        gl.glScalef(1., float(h - 1.) / h2, 1.)
        gl.glTranslatef(0., -y2, 0.)
        #for channel in self.channels:
        #    channel.render(x2, x2+w2, w)
            #self.channels_local[2].render_avg(x2, x2+w2, w)
        channel0 = self.channels[0]
        for channel in self.channels:
            channel.render(x2 * channel.freq / channel0.freq, (x2+w2) * channel.freq / channel0.freq, w)
        gl.glPopMatrix()

        gl.glTranslatef(0., -0.5, 0.)
        gl.glDisable(gl.GL_LINE_SMOOTH)
        self._render_grid_text(w, h, x2, y2, w2, h2)

        gl.glPopMatrix()

    def render(self, x, y, w, h, x2, y2, w2, h2):
        self._render_graphs(x, y, w, h, x2, y2, w2, h2)
