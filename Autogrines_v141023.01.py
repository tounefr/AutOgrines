# -*-coding:Utf-8 -*
import sys
import time
import re
import json
import os
import threading
import random
from colorama import init, Fore, Back, Style
from termcolor import colored
import requests
import string

class Util:

	def getDateNow():
		return time.strftime("%H:%M:%S")

	def timeLeft():
		return str(int(time.time() - Autogrines.TIME_START));
	
	def clear():
		os.system('cls')
		
	def randomword(length):
		return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))
		
	def stop():
		input("\n\nAppuyez sur une touche pour continuer")
		Autogrines.THREADS = False
		sys.exit(1)

init(autoreset=True)

"""
DEBUG : YELLOW
INFO  : GREEN
ERROR : RED
"""

class Console:

	def debug(text):
		print(Fore.YELLOW + Util.getDateNow() + " [DEBUG] " + text)

	def info(text):
		print(Fore.GREEN + Util.getDateNow() + " [INFO] " + text)

	def warning(text):
		print(Util.getDateNow() + " [WARNING] " + text)

	def error(text):
		print(Fore.RED + Util.getDateNow() + " [FATAL ERROR] " + text)
		
	def title(text):
		print("")
		print(Back.MAGENTA + text)
		print("")
		
	def title2(text):
		print("")
		print(Back.CYAN + text)
		print("")	
		
class DofusAccount:

	def __init__(self, account):
		self.logged = False
		self.account = account["account"]
		self.password = account["password"]
		self.dofusRequest = DofusRequest(self)
		self.id_server = int(account["id_server"])
		self.cost_min_ogrine = int(account["cost_min_ogrine"])
		self.cost_max_ogrine = int(account["cost_max_ogrine"])
		self.max_ogrines = int(account["max_ogrines"])
		self.totalKamas = 0
		self.totalOgrinesBought = 0
		self.certif_auto = int(account["certif_auto"])
		self.infos_console = []
		self.stopBuy = False
		
		if int(account["buy_ogrines"]) == 1:
			self.buy_ogrines = True
		else:
			self.buy_ogrines = False
			
		if int(account["subscribe_auto"]) == 1:
			self.subscribe_auto = True
		else:
			self.subscribe_auto = False

	def toDofusAccountsObjects(accounts):
		accountsObjects = []
		for account in accounts:
			accountsObjects.append(DofusAccount(account))
		return accountsObjects
		
