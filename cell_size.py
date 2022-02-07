from tkinter import *

root = Tk()

root.title("Calculator")


def equals():
    global current_operation
    global stored_val

    current_val = enter.get()

    ##logic here
    if current_operation == "add":
        result = float(stored_val) + float(current_val)
    elif current_operation == "subtract":
        result = float(stored_val) - float(current_val)
    elif current_operation == "multiply":
        result = float(stored_val) * float(current_val)
    elif current_operation == "divide":
        result = float(stored_val) / float(current_val)
    elif current_operation == "power":
        result = float(stored_val) ** float(current_val)
    enter.delete(0, END)
    enter.insert(0, result)


def enter_number(number):
    global current_operation
    global stored_val

    current = enter.get()
    enter.delete(0, END)
    enter.insert(0, str(current) + str(number))

def add_number():
    global current_operation
    global stored_val

    stored_val = enter.get()
    current_operation = "add"
    enter.delete(0, END)

def multiply_number():
    global current_operation
    global stored_val

    stored_val = enter.get()
    current_operation = "multiply"
    enter.delete(0, END)

def divide_number():
    global current_operation
    global stored_val

    stored_val = enter.get()
    current_operation = "divide"
    enter.delete(0, END)

def power_number():
    global current_operation
    global stored_val

    stored_val = enter.get()
    current_operation = "power"
    enter.delete(0, END)

def subtract_number():
    global current_operation
    global stored_val

    stored_val = enter.get()
    current_operation = "subtract"
    enter.delete(0, END)




#Makr Objects
enter = Entry(root)
button1 = Button(root, text="1", padx=40, pady=20, command=lambda: enter_number(1))
button2 = Button(root, text="2", padx=40, pady=20, command=lambda: enter_number(2))
button3 = Button(root, text="3", padx=40, pady=20, command=lambda: enter_number(3))
button4 = Button(root, text="4", padx=40, pady=20, command=lambda: enter_number(4))
button5 = Button(root, text="5", padx=40, pady=20, command=lambda: enter_number(5))
button6 = Button(root, text="6", padx=40, pady=20, command=lambda: enter_number(6))
button7 = Button(root, text="7", padx=40, pady=20, command=lambda: enter_number(7))
button8 = Button(root, text="8", padx=40, pady=20, command=lambda: enter_number(8))
button9 = Button(root, text="9", padx=40, pady=20, command=lambda: enter_number(9))
button0 = Button(root, text="0", padx=40, pady=20, command=lambda: enter_number(0))


button_clear = Button(root, text="Clear", padx=72, pady=20)
button_plus = Button(root, text="+", padx=40, pady=20, command=add_number)
button_equals = Button(root, text="=", padx=85, pady=20, command=equals)
button_minus = Button(root, text="-", padx=40, pady=20, command= subtract_number)
button_multiply = Button(root, text="*", padx=40, pady=20, command= multiply_number)
button_divide = Button(root, text="/", padx=40, pady=20, command= divide_number)
button_power = Button(root, text="^", padx=40, pady=20, command= power_number)


#Place Objects
button7.grid(column = 0, row = 1)
button8.grid(column = 1, row = 1)
button9.grid(column = 2, row = 1)

button4.grid(column = 0, row = 2)
button5.grid(column = 1, row = 2)
button6.grid(column = 2, row = 2)

button1.grid(column = 0, row = 3)
button2.grid(column = 1, row = 3)
button3.grid(column = 2, row = 3)

button_clear.grid(column = 0, row = 4, columnspan=2)
button_plus.grid(column = 2, row = 4)

button_equals.grid(column = 0, row = 5, columnspan=2)
button_minus.grid(column = 2, row = 5)

button_multiply.grid(column = 0, row = 6)
button_divide.grid(column = 1, row = 6)
button_power.grid(column = 2, row = 6)


enter.grid(column = 0 , row = 0, columnspan=3, pady=20)


root.mainloop()