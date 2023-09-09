import urllib.request
from urllib.parse import urlencode
from urllib.parse import quote
import json
import math
import time

class api():

	@staticmethod
	def sign(x): 
		return math.copysign(1, x)

	@staticmethod
	def getNextMemberOfSignedSequenceOfNaturalNumbers():
		currentMember = 0
		while True:
			currentMember = -1 * api.sign(currentMember) * (abs(currentMember) + 1)
			yield int(currentMember)

	@staticmethod
	def minimize(distributionByDay, groupAmount):
		videosAmount = len(distributionByDay)
		groupDist = []
		while groupAmount != 0:
			currentValue = videosAmount // groupAmount
			videosAmount -= currentValue
			groupDist.append(currentValue)
			groupAmount -= 1

		additionElCounter = len(distributionByDay) // 2
		additionElStep = 0
		gmssnnc = api.getNextMemberOfSignedSequenceOfNaturalNumbers()
		gmssnns = api.getNextMemberOfSignedSequenceOfNaturalNumbers()
		counter = 0

		results = []
		distributionByDay = sorted(distributionByDay, key=lambda x: x["amount"])
		groupDist = sorted(groupDist, reverse=True)		

		while len(groupDist) != 0:
			subResult = []
			amountofVideos = groupDist.pop()
			if amountofVideos % 2 == 0:
				while amountofVideos != 0:
					subResult.append(distributionByDay[counter])
					amountofVideos -= 1
					counter += next(gmssnnc)
			else:
				while amountofVideos != 1:
					subResult.append(distributionByDay[counter])
					amountofVideos -= 1
					counter += next(gmssnnc)
				subResult.append(distributionByDay[additionElCounter])
				additionElCounter += next(gmssnns)

			results.append(subResult)

		return results

	
	def __init__(self, vApi, accessToken):
		self.vApi = vApi
		self.accessToken = accessToken

	def getVideoByName(self, amount=30):
		q = quote(self.pattern)
		url = f'https://api.vk.com/method/newsfeed.search?q={q}&extended=1&count={amount}&v={self.vApi}&access_token={self.accessToken}'
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
		req = urllib.request.Request(url.replace(" ", "%20"), {}, headers)
		with urllib.request.urlopen(req) as response:
			html = response.read()
			return html

	def getPersonIdByName(self, name):
		url = f'https://api.vk.com/method/users.get?user_ids={name}&v={self.vApi}&access_token={self.accessToken}'
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
		req = urllib.request.Request(url.replace(" ", "%20"), {}, headers)
		with urllib.request.urlopen(req) as response:
			html = response.read()
			return json.loads(html)['response'][0]['id']

	def setPattern(self, pattern):
		self.pattern = pattern

	def getGroupNameById(self, id):
		url = f'https://api.vk.com/method/groups.getById?group_id={-1*id}&v={self.vApi}&access_token={self.accessToken}'
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
		req = urllib.request.Request(url.replace(" ", "%20"), {}, headers)
		with urllib.request.urlopen(req) as response:
			html = response.read()
			return json.loads(html)['response'][0]['screen_name']

	def getPersonNameById(self, id):
		url = f'https://api.vk.com/method/users.get?user_ids={id}&v={self.vApi}&access_token={self.accessToken}'
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
		req = urllib.request.Request(url.replace(" ", "%20"), {}, headers)
		with urllib.request.urlopen(req) as response:
			html = response.read()
			res = json.loads(html)['response'][0]
			return f'{res["first_name"]} {res["last_name"]}'

	def getOnlyVideo(self, data):
		buff = []
		for subdata in data['response']['items']:
			if 'attachments' not in subdata:
				continue
			for bit in subdata['attachments']:
				if (bit['type'] == 'video' and self.pattern in bit['video']['title']) or (bit['type'] == 'link' and self.pattern in bit['link']['title']):
					buff.append(subdata)
		return buff

	def cleaner(self, data):
		def subCleaner(bit):
			time.sleep(1)
			name = self.getGroupNameById(bit['owner_id']) if bit['owner_id'] < 0 else self.getPersonNameById(bit['owner_id'])
			typeSubject = 'group' if bit['owner_id'] < 0 else 'person'
			print(f"Найдено " + f"https://vk.com/id{bit['owner_id']}?w=wall{bit['owner_id']}_{bit['id']}")
			print("---------------------------------------------------------")
			return {
				'ownerId': bit['owner_id'],
				'type': typeSubject,
				'name': name,
				'linkTowardProfile': f"https://vk.com/id{bit['owner_id']}",
				'postId': f"https://vk.com/id{bit['owner_id']}?w=wall{bit['owner_id']}_{bit['id']}",
				'text': bit['text'],
			}
		return list(map(subCleaner, data))