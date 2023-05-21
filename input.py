n=int(input("Enter The Number Of Words"))
data=[]
for i in range(n):
	k=input("")
	data.append(k)

file = open("input.txt", "w")

for line in data:
    file.write(line + "\n")
    
file.close()