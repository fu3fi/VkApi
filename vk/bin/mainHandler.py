import json
import base64
import datetime
import os

from .api import vk, db, report
from ..core.libs.tool import Kit

kit = Kit.build()
cursor = kit.getCursor()

configFilePath = os.path.dirname(__file__) + '/../files/config.json'
configDirectoryPath = os.path.dirname(__file__) + '/../files/'
reportsDirectoryPath = os.path.dirname(__file__) + '/../files/reports/'
config = json.loads(open(configFilePath).read())

vApi = config['V_API']
accessToken = config['ACCESS_TOKEN']
postsAmount = config['POSTS_AMOUNT']
dbPath = configDirectoryPath + config['DB_PATH']
bulletinBoardPath = configDirectoryPath + config['BULLETIN_BOARD_PATH']


@cursor.command("register")
def registerVideo():

	DB = db.api(dbPath)
	with open(bulletinBoardPath, encoding='utf-8') as openFile:
		board = json.loads(openFile.read())
	dirtyVideos = DB.selectDirtyVideos([bit['link'] for bit in board['info']])
	if len(dirtyVideos) != 0:
		kit.error(f"Видео: {', '.join(list(map(lambda x: x[0][1], dirtyVideos)))} уже использовались!")
		kit.warning("Пожалуйста выберите другие..")
		return

	videos = json.loads(open(bulletinBoardPath).read())['info']
	vkApi = vk.api(vApi, accessToken)

	posts = []
	rawPostsStats = []
	for video in videos:
		kit.print('')
		kit.success(f"Ищем видео {video['link']}")
		kit.print('')
		
		vkApi.setPattern(video['title'])
		data = json.loads(vkApi.getVideoByName(postsAmount))
		postsWithVideo = vkApi.getOnlyVideo(data)
		cleanData = vkApi.cleaner(postsWithVideo)
		postOfPerson = list(filter(lambda bit: bit['type'] == 'person', cleanData))
		postOfGroup = list(filter(lambda bit: bit['type'] == 'group', cleanData))
		posts.append({
			'postsInfo': {
				"data": postOfPerson,
				"mode": video['mode'],
			},
			'amount': len(postOfPerson),
		})

	kit.success("Посты успешно загружены!\n")
	kit.warning("Общая статистика:\n")
	kit.print(f"\tВсего видео: {len(videos)}")
	kit.print(f"\tВсего постов: {sum(list(map(lambda x: x['amount'], posts)))}")
	kit.print(f"\tРаспределение: {', '.join(list(map(lambda x: str(x['amount']), posts)))}")
	kit.print('')

	if not kit.makeQuestion('Хотите внести изменения в базу данных? (Y/n)'):
		return

	try:
		DB.insertVideos(board['info'])
		kit.success("Видео были успешно зарегистрированы")
	except:
		kit.error("При регистрации произошла ошибка!")


@cursor.command("search")
def searchPosts():
	DB = db.api(dbPath)
	patterns = list(map(lambda x: (x[0], x[1], x[2], x[3]), DB.selectUnusedVideos()))

	if len(patterns) == 0:
		kit.error("Нет видео для поиска постов!")
		return

	vkApi = vk.api(vApi, accessToken)

	posts = {}
	rawPostsStats = []
	for fId, link, pattern, mode in patterns:
		kit.success(f"Ищем видео {link}")

		vkApi.setPattern(pattern)
		data = json.loads(vkApi.getVideoByName(postsAmount))
		postsWithVideo = vkApi.getOnlyVideo(data)
		cleanData = vkApi.cleaner(postsWithVideo)
		postOfPerson = list(filter(lambda bit: bit['type'] == 'person', cleanData))
		postOfGroup = list(filter(lambda bit: bit['type'] == 'group', cleanData))
		posts[fId] = {
			'postsInfo': {
				"data": postOfPerson,
				"mode": mode,
			},
			'amount': len(postOfPerson),
		}
		rawPostsStats.append({
			'fId': fId,
			'amount': len(postOfPerson),
		})

	kit.success("Посты успешно загружены!")
	kit.warning("Общая статистика:")
	kit.print(f"\tВсего видео: {len(patterns)}")
	kit.print(f"\tВсего постов: {sum(list(map(lambda x: x['amount'], posts.values())))}")
	kit.print(f"\tРаспределение: {', '.join(list(map(lambda x: str(x['amount']), posts.values())))}")
	kit.print('')
	
	daysAmount = 0
	while daysAmount not in [1, 2, 3, 4, 5, 6, 7]:
		daysAmount = int(input("На сколько дней разделить?\n"))


	kit.print("Запускаем квантовую генерацию!")
	distributionByDay = vkApi.minimize(rawPostsStats, daysAmount)
	kit.success("Успех!")
	kit.print("Статистика по дням:")
	kit.print(json.dumps(distributionByDay, indent=4, sort_keys=True, ensure_ascii=False))
	
	if not kit.makeQuestion('Хотите внести изменения в базу данных? (Y/n)'):
		return

	days = []
	dayCounter = 1
	
	for dayInfo in distributionByDay:
		days.append({
			"videosAmount": len(dayInfo),
			"postsAmount": sum([subday['amount'] for subday in dayInfo]),
			"date": (datetime.date.today() + datetime.timedelta(days=dayCounter)).isoformat(),
			"data": base64.b64encode(bytes(json.dumps([posts[video['fId']]['postsInfo'] for video in dayInfo], ensure_ascii=False), "utf-8")),
			"fIds": [video['fId'] for video in dayInfo],
		})
		dayCounter += 1

	DB.insertDays(days)

	kit.success("Данные успешно внесены!")


