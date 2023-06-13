from ctypes import cdll, c_char_p

# Load the Objective-C library
lib = cdll.LoadLibrary("./hello.dylib")

# Define the Objective-C function prototype
lib.getHelloMessage.restype = c_char_p

# Call the Objective-C function
hello_message = lib.getHelloMessage()

print(type(hello_message))

print(hello_message.decode("utf-8"))
