import sqlite3

class api():
	def __init__(self, dbName):
		self.con = sqlite3.connect(dbName)
		self.cursor = self.con.cursor()

	def __del__(self):
		self.con.close()

	def insertVideos(self, infos):
		for info in infos:
			self.cursor.execute(f'''
				INSERT INTO Videos 
				("link", "title", "mode", "used") 
				values 
				("{info["link"]}", "{info["title"]}", {info["mode"]}, 0)
			''')
		self.con.commit()

	def selectDirtyVideos(self, links):
		buff = []
		for link in links:
			self.cursor.execute(f'''SELECT * FROM Videos WHERE link = "{link}"''')
			buff.append(self.cursor.fetchall())
		return list(filter(lambda x: len(x) != 0, buff))

	def selectUnusedVideos(self):
		self.cursor.execute(f'''SELECT * FROM Videos WHERE used = 0''')
		return self.cursor.fetchall()

	def selectDays(self, toDay, amount):
		# print(toDay)
		# exit()
		self.cursor.execute(f'''SELECT * FROM Days WHERE date(date) <= date('{toDay}') ORDER BY id DESC LIMIT {amount};''')
		return self.cursor.fetchall()

	def checkAvailabilityPerson(self, personLink):
		self.cursor.execute(f'''SELECT * FROM Persons WHERE personLink = "{personLink}";''')
		res = self.cursor.fetchall()
		return len(res) == 0

	def insertPerson(self, newPersons):
		for newPerson in newPersons:
			self.cursor.execute(f'''
				INSERT INTO Persons 
				("personLink") 
				values 
				("{newPerson['personId']}")
			''')
		self.con.commit()

	def insertDays(self, daysInfo):
		for dayInfo in daysInfo:
			self.cursor.execute(f'''
				INSERT INTO Days 
				("videosAmount", "postsAmount", "date", "data") 
				values 
				({dayInfo["videosAmount"]}, {dayInfo["postsAmount"]}, "{dayInfo["date"]}", ?)
			''', (dayInfo["data"],))
			for fId in dayInfo['fIds']:
				self.cursor.execute(f'''
					UPDATE Videos
					SET 
						used = 1
					WHERE
						id = {fId}
				''')
		self.con.commit()