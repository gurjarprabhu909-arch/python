# Creating a new file

# #1.) mode - x - creates a file
# open("diwali.txt","r")

# #2.) mode - w - Creates a file and you can write inside that file
# file = open("navratri.txt","w")

# file.write("din bhar padhai karo chill karo job lag jaye gi")

# file = open("navratri.txt","a")

# file.write("\npresentation acchi rakho ho jaye gaa")

# file.close()

# # deleting the file
# from pathlib import Path
# import os  
# p = Path("navratri.txt")
# os.remove(p)


"""Another way of opening and working with a file"""

# with open("diwali.txt","a") as fs:
#     fs.write("hello how are you")


print("press 1 - for creating a folder ")
print("press 2 - for reading a folder ")
print("press 1 - for updating a folder ")
print("press 1 - for deleting a folder ")
print("press 1 - for creating a file ")
print("press 1 - for reading a file ")
print("press 1 - for updating a file ")
print("press 1 - for deleting a file ")