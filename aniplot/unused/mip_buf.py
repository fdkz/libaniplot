class MipBufEntry:
    def __init__(self, minval, maxval, avg):
        self.minval = minval
        self.maxval = maxval
        self.avg    = avg


class MipBuf:
    def __init__(self):
        self.buf = []
        self.child = None

    def append(self, minval, maxval, avg):
        self.buf.append(MipBufEntry(minval, maxval, avg))
        if len(self.buf) & 1 == 0:
            if not self.child:
                self.child = MipBuf()
            e1, e2 = self.buf[-2], self.buf[-1]
            self.child.append(min(e1.minval, e2.minval), max(e1.maxval, e2.maxval), (e1.avg + e2.avg) / 2.)

    def get_buf(self, start_index, end_index, resolution):
        """
        return:
            buf, start_pixel, start_index, end_pixel, end_index
            incoming indices can be out of bounds.
            end_index : one past last
        """
        index_range = end_index - start_index
        i_end = min(len(self.buf), end_index)
        i_start = max(0, start_index)
        start_pixel = float(i_start - start_index) / (end_index - start_index) * resolution
        end_pixel = resolution - float(end_index - i_end) / (end_index - start_index) * resolution

        entries_per_pixel = (end_index - start_index) / resolution
        if entries_per_pixel >= 2.:
            # too much resolution. get child buf.
            return self.child.get_buf(start_index // 2, end_index // 2, resolution)
        else:
            return self.buf, start_pixel, i_start, end_pixel, i_end

