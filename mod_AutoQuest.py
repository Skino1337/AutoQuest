'''AutoQuest by Skino'''
'''Version 0.1.1'''


import Account
import BigWorld
import ResMgr


from gui import SystemMessages
from CurrentVehicle import g_currentVehicle
from gui.shared import g_itemsCache
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.server_events import g_eventsCache


DEBUG = False

g_original_selectPotapovQuests = None
g_xmlSetting = None
g_callInMod = False
g_isFirstInit = True
g_previosPotapovQuestIDs = []
g_currentPotapovQuestIDs = []
g_currentVehicleName = ''
g_currentVehiclePQID = ''

g_originalCallback = None

def getQuestTileprefix(id):
	allPQuests = g_eventsCache.potapov.getQuests().values()
	return ('[' + str(allPQuests[id].getTileID()) + '] ')
	
def getSelectedQuestIDs():
	selectedPQuests = g_eventsCache.potapov.getSelectedQuests().values()
	selectedPQuestIDs = []
	for selectedPQuest in selectedPQuests:
		selectedPQuestIDs.append(selectedPQuest.getID())
	
	return selectedPQuestIDs

def getPQIDsChanges(oldPQIDs, newPQIDs):
	id = 0
	change = 'none'
	if len(newPQIDs) >= len(oldPQIDs):
		lst = list(set(newPQIDs).difference(set(oldPQIDs)))
		if len(lst) > 0:
			id = lst[0]
		change = 'set'
	elif len(newPQIDs) < len(oldPQIDs):
		id = list(set(oldPQIDs).difference(set(newPQIDs)))[0]
		change = 'del'
	
	return (id, change)

def checkVehClassForBattle():
	vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.CUSTOM(lambda v: v.type == g_currentVehicle.item.type)).values()
	for vehicle in vehicles:
		if vehicle.isInBattle():
			return False
	
	return True

def isPQIDBelongToVehicleType(pQID, vehicle):
	quest = g_eventsCache.potapov.getQuests().get(pQID)
	return vehicle.type in quest.getVehicleClasses()

def hook_response(code, callback):
	global g_previosPotapovQuestIDs, g_currentPotapovQuestIDs, g_callInMod
	if not g_callInMod:
		g_originalCallback(code, callback)
	
	g_previosPotapovQuestIDs = g_currentPotapovQuestIDs
	g_currentPotapovQuestIDs = getSelectedQuestIDs()
	
	if g_callInMod:
		g_callInMod = False
		if g_currentVehiclePQID > 0:
			if g_currentVehiclePQID in g_currentPotapovQuestIDs:
				SystemMessages.pushMessage('<font color=\'#00FF00\'><b>Боевые задачи скорректированы!</b></font>', SystemMessages.SM_TYPE.Information, 0)
			else:
				SystemMessages.pushMessage('<font color=\'#FF0000\'><b>Боевые задачи не скорректированы!</b></font>', SystemMessages.SM_TYPE.Information, 0)
		else:
			isIn = True
			i = len(g_currentPotapovQuestIDs)
			if i == 0:
				isIn = False
			else:
				isIn = False
				for curPQuestID in g_currentPotapovQuestIDs:
					if isPQIDBelongToVehicleType(curPQuestID, g_currentVehicle.item):
						isIn = True
						break
			if not isIn:
				SystemMessages.pushMessage('<font color=\'#00FF00\'><b>Боевые задачи скорректированы!</b></font>', SystemMessages.SM_TYPE.Information, 0)
			else:
				SystemMessages.pushMessage('<font color=\'#FF0000\'><b>Боевые задачи не скорректированы!</b></font>', SystemMessages.SM_TYPE.Information, 0)
				
		return
	
	id, change = getPQIDsChanges(g_previosPotapovQuestIDs, g_currentPotapovQuestIDs)
	if isPQIDBelongToVehicleType(id, g_currentVehicle.item):
		message = 'Техника:\n' + str(g_currentVehicle.item.userName)
		if change == 'set':
			g_xmlSetting.write(g_currentVehicle.item.name, '')
			g_xmlSetting[g_currentVehicle.item.name].writeInt('questID', id)
			g_xmlSetting.save()
			message += '\nПривязана задача:\n' + getQuestTileprefix(id)
			if DEBUG:
				message += '[id:' + str(id) + '] '
			message += g_eventsCache.potapov.getQuests().get(id).getUserName()
		elif change == 'del':
			g_xmlSetting.write(g_currentVehicle.item.name, '')
			g_xmlSetting[g_currentVehicle.item.name].writeInt('questID', 0)
			g_xmlSetting.save()
			message += '\nОтвязаны все задачи.'
		elif change == 'none':
			message =  'Задачи небыли изменены.'
		
		SystemMessages.pushMessage(message, SystemMessages.SM_TYPE.Information, 0)
	
	return

