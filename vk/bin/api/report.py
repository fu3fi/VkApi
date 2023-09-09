class api():
	def __init__(self, name):
		self.cursor = Document()
		self.name = name

	def addHeader(self, headerText):
		self.cursor.add_heading(headerText, level=1)

	def addTable(self, title, rows):
		table = self.cursor.add_table(rows=1, cols=len(title))
		cells = table.rows[0].cells
		for counter in range(len(title)):
			cells[counter].text = title[counter]
		for row in rows:
			cursorRow = table.add_row().cells
			for counter in range(len(title)):
				cursorRow[counter].text = row[counter]
		cursorRow = table.add_row().cells
		for counter in range(len(title)):
			cursorRow[counter].text = ''

	def addParagraph(self, paragraph):
		self.cursor.add_paragraph(
			paragraph,
		)

	def save(self):
		if not os.path.exists(self.name):
			with open(self.name, 'a'): pass
		self.cursor.save(self.name)

	def br(self):
		self.cursor.add_paragraph('')

	def saveDay(self, data):
		pass