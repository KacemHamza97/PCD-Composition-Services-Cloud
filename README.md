# PCD-Composition-Services-Cloud

Le module cloud.py comportera 3 classes : produit , service , workflow 


#######  Classe Produit  #######

la classe produit correspond à un produit utilisé dans un service .
on peut calculer le prix de ce produit à partir de la méthode getPrice() à partir des attribut unitNumber et unitPrice déja fournis en paramètre dans le constructeur.

####### Classe Service ########

la classe Service correspond à un service cloud construit ayant une activité correspondante ( indicée de 1 à n ) , un temps de réponse , une fiabilité , une diponibilité , une liste de produit , et un degrée de matching . tous ces paramètres sont fournis dans le constructeur .

Deux services sont candidats à une même activité d'indice x si leurs attributs activité = x

La classe service possède une méthode euclideanDist qui calcule la distance euclidéenne entre deux services donnés 

####### Classe WorkFlow #######

un objet de classe WorkFlow est construit à partir d'une rootServ ( service affectée à la première activité ) et un servGraph ( liste des (arcs = listes) ) 

chaque arc est sous la forme [S1 , S2 , type=0,1,-1] 
avec 0 : séquenciel 
	 1 : parallèle
	-1 : conditionnel
	
cette classe possède un attribut servSet qui correspond à l'ensemble des services dans ce flux

cette classe possède un attribut Graph qui correspond à un dictionnaire où les clés sont des services sources et les valeurs sonts des listes des arcs connectés à cette clé 

cette classe possède des méthodes de calcul récursives des critères de QoS et une méthode qui calcule la QoS en générale 

cette classe possède une méthode qui calcule le degré de matching

cette classe possède une méthode qui fait la mutation d'un service cible dans le flux par un autre donné de même activité

cette classe possède un attribut qui génère aléatoirement un service de ce flux 

#########################################"


Le module cloud comporte aussi une fonction randomWorkFlow qui à partir d'
-un rootAct ( indice de la première activité ) 
-actGraph( liste des arcs sous la forme [ A1 , A2  , type ]
-services (liste des listes) : chaque indice de sous liste correspond à une activité , et cette sous liste comporte les services candidats pour cette activité.

génère un flux de contrôle aléatoire en substituant les activités par des services correspondants.

#########################################
Le module cloud comporte aussi une fonction crossover qui à partir de deux flux parents crée un flux fils en faisant une copie du premier parent et des mutations de probabilité 0.5 sur toutes les services qui le composent par les services correspondants dans le deuxième parent. ( uniforme )

#########################################

Le module hybrid.py comporte une fonction getNeighbors qui retourne à partir d'un service donné la liste des services candidats qui peuvent le remplacer dans l'ordre decroissant des distances euclidéennes .

le module hybrid comporte aussi une fonction f qui prend en paramètre un flux de contrôle et retourne la somme de sa QoS et de son degré de matching global .


le modèle comporte aussi la fonction ABCgenetic