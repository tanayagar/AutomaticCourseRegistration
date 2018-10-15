import pandas as pd

def register(my_clas, df,reg,clashes):
	for i in range(0,clas.shape[0]):
		# global_i stores the position of record in the dataframe
		global global_i
		global_i = i
		# credit stores the credits registered
		global credit

		# Check if requested cours exists
		if (my_clas['cid']==df.loc[i,'cid'] and my_clas['slot']==df.loc[i,'slot'] and my_clas['faculty'] == df.loc[i,'faculty'] and my_clas['ctype']==df.loc[i,'ctype']):
			# Check if seats are left
			if(df.loc[i,'seats'] == 0):
				print("\n Seats Full")
				return 0
			
			# Check if credits are full
			if( credit +df.loc[i,'creds']>27):
				print("\n Maximum Credits Registered")
				return 0
			
			slotList=[]

			# Find the slots already full
			for key, value in reg.items():
				slotList.append(value['slot'])
			print("\n*** CURRENT SLOTS ***\n",slotList)

			# Check if Course slot is empty and does not clash
			if (my_clas['ctype']=='T' and my_clas['slot'] not in slotList):
				for i in range(0,clashes.shape[0]):
					if clashes.loc[i,'tslot'] == my_clas['slot'] and clashes.loc[i,'lslot'] in slotList:
						return 0
				credit = credit +df.loc[global_i,'creds']
				return 1

			if (my_clas['ctype']=='L' and my_clas['slot'] not in slotList):
				for i in range(0,clashes.shape[0]):
					if clashes.loc[i,'lslot'] == my_clas['slot'] and clashes.loc[i,'tslot'] in slotList:
						return 0
				credit = credit + df.loc[global_i,'creds']
				return 1

# Select important data from dict
def put_in(values):
	new = {}
	new['cid']=values['cid']
	new['slot']=values['slot']
	new['faculty']=values['faculty']
	new['ctype']=values['ctype']
	new['creds']=values['creds']
	return new

# Check the sam course already exists
def check(val,reg):
	for key,values in reg.items():
		if (values['cid'] == val['cid'] and values['ctype']==val['ctype']):
			return 0
	return 1

# Find alternate slots for any course that is not registered
def findalt(failed_clas,df, reg, clashes):
	sub = df['cid'] == failed_clas['cid']
	
	# Create a list of all alternate slots of the course
	if (failed_clas['ctype']=='T'):
		th = df['ctype'] == 'T'
		otherSlots = df[sub & th]
		
	if (failed_clas['ctype']=='L'):
		lb = df['ctype'] == 'L'
		otherSlots = df[sub & lb]

	other_slots_dict = otherSlots.to_dict(orient='records')
	#print(other_slots_dict)
	# Register the course
	for values in other_slots_dict:
		if(check(values,reg) and register(values,df,reg,clashes)):
			clas.loc[global_i,'seats']=clas.loc[global_i,'seats'] - 1;
			reg[str(clas.loc[global_i,'classno'])]=put_in(values)
			print("\n\tPASS 2: Registered (alternate Slot)\n\t",put_in(values))



# Input the tables
courses = pd.read_csv("course_list.csv")
classes = pd.read_csv("classes.csv")
clashes = pd.read_csv("clashes.csv")

# Find the dimensions of the dataframes
courses_rows = courses.shape[0]
courses_cols = courses.shape[1]

classes_rows = classes.shape[0]
classes_cols = classes.shape[1]

# Perfrom a full outer joim
clas = pd.merge(classes,courses,on='cid')

credit = 0
reg ={}
fail ={}

# Input for the program ( courses that need to be registered)
wishlist = {'R1' : {'cid':'CSE4001','slot':'A2','faculty':'Kumar R','ctype':'T','creds':3},
			'R2' : {'cid':'CSE4001','slot':'L31','faculty':'Jani','ctype':'L','creds':1},
			'R3' : {'cid':'CSE4011','slot':'D1','faculty':'Kumar R','ctype':'T','creds':4},
			'R4' : {'cid':'CSE4020','slot':'G1','faculty':'Syed ibrahim','ctype':'T','creds':3},
			'R5' : {'cid':'CSE4020','slot':'L27','faculty':'Nayemullah','ctype':'L','creds':1},
			'R6' : {'cid' :'CSE4019','slot':'E1','faculty':'G Malathy','ctype':'T','creds':4},
			'R7' : {'cid' :'CSE3024','slot':'F1','faculty':'VishnuPriya','ctype':'T','creds':3},
			'R8' : {'cid' :'CSE3024','slot':'L45','faculty':'Sridhar','ctype':'L','creds':1}}

# REGISTER FOR PASS 1 => Register in order skip what ever clashes
for key,values in wishlist.items():
	# Check if course can be registered
	if (register(values,clas,reg,clashes)):
		# Update table if registered
		clas.loc[global_i,'seats']=clas.loc[global_i,'seats'] - 1;
		reg[str(clas.loc[global_i,'classno'])]=values
		print("\nPASS 1: Registered  (from wishlist)\n",values)
	else:
		# If failed, try to find alternate slots
		fail[str(clas.loc[global_i,'classno'])]=values
		print("\nPASS 1: Failed (from wishlist)\n",values)
		findalt(values,clas,reg,clashes)

# REGISTER FOR PASS 2 => Register other slots of classes that clashed
if ( not fail == {}):
	#print (fail)
	for key,values in fail.items():
		findalt(values,clas,reg,clashes)

# REGISTER FOR PASS 3 => Remove incompletely registered courses
lst={}
# Find the credits registered for each course
for key,values in reg.items():
	if values['cid'] in lst:
		lst[values['cid']]+=values['creds']
	else:
		lst[values['cid']]=values['creds']
rml=[]
# Find the courses with complete registration
for key, values in reg.items():
	bool_value=lst[values['cid']] == clas[clas['classno']==int(key)]['credits']
	if(bool_value.iloc[0]==False):
		print("\nDeleted Course",values['cid'],"due to incomplete Registration\n")
		credit=credit-values['creds']
		rml.append(key)
for i in rml:
	del reg[key]

# Convert Dictionary to DataFrame

reg=pd.DataFrame.from_dict(reg)
wls=pd.DataFrame.from_dict(wishlist)

print("\n*** Registered ***\n")
print(reg)
print("\n*** Wishlist ***\n")
print(wls)
print("\n")
print("\n*** Credits Registered : ",credit," ***\n")
b=input("Update Dataset ? ")

# Export Registerd courses to html
if(b=='y'):
	updt=clas[['classno','slot','cid','faculty','ctype','seats']]
	updt.to_csv('classes.csv', mode='w', header=True)

	reg_cont = reg.to_html()
	with open("registered.html", "a") as f:
		f.write("</h3>Registered List </h3>")
		f.write(reg_cont)
else:
	print("Discarded\n")