class DofusRequest:

	def __init__(self, dofusAccount):
		# Pour garder les cookies
		self.sess = requests.Session()
		self.sess.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36"
		self.dofusAccount = dofusAccount	
		self.sess.verify = "cacert.pem"
		
	def identification(self):
		req = self.sess.get("https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/identification");

		postDatas = {
		  "action" : "login",
		  "from" : "https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/identification",
		  "login" : self.dofusAccount.account,
		  "password" : self.dofusAccount.password,
		  "remember" : 1
		}
		try:
			req = self.sess.post("https://account.ankama.com/sso", data=postDatas);
			if req.history[0].headers["Location"] == "https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/identification#loginfailed=failed":
				return False
		except IndexError:
			pass
		
		return True

	def choose_server(self):
		try:
			req = self.sess.post("https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/selection-serveur", data={"serverid" : self.dofusAccount.id_server})
			if req.history[0].headers["Location"] == "https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/0-francaise":
				return req.text
		except IndexError:
			pass
			
		return False

	def checkOffers(self):
		req = self.sess.get("https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/0-francaise")
		try:
			check_form = re.search("\<input\ type\=\'hidden\'\ name\=\'check_form\'\ value\=\'(.*)\'\ \/\>", req.text).group(1)
			offersUnparsed = re.search("MarketPlace\.ActiveBid\((.*)\)\;", req.text).group(1)
			offersParsed = json.loads(offersUnparsed)
		except AttributeError:
			Console.error("Impossible de recuperer les offres pour le compte '{}'".format(self.dofusAccount.account))
			Util.stop()
		
		return {
			'check_form' : check_form,
			'offers' : offersParsed['OGRINES']
		}

	def buyOgrines(self, check_form, nbrOgrines, offer):
		postDatas = {
			'rate' : int(offer['rate']),
			'check_form' : check_form,
			'postback' : 1,
			'bak_from' : 'QuickBuy',
			'want' : nbrOgrines,
			'search' : nbrOgrines,
			'give' : int(offer['rate']) * nbrOgrines
		}
		req = self.sess.post("https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/0-francaise/achat-ogrines/acheter", data=postDatas)
		postDatas = {
			'postback' : 1,
			'confirm' : 1,
			'check_form' : check_form,
			'want' : nbrOgrines,
			'give' : int(offer['rate']) * nbrOgrines,
			'rate' : int(offer['rate']),
			'server' : self.dofusAccount.id_server
		}

		req = self.sess.post("https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/0-francaise/achat-ogrines/acheter", data=postDatas)

		try:
			re.search("Les ogrines ont ete credites sur votre compte", req.text).group(0)
			return True
		except:
			return False

	def choose_pseudo(self):
		postDatas = {
			"usernickname" : Util.randomword(8),
			"sAction" : "submit"
		}
		headers = {"X-Requested-With" : "XMLHttpRequest"}
		req = self.sess.post("http://www.dofus.com/fr/choisir-votre-pseudo", data=postDatas, headers=headers)
		
	def certify(self):
	
		postDatas = {
			"postBack" : "1",
			"certify" : "",
			"civility" : "M",
			"fname" : Util.randomword(10),
			"lname" : Util.randomword(10),
			"birth_d" : "01",
			"birth_m" : "01",
			"birth_y" : random.randint(1950,2000),
			"address" : Util.randomword(10),
			"zipcode" : random.randint(10000, 99999),
			"city" : Util.randomword(8),
			"country" : "FR",
			"state" : "",
			"gsm" : "",
			"phone" : "",
			"secretquestion" : "26",
			"secretanswer" : Util.randomword(15)
		}
			
		req = self.sess.post("https://account.ankama.com/fr/votre-compte/certification", data=postDatas)
		req = self.sess.post("https://account.ankama.com/fr/votre-compte/certification", data={"postBack" : "1", "certify" : "1"})
		
	def subscribeOneWeek(self):
		postDatas = {
			"unlock" : "1",
			"article" : "1000",
			"postback" : "add",
			"payment" : "OG"
		}
		
		req = self.sess.post("https://secure.dofus.com/fr/boutique/paiement", data=postDatas)
		try:
			re.search("ak\-success", req.text).group(0)
			return True
		except:
			return False
			
	def isSubscriber(self):
		req = self.sess.get("https://account.ankama.com/fr/votre-compte/dofus")
		
		if re.search(r"Temps de jeu restant", req.text):
			return True
		else:
			return False
	
