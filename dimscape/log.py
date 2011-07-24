import logging as l
import logging.handlers as h

initted = False

def initLog(level=l.DEBUG):
	global initted
	if not initted:
		initted = True
		root = l.getLogger()
		root.setLevel(level)
		errHandler = h.SysLogHandler("/dev/log")
		errHandler.setLevel(l.ERROR)
		f = l.Formatter("%(name)s [%(module)s/%(funcName)s/%(lineno)d] %(levelname)s: %(message)s")
		errHandler.setFormatter(f)
		root.addHandler(errHandler)
		othHandler = l.StreamHandler()
		othHandler.setFormatter(l.Formatter(l.BASIC_FORMAT))
		othHandler.setLevel(level)
		root.addHandler(othHandler)
