###################################
#   US TOP CITIES INFO            #
#   Collected from wikipedia and  #
#   city-data.com                 #
#                                 #
#         Houzhu Ding             #
#         5/24/2019               #
#  Implemented in Python 36       #
###################################

from tkinter  import *
import datetime
import io
# from PIL import Image ,ImageTk 
from us_top_cities_info import *


class App(object):
	
	def __init__(self,master):

		self._keywordHistory = []
		self.url_title_dict = {}
		self.city_list = {}
		self.wikicity = wikisearch(1)
		self.cleaned_field_extra_list  = {}

		self.L0 =Label(master, text="US Top Cities Infomation ",font=("Helvetica", 20)).grid(rowspan=2,columnspan=6)
		# self.LL0 = Label(master, text ="--------------------------").grid(rowspan=2,column = 1)

################## Number of search  ##############################

		nums_of_city_text = StringVar()
		nums_of_city_text.set("Numbers of cites to show (less than 300)")
		self.L2 = Label(master,textvariable =nums_of_city_text)
		self.L2.grid(row = 4,column = 0,padx=15, pady=5,sticky=W)
		
		nums_of_city = StringVar(None)
		nums_of_city.set("100")
		self.EntryBoxNum = Entry(master,textvariable = nums_of_city )
		self.EntryBoxNum.grid(row = 4,column = 1,padx=15, pady=5)

#################### Start search Button ##############################

		self.com = Button(master,text = 'Start Search',command = self.search)
		self.com.grid(row = 9,column = 1)       
#################### Process Button ##############################
##      
		# self.inputCount = 0
		# self.save = Button(master,text = 'Process',command = self.save_city_info)
		# self.save.grid(row = 9,column = 2)  

#################### City name  ##############################
		city_data_text = StringVar()
		city_data_text.set("City Names ")
		self.L2 = Label(master,textvariable =city_data_text)
		self.L2.grid(row = 10,column = 0,padx=15, pady=5,sticky=W) 
#################### City list ##############################
		city_data_text = StringVar()
		city_data_text.set("City Data ")
		self.L2 = Label(master,textvariable =city_data_text)
		self.L2.grid(row = 10,column = 1,padx=15, pady=5,sticky=W) 
#################### Show city list ##############################

		self.city_name_list = Listbox(master,width = 30, height = 30)
		self.city_name_list.grid(row = 11,column=0,columnspan =  1)
		# self.city_name_list.bind("<Double-Button-1>", self.doubleClick)
		self.city_name_list.bind("<<ListboxSelect>>",self.oneClickListSel)

		self.city_fields_listbox = Listbox(master,width = 40, height = 30)
		self.city_fields_listbox.grid(row = 11,column=1,columnspan =  1)

		self.scrollb = Scrollbar(self.city_name_list, orient="vertical")

#################### Show some images   ##############################
	# used to visualize some field name after double click the data..
	# for future development
		self.w = Canvas(master, width=200, height=400,bg="white")
		self.w.grid(row = 11,column = 2,columnspan = 1,sticky=W+E+N+S)

		return
	def search(self,):
		self.w.delete("all") 
		self.city_name_list.delete(0,END)
		city_num = float(self.EntryBoxNum.get())

		self.wikicity = wikisearch(city_num)
		### Get city data from wikipedia (summary page and individual page) and city-data.com ###
		self.wikicity.start_collecting_city_data()
		self.city_list = self.wikicity.city_list
		self.city_list_table_head_save = self.wikicity.table_heads+self.wikicity.table_heads_extra
			
		population = []
		for key in self.city_list:
			# get population
			population.append(self.city_list[key]['Population 2018 estimate'])
			count = int(self.city_list[key]['Population 2018 rank'])
			insertText = str(count)+":"+key
			self.city_name_list.insert(count,insertText)

		self.city_list_citydata = self.wikicity.city_list_citydata
		self.city_list_table_head_save = self.wikicity.city_list_table_head_save

	def oneClickListSel(self,evt):
		# when click on the city name show the extracted basic fields
		self.city_fields_listbox.delete(0,END)
		widget = evt.widget
		selection=widget.curselection()
		try:
			_value = widget.get(selection[0])
			city_name = _value.split(':')[1]
			city_fields = self.city_list[city_name]
			count=0
			for idx in city_fields:
				# print(idx,city_fields[0][idx])
				count +=1
				city_info = idx+":"+ city_fields[idx]
				self.city_fields_listbox.insert(count,city_info)
		except Exception as e:
			print("No item to be selected!")
			# raise
			pass
		else:
			pass
		finally:
			pass

	def doubleClick(self,evt):
		pass

root = Tk()
root.title('Collect US City Data --by Houzhu Ding (dinghouzhu@gmail.com)')
root.geometry('800x700')
app = App(root)
root.mainloop()