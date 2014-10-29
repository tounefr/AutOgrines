# AutOgrines

AutOgrines est un utilitaire pour le jeu Dofus 2 permettant d'automatiser :
* **l'abonnement** : achat d'une semaine d'abonnement automatiquement
* **la certification d'un compte** par des informations généré aléatoirement
* **le choix d'un pseudo** : génère un pseudo aléatoirement.
* **l'achat d'ogrines** : vous entrez le prix minimum et maximum d'un ogrine que vous souhaitez acheter ainsi que le nombre d'ogrines maximum, le programme achetera l'offre dès qu'elle sera disponible sur le marché aux ogrines.

Autogrines fonctionne sur Windows (testé sur Win7), Linux (testé sur Ubuntu), et certainement sur Mac.

## Utilisation

* Exécutez *config.exe* pour configurer le programme. Suivez les instructions.  
  Un fichier *autogrines.conf* devrait être généré.
* Exécutez *autogrines.exe*

Pour ajouter un compte, exécutez à nouveau *config.exe*  
Pour supprimer un compte editez *autogrines.conf* ou supprimez le fichier.

## Compilation (Windows)

Autogrines utilise py2exe (http://www.py2exe.org/) pour générer un exécutable sur l'environnement Windows.

* Installez Python 3 sur le site officiel (https://www.python.org/)
* Installez Py2exe (voir site officiel py2exe)
* Ouvrez un cmd, dirigez vous vers le dossier Scripts
`cd C:\Python34\Scripts`
* Installez les dépendances
`pip install colorama requests termcolor`
* Compilez avec la commande suivante :
`build_exe autogrines.py -b 0 -c -i ctypes`  
L'exécutable vient d'être généré dans le dossier *dist*.

**Note** : vous devez placer le fichier *cacert.pem* à la racine de l'exécutable pour ne pas avoir de problèmes avec SSL.
