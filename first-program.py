name = input("enter your name: ")
print("hello "+name) #concatenation
print(f"hello, {name}")  #string formatting
#while True:
#    try:
#        age = int(input("enter your age: "))
        #operators
        # == equals to
        # != not equals to
        # > greater than
        # <less than
        # >= greater than or equals to
        # <= less than or equals to
        # logical operators
        # and, or, not
        # if, elif, else
        
#        if age < 16:
#            print("you are a minor")
#        elif age > 60:
#            print("you are elderly")
#        else:
#            print("you are eligible to work")
#            print(type(age)) #type of variable
#            print("age is: ",int(age))
#        print(f"your age is: {age}")
#    except:
#        print("please give numbers")
#    run = input("do you want to continue??(y/n)\n")
#    if run == "n":
#        break
for i in range(2,6,2):
    try:
        age = int(input("enter your age: "))
        if age < 16:
            print("you are a minor")
        elif age > 60:
            print("you are elderly")
        else:
            print("you are eligible to work")
            print(type(age)) #type of variable
            print("age is: ",int(age))
        print(f"your age is: {age}")
    except:
        print("please give numbers")

 