class Autogrines:

	ACCOUNTS = []
	OFFERS = []
	THREADS = True
	TIME_START = time.time()
	WAITIME_SECONDS = 1
	VERSION = "141023.01"
	DEBUG = False
	TIME_CHECK_OGRINES = 2
	TIME_CHECK_SUBSCRIBE = 60 # check toutes les minutes
	TIME_REFRESH = 1
	CHECK_NEW_VERSIONS = True

	DOFUS_SERVERS = {
		36 : "Agride",
		29 : "Vil Smisse",
		28 : "Ulette",
		27 : "Goultard",
		26 : "Mylaise",
		20 : "Otomai",
		30 : "Many",
		21 : "Lily",
		18 : "Helsephine",
		25 : "Kuri",
		 1 : "Jiva",
		23 : "Hel Munster",
		16 : "Rykke-Errel",
		19 : "Allister",
		15 : "Amayiro",
		24 : "Danathor",
		13 : "Silouate",
		10 : "Silvosse",
		35 : "Farle",
		11 : "Brumaire",
		32 : "Crocoburio",
		12 : "Pouchecot",
		 4 : "Raval",
		14 : "Domen",
		 5 : "Hecate",
		17 : "Hyrkul",
		 3 : "Djaul",
		 6 : "Sumens",
		 9 : "Maimane",
		 7 : "Menalt",
		37 : "Bowisse",
		33 : "Li Crounch"
	}
	
	CONFIG_FILE = "autogrines.conf"

	def writeHeaders():
		print(" _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _")
		print("|     ___         __                   _                 |")
		print("|    /   | __  __/ /_____  ____ ______(_)___  ___  _____ |")
		print("|   / /| |/ / / / __/ __ \/ __ `/ ___/ / __ \/ _ \/ ___/ |")
		print("|  / ___ / /_/ / /_/ /_/ / /_/ / /  / / / / /  __(__  )  |")
		print("| /_/  |_\__,_/\__/\____/\__, /_/  /_/_/ /_/\___/____/   |")
		print("|                       /____/                           |")
		print("| Version " + Autogrines.VERSION + "                             By Toune |")
		print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
		print("\n")
		
	def loadConfiguration():
		file = open(Autogrines.CONFIG_FILE, 'r')
		contentFileUnparsed = file.read()
		file.close()

		contentParsed = json.loads(contentFileUnparsed)
		try:
			Autogrines.ACCOUNTS = DofusAccount.toDofusAccountsObjects(contentParsed["accounts"])
		except:
			print("Impossible de charger les comptes dans le fichier de configuration.")
			Util.stop()
		try:
			if int(contentParsed["debug_mode"]) == 1:
				Autogrines.DEBUG = True
		except AttributeError:
			Autogrines.DEBUG = False
		
		for account in Autogrines.ACCOUNTS:
			try:
				if contentParsed["cost_min_ogrine"]:
					account.cost_min_ogrine = contentParsed["cost_min_ogrine"]
				if contentParsed["cost_max_ogrine"]:
					account.cost_max_ogrine = contentParsed["cost_max_ogrine"]
				if contentParsed["max_ogrines"]:
					account.max_ogrines = contentParsed["max_ogrines"]
			except AttributeError:
				continue
			except KeyError:
				continue
				
	def start():
		Util.clear()
		Autogrines.writeHeaders()
		
		if Updater.checkVersion() and Autogrines.CHECK_NEW_VERSIONS:
			response = input("Une nouvelle version d'autogrines est disponible, voulez vous la telecharger ? \n[O]ui/[N]on ")
			if str.lower(response[0]) == "o":
				if Updater.doUpdate():
					Console.info("Telechargement termine !")
					Util.stop()
				else:
					Console.error("Impossible de telecharger la nouvelle version !")
		try:
			Autogrines.loadConfiguration()
		except FileNotFoundError:
			Console.error("Impossible de charger le fichier de configuration '{}'".format(Autogrines.CONFIG_FILE))
			Util.stop()
		except:
			Console.error("Impossible de parser le fichier de configuration.")
			Util.stop()
			
		if len(Autogrines.ACCOUNTS) == 0:
			Console.error("Aucun compte n'a ete charge, utilisez le fichier '{}' pour renseignez vos identifiants".format(Autogrines.CONFIG_FILE))
			Util.stop()
		
		nbrAccountsUnavailable = 0
		Console.title("-- Identification des comptes en cours ... --")
		print("")
		for account in Autogrines.ACCOUNTS:
			account.logged = False
			if not account.dofusRequest.identification():
				Console.debug("Compte '{}' : Le nom de compte et/ou le mot de passe est incorrect".format(account.account))
				nbrAccountsUnavailable += 1 
			else:
				Console.debug("Compte '{}' connecte".format(account.account))
				account.dofusRequest.choose_pseudo()
				account.dofusRequest.certify()
				Console.debug("Compte '{}' certification & pseudo. OK !".format(account.account))
				if account.dofusRequest.isSubscriber():
					Console.info("Compte '{}' : Abonne".format(account.account))
				else:
					Console.info("Compte '{}' : Non abonne".format(account.account))
					
				if not account.dofusRequest.choose_server():
					Console.debug("Compte '{}' : Impossible de choisir le serveur".format(account.account))
					nbrAccountsUnavailable += 1 
				else:
					account.logged = True
					
		if nbrAccountsUnavailable >= len(Autogrines.ACCOUNTS):
			Console.error("Aucun compte n'est connecte")
			Util.stop()
		else:
			Console.info("Les comptes sont connectes, demarrage des threads...")

			
		subscribeThread = threading.Thread(None, Autogrines.subscribeThread) 
		subscribeThread.start()
		checkOgrinesThread = threading.Thread(None, Autogrines.checkOgrinesThread)
		checkOgrinesThread.start()
		
		Autogrines.refreshThread()

	def subscribeThread():
		while Autogrines.THREADS:
			for account in Autogrines.ACCOUNTS:
				if not account.dofusRequest.isSubscriber():
					if account.dofusRequest.subscribeOneWeek():
						account.infos_console.append("Achat d'une semaine d'abonnement")		
			time.sleep(Autogrines.TIME_CHECK_SUBSCRIBE)
			
	def checkOffers():
		randAccount = random.randint(0,len(Autogrines.ACCOUNTS) - 1)
		Autogrines.OFFERS = Autogrines.ACCOUNTS[randAccount].dofusRequest.checkOffers()
			
	def checkOgrinesThread():
		while Autogrines.THREADS:
			for account in Autogrines.ACCOUNTS:
				if account.logged and not account.stopBuy and account.buy_ogrines:
					Autogrines.OFFERS = account.dofusRequest.checkOffers()
					if len(Autogrines.OFFERS['offers']) > 0:
						for offer in Autogrines.OFFERS['offers']:
							if not account.stopBuy:
								nbrOgrinesLeft = account.max_ogrines - account.totalOgrinesBought
								if int(offer['rate']) <= account.cost_max_ogrine and int(offer['rate']) >= account.cost_min_ogrine:
									if account.totalOgrinesBought < account.max_ogrines:
										if int(offer['sum']) < nbrOgrinesLeft:
											account.dofusRequest.buyOgrines(Autogrines.OFFERS['check_form'], int(offer['sum']), offer)
											account.totalOgrinesBought += int(offer['sum'])
											ogrinesBought = offer['sum']
											nbrKamas = int(offer['rate']) * int(offer['sum'])
										else:
											account.dofusRequest.buyOgrines(Autogrines.OFFERS['check_form'], nbrOgrinesLeft, offer)
											account.totalOgrinesBought += nbrOgrinesLeft
											nbrKamas = int(offer['rate']) * nbrOgrinesLeft
											ogrinesBought = nbrOgrinesLeft
											
										account.totalKamas += nbrKamas
										Autogrines.OFFERS = account.dofusRequest.checkOffers()
										
										account.infos_console.append("Achat " + str(ogrinesBought) + " ogrines pour " + str(nbrKamas) + " kamas (" + str(offer['rate']) + "kamas/u)")
									else:
										account.stopBuy = True
										account.infos_console.append("Vous avez acheter tous les ogrines.")
					else:
						Console.debug("WTF ?! Aucune offres disponible")
			time.sleep(Autogrines.TIME_CHECK_OGRINES)
			
	def refreshThread():
		
		Console.title("-- Demarrage dans 5 secondes ... --")
		time.sleep(5)
		Util.clear()
				
		while True:
			Autogrines.writeHeaders()
			Console.title2("-- {} --".format(Util.getDateNow()))
			
			try:
				print("Nbr offres : {}".format(len(Autogrines.OFFERS['offers'])))
				print("Cout actuel ogrine : {}".format(Autogrines.OFFERS['offers'][0]['rate']))
			except TypeError:
				print("")
		
			for account in Autogrines.ACCOUNTS:
				if account.logged:
					Console.title(account.account)
					
					if account.buy_ogrines:
						print("Cout min ogrine : {}".format(account.cost_min_ogrine))
						print("Cout max ogrine : {}".format(account.cost_max_ogrine))
						print("Nbr ogrines : {}/{}".format(account.totalOgrinesBought, account.max_ogrines))
						
					if len(account.infos_console) > 0:
						print("\n")
						for info in account.infos_console:
							print(info)
						print("\n")
				
			time.sleep(Autogrines.TIME_REFRESH)
			Util.clear()

class Updater:

	NEW_VERSION = ""

	def checkVersion():
		req = requests.get("http://redoxtools.no-ip.org/autogrines/version.txt")
		if req.text != Autogrines.VERSION:
			Updater.NEW_VERSION = req.text
			return True
		return False


	def doUpdate():
		fileName = "AutOgrines_" + Updater.NEW_VERSION + ".zip"
		with open(fileName, 'wb') as handle:
				print("Telechargement de la nouvelle version en cours ...")
				response = requests.get("http://redoxtools.no-ip.org/autogrines/" + fileName, stream=True)

				if not response.ok:
					return False

				for block in response.iter_content(1024):
						if not block:
							break
						handle.write(block)
				return True

			
if __name__ == "__main__":
	try:
		Autogrines.start()
	except requests.exceptions.ConnectionError:
		Console.error("Impossible de se connecter au site de Dofus.\nVerifiez votre connexion a Internet.")
	except KeyboardInterrupt:
		print("Bye bye")
		Autogrines.THREADS = False