def changeVehicle():
	global g_currentVehiclePQID, g_callInMod
	
	g_currentVehiclePQID = None
	if not g_xmlSetting[g_currentVehicleName]:
		return
	g_currentVehiclePQID = g_xmlSetting[g_currentVehicleName].readInt('questID', 0)
	
	selectedPQuestIDs = g_currentPotapovQuestIDs
	if g_currentVehiclePQID in selectedPQuestIDs:
		return
	
	allPQuests = g_eventsCache.potapov.getQuests().values()
	if allPQuests[g_currentVehiclePQID-1].isDone():
		SystemMessages.pushMessage('<font color=\'#FF0000\'><b>Боевая задача уже выполнена!</b></font>', SystemMessages.SM_TYPE.Information, 0)
		return
	
	m = 'Try to select correct quest.\n'
	m += str(g_currentVehiclePQID) + '\n'
	m += str(selectedPQuestIDs) + '\n'
	
	i = len(selectedPQuestIDs)
	if i == 0:
		if g_currentVehiclePQID > 0:
			selectedPQuestIDs.append(g_currentVehiclePQID)
	else:
		for selectedPQuestID in selectedPQuestIDs:
			i = i - 1
			if isPQIDBelongToVehicleType(selectedPQuestID, g_currentVehicle.item):
				selectedPQuestIDs.remove(selectedPQuestID)
				if g_currentVehiclePQID > 0:
					selectedPQuestIDs.append(g_currentVehiclePQID)
				break
			elif i == 0:
				if g_currentVehiclePQID > 0:
					selectedPQuestIDs.append(g_currentVehiclePQID)
	
	m += str(selectedPQuestIDs)
	if DEBUG:
		print m
		SystemMessages.pushMessage(m, SystemMessages.SM_TYPE.Information, 0)
	
	g_callInMod = True
	BigWorld.player().selectPotapovQuests(selectedPQuestIDs, 0, hook_response)
	
	return

def vehicleCheck():
	global g_currentVehicleName, g_isFirstInit, g_currentPotapovQuestIDs
	
	if not g_currentVehicle.isInHangar:
		return
	
	if not hasattr(g_currentVehicle.item, 'name'):
		return
	
	if g_currentVehicleName == g_currentVehicle.item.name:
		return
	
	g_currentVehicleName = g_currentVehicle.item.name
	if g_isFirstInit:
		g_isFirstInit = False
		g_currentPotapovQuestIDs = getSelectedQuestIDs()
		if DEBUG:
			m = 'Initial quests IDs:\n' + str(g_currentPotapovQuestIDs)
			for id in g_currentPotapovQuestIDs:
				m += '\n' + g_eventsCache.potapov.getQuests().get(id).getUserName()
			print m
			SystemMessages.pushMessage(m, SystemMessages.SM_TYPE.Information, 0)
	
	changeVehicle()
	
	return

def hook_selectPotapovQuests(PlayerAccountClassSpecimen, potapovQuestIDs, questType, callback):
	global g_originalCallback
	g_originalCallback = callback
	g_original_selectPotapovQuests(PlayerAccountClassSpecimen, potapovQuestIDs, questType, hook_response)
	
	return

def init():
	global g_original_selectPotapovQuests, g_xmlSetting
	
	print '[AutoQuest] Version 0.1.1 by Skino'
	
	g_original_selectPotapovQuests = Account.PlayerAccount.selectPotapovQuests
	Account.PlayerAccount.selectPotapovQuests = hook_selectPotapovQuests
	
	g_xmlSetting = ResMgr.openSection('scripts/client/gui/mods/mod_AutoQuest.xml', True)
	if not g_xmlSetting:
		g_xmlSetting.save()
	
	def vehicleCheckCallback():
		vehicleCheck()
		BigWorld.callback(1, vehicleCheckCallback)
		
		return
	
	vehicleCheckCallback()
	
	return