@cursor.command("report")
def createReport():
	DB = db.api(dbPath)
	
	modesMap = {}
	with open(bulletinBoardPath, encoding='utf-8') as openFile:
		modesMap = json.loads(openFile.read())['map']

	numberOfDays = int(input("Сколько дней включить в отчет?\n"))
	toDay = datetime.date.today().isoformat()
	days = DB.selectDays(toDay, numberOfDays)
	# print(days)

	# sId
	# videosAmount
	# postsAmount
	# date
	# data
	allData = {}
	allAmount = 0
	newPersons = []
	newPersonsBuffSet = set()
	for day in days:
		allAmount += day[2]
		dayPosts = json.loads(base64.b64decode(day[4]))
		for video in dayPosts:
			for post in video['data']:
				if DB.checkAvailabilityPerson(post['linkTowardProfile']) and post['linkTowardProfile'] not in newPersonsBuffSet:
					newPersonsBuffSet.add(post['linkTowardProfile'])
					newPersons.append({
						'personId': post['linkTowardProfile'],
					})
				if post['linkTowardProfile'] not in allData:
					allData[post['linkTowardProfile']] = {
						"id": post['linkTowardProfile'],
						"name": post['name'],
						"posts": [],
						"mode": video['mode'],
					}
				if video['mode'] != allData[post['linkTowardProfile']]['mode']:
					allData[post['linkTowardProfile']]['mode'] = 3
				allData[post['linkTowardProfile']]['posts'].append(post['postId'])
	

	def subTransf(person):
		return (
			'', 
			f'Новости в социальной сети ВКонтакте «{person["name"]}» {person["id"]}', 
			modesMap[str(person["mode"])],
			'',
			'',
			f'Что нашлось: {" ".join(person["posts"])}',
		)

	dataIntoTable = list(map(subTransf, allData.values()))

	with open(reportsDirectoryPath + f'Видео {toDay} (всего {allAmount}, новых {len(newPersons)}).csv', 'w+') as openCsv:
		for line in dataIntoTable:	
			openCsv.write('\n'.join(line[5][16:].split(' ')) + '\n')

	with open(reportsDirectoryPath + f'Видео {toDay} (всего {allAmount}, новых {len(newPersons)}) (full).csv', 'w+') as openCsv:
		for line in dataIntoTable:	
			openCsv.write(';'.join(line) + '\n')

	kit.success("Файл отчета был сгенерирован и сохранен!")

	if not kit.makeQuestion('Хотите добавить новых пользователей в базу данных? (Y/n)'):
		return

	DB.insertPerson(newPersons)

	kit.success("Новые аккаунты успешно внесены!")


@cursor.command("stats")
def getStats():
	DB = db.api(dbPath)
	numberOfDays = 7

	# sId
	# videosAmount
	# postsAmount
	# date
	# data
	days = DB.selectDays((datetime.date.today() + datetime.timedelta(days=365)).isoformat(), numberOfDays)
	for day in days:
		kit.print('')
		kit.success(f"Дата: {day[3]}")
		kit.print(f"Количество видео {day[1]}")
		kit.print(f"Количество постов: {day[2]}")