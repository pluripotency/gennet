import re
ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def rm_color(sometext):
    return ansi_escape.sub('', sometext)


coloring = lambda msg, num: '\033[%sm%s\033[0m' % (num, msg)
red          = lambda msg: coloring(msg, '00;31')
green        = lambda msg: coloring(msg, '00;32')
brown        = lambda msg: coloring(msg, '00;33')
blue         = lambda msg: coloring(msg, '00;34')
purple       = lambda msg: coloring(msg, '00;35')
cyan         = lambda msg: coloring(msg, '00;36')
white        = lambda msg: coloring(msg, '00;37')
light_red    = lambda msg: coloring(msg, '01;31')
light_green  = lambda msg: coloring(msg, '01;32')
yellow       = lambda msg: coloring(msg, '01;33')
light_blue   = lambda msg: coloring(msg, '01;34')
pink         = lambda msg: coloring(msg, '01;35')
light_cyan   = lambda msg: coloring(msg, '01;36')


def dummy_color(msg):
    return msg


def set_colors(self, enable=False):
    if enable:
        self.red          = red
        self.green        = green
        self.brown        = brown
        self.blue         = blue
        self.purple       = purple
        self.cyan         = cyan
        self.white        = white
        self.light_red    = light_red
        self.light_green  = light_green
        self.yellow       = yellow
        self.light_blue   = light_blue
        self.pink         = pink
        self.light_cyan   = light_cyan
    else:
        self.red          = dummy_color
        self.green        = dummy_color
        self.brown        = dummy_color
        self.blue         = dummy_color
        self.purple       = dummy_color
        self.cyan         = dummy_color
        self.white        = dummy_color
        self.light_red    = dummy_color
        self.light_green  = dummy_color
        self.yellow       = dummy_color
        self.light_blue   = dummy_color
        self.pink         = dummy_color
        self.light_cyan   = dummy_color
