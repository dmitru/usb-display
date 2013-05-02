
import serial
import time

class Lcd:

	INTER_BYTE_DELAY = 0.002
	NUMBER_OF_LINES = 4
	NUMBER_OF_COLUMNS = 20

	def __init__(self, *args, **kargs):
		self.serial = serial.Serial(*args, **kargs)
		self.line = 0
		self.pos = 0
		self.cursor_off()
		if not self.serial.isOpen():
			raise IOError

	def write(self, bs):
		for b in bs:
			self.serial.write(bytes([b]))
			self.pos += 1
			if self.pos >= Lcd.NUMBER_OF_COLUMNS:
				self.pos = 0
				self.line += 1
				if self.line >= Lcd.NUMBER_OF_LINES:
					self.line = 0
				self.move_cursor(self.line, self.pos)
				time.sleep(Lcd.INTER_BYTE_DELAY)
			time.sleep(Lcd.INTER_BYTE_DELAY)

	def print(self, s):
		self.write(s.encode('ascii'))

	def cmd(self, cmd):
		self.serial.write(bytes([0, cmd]))

	def move_cursor(self, line=0, pos=0):
		if line < 0 or line >= Lcd.NUMBER_OF_LINES:
			raise ValueError
		if pos < 0 or pos >= Lcd.NUMBER_OF_COLUMNS:
			raise ValueError
		self.cmd(128 + pos + [0, 64, 20, 84][line])
		self.line = line
		self.pos = pos

	def cursor_on(self):
		self.cmd(0b00001111)

	def cursor_off(self):
		self.cmd(0b00001100)

	def clear(self):
		self.pos = 0
		self.line = 0
		self.cmd(1)

	def close(self):
		self.serial.close()


