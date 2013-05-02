/*
 * usb_lcd_display.asm
 *
 *  Created: 08.04.2013 10:52:13
 *   Author: dmitriy.borodiy@mail.com
 */ 

 /************** Global vars *****************/
 .equ LCD_DATA_PORT = PORTC
 .equ LCD_DATA_DDR = DDRC
 .equ LCD_DATA_PIN = PINC
 .equ LCD_CONTROL_PORT = PORTA
 .equ LCD_CONTROL_DDR = DDRA
 .equ LCD_A0 = 0b00000001
 .equ LCD_RW = 0b00000010
 .equ LCD_E = 0b00000100
 .equ LCD_BS = 7
 /********************************************/


 /************* Interrupt vector *************/
 .org 0x000
 rjmp init
 .org 0x00b
 rjmp uart_rx
 /********************************************/

delay_16ms:
	push r18
	push r19
    ldi  r18, 16
    ldi  r19, 149
L11: 
	dec  r19
    brne L11
    dec  r18
    brne L11
	pop r19
	pop r18
	ret

delay_40us:
	push r18
	ldi  r18, 106
L12: 
	dec  r18
    brne L12
    rjmp PC+1
	pop r18
	ret


/************ Called at power up *************/
 init:
/* Init the command register */
	clr r21
/* Stack init */
	ldi r16, high(RAMEND)
	out SPH, r16
	ldi r16, low(RAMEND)
	out SPL, r16
/* LCD screen init */
	rcall lcd_init
	rcall delay_16ms
/* Set the cursor at the beginning of first line */
	ldi r18, 0x01
	rcall lcd_write_cmd
/* USART init */
	rcall usart_init
/* Enable global interrupts */
	sei
/* Enter the endless loop */
loop:
	rjmp loop
/*********************************************/


/*************** Init USART ******************/
usart_init:
/* Set the baud rate at 19200 */
	ldi r16, low(25)
	out UBRRL, r16
	ldi r16, high(25)
	out UBRRH, r16
/* Enable RX and TX and TX interrupt*/ 
	ldi r16, 0b10011000
	out UCSRB, r16
	ldi r16, (1<<URSEL)|(1<<UCSZ0)|(1<<UCSZ1)
	out UCSRC, r16
	ret
/*********************************************/


/************** Init LCD screen **************/
lcd_init:
	/* Set LCD ports to output */
	ldi r16, 0xFF
	out LCD_DATA_DDR, r16
	ldi r16, 0x00
	out LCD_DATA_PORT, r16
	ldi r16, 0b00000111
	out LCD_CONTROL_DDR, r16
	//ldi r16, 0x00
	//out LCD_CONTROL_PORT, r16
	/* Enable access to the LCD module */
	in r16, LCD_CONTROL_PORT
	sbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	/* Delay 20 ms */
	ldi  r18, 208
    ldi  r19, 202
L1: dec  r19
    brne L1
    dec  r18
    brne L1
    /* Set up the interface type (8-bit) */
	in r16, LCD_CONTROL_PORT
	cbr r16, LCD_RW
	cbr r16, LCD_A0
	out LCD_CONTROL_PORT, r16
	ldi r16, 0x30 
	out LCD_DATA_PORT, r16
	/* Get the display in normal mode */
	nop
	nop
	nop
	/* Set E flag */
	in r16, LCD_CONTROL_PORT
	sbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	nop
	nop
	nop
	nop
	/* Clear E flag */
	in r16, LCD_CONTROL_PORT
	cbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	ldi  r18, 106
L4: dec  r18
    brne L4
	/* Set E flag */
	in r16, LCD_CONTROL_PORT
	sbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	nop
	nop
	nop
	nop
	/* Clear E flag */
	in r16, LCD_CONTROL_PORT
	cbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	ldi  r18, 106
L5: dec  r18
    brne L5
	/* Set E flag */
	in r16, LCD_CONTROL_PORT
	sbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	nop
	nop
	nop
	nop
	/* Clear E flag */
	in r16, LCD_CONTROL_PORT
	cbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	ldi  r18, 106
L6: dec  r18
    brne L6
	/* Now it's ready to accept commands */
	/* Set up the right LCD working mode */
	ldi r18, 0x38
	rcall lcd_write_cmd
	rcall delay_40us
	/* Turn on the display, turn on the cursor */
	ldi r18, 0x0F
	rcall lcd_write_cmd
	rcall delay_40us
	/* Clear the display */
	ldi r18, 0x01
	rcall lcd_write_cmd
	rcall delay_16ms
	/* Set data input mode */
	ldi r18, 0x06
	rcall lcd_write_cmd
	rcall delay_40us
	ret
/*********************************************/	

/** 
* Write a byte to LCD data port. 
* The byte is passed in r18 register.
* If register 19 is 0, write command, otherwise
* write data byte.
*/
lcd_write_byte:
	/* Set LCD data port to input */
	ldi r16, 0x00
	out LCD_DATA_DDR, r16
	ldi r16, 0x00
	out LCD_DATA_PORT, r16
	/* Read the busy flag BS */
	in r16, LCD_CONTROL_PORT
	sbr r16, LCD_RW
	cbr r16, LCD_A0
	out LCD_CONTROL_PORT, r16
	nop
	/* Set E flag */
	in r16, LCD_CONTROL_PORT
	sbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	ldi  r16, 106
L7: dec  r16
    brne L7
	/* Clear E flag */
	in r16, LCD_CONTROL_PORT
	cbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	ldi  r16, 106
L8: dec  r16
    brne L8
	/* Set LCD data port to output */
	ldi r16, 0xFF
	out LCD_DATA_DDR, r16
	in r16, LCD_CONTROL_PORT
	cbr r16, LCD_RW
	/* Select between command and data */
	cbr r16, LCD_A0
	tst r19
	breq L3
	sbr r16, LCD_A0
L3:
	out LCD_CONTROL_PORT, r16
	/* Output the byte */
	out LCD_DATA_PORT, r18
	/* Set E flag */
	in r16, LCD_CONTROL_PORT
	sbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	ldi  r16, 106
L9: dec  r16
    brne L9
	/* Clear E flag */
	in r16, LCD_CONTROL_PORT
	cbr r16, LCD_E
	out LCD_CONTROL_PORT, r16
	ldi  r16, 106
L10: dec  r16
    brne L10
	ret

lcd_write_cmd:
	ldi r19, 0x00
	rcall lcd_write_byte
	rcall delay_16ms
	ret

lcd_write_data:
	ldi r19, 0x01
	rcall lcd_write_byte
	rcall delay_16ms
	ret
/*********************************************/	


/********** Called at byte received **********/
uart_rx:
	in r16, UDR
	tst r21
	breq after_data_byte
	mov r18, r16
	rcall lcd_write_cmd
	clr r21
	rjmp uart_rx_end
after_data_byte:
	tst r16
	brne data_byte_arrived
	// Zero incoming byte indicates the beginning 
	// a command 
	ser r21
	rjmp uart_rx_end
data_byte_arrived:
	mov r18, r16
	rcall lcd_write_data 
uart_rx_end:
	reti
/*********************************************/	
