import os

try:
    os.mkdir("output")
    print("Created '/output")
        
except:
    print("Could not create '/output'")

try:
    os.mkdir("input")
    print("Created '/input'")
        
except:
    print("Could not create '/input'")

try:
    os.mkdir("models")
    print("Created '/models'")
        
except:
    print("Could not create '/models'")


os.chdir(os.getcwd()+'/models')
