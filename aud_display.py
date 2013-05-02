
import time
import subprocess
import sys
import threading	

import usb_lcd_lib

class AudaciousDisplay(threading.Thread):

	WIDTH = 20
	SCROLL_CNT_MAX = 1
	SCROLL_CNT_ENDS_MAX = 10
	DELAY_BETWEEN_UPDATES = 0.1

	def run(self):
		try:
			while self.is_running:
				self._update()
				time.sleep(AudaciousDisplay.DELAY_BETWEEN_UPDATES)
		finally:
				self._lcd.close()

	def stop(self):
		self.is_running = False

	def __init__(self, *args, **kargs):
		super().__init__()

		self._lcd = usb_lcd_lib.Lcd(*args, **kargs)
		self._lcd.clear()

		self._status = ''
		self._status_prev = None
		self._band = ''
		self._band_prev = None
		self._album = ''
		self._album_prev = None
		self._title = ''
		self._title_prev = None

		self._status_line = ''
		self._status_line_prev = None
		self._band_line = ''
		self._band_line_prev = None
		self._album_line = ''
		self._album_line_prev = None
		self._title_line = ''
		self._title_line_prev = None

		self._band_scroll_offset = 0
		self._band_scroll_dir = 1
		self._band_scroll_cnt = 0
		self._album_scroll_offset = 0
		self._album_scroll_dir = 1
		self._album_scroll_cnt = 0
		self._title_scroll_offset = 0
		self._title_scroll_dir = 1
		self._title_scroll_cnt = 0

		self.is_running = True

	def _update(self):
		self._get_song_info()
		self._update_display_text()
		self._write_on_display()

	def _get_song_info(self):

		self._status_prev = self._status
		self._band_prev = self._band
		self._album_prev = self._album
		self._title_prev = self._title

		self._status = subprocess.check_output('audtool playback-status', \
			shell=True).decode('ascii').strip()
		info = subprocess.check_output('audtool current-song', \
			shell=True).decode('ascii').strip()
		if info == 'No song playing.':
			info = ['No song', 'playing :(', '']
		else:
			info = info.split(' - ')
		if len(info) < 3:
			info += [''] * (3 - len(info))
		elif len(info) > 3:
			info = info[:3]
		self._band, self._album, self._title = info

		# If song info has changed, unscroll the lines and 
		# set scrolling values to default
		if self._band_prev != self._band or self._album_prev != self._album \
			or self._title != self._title_prev:
			self._band_scroll_offset = 0
			self._band_scroll_dir = 1
			self._band_scroll_cnt = 0
			self._album_scroll_offset = 0
			self._album_scroll_dir = 1
			self._album_scroll_cnt = 0
			self._title_scroll_offset = 0
			self._title_scroll_dir = 1
			self._title_scroll_cnt = 0

	def _update_display_text(self):
		width = AudaciousDisplay.WIDTH

		self._status_line_prev = self._status_line
		self._band_line_prev = self._band_line
		self._album_line_prev = self._album_line
		self._title_line_prev = self._title_line

		self._status_line = '* ' + self._status[: width] + ' *'
		offset = self._band_scroll_offset
		self._band_line = self._band[offset : offset + width]
		offset = self._album_scroll_offset
		self._album_line = self._album[offset : offset + width]
		offset = self._title_scroll_offset
		self._title_line = self._title[offset : offset + width]

		if len(self._band) < width:
		# If the line is shorter than display, complete it with spaces to
		# print it in the center of the display
			self._band_line = ' ' * ((width - len(self._band_line)) // 2) + self._band_line
			self._band_line += ' ' * (width - len(self._band_line))
		elif len(self._band) > width:
		# If the line is too long, track the scrolling parameters and scroll 
		# the line back and forth
			if self._band_scroll_offset == 0 or self._band_scroll_offset == len(self._band) - width:
				if self._band_scroll_cnt > AudaciousDisplay.SCROLL_CNT_ENDS_MAX:
					self._band_scroll_cnt = 1
					self._band_scroll_offset += self._band_scroll_dir
					if self._band_scroll_offset == 0 or self._band_scroll_offset == len(self._band) - width:
						self._band_scroll_dir *= -1
				else:
					self._band_scroll_cnt += 1
			else:
				if self._band_scroll_cnt > AudaciousDisplay.SCROLL_CNT_MAX:
					self._band_scroll_cnt = 1
					self._band_scroll_offset += self._band_scroll_dir
					if self._band_scroll_offset == 0 or self._band_scroll_offset == len(self._band) - width:
						self._band_scroll_dir *= -1
				else:
					self._band_scroll_cnt += 1
			

		if len(self._album_line) < width:
			self._album_line = ' ' * ((width - len(self._album_line)) // 2) + self._album_line
			self._album_line += ' ' * (width - len(self._album_line))
		elif len(self._album) > width:
		# If the line is too long, track the scrolling parameters and scroll 
		# the line back and forth
			if self._album_scroll_offset == 0 or self._album_scroll_offset == len(self._album) - width:
				if self._album_scroll_cnt > AudaciousDisplay.SCROLL_CNT_ENDS_MAX:
					self._album_scroll_cnt = 1
					self._album_scroll_offset += self._album_scroll_dir
					if self._album_scroll_offset == 0 or self._album_scroll_offset == len(self._album) - width:
						self._album_scroll_dir *= -1
				else:
					self._album_scroll_cnt += 1
			else:
				if self._album_scroll_cnt > AudaciousDisplay.SCROLL_CNT_MAX:
					self._album_scroll_cnt = 1
					self._album_scroll_offset += self._album_scroll_dir
					if self._album_scroll_offset == 0 or self._album_scroll_offset == len(self._album) - width:
						self._album_scroll_dir *= -1
				else:
					self._album_scroll_cnt += 1

		if len(self._title_line) < width:
			self._title_line = ' ' * ((width - len(self._title_line)) // 2) + self._title_line
			self._title_line += ' ' * (width - len(self._title_line))
		elif len(self._title) > width:
		# If the line is too long, track the scrolling parameters and scroll 
		# the line back and forth
			if self._title_scroll_offset == 0 or self._title_scroll_offset == len(self._title) - width:
				if self._title_scroll_cnt > AudaciousDisplay.SCROLL_CNT_ENDS_MAX:
					self._title_scroll_cnt = 1
					self._title_scroll_offset += self._title_scroll_dir
					if self._title_scroll_offset == 0 or self._title_scroll_offset == len(self._title) - width:
						self._title_scroll_dir *= -1
				else:
					self._title_scroll_cnt += 1
			else:
				if self._title_scroll_cnt > AudaciousDisplay.SCROLL_CNT_MAX:
					self._title_scroll_cnt = 1
					self._title_scroll_offset += self._title_scroll_dir
					if self._title_scroll_offset == 0 or self._title_scroll_offset == len(self._title) - width:
						self._title_scroll_dir *= -1
				else:
					self._title_scroll_cnt += 1

		if len(self._status_line) < width:
			self._status_line = ' ' * ((width - len(self._status_line)) // 2) + self._status_line
			self._status_line += ' ' * (width - len(self._status_line))

	def _write_on_display(self):
		if self._status_line != self._status_line_prev:
			self._lcd.move_cursor(0)
			self._lcd.print(self._status_line)
		self._status_line_prev = self._status_line
			
		if self._band_line != self._band_line_prev:
			self._lcd.move_cursor(1)
			self._lcd.print(self._band_line)
		self._band_line_prev = self._band_line
		
		if self._album_line != self._album_line_prev:
			self._lcd.move_cursor(2)
			self._lcd.print(self._album_line)
		self._album_line_prev = self._album_line
		
		if self._title_line != self._title_line_prev:
			self._lcd.move_cursor(3)
			self._lcd.print(self._title_line)
		self._title_line_prev = self._title_line

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Usage: %s <device filename>' % sys.argv[0])

	display = AudaciousDisplay(port=sys.argv[1], baudrate=19200)
	display.start()

	print('For exit, enter \'quit\' or \'exit\'...')

	user_input = input()
	while user_input.strip().lower() not in ['quit', 'exit', 'q']:
		user_input = input()

	display.stop()
