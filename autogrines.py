import requests
import sys
import time
import re
import json
import os

# Nom de compte Dofus
__dofus_account__ = None

# Mot de passe compte Dofus
__dofus_password__ = None

# Id du serveur de jeu
__server_id__ = None

# Prix minimum d'un ogrine à acheter
__cost_min_ogrine__ = None

# Prix maximum d'un ogrine à acheter
__cost_max_ogrine__ = None

# Nombre total d'ogrines à acheter
__max_ogrines__ = None

# Nom d'ogrines achetés depuis le lancement de Autogrines
__total_ogrines_bought__ = 0

# Nombre de kamas dépensés
__total_kamas__ = 0

# Serveurs de jeu
__dofus__servers__ = {
    "36" : "Agride",
    "29" : "Vil Smisse",
    "28" : "Ulette",
    "27" : "Goultard",
    "26" : "Mylaise",
    "20" : "Otomai",
    "30" : "Many",
    "21" : "Lily",
    "18" : "Helsephine",
    "25" : "Kuri",
    "1" : "Jiva",
    "23" : "Hel Munster",
    "16" : "Rykke-Errel",
    "19" : "Allister",
    "15" : "Amayiro",
    "24" : "Danathor",
    "13" : "Silouate",
    "10" : "Silvosse",
    "35" : "Farle",
    "11" : "Brumaire",
    "32" : "Crocoburio",
    "12" : "Pouchecot",
    "4" : "Raval",
    "14" : "Domen",
    "5" : "Hecate",
    "17" : "Hyrkul",
    "3" : "Djaul",
    "6" : "Sumens",
    "9" : "Maimane",
    "7" : "Menalt",
    "37" : "Bowisse",
    "33" : "Li Crounch"
}

# Temps écoulé depuis le lancement de Autogrines
__time_start__ = time.time()

# Temps entre 2 checks des offres d'ogrines
__waitimeInSeconds__ = 1

# Version
__version__ = "141015.01"

# debug mode
__DEBUG__ = False

# Variable pour les requêtes persistentes
__sess__ = requests.Session()
__sess__.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36"
cert ='cacert.pem'
# or os.environ['REQUESTS_CA_BUNDLE'] = cert 
os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.getcwd(), cert)

def getDateNow():
    return time.strftime("%H:%M:%S")
    
# Message de debug
def debug(text):
    if __DEBUG__:
        print(getDateNow() + " [DEBUG] " + text)

# Message d'information
def info(text):
    print(getDateNow() + " [INFO] " + text)

# Message important
def warning(text):
    print(getDateNow() + " [WARNING] " + text)

# Message d'erreur qui arrête le programme
def error(text):
    print(getDateNow() + " [FATAL ERROR] " + text)
    #sys.exit(-1)

# Procédure d'identification
def identification(login, password):
    req = __sess__.get("https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/identification");

    postDatas = {
      "action" : "login",
      "from" : "https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/identification",
      "login" : login,
      "password" : password,
      "remember" : 1
    }
    try:
        req = __sess__.post("https://account.ankama.com/sso", data=postDatas, cert="cacert.pem");
        if req.history[0].headers["Location"] == "https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/identification#loginfailed=failed":
            return False
    except IndexError:
        pass
    
    return True

# Après être identifié, on choisit le serveur par son id
def choose_server(id_serv):
    try:
        req = __sess__.post("https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/selection-serveur", data={"serverid" : id_serv}, cert="cacert.pem")
        if req.history[0].headers["Location"] == "https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/0-francaise":
            return req.text
    except IndexError:
        pass
    
    error("Impossible de choisir un serveur.")
    return False

