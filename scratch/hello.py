import os
import platform
import sys
 
print("Hello from inside the sandbox!")
print("Python:", sys.version.split()[0])
print("User id:", os.getuid())
print("Working dir:", os.getcwd())
print("Files visible here:", sorted(os.listdir(".")))
print("Hostname:", platform.node())