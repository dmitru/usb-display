
import time
import sys
import threading	

import usb_lcd_lib

class TimeDisplay(threading.Thread):

	WIDTH = 20
	DELAY_BETWEEN_UPDATES = 1

	def run(self):
		try:
			while self.is_running:
				self._update()
				time.sleep(TimeDisplay.DELAY_BETWEEN_UPDATES)
		finally:
				self._lcd.close()

	def stop(self):
		self.is_running = False

	def __init__(self, *args, **kargs):
		super().__init__()

		self._lcd = usb_lcd_lib.Lcd(*args, **kargs)
		self._lcd.clear()
		time.sleep(TimeDisplay.DELAY_BETWEEN_UPDATES)

		self.is_running = True

	def _update(self):
		ct = time.localtime()
		width = TimeDisplay.WIDTH
		date_line = '%d/%02d/%d' % (ct.tm_year, ct.tm_mon, ct.tm_mday)
		date_line = ' ' * ((width - len(date_line)) // 2) + date_line
		date_line += ' ' * (width - len(date_line))
		time_line = '%02d:%02d:%02d' % (ct.tm_hour, ct.tm_min, ct.tm_sec)
		time_line = ' ' * ((width - len(time_line)) // 2) + time_line
		time_line += ' ' * (width - len(time_line))
		self._lcd.move_cursor(1, 0)
		self._lcd.print(date_line)
		self._lcd.move_cursor(2, 0)
		self._lcd.print(time_line)
			

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Usage: %s <device filename>' % sys.argv[0])

	display = TimeDisplay(port=sys.argv[1], baudrate=19200)
	display.start()

	print('For exit, enter \'quit\' or \'exit\'...')

	user_input = input()
	while user_input.strip().lower() not in ['quit', 'exit', 'q']:
		user_input = input()

	display.stop()