# Récupère le nombre d'offres d'ogrines disponible
def checkOffers():
    req = __sess__.get("https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/0-francaise", cert="cacert.pem")
    check_form = re.search("\<input\ type\=\'hidden\'\ name\=\'check_form\'\ value\=\'(.*)\'\ \/\>", req.text).group(1)
    offersUnparsed = re.search("MarketPlace\.ActiveBid\((.*)\)\;", req.text).group(1)
    offersParsed = json.loads(offersUnparsed)
    
    return {
        'check_form' : check_form,
        'offers' : offersParsed['OGRINES']
    }

def buyOgrines(check_form, nbrOgrines, offer):
    postDatas = {
        'rate' : int(offer['rate']),
        'check_form' : check_form,
        'postback' : 1,
        'bak_from' : 'QuickBuy',
        'want' : nbrOgrines,
        'search' : nbrOgrines,
        'give' : int(offer['rate']) * nbrOgrines
    }
    req = __sess__.post("https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/0-francaise/achat-ogrines/acheter", data=postDatas, cert="cacert.pem")
    postDatas = {
        'postback' : 1,
        'confirm' : 1,
        'check_form' : check_form,
        'want' : nbrOgrines,
        'give' : int(offer['rate']) * nbrOgrines,
        'rate' : int(offer['rate']),
        'server' : __server_id__
    }

    req = __sess__.post("https://secure.dofus.com/fr/achat-bourses-kamas-ogrines/0-francaise/achat-ogrines/acheter", data=postDatas, cert="cacert.pem")

    if re.match("Les ogrines ont été crédités sur votre compte", req.text):
        return True
    
    return False

# entêtes
def writeHeaders():
    print(" _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _")
    print("|     ___         __                   _                 |")
    print("|    /   | __  __/ /_____  ____ ______(_)___  ___  _____ |")
    print("|   / /| |/ / / / __/ __ \/ __ `/ ___/ / __ \/ _ \/ ___/ |")
    print("|  / ___ / /_/ / /_/ /_/ / /_/ / /  / / / / /  __(__  )  |")
    print("| /_/  |_\__,_/\__/\____/\__, /_/  /_/_/ /_/\___/____/   |")
    print("|                       /____/                           |")
    print("| Version " + __version__ + "                             By Toune |")
    print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("\n")
                      
# Fonction de démarrage du programme    
def main():
    writeHeaders()
    
    global __dofus_account__, __dofus_password__, __server_id__, __cost_min_ogrine__, __cost_max_ogrine__, __max_ogrines__, __dofus__servers__
    if len(sys.argv) > 1:
        for arg, argValue in enumerate(sys.argv):
            if arg[2:] == "account":
                __dofus_account__ = argValue
            elif arg[2:] == "password":
                __dofus_password__ = argValue
            elif arg[2:] == "cost-min-ogrine":
                __cost_min_ogrine__ = int(argValue)
            elif arg[2:] == "cost-max-ogrine":
                __cost_max_ogrine__ = int(argValue)
            elif arg[2:] == "max-ogrines":
                __max_ogrines__ = argValue
            elif arg[2:] == "serverid":
                __server_id__ = argValue
                
    if __dofus_account__ is None:
        __dofus_account__ = input("Entrez votre nom de compte : ")
    if __dofus_password__ is None:
        __dofus_password__ = input("Entrez votre mot de passe : ")
    if __cost_min_ogrine__ is None:
        __cost_min_ogrine__ = int(input("Entrez le prix minimum d'un ogrine a acheter : "))
    if __cost_max_ogrine__ is None:
        __cost_max_ogrine__ = int(input("Entrez le prix maximum d'un ogrine a acheter : "))
    if __max_ogrines__ is None:
        __max_ogrines__ = int(input("Entrez le nombre maximum d'ogrines a acheter : "))

    if __server_id__ is None:
        for k,v in __dofus__servers__.items():
            print(v + ". " + k)
        __server_id__ = int(input("\nEntrez l'id de votre serveur : "))
        print("")
    
    startAutogrines()
    input("")

# Temps écoulé depuis le lancement de Autogrines
def timeLeft():
    return str(int(time.time() - __time_start__));

