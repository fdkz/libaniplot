import time

from modules import cpp
import copengl as gl


class GraphChannel:
    """
    hold MipBufRenderer and add some channel-specific variables
    """
    def __init__(self, frequency, legend="graph", unit="V", color=(1.0,0.5,0.5,1.0,)):
        """
        """
        self.freq = frequency
        # mappings from raw values in MipBuf to displayed values. for example, maybe the raw recorded value 255 should
        # be shown as 5V on the screen. it's ok if value_max < value_min (same for the raw variant)
        self.value_min     = 0.
        self.value_min_raw = 0.
        self.value_max     = 5.
        self.value_max_raw = 255.

        r, g, b, a = color
        # visual settings flags. read/write. used in render()
        self.f_color_avg = (r, g, b, a)
        self.f_color_minmax = (.4, .1, .1, 1.)
        self.f_render_minmax = False
        self.f_render_avg = True
        self.f_linewidth = 1.

        # can be displayed on the legend
        self.name = legend
        self.si_unit = unit

        self.data = cpp.MipBufRenderer()

        # list of timestamps for every self.freq samples (one timestamp for every second)
        self._timelist = []
        self._seconds = 1
        self._size = 0
        # unit value / raw value
        self._value_scale = 1.
        self.set_mapping(self.value_min, self.value_min_raw, self.value_max, self.value_max_raw)

    def set_mapping(self, value_min, value_min_raw, value_max, value_max_raw):
        """ set graph scale/offset mapping.
        example, using 8 bits to measure 0..5V values:
            value_min = 0V
            value_min_raw = 0
            value_max = 5V
            value_max_raw = 255 """
        assert value_min <= value_max
        # prevent division by zero.
        if value_min == value_max:
            value_max += 1.
        if value_min_raw == value_max_raw:
            value_max_raw += 1.
        self.value_min = value_min
        self.value_max = value_max
        self.value_min_raw = value_min_raw
        self.value_max_raw = value_max_raw
        self._value_scale = (self.value_max - self.value_min) / (self.value_max_raw - self.value_min_raw)

    def render(self, start_index, end_index, resolution):
        """ combined render of avg and minmax lines """
        # TODO: use ideas from these places:
        # http://jet.ro/2011/06/04/better-looking-anti-aliased-lines-with-simple-trick/
        # http://artgrammer.blogspot.com/2011/05/drawing-nearly-perfect-2d-line-segments.html
        # http://artgrammer.blogspot.com/2011/07/drawing-polylines-by-tessellation.html
        # http://homepage.mac.com/arekkusu/bugs/invariance/TexAA.html
        # http://people.csail.mit.edu/ericchan/articles/prefilter/
        if self.f_render_minmax:
            self.render_minmax(start_index, end_index, resolution)
        if self.f_render_avg:
            self.render_avg(start_index, end_index, resolution)

    def render_avg(self, start_index, end_index, resolution):
        gl.glPushMatrix()
        gl.glScalef(1., self._value_scale, 1.)
        gl.glTranslatef(0., -self.value_min_raw, 0.)
        gl.glColor4f(*self.f_color_avg)
        gl.glLineWidth(self.f_linewidth)
        self.data.render_avg(start_index, end_index, resolution)
        gl.glPopMatrix()

    def render_minmax(self, start_index, end_index, resolution):
        gl.glPushMatrix()
        gl.glScalef(1., self._value_scale, 1.)
        gl.glTranslatef(0., -self.value_min_raw, 0.)
        gl.glColor4f(*self.f_color_minmax)
        self.data.render_minmax(start_index, end_index, resolution)
        gl.glPopMatrix()

    def size(self):
        return self.data.size()

    def get(self, i):
        """ return: minval, maxval, avg """
        return self.data.get(i)

    def append(self, avg, timestamp=None):
        """ append raw values (direct measurements) that go directly to the underlying MipBuf object """
        self.data.append(avg)
        # add timestamp every second
        if not self._size % int(self.freq * self._seconds):
            if not timestamp:
                timestamp = time.time()
            self._timelist.append(timestamp)
        self._size += 1

    def append_minmaxavg(self, minval, maxval, avg):
        self.data.append_minmaxavg(minval, maxval, avg)
        # add timestamp every second
        if not self._size % int(self.freq * self._seconds):
            self._timelist.append(timestamp)
        self._size += 1

    def sample_to_timeutc(self, sample_num):
        if not self._timelist:
            return 0.
        assert self._timelist
        tl = self._timelist
        timeindex = int(sample_num) / int(self.freq * self._seconds)
        if timeindex < 0:
            return 0.
        if timeindex >= len(tl) - 1:
            return tl[-1] + (sample_num - (len(tl) - 1) * int(self.freq * self._seconds)) / self.freq
        return tl[timeindex] + (tl[timeindex + 1] - tl[timeindex]) / int(self.freq * self._seconds) * \
                               (sample_num - int(self.freq * self._seconds) * timeindex)

    def value_to_rawvalue(self, value):
        """ map graph-coordinates (final values, unit values) to raw values in MapBuf. for example 1V to raw 255 """
        return self.value_min_raw + 1./ self._value_scale * value

    def rawvalue_to_value(self, rawvalue):
        """ inverse of value_to_rawvalue """
        return self.value_min + self._value_scale * rawvalue

    def sample_to_time(self, sample_num):
        """ return relative time of the sample from first append """
        return sample_num / self.freq

    def time_to_sample(self, time):
        """ convert relative time (beginning from first append) to sample num """
        return time * self.freq


if __name__ == "__main__":
    g = GraphChannel(100.)
    print "test done"