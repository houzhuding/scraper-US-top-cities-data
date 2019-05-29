"""
US cities information from wikipedia and city-data.com
The final format should be a CSV file that is ready to be uploaded 
to a BigQuery table. The fields collected from those data sources
after cleanning are: (Total 21 fields)

['Population 2018 rank','Name','State','Population 2018 estimate','Population 2010 census',
'Change(%,2010-2018)','Land area 2016(sqmi)','Land area 2016(km2)','Population density 2016(sqmi)',
'Population density 2016(km2)','Location(N,W)','Elevation','Mayor','Time zone','Website','Area code','Demonym',
'Male-female percentage','Median household income','Mean_housing_price','Living index']

The city number has upper limit of 314 based on the original wikipedia page
However, as city numbers go over 100, the usage of google-search api is not stable (will be blocked)
So here the safe city number is 114 so far...

The city data is saved as csv format file (actually US_cities.txt, with comma seperated),
This file has been tested to be uploaded to goolge BigQuery.

5/24/2019

Houzhu Ding
"""
import re
import csv
import time
import requests
from bs4 import BeautifulSoup
from googlesearch import search 

class wikisearch():
	def __init__(self,city_num):
		# define a list of initial parameters
		self.city_num = city_num
		self.city_list = {}
		self.table_heads = ['Population 2018 rank','Name','State','Population 2018 estimate','Population 2010 census',
						'Change(%,2010-2018)','Land area 2016(sqmi)','Land area 2016(km2)','Population density 2016(sqmi)',
						'Population density 2016(km2)','Location(N,W)']
		# extra city info
		self.city_field_extra_dict = {}	

		# get all the extra field names and cluster them by character frequency
		self.table_heads_extra = ['Elevation','Mayor','Time zone','Website','Area code','Demonym']
		self.similarity_threshold = 0.5

		# get city info from city-data.com
		self.city_list_citydata = {}
		self.city_list_table_head_citydata = ['male-female percentage','median household income','mean_housing_price','living index']

		self.city_list_table_head_save = self.table_heads+self.table_heads_extra+self.city_list_table_head_citydata

		# finally filename to store csv file
		self.filename = 'US_cities.txt'

	def start_collecting_city_data(self):
		# Get US top cities data, user define a city num (e.g 100)

		# Get top cities list from wikipedia by population (Main page and each individual city page)
		self.parse_cities_from_wikipedia('List of United States cities by population')

		# Get top cities data from city-data.com (top 100 city list, fast and safe to use those data first)
		self.parse_cities_from_citydata(self.city_num)

		# Save those cities already found/ Google search may be blocked sometime and should save data continously
		self.save_city_fields_name(self.filename,self.city_list_table_head_save)
		# Deal with cities that cannot be found top 100 list in city-data.com, use google search to search separately, slow, unsafe
		
		city_not_found_in_citydata = []
		count = 0
		for key in self.city_list:
			similar_key = self.find_similar_key(key,self.city_list_citydata.keys(),0.5)
			if similar_key != "NO_KEY_SIMILAR":# found similar key
				print('found in city-data.com top 100 city list : ',similar_key)
				self.city_list[key].update(self.city_list_citydata[similar_key]) 
			else:# similar key not found! means city is not list in city-data.com top 100 cites
				print('Not found in city-data.com top 100 city list... will google search instead...')
				# city_not_found_in_citydata.append(key)

				self.parse_cities_from_citydata_by_google(key)
				print('Wait until 5 sec to proceed to next city...')
				time.sleep(5)
			
			self.save_single_city_info(self.filename,self.city_list[key])
			count += 1
			print(count,'city info saved ! :',key)
	### get city list from google search page to guide to city-data.com ###
	def parse_cities_from_citydata_by_google(self,city_not_found_in_citydata):

		############ search on city-data.com separately of those un-listed cities... ############ 
		# for example, in top 100 cities list, they are :['Charlotte, North Carolina', 
		# 'Nashville, Tennessee', 'Raleigh, North Carolina', 'Lexington, Kentucky', 
		# 'Saint Paul, Minnesota', 'Greensboro, North Carolina', 'Irvine, California', 
		# 'Newark, New Jersey', 'Durham, North Carolina', 'Fort Wayne, Indiana', 
		# 'St. Petersburg, Florida', 'Laredo, Texas', 'Madison, Wisconsin', 'Chandler, Arizona', 
		# 'Lubbock, Texas', 'Scottsdale, Arizona', 'Reno, Nevada', 'Glendale, Arizona', 
		# 'Gilbert, Arizona', 'Winston–Salem, North Carolina', 'North Las Vegas, Nevada', 
		# 'Norfolk, Virginia', 'Chesapeake, Virginia', 'Garland, Texas', 'Irving, Texas', 
		# 'Hialeah, Florida', 'Fremont, California', 'Boise, Idaho', 'Richmond, Virginia', 
		# 'Baton Rouge, Louisiana', 'Spokane, Washington']
		# To find each individual city info from city-data.com, their corresponding website link
		# should be parsed correctly! 
		##########################################################################################
		
		# google search to find the city website in city-data.com with format query = 'city-data.com city name'
		
		query = "city-data.com "+city_not_found_in_citydata
		try:
			for url in search(query, tld="com", num=10, start=0, stop=1, pause=5):
				city_data_com_city_url = url
				print("Google search to find city url in city-data.com",city_not_found_in_citydata,url)
				city_not_found_in_citydata_by_google = {}
				city_not_found_in_citydata_by_google = self.parse_individual_city_from_citydata(city_data_com_city_url)
				self.city_list[city_not_found_in_citydata].update(city_not_found_in_citydata_by_google) 
		except Exception as e:
			print("Error happens, Goolge search error (maybe too many requests)")
			# raise
			pass
		else:
			pass
		finally:
			pass

	### get city list from wikipedia page ###	
	def parse_cities_from_wikipedia(self,title):
		"""
		Parse from US city list to get city names and 
		common city fields including: 

		['Population 2018 rank','Name','State','Population 2018 estimate',
		'Population 2010 census','Change(%,2010-2018)','Land area 2016(sqmi)',
		'Land area 2016(km2)','Population density 2016(sqmi)',
		'Population density 2016(km2)','Location(N,W)']

		More fields will be parsed on each individual city's page

		"""
		params = {
		'action':"parse",
		'page': title,
		'prop':'text',
		# 'section':section_num,
		}
		result = self._get_content(params)

		text = result['parse']['text']['*']
		# print(text)
		soup = BeautifulSoup(text,'html.parser')
		table = soup.find('table',{'class':'wikitable sortable'})


		###                  Parse the table head as original fields names       ###		
		# columnspan = {}
		# table_heads = []
		# ths = table.find_all('th') # find the table head 
		# for tr in ths:                  # remove tags such as reference [1]
		# 	for tag in tr(['sup']): 
		# 		tag.decompose()
			
		# 	if tr.has_attr('colspan'): # parse the table head (considering column span)
		# 		columnspan[tr.text.strip()] = int(tr['colspan'])
		# 		for i in range(1,int(tr['colspan'])+1):
		# 			table_heads.append(tr.text.strip()+'('+str(i)+')')
		# 	else:
		# 		table_heads.append(tr.text.strip())
		###########################################################################
		
		# initial return_val by using prescribed fields in wikipedia table list
		original_city_info={}
		for key in self.table_heads:
			original_city_info[key] = " "
		
		# initial return_val by using prescribed fields in individual city page
		return_val={}
		for key in self.table_heads_extra:
			return_val[key] = " "

		### parse city info from city rank table ###
		table_heads = self.table_heads
		references = table.findAll("sup", {"class": "reference"})
		if references:
		    for ref in references:
		        ref.extract()

		# Strip sortkeys from the cell
		sortkeys = table.findAll("span", {"class": "sortkey"})
		if sortkeys:
		    for ref in sortkeys:
		        ref.extract()
		for idx,tr in enumerate(table.find_all('tr')):
			if idx<self.city_num+1:

				tds = tr.find_all('td')
				if not tds:
					continue
				city_name = 'N/A'
				
				for idx,td in enumerate(tds):	
					city_field_key   = table_heads[idx]				
					if idx == 1:# get individual city link from wikipedia 
						city_name_link = td.find_all('a',href=True)
						city_name= (city_name_link[0]['title'])
						##### After get city name, collect city data and individual city page #####
						print('Collecting data for:'+city_name+'\n')
						original_city_info[city_field_key] = city_name
						# get individual city wikipedia page and find common feilds
						return_val = self.parse_individual_city_from_wikipedia(city_name,return_val)
						self.city_field_extra_dict[city_name]=return_val
					else:
						city_field_value = td.text.strip()
						if idx == 2:
							original_city_info[city_field_key] = city_field_value # the state of the city
						else:	
							# extract the numbers from city field value
							city_field_value_new = re.sub('[^0-9.]', "", city_field_value)
							# print(idx,city_field_value_new)
							if idx ==10:
								city_field_value_new = re.sub('[^0-9.-/N]', "", city_field_value)
								# print(city_field_value_new)
								city_field_value_new_split = city_field_value_new.split('/')
								Lattitude = city_field_value_new_split[1].split('N')[0]
								Logtitude = city_field_value_new_split[1].split('N')[1][:-1]
								original_city_info[city_field_key] = Lattitude+'N,'+Logtitude+'W'
							else:
								original_city_info[city_field_key] = city_field_value_new
				# merge_city_info_save = {**original_city_info,**return_val}
				merge_city_info_save = dict(original_city_info)
				merge_city_info_save.update(return_val)
				# print(merge_city_info_save)
				self.city_list[city_name] = merge_city_info_save

	### get city data from each individual wikipedia city page ###
	def parse_individual_city_from_wikipedia(self,city_name,return_val):

		# parameter for parse each singel city's data
		params = {
		'action':"parse",
		'page': city_name,
		'prop':'text',
		# 'section':section_num,
		}
		try:
			result = self._get_content(params)
			text = result['parse']['text']['*']
			soup = BeautifulSoup(text,'html.parser')
			table = soup.find('table',{'class':['infobox geography vcard']})

			# Strip references from the cell
			references = table.findAll("sup", {"class": "reference"})
			if references:
			    for ref in references:
			        ref.extract()
			# Strip sortkeys from the cell
			sortkeys = table.findAll("span", {"class": "sortkey"})
			if sortkeys:
			    for ref in sortkeys:
			        ref.extract()
			city_info=[]
			field_starting_point = 9
			for idx,tr in enumerate(table.find_all('tr')):
				if idx>field_starting_point:
					# get field name
					ths = tr.find_all('th')
					if not ths:
						continue
					for th in ths:
		                #This is to discard reference/citation links
						clean_text = th.text.split('&#91;')[0]
		              	#This is to clean the header row of the sort icons
						clean_text = clean_text.split('&#160;')[-1]
						clean_text = clean_text.strip().replace('•', ' ')
						city_info_field=clean_text.strip().replace('\xa0', ' ')

						# set inital fields 
						# if city_name == 'New York City':
						# 	self.fields_names_pool.append(city_info_field)
						# 	city_info_field_key = city_info_field
						# else:

						# find similar key in preivious key data pool, if no return 'NO_KEY_SIMILAR'
						similar_key = self.find_similar_key(city_info_field,self.table_heads_extra,self.similarity_threshold)
						if similar_key == 'NO_KEY_SIMILAR':
							# add this new key to the key pool
							# self.fields_names_pool.append(city_info_field)
							# city_info_field_key = city_info_field
							continue
						else:
							# found similar key, the use the founded on as key
							city_info_field_key = similar_key
						# print(city_info_field_key)
							# get field value
							tds = tr.find_all('td')
							if not tds:
								continue
							# extract link instead of text on city website
							if city_info_field_key == 'Website':
								city_info_field_value = tds[0].find_all('a',href=True)[0]['href']
							else:
						        #This is to discard reference/citation links
								clean_text = tds[0].text.split('&#91;')[0]
				                #This is to clean the header row of the sort icons
								clean_text = clean_text.split('&#160;')[-1]
								city_info_field_value=clean_text.strip().replace('\xa0', ' ')
							"""
							Only add some of the fields to the extra fields:
							Mayor, Time zone, Website,
							"""
							return_val[city_info_field_key]=city_info_field_value
		except Exception as e:
			print("Error happens, some city data cannot be parsed!")
			pass
		else:
			pass
		finally:
			pass
		return return_val

	### general search to get web content by using wikipedia API ###	
	def _get_content(self,params):
		URL = 'http://en.wikipedia.org/w/api.php'
		Search = requests.Session()
		# define general parameters
		if not 'action' in params:
			params['action'] = 'query'
		params['format'] = 'json'
		headers = {'User-Agent':'Houzhu Ding/Wikipedia US cities'}
		search_result_raw = Search.get(URL,params=params,headers=headers)	
		return search_result_raw.json()

	### get top 100 city list data from City-data.com ###
	def parse_cities_from_citydata(self,city_num):
		print('Collecting data from city-data.com top 100 city list...\n')
		base_URL = "http://www.city-data.com/top1.html"
		text = requests.get(base_URL)
		soup = BeautifulSoup(text.content,'html.parser')
		table = soup.find('table',{'class':'tabBlue tblsort tblsticky'})
		for i,tr in enumerate(table.find_all('tr')):
			if i<city_num:
				print('Collecting top city '+str(i+1)+' data from city-data.com:\n')
				tds = tr.find_all('td')
				if not tds:
					continue
				city_info_strip = {}
				city_name = 'N/A'
				for idx,td in enumerate(tds):					
					if idx == 1:
						# get city name get individual city link from city-data.com top100 city list
						city_name_link = td.find_all('a',href=True)
						# print(city_name_link)
						city_name= (city_name_link[1].text)
						city_link = city_name_link[1]['href']
						full_city_link = 'http://www.city-data.com/'+city_link+'/.html'
						# print(city_name,city_link)
						city_info_strip = self.parse_individual_city_from_citydata(full_city_link)
						self.city_list_citydata[city_name] = city_info_strip
		# print(city_fields_citydata)
		print('Done with collecting data from city-data.com top 100 city list!\n')

	### get individual city data from City-data.com ###
	def parse_individual_city_from_citydata(self,full_city_link):
		text = requests.get(full_city_link)
		soup = BeautifulSoup(text.content,'html.parser')

		""" 
		identify some fields to be parsed, there are two many fields,
		I choose several interesting ones including:

		Males population percentage
		Females population percentage
		Estimated median household income
		Mean prices in 2016: All housing
		2016 Cost of living index 

		"""
		city_fields = {}
		# find male and female percentage 
		section = soup.find('section',{'id':'population-by-sex'})
		percents = ""
		for idx,tr in enumerate(section.find_all('tr')):
			tds = tr.find_all('td')
			female_percent= tds[1].text.strip()
			percent= tds[1].text.strip()
			percents+=(percent)
		city_fields['male-female percentage'] = percents

		# median household income 
		median_income = "$ 0"
		mean_house_price = "$ 0"
		section = soup.find('section',{'id':'median-income'})
		tag = section.find('b',text='Estimated median household income in 2016:')
		median_income = tag.next_sibling.string.replace('(','') 

		# average housing price
		tag = section.find('b',text='All housing units:')
		mean_house_price = tag.next_sibling.string.replace(';','')

		city_fields['median household income'] = median_income
		city_fields['mean_housing_price'] = mean_house_price

		# living cost
		living_index = '0'
		section = soup.find('section',{'id':'cost-of-living-index'})
		for idx,b_tag in enumerate(section.find_all('b')):
			if idx==0:
				living_index = b_tag.next_sibling.string
				break
		city_fields['living index'] = living_index

		return city_fields

	################# find similarity between 2 words ########################
	# the algorithm is : find the common substring of two string, if overlaps, and then 
	# compute the length difference, similarity is defined as: 
	#                    1-len(diff)/max(len(word1),len(word2))
	# if there is no overlap, similarity = 0
	##########################################################################
	def find_similar_key(self,key,key_list,threshold):
		# compute similarity of two string

		def longest_common_substring(s1, s2):
			m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
			longest, x_longest = 0, 0
			for x in range(1, 1 + len(s1)):
				for y in range(1, 1 + len(s2)):
					if s1[x - 1] == s2[y - 1]:
						m[x][y] = m[x - 1][y - 1] + 1
						if m[x][y] > longest:
							longest = m[x][y]
							x_longest = x
						else:
							m[x][y] = 0
			return s1[x_longest - longest: x_longest]

		def similar_compare(word1,word2):
			ans = longest_common_substring(word1,word2)
			word1_diff = word1.replace(ans,'')
			word2_diff = word2.replace(ans,'')

			un_match_len = max(len(word1_diff),len(word2_diff))
			longest_len = max(len(word1),len(word2))

			similarity = 1-un_match_len/longest_len	
			return similarity	

		# find similar key in the fields name pool
		if key in key_list:
			# if the new city info field is in the pool
			return key # return itself
		else:
			max_similarity = 0
			similar_key = 'NO_KEY_SIMILAR'
			for item in key_list:
				word1 = key.replace('(','').replace(')','').replace(',','').replace(' ','').lower()
				word2 = item.replace('(','').replace(')','').replace(',','').replace(' ','').lower()
				similarity = similar_compare(key.lower(), item.lower())
				if similarity > max_similarity:
					max_similarity = similarity
					similar_key = item
			# print(key,similar_key,max_similarity)
			if max_similarity>threshold:
				return similar_key
			else:
				return 'NO_KEY_SIMILAR'
		
	def save_city_fields_name(self,filename,city_list_table_head_save):

		writer = csv.writer(open(filename,'w',newline='',encoding='utf-8'),delimiter=',')
		writer.writerow(city_list_table_head_save)

	def save_single_city_info(self,filename,city_info):

		writer = csv.writer(open(filename,'a',newline='',encoding='utf-8'),delimiter=',')
		city_info_save = []
		for idx in city_info:
			city_info_value = city_info[idx]
			city_info_save.append(city_info_value)
		writer.writerow(city_info_save)