STORE_FILE = 'store.dat'


class Configparser:

    def __init__(self):
        try:
            with open(STORE_FILE) as f:
                lines = f.readlines()
        except:
            lines = []
        self.lines = lines

    def _line_strip(self, line):
        return line.strip("\n").split("=")

    def _write(self, lines):
        with open(STORE_FILE, "w") as f:
            f.write(''.join(lines))
        self.lines = lines

    def get(self, key, default=None):
        for line in self.lines:
            k, v = self._line_strip(line)
            if k == key:
                return v
        return default

    def set(self, key, value):
        lines2 = []
        for line in self.lines:
            k, v = self._line_strip(line)
            if k == key:
                lines2.append("%s=%s\n" % (key, value))
            else:
                lines2.append(line)
        is_update = 0
        for line in lines2:
            k, v = self._line_strip(line)
            if k == key:
                is_update = 1
                break
        if is_update == 0:
            lines2.append("%s=%s\n" % (key, value))

        self._write(lines2)

    def delete(self, key):
        lines2 = []
        for line in self.lines:
            k, v = self._line_strip(line)
            if k != key:
                lines2.append(line)

        self._write(lines2)

