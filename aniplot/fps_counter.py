class FpsCounter:

    def __init__(self, update_interval_seconds = 0.5, print_log=False):
        """
        read self.fps for output. updated every update_interval_seconds.
        """

        self.fps = 0.
        self.interval = update_interval_seconds
        self.print_log = print_log

        self._counter = 0.
        self._age     = 0.

    def tick(self, dt):

        self._age     += dt
        self._counter += 1.

        if self._age > self.interval:
            self.fps = self._counter / self._age
            self._age     = 0.
            self._counter = 0.
            if self.print_log:
                print "fps:", self.fps

