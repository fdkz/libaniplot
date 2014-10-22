from PySide import QtGui

from aniplot_base import AniplotBase
from graph_channel import GraphChannel



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
        channel = GraphChannel(frequency=frequency, legend=legend, unit=unit, color=(r/255., g/255., b/255., a/255.,))
        channel.set_mapping(value_min=value_min, value_min_raw=value_min_raw, value_max=value_max, value_max_raw=value_max_raw)
        self.channels.append(channel)
        return channel

    def start(self):
        ''' Start drawing.
            If channels are setup call this method to begin plotting.
        '''
        self._start()