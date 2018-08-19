Bienvenue dans le guide d'utilisation de topic_dler !

Ce script est développé et maintenu pour l'élite de la nation. Tout utilisateur en dessous de la moyenne basse du forum est prié de fermer ce document, de retourner méditer dans sa médiocrité.


1.PRINCIPE

Cette application a pour objectif le "minage" de topics de n'importe quel forum jeuxvideo.com (+JVParallele) c-à-d le téléchargement automatique de tout type de ressource postée sur un topic : images (stickers ou autre), webm cachée derrière un URL, vocaroo mais également les posts en eux-mêmes et les risitas.
L'idée générale étant de télécharger localement tout ce qu'on peut tirer du topic (toutes les pages sont parcourues automatiquement) à partir d'un URL d'une des pages que vous fournissez.
L'application inclut également une part d'intelligence pour le tri automatique des stickers si désiré, ou même la détection des posts étant un chapitre de risitas.

Si vous le désirez vous pouvez donc carrément télécharger le topic en entier ! (toutes les pages sont alors rassemblées bout à bout dans un fichier HTML (page internet) que vous obtenez en local, donc reconsultable même si le topic est 410!).


2.FONCTIONNALITES

L'interface graphique est complète, vous ne devez saisir que l'URL d'une des pages du topic pour lancer la collecte automatique de tout ce que vous ciblez, déterminé par les options ci-bas.

 2.1 RESSOURCES
    -images/stickers : vous pouvez choisir d'activer le tri automatique et ne dl que les images qui ne sont pas des stickers, ou juste ceux-ci. Le slider à droite indique à quel point l'IA doit travailler pour trier, donc demander plus de ressources à votre processeur. Mais vous pouvez le laisser à 1, c'est très rapide au final !
    -webm : le script tentera de dl les webm données par des URL dans les posts du topic
    -vocaroo : si un lien vers le site vocaroo.com est donné, dl le son en .mp3
    -posts : créera une page HTML en local avec tous les posts des forumeurs sélectionnés sur le topic (incluant images noelshack clickables, même si topic 410 bien sur!)
    -RISITAS : utilise une IA pour trier et ne garder que les posts qui sont des chapitres de l'histoire, et en crée une page HTML. Vous pourrez lire tout le récit de l'op sans interruption !


 2.2 DOSSIER CIBLE
    Puisque le script va dl tout ce que vous voulez, vous pouvez indiquer le dossier cible dans lequel les ressources seront placées, ou si vous ne donnez rien ce sera là ou l'appli est lancée. Si <nouveau dossier>, tout sera placé dans un sous-dossier au nom du topic et si <post-ouverture> et sous Windows, ouvrira l'explorateur de base là où tout a été dl à la fin.

 2.3 FORUMEURS CIBLES
    Si seuls les posts de quelques kheys vous intéressent (en particulier l'op pour lequel vous avez un raccourci) vous pouvez rentrer leurs pseudos dans la fenêtre contextuelle ouverte par le bouton <autres>. Le script ne fera ses recherches que dans ces posts sélectionnés, ou dans tous si aucun n'est spécifié.

 2.4 DIVERS
    -<abréviations> : les noms de fichiers depuis noelshack etc. sont souvent longs et réduisent la visibilité dans votre gallerie. Cette option les écourte grandement pour que ce soit plus propre
    -<verbeux> : affiche ou non les infos au cours de l'exécution du script (joli mais utile aussi)
    -<noms auto> : les fichiers se verront attribuer des noms automatiques en fonction de l'ordre de leur dl
    -slider <puissance> : désigne l'acharnement du script pour récupérer une ressource qui n'est pas retournée par le serveur la 1ere fois parce qu'il boude. Mettez à 1 pour que le script ne lache rien !

Copiez/collez l'url d'une page du topic sur lequel vous voulez lancer le script avez vos options, appuyez sur go et allez vous astiquer le jonc le temps qu'il travaille !


3.TRUCS SYMPAS
    3.1 Multi-threading : vous pouvez lancer le script sur plusieurs topics en même temps ! Une fenêtre s'ouvrira pour chaque thread affichant la progression pour le topic lié !

    3.2 Adaptation à JVParallel
        Malheureusement l'utilisation n'est pas aussi simple. Vous allez devoir enregistrer la page du topic localement avant d'appliquer le script dessus (la page résultant parès l'exécution du Javascript lié à JVP). 
        Pour cela utilisez l'extension Firefox Save Page WE : https://addons.mozilla.org/en-US/firefox/addon/save-page-we/
        Une fois le téléchargement de la page HTML fini, dans la barre à url c/c le chemin de ce fichier sur votre pc et lancez le script normalement (il n'ira pas sur toutes les pages du topic)

    3.3 Les images dl possèdent les données EXIF originales !

Bonne collecte les crays !

 