# Démarrage du programme après initialisation
def startAutogrines():
    global __total_ogrines_bought__
    global __total_kamas__
    
    try:
        if(identification(__dofus_account__, __dofus_password__)):
            info("Vous etes connecte !")
        else:
            error("Le nom de compte et/ou le mot de passe est incorrect !")
            return

        responseChooseServer = choose_server(__server_id__)
        if type(responseChooseServer) is str:    
            info("Vous avez choisis le serveur : " + str(__dofus__servers__[str(__server_id__)]) + "\n")
        else:
            error("Impossible de choisir un serveur !\n")
            return
        
        crtTime = 30
        purchases = []
        
        while __total_ogrines_bought__ < __max_ogrines__:
            offers = checkOffers()
            nbrOffersAvailable = len(offers['offers'])
			
            if nbrOffersAvailable > 0:
                for offer in offers['offers']:
                    nbrOgrinesLeft = __max_ogrines__ - __total_ogrines_bought__

                    if (int(time.time()) - crtTime) >= 30:
                        print("")
                        info("Nbr offres : {}".format(nbrOffersAvailable))
                        info("Cout min ogrine : {}".format(__cost_min_ogrine__))
                        info("Cout max ogrine : {}".format(__cost_max_ogrine__))
                        info("Nbr ogrines {}/{}".format(__total_ogrines_bought__, __max_ogrines__))
                        info("Cout actuel ogrine : {}".format(offers['offers'][0]['rate']))
                        print("")
                        crtTime = time.time()
                    
                    # vérifie le prix de l'ogrine
                    if int(offer['rate']) <= __cost_max_ogrine__ and int(offer['rate']) >= __cost_min_ogrine__:
                        # vérifie qu'on a pas déjà tout acheté
                        if __total_ogrines_bought__ < __max_ogrines__:
                            if int(offer['sum']) < nbrOgrinesLeft:
                                buyOgrines(offers['check_form'], int(offer['sum']), offer)
                                __total_ogrines_bought__ = __total_ogrines_bought__ + int(offer['sum'])
                                ogrinesBought = offer['sum']
                                nbrKamas = int(offer['rate']) * int(offer['sum'])
                                
                            else:
                                buyOgrines(offers['check_form'], nbrOgrinesLeft, offer)
                                __total_ogrines_bought__ = __total_ogrines_bought__ + nbrOgrinesLeft
                                nbrKamas = int(offer['rate']) * nbrOgrinesLeft
                                ogrinesBought = nbrOgrinesLeft

                            purchases.append({
                                'time' : getDateNow(),
                                'ogrines' : ogrinesBought,
                                'kamas' : nbrKamas
                            })
                            __total_kamas__ = __total_kamas__ + nbrKamas
                            
                            info("Achat " + str(ogrinesBought) + " ogrines pour " + str(nbrKamas) + " kamas (" + str(offer['rate']) + "kamas/u)")
                        else:
                            info("Vous avez acheter tous les ogrines.")
                            print("\n\n")
                            if len(purchases) > 0:
                                info("Resume des achats :")
                                for purchase in purchases:
                                    info("Date : " + str(purchase['time']) + " Nbr ogrines : " + str(purchase['ogrines']) + " Nbr Kamas : " + str(purchase['kamas']))
                                print("\n\n" + timeLeft() + " secondes ecoulees")
                                break
            else:
                debug("Aucune offres disponible.")
            time.sleep(__waitimeInSeconds__)
                
        
    except KeyboardInterrupt:
        print("\n\n")
        if len(purchases) > 0:
            info("Resume des achats :")
            for purchase in purchases:
                info("Date : " + str(purchase['time']) + " Nbr ogrines : " + str(purchase['ogrines']) + " Nbr Kamas : " + str(purchase['kamas']))
                
        print("\n\n" + timeLeft() + " secondes ecoulees")            
        print("ByeBye")
    
if __name__ == "__main__":
    main()
