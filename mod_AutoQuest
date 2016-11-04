'''AutoQuest by Skino'''
'''Version 0.1'''

import Account
import BigWorld
import ResMgr
import functools

from gui.Scaleform.Waiting import Waiting
from gui import SystemMessages
from CurrentVehicle import g_currentVehicle
from gui.shared.gui_items.processors import Processor
from gui.shared import g_itemsCache
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils import decorators
from gui.shared.gui_items import Vehicle
from gui.server_events import g_eventsCache
from constants import EVENT_TYPE

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

def isPQIDBelongToVehicleType(pQID, vehicle):
	allPQuests = g_eventsCache.potapov.getQuests().values()
	return vehicle.type.lower() == list(allPQuests[pQID].getVehicleClasses())[0].lower()

def checkVehClassForBattle():
	vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.CUSTOM(lambda item: item.type.lower() == g_currentVehicle.item.type.lower())).values()
	for vehicle in vehicles:
		if vehicle.isInBattle():
			return False
	
	return True

def changePQuests(newPQuestID):
	global g_callInMod
	
	selectedPQuestIDs = g_currentPotapovQuestIDs
	if newPQuestID in selectedPQuestIDs:
		return
	
	allPQuests = g_eventsCache.potapov.getQuests().values()
	if allPQuests[newPQuestID-1].isDone():
		SystemMessages.pushMessage('<font color=\'#FF0000\'><b>Боевая задача уже выполнена!</b></font>', SystemMessages.SM_TYPE.Information, 0)
		return
	
	message = str(newPQuestID)
	message += '\n' + str(selectedPQuestIDs)	
	
	i = len(selectedPQuestIDs)
	if i == 0:
		if newPQuestID > 0:
			selectedPQuestIDs.append(newPQuestID)
	else:
		for selectedPQuestID in selectedPQuestIDs:
			i = i - 1
			if isPQIDBelongToVehicleType(selectedPQuestID-1, g_currentVehicle.item):
				selectedPQuestIDs.remove(selectedPQuestID)
				if newPQuestID > 0:
					selectedPQuestIDs.append(newPQuestID)
				break
			elif i == 0:
				if newPQuestID > 0:
					selectedPQuestIDs.append(newPQuestID)
	
	message += '\n' + str(selectedPQuestIDs)
	if DEBUG:
		SystemMessages.pushMessage(message, SystemMessages.SM_TYPE.Information, 0)
	
	g_callInMod = True
	BigWorld.player().selectPotapovQuests(selectedPQuestIDs, 0, hook_response)
	
	return

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
	toCurrent = isPQIDBelongToVehicleType(id, g_currentVehicle.item)
	if toCurrent:
		message = 'Техника:\n' + str(g_currentVehicle.item.userName)
		if change == 'set':
			g_xmlSetting.write(g_currentVehicle.item.name, '')
			g_xmlSetting[g_currentVehicle.item.name].writeInt('questID', id)
			g_xmlSetting.save()
			message += '\nПривязана задача:\n' + getQuestTileprefix(id-1) + g_eventsCache.potapov.getQuests().values()[id-1].getUserName()
		elif change == 'del':
			g_xmlSetting.write(g_currentVehicle.item.name, '')
			g_xmlSetting[g_currentVehicle.item.name].writeInt('questID', 0)
			g_xmlSetting.save()
			message += '\nОтвязаны все задачи.'
		if change == 'none':
			message = 'Задачи небыли изменены.'
		
		SystemMessages.pushMessage(message, SystemMessages.SM_TYPE.Information, 0)
	
	return

def vehicleCheckCallback():
	global g_currentVehicleName, g_isFirstInit, g_currentVehiclePQID, g_currentPotapovQuestIDs
	
	if g_currentVehicle.isInHangar and hasattr(g_currentVehicle.item, 'name'):
		if g_currentVehicleName != g_currentVehicle.item.name:
			g_currentVehicleName = g_currentVehicle.item.name
			if g_isFirstInit:
				g_isFirstInit = False
				g_currentPotapovQuestIDs = getSelectedQuestIDs()
				if DEBUG:
					SystemMessages.pushMessage('startedPQIDs: ' + str(g_currentPotapovQuestIDs), SystemMessages.SM_TYPE.Information, 0)
	
			g_currentVehiclePQID = None
			if g_xmlSetting[g_currentVehicleName]:
				g_currentVehiclePQID = g_xmlSetting[g_currentVehicleName].readInt('questID', 0)
				changePQuests(g_currentVehiclePQID)
	
	BigWorld.callback(1, vehicleCheckCallback)
	
	return

def hook_selectPotapovQuests(PlayerAccountClassSpecimen, potapovQuestIDs, questType, callback):
	global g_originalCallback
	g_originalCallback = callback
	g_original_selectPotapovQuests(PlayerAccountClassSpecimen, potapovQuestIDs, questType, hook_response)
	
	return

def init():
	global g_original_selectPotapovQuests, g_xmlSetting
	
	print '[AutoQuest] Version 0.1 by Skino'
	
	g_original_selectPotapovQuests = Account.PlayerAccount.selectPotapovQuests
	Account.PlayerAccount.selectPotapovQuests = hook_selectPotapovQuests
	
	BigWorld.callback(2, vehicleCheckCallback)
	
	g_xmlSetting = ResMgr.openSection('scripts/client/gui/mods/mod_AutoQuest.xml', True)
	if not g_xmlSetting:
		g_xmlSetting.save()
	
	return
