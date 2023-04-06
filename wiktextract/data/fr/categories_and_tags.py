"""
These lists are used to determine which templates of the French Wiktionary refer to categories or (grammatical) tags. 

For easier assignment, the category or tag names (as it will be extracted) and the expanded template are included as comments.

These lists were "farmed" from error messages of the Wiktionary parser. They are not complete, but they are a good start.
"""

# Templates used to refer to topical categories
french_category_templates = [
"Acadie",                       # Acadie                               (Acadie)Catégorie:français d’Acadie
"affectueux",                   # Affectueux                           (Affectueux)Catégorie:Mots affectueux en français
"Afghanistan",                  # Afghanistan                          (Afghanistan)Catégorie:français d’Afghanistan
"Afrique de l’Ouest",           # Afrique de l’Ouest                   (Afrique de l’Ouest)Catégorie:français d’Afrique de l’Ouest
"Afrique du Sud",               # Afrique du Sud                       (Afrique du Sud)Catégorie:français d’Afrique du Sud
"Afrique",                      # Afrique                              (Afrique)
"Afrique",                      # Afrique                              (Afrique)Catégorie:français d’Afrique
"agrumes",                      # Botanique                            (Botanique)Catégorie:Agrumes en français
"alcaloïdes",                   # Chimie                               (Chimie)Catégorie:Alcaloïdes en français
"alcools",                      # Boisson                              (Boisson)Catégorie:Boissons alcoolisées en français
"Algérie",                      # Algérie                              (Algérie)Catégorie:français d’Algérie
"algues",                       # Phycologie                           (Phycologie)Catégorie:Algues en français
"aliments",                     # Cuisine                              (Cuisine)Catégorie:Aliments en français
"alliages",                     # Chimie                               (Chimie)Catégorie:Alliages en français
"Alsace",                       # Alsace                               (Alsace)Catégorie:français d’Alsace
"Amérique du Nord",             # Amérique du Nord                     (Amérique du Nord)Catégorie:français d’Amérique du Nord
"Amérique du Sud",              # Amérique du Sud                      (Amérique du Sud)
"amphibiens",                   # Zoologie                             (Zoologie)Catégorie:Amphibiens en français
"anciennes divisions",          # Histoire                             (Histoire)Catégorie:Anciennes divisions géographiques en français
"anciennes localités",          # Histoire                             (Histoire)Catégorie:Anciennes localités en français
"Andorre",                      # Andorre                              (Andorre)Catégorie:français d’Andorre
"anglicisme informatique",      # Anglicisme informatique              (Anglicisme informatique)Catégorie:Anglicismes informatiques en français
"anglicismes informatiques",    # Anglicisme informatique              (Anglicisme informatique)Catégorie:Anglicismes informatiques en français
"animaux",                      # Zoologie                             (Zoologie)
"animaux",                      # Zoologie                             (Zoologie)Catégorie:Animaux imaginaires en français
"Anjou",                        # Anjou                                (Anjou)
"Anjou",                        # Anjou                                (Anjou)Catégorie:français d’Anjou
"Antilles",                     # Antilles                             (Antilles)Catégorie:français des Antilles
"antilopes",                    # Zoologie                             (Zoologie)Catégorie:Antilopes en français
"appareils",                    # Électroménager                       (Électroménager)Catégorie:Appareils électroménagers en français
"application",                  # Couche application                   (Couche application)Catégorie:Protocoles réseaux en français
"Aquitaine",                    # Aquitaine                            (Aquitaine)Catégorie:français d’Aquitaine
"araignées",                    # Zoologie                             (Zoologie)Catégorie:Araignées en français
"arbres",                       # Botanique                            (Botanique)
"arbres",                       # Botanique                            (Botanique)Catégorie:Arbres en français
"Ardèche",                      # Ardèche                              (Ardèche)Catégorie:français de l’Ardèche
"Ardennes",                     # Ardennes                             (Ardennes)Catégorie:français des Ardennes
"Argadz",                       # Argot des Gadz’Arts                  (Argot des Gadz’Arts)Catégorie:Argot de l’école nationale supérieure des Arts et Métiers en français
"argot de l’université Paris-Cité", # Argot de l’université Paris-Cité     (Argot de l’université Paris-Cité)Catégorie:Argot de l’université Paris-Cité en français
"argot de la Famille",          # Argot de la Famille                  (Argot de la Famille)Catégorie:Argot de la Famille en français
"argot internet",               # Argot Internet                       (Argot Internet)Catégorie:Argot Internet en français
"argot Internet",               # Argot Internet                       (Argot Internet)Catégorie:Argot Internet en français
"argot militaire",              # Argot militaire                      (Argot militaire)Catégorie:Argot militaire en français
"argot poilu",                  # Argot poilu                          (Argot poilu)Catégorie:Argot poilu en français
"argot policier",               # Argot policier                       (Argot policier)Catégorie:Argot policier en français
"argot scolaire",               # Argot scolaire                       (Argot scolaire)Catégorie:Argot scolaire en français
"argot typographes",            # Argot des typographes                (Argot des typographes)Catégorie:Argot des typographes en français
"argot voleurs",                # Argot des voleurs                    (Argot des voleurs)Catégorie:Argot des voleurs en français
"armes",                        # Armement                             (Armement)Catégorie:Armes à feu en français
"armures",                      # Armurerie                            (Armurerie)Catégorie:Armures en français
"aromates",                     # Aromate                              (Aromate)Catégorie:Aromates en français
"arrondissements",              # Géographie                           (Géographie)Catégorie:Arrondissements du Viêt Nam en français
"arthropodes",                  # Zoologie                             (Zoologie)Catégorie:Arthropodes en français
"artistes",                     # Art                                  (Art)*
"artistes",                     # Art                                  (Art)Catégorie:Artistes en français
"arts martiaux",                # Arts martiaux                        (Arts martiaux)Catégorie:Arts martiaux en français
"Asie centrale",                # Asie centrale                        (Asie centrale)
"Asie",                         # Asie                                 (Asie)Catégorie:français d’Asie
"Astérix",                      # Univers d’Astérix                    (Univers d’Astérix)Catégorie:Astérixologie en français
"atomes",                       # Chimie                               (Chimie)Catégorie:Atomes en français
"Aube",                         # Aube                                 (Aube)Catégorie:champenois de l’Aube
"Australie",                    # Australie                            (Australie)
"Australie",                    # Australie                            (Australie)Catégorie:anglais d’Australie
"Autunois",                     # Autunois                             (Autunois)Catégorie:français de l’Autunois
"Auvergne",                     # Auvergne                             (Auvergne)Catégorie:français d’Auvergne
"avions",                       # Aéronautique                         (Aéronautique)Catégorie:Avions en français
"bactéries",                    # Bactériologie                        (Bactériologie)Catégorie:Bactéries en français
"bateaux",                      # Navigation                           (Navigation)Catégorie:Bateaux en français
"BE",                           # Belgique                             (Belgique)Catégorie:français de Belgique
"Beaujolais",                   # Beaujolais                           (Beaujolais)Catégorie:français du Beaujolais
"Belgique",                     # Belgique                             (Belgique)Catégorie:français de Belgique
"Bénin",                        # Bénin                                (Bénin)Catégorie:français du Bénin
"Berry",                        # Berry                                (Berry)Catégorie:français du Berry
"bières",                       # Bière                                (Bière)Catégorie:Bières en français
"bivalves",                     # Malacologie                          (Malacologie)Catégorie:Bivalves en français
"boissons",                     # Boisson                              (Boisson)Catégorie:Boissons en français
"Bordelais",                    # Bordelais                            (Bordelais)Catégorie:français du Bordelais
"Bourbonnais",                  # Bourbonnais                          (Bourbonnais)Catégorie:français du Bourbonnais
"Bourgogne",                    # Bourgogne                            (Bourgogne)Catégorie:français de Bourgogne
"bovins",                       # Zoologie                             (Zoologie)Catégorie:Bovins en français
"Bray",                         # Pays de Bray                         (Pays de Bray)Catégorie:français du pays de Bray
"Brésil",                       # Brésil                               (Brésil)
"Brésil",                       # Brésil                               (Brésil)Catégorie:portugais du Brésil
"Bretagne celtique",            # Bretagne celtique                    (Bretagne celtique)Catégorie:français de Bretagne celtique
"Bretagne",                     # Bretagne                             (Bretagne)
"Bretagne",                     # Bretagne                             (Bretagne)Catégorie:français de Bretagne
"Bruxelles",                    # Bruxellois                           (Bruxellois)Catégorie:français de Bruxelles
"Burkina Faso",                 # Burkina Faso                         (Burkina Faso)Catégorie:français du Burkina Faso
"Burundi",                      # Burundi                              (Burundi)Catégorie:français du Burundi
"CA",                           # Canada                               (Canada)Catégorie:français du Canada
"calendrier",                   # Chronologie                          (Chronologie)Catégorie:Calendrier en français
"Cambodge",                     # Cambodge                             (Cambodge)Catégorie:français du Cambodge
"camélidés",                    # Zoologie                             (Zoologie)Catégorie:Camélidés en français
"Cameroun",                     # Cameroun                             (Cameroun)Catégorie:français du Cameroun
"Canada",                       # Canada                               (Canada)Catégorie:français du Canada
"canards",                      # Ornithologie                         (Ornithologie)Catégorie:Canards en français
"canidés",                      # Mammifères                           (Mammifères)Catégorie:Canidés en français
"capitales",                    # Géographie                           (Géographie)Catégorie:Capitales en français
"caprins",                      # Zoologie                             (Zoologie)Catégorie:Caprins en français
"carnivore",                    # Zoologie                             (Zoologie)
"carnivore",                    # Zoologie                             (Zoologie)Catégorie:Carnivores en français
"carnivores",                   # Zoologie                             (Zoologie)Catégorie:Carnivores en français
"Caux",                         # Pays de Caux                         (Pays de Caux)Catégorie:français du pays de Caux
"Centrafrique",                 # Centrafrique                         (Centrafrique)Catégorie:français de République centrafricaine
"cépages",                      # Viticulture                          (Viticulture)Catégorie:Cépages en français
"céphalopodes",                 # Malacologie                          (Malacologie)Catégorie:Céphalopodes en français
"céréales",                     # Botanique                            (Botanique)Catégorie:Céréales en français
"cervidés",                     # Zoologie                             (Zoologie)Catégorie:Cervidés en français
"cétacés",                      # Mammalogie                           (Mammalogie)Catégorie:Cétacés en français
"CH",                           # Suisse                               (Suisse)Catégorie:français de Suisse
"chaînes de montagnes",         # Géographie                           (Géographie)Catégorie:Chaînes de montagnes en français
"chameaux",                     # Zoologie                             (Zoologie)Catégorie:Chameaux en français
"Champagne",                    # Champagne                            (Champagne)Catégorie:français de Champagne
"champignon",                   # Mycologie                            (Mycologie)Catégorie:Champignons en français
"champignons",                  # Mycologie                            (Mycologie)Catégorie:Champignons en français
"Charente-Maritime",            # Charente-Maritime                    (Charente-Maritime)Catégorie:français de la Charente-Maritime
"Charentes",                    # Charentes                            (Charentes)Catégorie:français des Charentes
"Châtellerault",                # Châtellerault                        (Châtellerault)Catégorie:tourangeau de Châtellerault
"chats",                        # Zoologie                             (Zoologie)Catégorie:Chats en français
"chaussures",                   # Vêtement                             (Vêtement)Catégorie:Chaussures en français
"chauves-souris",               # Zoologie                             (Zoologie)Catégorie:Chauves-souris en français
"chênes",                       # Botanique                            (Botanique)Catégorie:Chênes en français
"Chenou",                       # Chenou                               (Chenou)Catégorie:français de Chenou
"chevaux",                      # Zoologie                             (Zoologie)Catégorie:Chevaux en français
"chiens",                       # Zoologie                             (Zoologie)Catégorie:Chiens en français
"Chine",                        # Chine                                (Chine)
"CM",                           # Cameroun                             (Cameroun)Catégorie:français du Cameroun
"cnidaires",                    # Zoologie                             (Zoologie)Catégorie:Cnidaires en français
"cocktails",                    # Boisson                              (Boisson)Catégorie:Cocktails en français
"coléoptères",                  # Entomologie                          (Entomologie)Catégorie:Coléoptères en français
"Combrailles",                  # Combrailles                          (Combrailles)Catégorie:français des Combrailles
"commerces",                    # Commerce                             (Commerce)Catégorie:Commerces en français
"Commonwealth",                 # Commonwealth                         (Commonwealth)
"Commonwealth",                 # Commonwealth                         (Commonwealth)Catégorie:français du Commonwealth
"composants électriques",       # Électricité                          (Électricité)
"composants électriques",       # Électricité                          (Électricité)Catégorie:Composants électriques en français
"composants électroniques",     # Électronique                         (Électronique)Catégorie:Composants électroniques en français
"composants",                   # Électronique                         (Électronique)Catégorie:Composants électroniques en français
"comtés",                       # Géographie                           (Géographie)Catégorie:Comtés de l’Alabama en français
"condiments",                   # Cuisine                              (Cuisine)Catégorie:Condiments en français
"confiserie",                   # Confiserie                           (Confiserie)Catégorie:Confiseries en français
"confiseries",                  # Confiserie                           (Confiserie)Catégorie:Confiseries en français
"Congo-Brazzaville",            # Congo-Brazzaville                    (Congo-Brazzaville)Catégorie:français du Congo-Brazzaville
"Congo-Kinshasa",               # Congo-Kinshasa                       (Congo-Kinshasa)Catégorie:français du Congo-Kinshasa
"conifères",                    # Botanique                            (Botanique)Catégorie:Conifères en français
"constellations",               # Astronomie                           (Astronomie)*
"constellations",               # Astronomie                           (Astronomie)Catégorie:Constellations en français
"contexte",                     # Musique, hapax                       (Musique, hapax)
"continents",                   # Géographie                           (Géographie)Catégorie:Continents en français
"coquillages",                  # Coquillage                           (Coquillage)Catégorie:Coquillages en français
"Corée du Nord",                # Corée du Nord                        (Corée du Nord)
"Corse",                        # Corse                                (Corse)Catégorie:français de Corse
"Côte d'Ivoire",                # Côte d’Ivoire                        (Côte d’Ivoire)Catégorie:français de Côte d’Ivoire
"Côte d’Ivoire",                # Côte d’Ivoire                        (Côte d’Ivoire)Catégorie:français de Côte d’Ivoire
"Côte-d’Ivoire",                # Côte d’Ivoire                        (Côte d’Ivoire)Catégorie:français de Côte d’Ivoire
"Cotentin",                     # Cotentin                             (Cotentin)Catégorie:français du Cotentin
"couche application",           # Couche application                   (Couche application)Catégorie:Protocoles réseaux en français
"couche liaison",               # Couche liaison                       (Couche liaison)Catégorie:Protocoles réseaux en français
"couche physique",              # Couche physique                      (Couche physique)Catégorie:Protocoles réseaux en français
"couche présentation",          # Couche présentation                  (Couche présentation)Catégorie:Protocoles réseaux en français
"couche réseau",                # Couche réseau                        (Couche réseau)Catégorie:Protocoles réseaux en français
"couche session",               # Couche session                       (Couche session)Catégorie:Protocoles réseaux en français
"couche transport",             # Couche transport                     (Couche transport)Catégorie:Protocoles réseaux en français
"couleurs",                     # Colorimétrie                         (Colorimétrie)Catégorie:Couleurs en français
"cours d’eau",                  # Géographie                           (Géographie)
"cours d’eau",                  # Géographie                           (Géographie)Catégorie:Cours d’eau de France en français
"couteaux",                     # Couteaux                             (Couteaux)Catégorie:Couteaux en français
"couverture",                   # Couvertures                          (Couvertures)Catégorie:Couvertures en français
"couvertures",                  # Couvertures                          (Couvertures)Catégorie:Couvertures en français
"couvre-chefs",                 # Habillement                          (Habillement)Catégorie:Couvre-chefs en français
"crabes",                       # Zoologie                             (Zoologie)Catégorie:Crabes en français
"crapauds",                     # Zoologie                             (Zoologie)Catégorie:Crapauds en français
"créatures",                    # Mythologie                           (Mythologie)Catégorie:Créatures mythologiques en français
"crimes",                       # Droit                                (Droit)Catégorie:Crimes et délits en français
"criminels",                    # Droit                                (Droit)Catégorie:Criminels et délinquants en français
"crustacés",                    # Carcinologie                         (Carcinologie)Catégorie:Crustacés en français
"cygnes",                       # Ornithologie                         (Ornithologie)Catégorie:Cygnes en français
"danses",                       # Danse                                (Danse)Catégorie:Danses en français
"Dauphiné",                     # Dauphiné                             (Dauphiné)Catégorie:français du Dauphiné
"délinquants",                  # Droit                                (Droit)Catégorie:Criminels et délinquants en français
"délits",                       # Droit                                (Droit)Catégorie:Crimes et délits en français
"dénombrable",                  # Dénombrable                          (Dénombrable)Catégorie:Noms dénombrables en français
"départements",                 # Géographie                           (Géographie)Catégorie:Départements de Colombie en français
"déserts",                      # Géographie                           (Géographie)Catégorie:Déserts en français
"desserts",                     # Cuisine                              (Cuisine)Catégorie:Desserts en français
"détroit",                      # Géographie                           (Géographie)Bismarck
"détroit",                      # Géographie                           (Géographie)Catégorie:Détroits en français
"détroits",                     # Géographie                           (Géographie)Catégorie:Détroits en français
"dévanâgarî",                   # Linguistique                         (Linguistique)Catégorie:Alphabet dévanâgarî en français
"diacritiques",                 # Grammaire                            (Grammaire)Catégorie:Diacritiques en français
"dialectes",                    # Dialectologie                        (Dialectologie)Catégorie:Dialectes en français
"didactique",                   # Didactique                           (Didactique)
"didactique",                   # Didactique                           (Didactique)Catégorie:Termes didactiques en français
"Dijonnais",                    # Dijonnais                            (Dijonnais)
"dindons",                      # Zoologie                             (Zoologie)Catégorie:Dindons en français
"dinosaures",                   # Paléontologie                        (Paléontologie)Catégorie:Dinosaures en français
"distinctions",                 # Distinction                          (Distinction)Catégorie:Distinctions en français
"divinités",                    # Divinité                             (Divinité)Catégorie:Divinités en français
"documents",                    # Média                                (Média)Catégorie:Documents en français
"Dominique",                    # Dominique                            (Dominique)Catégorie:français de la Dominique
"doute",                        # information à préciser ou à vérifier  (information à préciser ou à vérifier)Catégorie:Pages à vérifier en français
"drogues",                      # Pharmacologie                        (Pharmacologie)Catégorie:Drogues en français
"Drôme",                        # Drôme                                (Drôme)Catégorie:français de la Drôme
"Dunkerque",                    # Dunkerque                            (Dunkerque)Catégorie:français de Dunkerque
"échinodermes",                 # Zoologie                             (Zoologie)*
"échinodermes",                 # Zoologie                             (Zoologie)Catégorie:Échinodermes en français
"écouter",                      # Région à préciser                    (Région à préciser) : écouter « complétaitCatégorie:Prononciations audio en français //wiki.local/w/index.php?action=edit&title=compl%C3%A9tait Prononciation ?Catégorie:Wiktionnaire:Prononciations phonétiques manquantes en français »File:LL-Q150 (fra)-Manestra-complétait.wav
"écureuils",                    # Zoologie                             (Zoologie)Catégorie:Écureuils en français
"édifices",                     # Construction                         (Construction)Catégorie:Édifices en français
"Égypte",                       # Égypte                               (Égypte)
"Égypte",                       # Égypte                               (Égypte)Catégorie:français d’Égypte
"éléments",                     # Chimie                               (Chimie)Catégorie:Éléments chimiques en français
"éléphantidés",                 # Zoologie                             (Zoologie)Catégorie:Éléphantidés en français
"Empire ottoman",               # Empire ottoman                       (Empire ottoman)
"emploi",                       # En parlant d’un régime parlementaire  (En parlant d’un régime parlementaire)
"énallages",                    # Énallage                             (Énallage)Catégorie:Énallages en français
"enfantin",                     # Langage enfantin                     (Langage enfantin)Catégorie:Langage enfantin sans langue précisée
"enzymes",                      # Biochimie                            (Biochimie)Catégorie:Enzymes en français
"épices",                       # Cuisine                              (Cuisine)Catégorie:Épices en français
"équins",                       # Zoologie                             (Zoologie)*
"équins",                       # Zoologie                             (Zoologie)Catégorie:Équins en français
"Espagne",                      # Espagne                              (Espagne)Catégorie:espagnol d’Espagne
"établissements",               # Commerce                             (Commerce)Catégorie:Établissements de restauration en français
"États-Unis",                   # États-Unis                           (États-Unis)
"États-Unis",                   # États-Unis                           (États-Unis)Catégorie:anglais des États-Unis
"états",                        # État                                 (État)Catégorie:États du Brésil en français
"états",                        # État                                 (État)Pondichery
"Éthiopie",                     # Éthiopie                             (Éthiopie)Catégorie:français d’Éthiopie
"ethnonymes",                   # Ethnonymie                           (Ethnonymie)*
"ethnonymes",                   # Ethnonymie                           (Ethnonymie)Catégorie:Ethnonymes d’Afrique en français
"étoiles",                      # Astronomie                           (Astronomie)Catégorie:Étoiles en français
"EU",                           # Europe                               (Europe)Catégorie:français d’Europe
"Europe",                       # Europe                               (Europe)
"Europe",                       # Europe                               (Europe)Catégorie:français d’Europe
"familles de plantes",          # Botanique                            (Botanique)Catégorie:Familles de plantes en français
"félins",                       # Mammalogie                           (Mammalogie)Catégorie:Félins en français
"figure",                       # Rhétorique                           (Rhétorique)Catégorie:Figures de style en français
"figures",                      # Rhétorique                           (Rhétorique)Catégorie:Figures de style en français
"fleurs",                       # Botanique                            (Botanique)
"fleurs",                       # Botanique                            (Botanique)Catégorie:Fleurs en français
"formations musicales",         # Musique                              (Musique)Catégorie:Formations musicales en français
"FR-Cher",                      # Cher                                 (Cher)Catégorie:français du Cher
"FR",                           # France                               (France)Catégorie:français de France
"France",                       # France                               (France)
"France",                       # France                               (France)Catégorie:français de France
"Franche-Comté",                # Franche-Comté                        (Franche-Comté)Catégorie:français de Franche-Comté
"fromages",                     # Fromage                              (Fromage)
"fromages",                     # Fromage                              (Fromage)Catégorie:Fromages en français
"fruits",                       # Botanique                            (Botanique)
"fruits",                       # Botanique                            (Botanique)Catégorie:Fruits en français
"Gabon",                        # Gabon                                (Gabon)Catégorie:français du Gabon
"gallicisme",                   # Gallicisme                           (Gallicisme)Catégorie:Gallicismes en français
"Gascogne",                     # Gascogne                             (Gascogne)Catégorie:français de Gascogne
"Gaspésie",                     # Gaspésie                             (Gaspésie)Catégorie:français de Gaspésie
"gastéropodes",                 # Malacologie                          (Malacologie)Catégorie:Gastéropodes en français
"gâteaux",                      # Cuisine                              (Cuisine)Catégorie:Gâteaux en français
"généralement pluriel",         #  Ce terme est généralement utilisé au pluriel.Catégorie:Termes généralement pluriels en françai  Ce terme est généralement utilisé au pluriel.Catégorie:Termes généralement pluriels en français
"genres littéraires",           # Littérature                          (Littérature)Catégorie:Genres littéraires en français
"genres musicaux",              # Musique                              (Musique)Catégorie:Genres musicaux en français
"gentilés",                     # Géographie                           (Géographie)*
"gentilés",                     # Géographie                           (Géographie)Catégorie:Gentilés de France en français
"germanisme",                   # Germanisme                           (Germanisme)Catégorie:Germanismes en français
"Ghana",                        # Ghana                                (Ghana)Catégorie:français du Ghana
"giraffidés",                   # Zoologie                             (Zoologie)Catégorie:Giraffidés en français
"gladiateurs",                  # Antiquité                            (Antiquité)Catégorie:Gladiateurs en français
"golfes",                       # Géographie                           (Géographie)Catégorie:Golfes et baies en français
"grades",                       # Militaire                            (Militaire)Catégorie:Grades militaires en français
"Grèce",                        # Grèce                                (Grèce)Catégorie:français de Grèce
"Grenoble",                     # Grenoble                             (Grenoble)Catégorie:français de Grenoble
"grenouilles",                  # Zoologie                             (Zoologie)Catégorie:Grenouilles en français
"Guadeloupe",                   # Guadeloupe                           (Guadeloupe)Catégorie:français de Guadeloupe
"Guinée équatoriale",           # Guinée équatoriale                   (Guinée équatoriale)Catégorie:français de la Guinée équatoriale
"Guinée",                       # Guinée                               (Guinée)Catégorie:français de Guinée
"Guyane",                       # Guyane                               (Guyane)Catégorie:français de Guyane
"Haïti",                        # Haïti                                (Haïti)Catégorie:français d’Haïti
"hapax",                        # Hapax                                (Hapax)Catégorie:Hapax en français
"Haute-Marne",                  # Haute-Marne                          (Haute-Marne)Catégorie:champenois de la Haute-Marne
"hispanisme",                   # Hispanisme                           (Hispanisme)Catégorie:Hispanismes en français
"idiom",                        # Idiotisme                            (Idiotisme)
"idiotisme",                    # Idiotisme                            (Idiotisme)
"IDLMadeleine",                 # Îles-de-la-Madeleine                 (Îles-de-la-Madeleine)Catégorie:français des Îles-de-la-Madeleine
"Île-de-France",                # Île-de-France                        (Île-de-France)Catégorie:français d’Île-de-France
"îles",                         # Géographie                           (Géographie)Catégorie:Îles en français
"îles",                         # Géographie                           (Géographie)reine charlotte
"info lex",                     # Métrologie                           (Métrologie)
"injurieux",                    # Injurieux                            (Injurieux)
"injurieux",                    # Injurieux                            (Injurieux)Catégorie:Insultes en français
"insectes",                     # Entomologie                          (Entomologie)
"instruments à cordes",         # Musique                              (Musique)*
"instruments à cordes",         # Musique                              (Musique)Catégorie:Instruments à cordes en français
"instruments à vent",           # Musique                              (Musique)Catégorie:Instruments à vent en français
"instruments de mesure",        # Métrologie                           (Métrologie)Catégorie:Instruments de mesure en français
"instruments de musique",       # Musique                              (Musique)Catégorie:Instruments de musique en français
"instruments électroniques",    # Musique                              (Musique)Catégorie:Instruments électroniques en français
"instruments",                  # Musique                              (Musique)Catégorie:Instruments de musique en français
"insultes",                     # Insulte                              (Insulte)Catégorie:Insultes en français
"ironique",                     # Ironique                             (Ironique)
"italianisme",                  # Italianisme                          (Italianisme)Catégorie:Italianismes en français
"Japon",                        # Japon                                (Japon)
"Japon",                        # Japon                                (Japon)Catégorie:français du Japon
"Jersey",                       # Jersey                               (Jersey)Catégorie:français de Jersey
"jeux de cartes",               # Cartes à jouer                       (Cartes à jouer)Catégorie:Jeux de cartes en français
"jeux",                         # Jeux                                 (Jeux)Catégorie:Jeux en français
"jouets",                       # Jeux                                 (Jeux)Catégorie:Jouets en français
"Jura",                         # Jura                                 (Jura)Catégorie:français du Jura
"Kabylie",                      # Kabylie                              (Kabylie)Catégorie:français de Kabylie
"lacs",                         # Géographie                           (Géographie)Catégorie:Lacs en français
"langage SMS",                  # Langage SMS                          (Langage SMS)Catégorie:Langage SMS en français
"langages",                     # Informatique                         (Informatique)Catégorie:Langages informatiques en français
"Languedoc-Roussillon",         # Languedoc-Roussillon                 (Languedoc-Roussillon)Catégorie:français du Languedoc-Roussillon
"Languedoc",                    # Languedoc                            (Languedoc)Catégorie:français du Languedoc
"langues",                      # Linguistique                         (Linguistique)Catégorie:Langues en français
"Laos",                         # Laos                                 (Laos)Catégorie:français du Laos
"lapins",                       # Zoologie                             (Zoologie)Catégorie:Lapins en français
"latinisme droit",              # Latinisme en droit                   (Latinisme en droit)Catégorie:Latinismes en droit en français
"latinisme",                    # Latinisme                            (Latinisme)Catégorie:Latinismes en français
"latinismes en droit",          # Latinisme en droit                   (Latinisme en droit)Catégorie:Latinismes en droit en français
"Le Havre",                     # Le Havre                             (Le Havre)Catégorie:français du Havre
"Le Mans",                      # Le Mans                              (Le Mans)Catégorie:français du Mans
"légumes",                      # Botanique                            (Botanique)Catégorie:Légumes en français
"léporidés",                    # Mammalogie                           (Mammalogie)Catégorie:Léporidés en français
"lexique",                      # Psychologie                          (Psychologie)Catégorie:Lexique en français de la psychologie
"lézards",                      # Herpétologie                         (Herpétologie)Catégorie:Lézards en français
"LGBT",                         # LGBT                                 (LGBT)Catégorie:Vocabulaire LGBTIQ en français
"lianes",                       # Botanique                            (Botanique)Catégorie:Lianes en français
"Liban",                        # Liban                                (Liban)Catégorie:français du Liban
"lieux imaginaires",            # Géographie                           (Géographie)Catégorie:Lieux imaginaires en français
"lieux mythologiques",          # Mythologie                           (Mythologie)Catégorie:Lieux mythologiques en français
"Limagne",                      # Limagne                              (Limagne)Catégorie:français de la Limagne
"Limousin",                     # Limousin                             (Limousin)Catégorie:français du Limousin
"localités",                    # Géographie                           (Géographie)
"localités",                    # Géographie                           (Géographie)Catégorie:Localités d’Algérie en français
"Loire-Atlantique",             # Loire-Atlantique                     (Loire-Atlantique)Catégorie:français de Loire-Atlantique
"Loiret",                       # Loiret                               (Loiret)Catégorie:français du Berry
"Lorraine",                     # Lorraine                             (Lorraine)Catégorie:français de Lorraine
"louchébem",                    # Louchébem                            (Louchébem)Catégorie:Louchébem
"Louisiane",                    # Louisiane                            (Louisiane)Catégorie:français de Louisiane
"lusitanisme",                  # Lusitanisme                          (Lusitanisme)Catégorie:Lusitanismes en français
"Luxembourg",                   # Luxembourg                           (Luxembourg)Catégorie:français du Luxembourg
"Lyon",                         # Lyonnais                             (Lyonnais)Catégorie:français du Lyonnais
"lyonnais",                     # Lyonnais                             (Lyonnais)Catégorie:français du Lyonnais
"Lyonnais",                     # Lyonnais                             (Lyonnais)Catégorie:français du Lyonnais
"machines",                     # Technologie                          (Technologie)Catégorie:Machines en français
"Madagascar",                   # Madagascar                           (Madagascar)Catégorie:français de Madagascar
"Maghreb",                      # Maghreb                              (Maghreb)
"Maghreb",                      # Maghreb                              (Maghreb)Catégorie:français du Maghreb
"maladie",                      # Nosologie                            (Nosologie)Catégorie:Maladies en français
"maladies",                     # Nosologie                            (Nosologie)
"maladies",                     # Nosologie                            (Nosologie)Catégorie:Maladies en français
"Malaisie",                     # Malaisie                             (Malaisie)Catégorie:anglais de Malaisie
"Mali",                         # Mali                                 (Mali)Catégorie:français du Mali
"mammifère",                    # Zoologie                             (Zoologie)Catégorie:Mammifères en français
"mammifères",                   # Zoologie                             (Zoologie)
"mammifères",                   # Zoologie                             (Zoologie)Catégorie:Mammifères en français
"Manche",                       # Manche                               (Manche)Catégorie:français de la Manche
"Marche",                       # Marche                               (Marche)Catégorie:français de la Marche
"Marne",                        # Marne                                (Marne)Catégorie:français de la Marne
"Maroc",                        # Maroc                                (Maroc)Catégorie:français du Maroc
"marque déposée",               # Marque commerciale                   (Marque commerciale)Catégorie:Marques déposées
"marque",                       # Marque commerciale                   (Marque commerciale)Catégorie:Marques déposées
"Marseille",                    # Marseille                            (Marseille)Catégorie:français de Provence
"marsupial",                    # Zoologie                             (Zoologie)Catégorie:Marsupiaux en français
"marsupiaux",                   # Zoologie                             (Zoologie)Catégorie:Marsupiaux en français
"Martinique",                   # Martinique                           (Martinique)Catégorie:français de Martinique
"Maurice",                      # Île Maurice                          (Île Maurice)Catégorie:français de l’Île Maurice
"Mauricie",                     # Mauricie                             (Mauricie)Catégorie:français de Mauricie
"Mauritanie",                   # Mauritanie                           (Mauritanie)Catégorie:français de Mauritanie
"Mayenne",                      # Mayenne                              (Mayenne)Catégorie:français de Mayenne
"Mayotte",                      # Mayotte                              (Mayotte)Catégorie:français de Mayotte
"médicaments",                  # Pharmacologie                        (Pharmacologie)Catégorie:Médicaments en français
"méduses",                      # Zoologie                             (Zoologie)Catégorie:Méduses en français                   # Sens figuré                          (Sens figuré)Catégorie:Métaphores en français
"mers",                         # Géographie                           (Géographie)Catégorie:Mers en français
"mers",                         # Géographie                           (Géographie)Philippines
"métaplasmes",                  # Linguistique                         (Linguistique)Catégorie:Métaplasmes en français
"meuble",                       # Mobilier                             (Mobilier)Catégorie:Meubles en français
"meubles héraldiques",          # Héraldique                           (Héraldique)Catégorie:Meubles héraldiques en français
"meubles",                      # Mobilier                             (Mobilier)Catégorie:Meubles en français
"Midi toulousain",              # Midi toulousain                      (Midi toulousain)Catégorie:français du Midi toulousain
"Midi",                         # Midi de la France                    (Midi de la France)Catégorie:français du Midi de la France
"militant",                     # Vocabulaire militant                 (Vocabulaire militant)Catégorie:Vocabulaire militant en français
"minéraux",                     # Minéralogie                          (Minéralogie)Catégorie:Minéraux en français
"Missouri",                     # Missouri                             (Missouri)Catégorie: français du Missouri
"mobilier",                     # Mobilier                             (Mobilier)Catégorie:Meubles en français
"moderne",                      # Moderne                              (Moderne)
"mollusques",                   # Malacologie                          (Malacologie)
"mollusques",                   # Malacologie                          (Malacologie)Catégorie:Mollusques en français
"monnaies",                     # Numismatique                         (Numismatique)
"monnaies",                     # Numismatique                         (Numismatique)Catégorie:Monnaies en français
"montagnes",                    # Géographie                           (Géographie)Caroux
"montagnes",                    # Géographie                           (Géographie)Catégorie:Montagnes en français
"Montréal",                     # Montréal                             (Montréal)Catégorie:français de Montréal
"Moselle",                      # Moselle                              (Moselle)Catégorie:français de Moselle
"mouches",                      # Entomologie                          (Entomologie)Catégorie:Mouches en français
"muscles",                      # Anatomie                             (Anatomie)Catégorie:Muscles en français
"muscles",                      # Anatomie                             (Anatomie)sphincter de la pupille
"musiciens",                    # Musique                              (Musique)Catégorie:Musiciens en français
"Myanmar",                      # Myanmar                              (Myanmar)
"Nantes",                       # Nantes                               (Nantes)Catégorie:français de Nantes
"néerlandisme",                 # Néerlandisme                         (Néerlandisme)Catégorie:Néerlandismes en français
"Nicaragua",                    # Nicaragua                            (Nicaragua)Catégorie:espagnol du Nicaragua
"Niger",                        # Niger                                (Niger)Catégorie:français du Niger
"Nigeria",                      # Nigeria                              (Nigeria)Catégorie:français du Nigeria
"nom-déposé",                   # Marque commerciale                   (Marque commerciale)Catégorie:Marques déposées
"Nord de la France",            # Nord de la France                    (Nord de la France)Catégorie:français du Nord
"Nord-Pas-de-Calais",           # Nord-Pas-de-Calais                   (Nord-Pas-de-Calais)Catégorie:français du Nord-Pas-de-Calais
"Normandie",                    # Normandie                            (Normandie)Catégorie:français de Normandie
"Nouvelle-Calédonie",           # Nouvelle-Calédonie                   (Nouvelle-Calédonie)Catégorie:français de Nouvelle-Calédonie
"Nouvelle-Zélande",             # Nouvelle-Zélande                     (Nouvelle-Zélande)
"nuages",                       # Météorologie                         (Météorologie)*
"nuages",                       # Météorologie                         (Météorologie)Catégorie:Nuages en français
"nymphes",                      # Mythologie                           (Mythologie)Catégorie:Nymphes en français
"Occitanie",                    # Occitanie                            (Occitanie)Catégorie:français d’Occitanie
"Océanie",                      # Océanie                              (Océanie)Catégorie:français d’Océanie
"oies",                         # Ornithologie                         (Ornithologie)Catégorie:Oies en français
"Oise",                         # Oise                                 (Oise)Catégorie:français de l’Oise
"oiseaux",                      # Ornithologie                         (Ornithologie)
"oiseaux",                      # Ornithologie                         (Ornithologie)Catégorie:Passereaux en français
"Ontario",                      # Ontario                              (Ontario)Catégorie: français de l’Ontario
"orgues",                       # Orgues                               (Orgues)*
"orgues",                       # Orgues                               (Orgues)Catégorie:Lexique en français des orgues
"Ouessant",                     # Ouessant                             (Ouessant)Catégorie:français de Ouessant
"outils",                       # Technique                            (Technique)Catégorie:Outils en français
"ovins",                        # Zoologie                             (Zoologie)Catégorie:Ovins en français
"palmiers",                     # Botanique                            (Botanique)Catégorie:Palmiers en français
"palmipèdes",                   # Ornithologie                         (Ornithologie)Catégorie:Palmipèdes en français
"papillons",                    # Entomologie                          (Entomologie)Catégorie:Papillons en français
"Paris",                        # Paris                                (Paris)Catégorie:français d’Île-de-France
"parler bellifontain",          # Parler bellifontain                  (Parler bellifontain)Catégorie:parler bellifontain
"parler gaga",                  # Parler gaga                          (Parler gaga)Catégorie:français de la région stéphanoise
"Parler gaga",                  # Parler gaga                          (Parler gaga)Catégorie:français de la région stéphanoise
"particules",                   # Physique                             (Physique)Catégorie:Particules subatomiques en français
"pâtes alimentaires",           # Cuisine                              (Cuisine)Catégorie:Pâtes alimentaires en français
"pâtes",                        # Cuisine                              (Cuisine)Catégorie:Pâtes alimentaires en français
"pathologie",                   # Nosologie                            (Nosologie)Catégorie:Maladies en français
"pâtisseries",                  # Pâtisserie                           (Pâtisserie)Catégorie:Pâtisseries en français
"Pays basque",                  # Pays basque                          (Pays basque)Catégorie:français du Pays basque
"pays gallo",                   # Pays Gallo                           (Pays Gallo)Catégorie:français du pays gallo
"pays",                         # Géographie                           (Géographie)Andorre republique
"pays",                         # Géographie                           (Géographie)Catégorie:Pays en français
"pêches",                       # Botanique                            (Botanique)Catégorie:Pêches en français
"pêches",                       # Botanique                            (Botanique)plate
"Perche",                       # Perche                               (Perche)Catégorie:français du Perche
"percussions",                  # Musique                              (Musique)*
"percussions",                  # Musique                              (Musique)Catégorie:Instruments de percussion en français
"périodes",                     # Géologie                             (Géologie)Catégorie:Temps géologiques en français
"perroquets",                   # Ornithologie                         (Ornithologie)Catégorie:Perroquets et perruches en français
"personnalités",                # Anthroponyme                         (Anthroponyme)Catégorie:Personnalités mythologiques en français
"personnification",             # Rhétorique                           (Rhétorique)Catégorie:Personnifications en français
"peupliers",                    # Botanique                            (Botanique)Catégorie:Peupliers en français
"phobies",                      # Médecine                             (Médecine)Catégorie:Phobies en français
"phyton",                       # Botanique                            (Botanique)
"phyton",                       # Botanique                            (Botanique)Catégorie:Plantes en français
"Picardie",                     # Picardie                             (Picardie)Catégorie:français de Picardie
"pigeons",                      # Zoologie                             (Zoologie)Catégorie:Pigeons en français
"planètes",                     # Astronomie                           (Astronomie)
"planètes",                     # Astronomie                           (Astronomie)Catégorie:Planètes en français
"plans d’eau",                  # Géographie                           (Géographie)Catégorie:Lacs en français
"plans d’eau",                  # Géographie                           (Géographie)saint jean
"plantes",                      # Botanique                            (Botanique)Catégorie:Plantes en français
"poétique",                     # Poétique                             (Poétique)Catégorie:Termes poétiques en français
"points cardinaux",             # Géographie                           (Géographie)Catégorie:Rose des vents en français
"poires",                       # Botanique                            (Botanique)Catégorie:Poires en français
"poissons",                     # Ichtyologie                          (Ichtyologie)Catégorie:Poissons en français
"Poitou",                       # Poitou                               (Poitou)Catégorie:français du Poitou
"Polynésie française",          # Polynésie française                  (Polynésie française)Catégorie:français de Polynésie française
"pommes",                       # Botanique                            (Botanique)Catégorie:Pommes en français
"ponctuations",                 # Typographie                          (Typographie)Catégorie:Signes de ponctuation en français
"ponts",                        # Architecture                         (Architecture)Catégorie:Ponts en français
"popu",                         # Populaire                            (Populaire)Catégorie:Termes populaires en français
"porcins",                      # Zoologie                             (Zoologie)Catégorie:Porcins en français
"positions",                    # Sexualité                            (Sexualité)Catégorie:Positions sexuelles en français
"poules",                       # Élevage                              (Élevage)Catégorie:Poules en français
"préparations",                 # Cuisine                              (Cuisine)Catégorie:Préparations culinaires en français
"primates",                     # Zoologie                             (Zoologie)Catégorie:Primates en français
"protéines",                    # Biochimie                            (Biochimie)Catégorie:Protéines en français
"protocoles",                   # Réseaux                              (Réseaux)Catégorie:Protocoles réseaux en français
"Provence",                     # Provence                             (Provence)Catégorie:français de Provence
"proverbe",                     # Proverbe                             (Proverbe)Catégorie:Proverbes en français
"proverbes",                    # Proverbe                             (Proverbe)Catégorie:Proverbes en français
"provinces",                    # Géographie                           (Géographie)Catégorie:Provinces d’Italie en français
"provinces",                    # Géographie                           (Géographie)palmas
"prunes",                       # Botanique                            (Botanique)Catégorie:Prunes en français
"psychotropes",                 # Psychotrope                          (Psychotrope)Catégorie:Psychotropes en français
"Puy-de-Dôme",                  # Puy-de-Dôme                          (Puy-de-Dôme)Catégorie:français du Puy-de-Dôme
"QC",                           # Québec                               (Québec)
"QC",                           # Québec                               (Québec)Catégorie: français du Québec
"quartiers",                    # Toponyme                             (Toponyme)Catégorie:Quartiers de Lyon en français
"Québec",                       # Québec                               (Québec)Catégorie: français du Québec
"Quercy",                       # Quercy                               (Quercy)Catégorie:français du Quercy
"questions rhétoriques",        # Questions rhétoriques                (Questions rhétoriques)Catégorie:Questions rhétoriques en français
"raies",                        # Ichtyologie                          (Ichtyologie)Catégorie:Raies en français
"rapaces",                      # Ornithologie                         (Ornithologie)Catégorie:Rapaces en français
"RDC",                          # Congo-Kinshasa                       (Congo-Kinshasa)Catégorie:français du Congo-Kinshasa
"RDCongo",                      # Congo-Kinshasa                       (Congo-Kinshasa)Catégorie:français du Congo-Kinshasa
"région",                       # Cévennes                             (Cévennes)
"régional",                     # Régionalisme                         (Régionalisme)
"régionalisme",                 # Régionalisme                         (Régionalisme)
"régionalisme",                 # Régionalisme                         (Régionalisme)Catégorie:français régional
"régions",                      # Toponyme                             (Toponyme)Catégorie:Régions de Russie en français
"religieux",                    # Religion                             (Religion)Catégorie:Religieux en français
"religions",                    # Religion                             (Religion)Catégorie:Religions en français
"reptiles",                     # Herpétologie                         (Herpétologie)Catégorie:Reptiles en français
"République centrafricaine",    # République centrafricaine            (République centrafricaine)Catégorie:français de la République centrafricaine
"République Démocratique du Congo", # Congo-Kinshasa                       (Congo-Kinshasa)Catégorie:français du Congo-Kinshasa
"requins",                      # Ichtyologie                          (Ichtyologie)Catégorie:Requins en français
"Réunion",                      # La Réunion                           (La Réunion)
"Réunion",                      # La Réunion                           (La Réunion)Catégorie:français de la Réunion
"Rhône-Alpes",                  # Rhône-Alpes                          (Rhône-Alpes)Catégorie:français de Rhône-Alpes
"roches",                       # Pétrographie                         (Pétrographie)Catégorie:Roches en français
"rongeur",                      # Zoologie                             (Zoologie)Catégorie:Rongeurs en français
"rongeurs",                     # Zoologie                             (Zoologie)Catégorie:Rongeurs en français
"Rouen",                        # Rouen                                (Rouen)Catégorie:français de Rouen
"Royaume-Uni",                  # Royaume-Uni                          (Royaume-Uni)Catégorie:français du Royaume-Uni
"Russie",                       # Russie                               (Russie)
"Russie",                       # Russie                               (Russie)Catégorie:français de Russie
"Rwanda",                       # Rwanda                               (Rwanda)Catégorie:français du Rwanda
"Saint-Martin",                 # Saint-Martin                         (Saint-Martin)Catégorie:français de Saint-Martin
"Saint-Pierre-et-Miquelon",     # Saint-Pierre-et-Miquelon             (Saint-Pierre-et-Miquelon)Catégorie:français de Saint-Pierre-et-Miquelon
"salades",                      # Cuisine                              (Cuisine)Catégorie:Salades en français
"salles",                       # Construction                         (Construction)Catégorie:Salles en français
"sandwichs",                    # Cuisine                              (Cuisine)Catégorie:Sandwichs en français
"Sarthe",                       # Sarthe                               (Sarthe)Catégorie:français de la Sarthe
"satellites",                   # Astronomie                           (Astronomie)Catégorie:Satellites en français
"sauces",                       # Sauces                               (Sauces)Catégorie:Sauces en français
"saules",                       # Botanique                            (Botanique)Catégorie:Saules en français
"Savoie",                       # Savoie                               (Savoie)Catégorie:français de Savoie
"sciences",                     # Sciences                             (Sciences)Catégorie:Noms de sciences en français
"scientifiques",                # Science                              (Science)Catégorie:Métiers de la science en français
"seigneuries",                  # Histoire                             (Histoire)Catégorie:Seigneuries en français
"Sénégal",                      # Sénégal                              (Sénégal)Catégorie:français du Sénégal
"sentiments",                   # Psychologie                          (Psychologie)Catégorie:Sentiments en français
"serpents",                     # Herpétologie                         (Herpétologie)Catégorie:Serpents en français
"sexiste",                      # Sexiste                              (Sexiste)Catégorie:Termes discriminants en français
"Seychelles",                   # Seychelles                           (Seychelles)Catégorie:français des Seychelles
"sigle",                        # Sigle                                (Sigle)Catégorie:Sigles en français
"signalisations",               # Sécurité routière                    (Sécurité routière)Catégorie:Signalisations routières en français
"singes",                       # Zoologie                             (Zoologie)Catégorie:Singes en français
"SMS",                          # Langage SMS                          (Langage SMS)Catégorie:Langage SMS en français
"soldats",                      # Militaire                            (Militaire)Catégorie:Soldats en français
"Sologne",                      # Sologne                              (Sologne)Catégorie:français de la Sologne
"sols",                         # Pédologie                            (Pédologie)Catégorie:Sols en français
"sous-régions",                 # Toponyme                             (Toponyme)Catégorie:Sous-régions du Portugal en français
"soutenu",                      # Soutenu                              (Soutenu)Catégorie:Termes soutenus en français
"sportifs",                     # Sport                                (Sport)Catégorie:Sportifs en français
"sports d’hiver",               # Sport                                (Sport)Catégorie:Sports d’hiver en français
"sports nautiques",             # Sport                                (Sport)Catégorie:Sports nautiques en français
"sports",                       # Sport                                (Sport)*
"sports",                       # Sport                                (Sport)Catégorie:Sports de glisse en français
"stéréotypes",                  # Stéréotype                           (Stéréotype)Catégorie:Stéréotypes en français
"substances",                   # Chimie                               (Chimie)
"substances",                   # Chimie                               (Chimie)Catégorie:Substances chimiques en français
"Suisse",                       # Suisse                               (Suisse)
"Suisse",                       # Suisse                               (Suisse)Catégorie:français de Suisse
"symboles unités",              # Métrologie                           (Métrologie)Catégorie:Symboles d’unités de mesure en français
"TAAF",                         # Vocabulaire des TAAF                 (Vocabulaire des TAAF)Catégorie:français des TAAF
"Tchad",                        # Tchad                                (Tchad)Catégorie:français du Tchad
"temps géologiques",            # Géologie                             (Géologie)Catégorie:Temps géologiques en français
"term",                         # Vocabulaire militant                 (Vocabulaire militant)
"Terre-Neuve",                  # Terre-Neuve                          (Terre-Neuve)Catégorie: français de Terre-Neuve
"territoires",                  # Toponyme                             (Toponyme)Catégorie:Territoires de Chine en français
"territoires",                  # Toponyme                             (Toponyme)Cholistan
"textiles",                     # Textile                              (Textile)Catégorie:Textiles en français
"thérapies",                    # Médecine                             (Médecine)Catégorie:Thérapies en français
"Tintin",                       # Univers de Tintin                    (Univers de Tintin)*
"Tintin",                       # Univers de Tintin                    (Univers de Tintin)Catégorie:Tintinologie en français
"tissus",                       # Textile                              (Textile)Catégorie:Tissus en français
"titres",                       # Noblesse                             (Noblesse)Catégorie:Titres de noblesse en français
"Togo",                         # Togo                                 (Togo)Catégorie:français du Togo
"toponymes",                    # Géographie                           (Géographie)
"toponymes",                    # Géographie                           (Géographie)Catégorie:Toponymes en français
"tortues",                      # Zoologie                             (Zoologie)Catégorie:Tortues en français
"Touraine",                     # Touraine                             (Touraine)Catégorie: français de Touraine
"Tunisie",                      # Tunisie                              (Tunisie)Catégorie:français de Tunisie
"Turquie",                      # Turquie                              (Turquie)Catégorie:roumain de Turquie
"Ukraine",                      # Ukraine                              (Ukraine)Catégorie:français d’Ukraine
"un os",                        # Anatomie                             (Anatomie)Catégorie:Os en français
"un_os",                        # Anatomie                             (Anatomie)Catégorie:Os en français
"unités",                       # Métrologie                           (Métrologie)Catégorie:Unités de mesure de longueur en français
"univers des canards",          # Univers des canards de Disney        (Univers des canards de Disney)Catégorie:Univers des canards de Disney en français
"US",                           # États-Unis                           (États-Unis)Catégorie:français des États-Unis
"USA",                   
       # États-Unis                           (États-Unis)Catégorie:français des États-Unis
"usines",                       # Industrie                            (Industrie)*
"usines",                       # Industrie                            (Industrie)Catégorie:Usines en français
"ustensiles",                   # Cuisine                              (Cuisine)Catégorie:Ustensiles de cuisine en français
"Vallée d'Yères",               # Vallée d'Yères                       (Vallée d'Yères)Catégorie:français de la vallée d'Yères
"Var",                          # Var                                  (Var)Catégorie:français du Var
"Vaucluse",                     # Vaucluse                             (Vaucluse)Catégorie:français de Vaucluse
"véhicule",                     # Transport                            (Transport)Catégorie:Véhicules en français
"véhicules",                    # Transport                            (Transport)Catégorie:Véhicules en français
"Velay",                        # Velay                                (Velay)Catégorie:français du Velay
"vélos",                        # Cyclisme                             (Cyclisme)Catégorie:Vélos en français
"Vendée",                       # Vendée                               (Vendée)Catégorie:français de Vendée
"vents",                        # Météorologie                         (Météorologie)Catégorie:Vents en français
"verlan",                       # Verlan                               (Verlan)Catégorie:Verlan
"vers",                         # Zoologie                             (Zoologie)Catégorie:Vers en français
"vête",                         # Habillement                          (Habillement)Catégorie:Vêtements en français
"vêtements",                    # Habillement                          (Habillement)
"vêtements",                    # Habillement                          (Habillement)Catégorie:Vêtements en français
"viandes",                      # Cuisine                              (Cuisine)Catégorie:Viandes en français
"Viêt Nam",                     # Viêt Nam                             (Viêt Nam)Catégorie:français du Viêt Nam
"Vietnam",                      # Viêt Nam                             (Viêt Nam)Catégorie:français du Viêt Nam
"vins",                         # Œnologie                             (Œnologie)Catégorie:Vins en français
"virus",                        # Virologie                            (Virologie)Catégorie:Virus en français
"voitures",                     # Automobile                           (Automobile)Catégorie:Voitures en français
"Vosges",                       # Vosges                               (Vosges)Catégorie:français des Vosges
"Wallonie",                     # Wallonie                             (Wallonie)Catégorie:français de la Wallonie
"xénarthres",                   # Mammalogie                           (Mammalogie)Catégorie:Xénarthres en français
"Yonne",                        # Yonne                                (Yonne)Catégorie:français de l’Yonne
"faux anglicisme",              # Faux anglicisme                      (Faux anglicisme)Catégorie:Faux anglicismes en français
"faux anglicismes",             # Faux anglicisme                      (Faux anglicisme)Catégorie:Faux anglicismes en français
]

# Templates used to refer to (grammatical) tags. This is loosely based on https://fr.wiktionary.org/wiki/Annexe:Glossaire_grammatical#D
french_tag_templates = [
"absolument",                   # Absolument                           (Absolument)
"acronyme",                     # Acronyme                             (Acronyme)Catégorie:Acronymes en français
"anglicisme",                   # Anglicisme                           (Anglicisme)Catégorie:Anglicismes en français
"archaïsme",                    # Archaïsme                            (Archaïsme)Catégorie:Termes archaïques en français
"argot polytechnicien",         # Argot polytechnicien                 (Argot polytechnicien)Catégorie:Argot polytechnicien en français
"argot",                        # Argot                                (Argot)Catégorie:Termes argotiques en français
"au féminin",                   # Au féminin                           (Au féminin)
"au figuré",                    # Sens figuré                          (Sens figuré)Catégorie:Métaphores en français
"au masculin",                  # Au masculin                          (Au masculin)
"au pluriel",                   # Au pluriel                           (Au pluriel)
"au singulier",                 # Au singulier                         (Au singulier)
"auxiliaire",                   # Auxiliaire                           (Auxiliaire)Catégorie:Verbes auxiliaires en français
"beaucoup moins courant",       # Beaucoup moins courant               (Beaucoup moins courant)
"beaucoup plus courant",        # Beaucoup plus courant                (Beaucoup plus courant)"conj",                         # voir la conjugaison                  1ᵉʳ groupe (voir la conjugaison)
"courant",                      # Courant                              (Courant)
"critiqué",                     # Usage critiqué                       (Usage critiqué)
"critiqué",                     # Usage critiqué                       (Usage critiqué)Catégorie:Usages critiqués en français
"désuet",                       # Désuet                               (Désuet)Catégorie:Termes désuets en français
"diaéthique",                   # Variation diaéthique                 (Variation diaéthique)Catégorie:Variation diaéthique en français
"ellipse",                      # Par ellipse                          (Par ellipse)
"ellipse",                      # Par ellipse                          (Par ellipse)Catégorie:Ellipses en français
"en particulier",               # En particulier                       (En particulier)
"extrêmement rare",             # Extrêmement rare                     (Extrêmement rare)Catégorie:Termes extrêmement rares en français
"extrêmement_rare",             # Extrêmement rare                     (Extrêmement rare)Catégorie:Termes extrêmement rares en français
"familier",                     # Familier                             (Familier)Catégorie:Termes familiers en français
"figuré",                       # Sens figuré                          (Sens figuré)
"figuré",                       # Sens figuré                          (Sens figuré)Catégorie:Métaphores en français
"généralement",                 # Généralement                         (Généralement)
"génériquement",                # Génériquement                        (Génériquement)
"idiomatique",                  # Sens figuré                          (Sens figuré)Catégorie:Métaphores en français
"impersonnel",                  # Impersonnel                          (Impersonnel)Catégorie:Verbes impersonnels en français
"improprement",                 # Usage critiqué                       (Usage critiqué)Catégorie:Usages critiqués en français
"indénombrable",                # Indénombrable                        (Indénombrable)
"indénombrable",                # Indénombrable                        (Indénombrable)Catégorie:Noms indénombrables en français
"informel",                     # Informel                             (Informel)
"informel",                     # Informel                             (Informel)Catégorie:Termes informels en français
"intrans",                      # Intransitif                          (Intransitif)Catégorie:Verbes intransitifs en français
"intransitif",                  # Intransitif                          (Intransitif)Catégorie:Verbes intransitifs en français
"ironique",                     # Ironique                             (Ironique)Catégorie:Ironies en français
"littéraire",                   # Littéraire                           (Littéraire)Catégorie:Termes littéraires en français
"m-cour",                       # Moins courant                        (Moins courant)
"mélioratif",                   # Mélioratif                           (Mélioratif)Catégorie:Termes mélioratifs en français
"métaphore",                    # Sens figuré                          (Sens figuré)Catégorie:Métaphores en français
"moins courant",                # Moins courant                        (Moins courant)
"néologisme",                   # Néologisme                           (Néologisme)Catégorie:Néologismes en français
"nom collectif",                # Nom collectif                        (Nom collectif)Catégorie:Noms collectifs en français
"par analogie",                 # Par analogie                         (Par analogie)Catégorie:Analogies en français
"par dérision",                 # Par dérision                         (Par dérision)Catégorie:Termes par dérision en français
"par ellipse",                  # Par ellipse                          (Par ellipse)
"par ellipse",                  # Par ellipse                          (Par ellipse)Catégorie:Ellipses en français
"par euphémisme",               # Par euphémisme                       (Par euphémisme)Catégorie:Euphémismes en français
"par extension",                # Par extension                        (Par extension)
"par hyperbole",                # Par hyperbole                        (Par hyperbole)
"par hyperbole",                # Par hyperbole                        (Par hyperbole)Catégorie:Hyperboles en français
"par litote",                   # Par litote                           (Par litote)Catégorie:Litotes en français
"par métonymie",                # Par métonymie                        (Par métonymie)Catégorie:Métonymies en français
"par plaisanterie",             # Par plaisanterie                     (Par plaisanterie)Catégorie:Plaisanteries en français
"par troponymie",               # Par troponymie                       (Par troponymie)Catégorie:Troponymes en français
"péjoratif",                    # Péjoratif                            (Péjoratif)Catégorie:Termes péjoratifs en français
"peu usité",                    # Peu usité                            (Peu usité)Catégorie:Termes rares en français
"plus courant",                 # Plus courant                         (Plus courant)
"plus rare",                    # Plus rare                            (Plus rare)
"popu",                         # Populaire                            (Populaire)
"populaire",                    # Populaire                            (Populaire)Catégorie:Termes populaires en français
"pronl",                        # Pronominal                           (Pronominal)Catégorie:Verbes pronominaux en français
"pronominal",                   # Pronominal                           (Pronominal)
"pronominal",                   # Pronominal                           (Pronominal)Catégorie:Verbes pronominaux en français
"prov",                         # Proverbial                           (Proverbial)Catégorie:Mots proverbiaux en français
"proverbial",                   # Proverbial                           (Proverbial)Catégorie:Mots proverbiaux en français
"rare",                         # Rare                                 (Rare)Catégorie:Termes rares en français
"réfléchi",                     # Réfléchi                             (Réfléchi)
"réflexif",                     # Réfléchi                             (Réfléchi)
"registre",                     # Familier                             (Familier)
"sens propre",                  # Sens propre                          (Sens propre)
"soutenu",                      # Soutenu                              (Soutenu)
"spécialement",                 # Spécialement                         (Spécialement)
"spécifiquement",               # Spécifiquement                       (Spécifiquement)
"spécifiquement",               # Spécifiquement                       (Spécifiquement)
"tr-fam",                       # Très familier                        (Très familier)Catégorie:Termes très familiers en français
"trans",                        # Transitif                            (Transitif)Catégorie:Verbes transitifs en français
"transitif",                    # Transitif                            (Transitif)
"transitif",                    # Transitif                            (Transitif)Catégorie:Verbes transitifs sans langue précisée
"très familier",                # Très familier                        (Très familier)Catégorie:Termes très familiers en français
"très rare",                    # Très rare                            (Très rare)Catégorie:Termes rares en français
"très très rare",               # Extrêmement rare                     (Extrêmement rare)Catégorie:Termes extrêmement rares en français
"vieilli",                      # Vieilli                              (Vieilli)Catégorie:Termes vieillis en français
"vulgaire",                     # Vulgaire                             (Vulgaire)Catégorie:Termes vulgaires en français
]

# Templates that should be kept and written to glosses etc.
french_keep_templates = [
"1er",                          #  1ᵉ                                  1ᵉʳ
"ar-cf",                        # kâkaka                               كَاكَكَ (kâkaka) (« entretenir une correspondance »)
"ar-mo",                        #  مَصْدَر                             مَصْدَرٌ
"ar-mot",                       # -iy²ũ                                ـِيٌّ (-iy²ũ)
"ar-racine/nom",                #  ك ت                                 ك ت&
"ar-sch",                       #  زَازَز                              زَازَزَ
"Arab",                         #  أَكْبَ                              أَكْبَر
"avJC",                         #  av. J.-C                            av. J.-C.
"e",                            #  ¹                                   ¹⁸
"ème",                          #                                      ᵉ
"er",                           #  ᵉ                                   ᵉʳ
"ère",                          #  ʳ                                   ʳᵉ
"exp",                          #  ᵐ                                   ᵐᵉ
"fchim",                        # AsO₄                                 Ca₂Cu₉(AsO₄)₄(CO3)(OH)₈· 11H₂O
"Lang-ar",                      #  نهر ابراهي                          نهر ابراهيم
"lang",                         #  РПО-А Шмел                          РПО-А Шмель
"Lang",                         #  ـيـ ـنـ ـثـ ـتـ ـب                  ـيـ ـنـ ـثـ ـتـ ـبـ
"Lang",                         # « j'ai demandé »                     jsem žádal (« j'ai demandé »)
"Mme",                          #  Mᵐ                                  Mᵐᵉ
"n°",                           #  nᵒ 1499                             nᵒ 1499S
"nobr",                         #  HOOC–CO–CH₂–COO                     HOOC–CO–CH₂–COOH
"nobr",                         # ℵ₀                                   2^(ℵ₀)
"numéro",                       #  n                                   nᵒ
"o",                            #                                      ᵒ
"polytonique",                  # « nez »                              ῥίς, ῥινός, rhís, rhinós (« nez »)
"pron",                         #  \sis.sɑ̃.tʁe                        \sis.sɑ̃.tʁe\
"sic",                          # [sic]                                ^([sic])
"siècle2",                      #  XVIII                               XVIIIᵉ
"Unité",                        #  2,000                               2,000 m
"unité",                        #  55 k                                55 km
"w",                            #  Alexandre Kerensk                   Alexandre Kerenski
"x10",                          #  ×10²                                ×10²¹
"zh-lien",                      # gè                                   个 (gè)
]

# Templates that should be ignored and not written to glosses etc.
french_ignore_templates = [
"*",                            # [*]                                  ^([*])
"R",                            #                                      
"RÉF",                          # [1]                                  ^([1])
"réf",                          # [2]                                  ^([2])
"ébauche-déf",                  # //dummy.host/index.php?title=finit%C3%A9simal&action=edit Ajouter  Définition manquante ou à compléter. (//dummy.host/index.php?title=finit%C3%A9simal&action=edit Ajouter)Catégorie:Wiktionnaire:Définitions manquantes en français
]

# This list is not currently used. It keeps track of templates that were found in error messages but are not in the above lists. Usually, either their meaning isn't clear or their expanded form resists easy extraction of a tag or category. By default, they will be written to glosses etc.
to_decide = [
"???",                          #                                      
"?",                            # information à préciser ou à vérifier  (information à préciser ou à vérifier)Catégorie:Pages à vérifier sans langue précisée
"'",                            #                                      ’
"abréviation",                  #  Abréviation de cathode à émission par effet de champCatégorie:Abréviations en françai  Abréviation de cathode à émission par effet de champCatégorie:Abréviations en français
"Accord des couleurs",          #  Voir la note sur les accords grammaticaux des noms de couleurs employés comme noms ou adjectifs  Voir la note sur les accords grammaticaux des noms de couleurs employés comme noms ou adjectifs.
"adj-indéf-avec-de",            # Avec de                              (Avec de)Catégorie:Adjectifs indéfinis en français avec de
"ancre",                        #                                      
"antonomase",                   #  Antonomasekapos                     Antonomasekaposi
"aphérèse",                     #  Aphérèsetachygraph                  Aphérèsetachygraphe
"apJC",                         #  apr. J.-C                           apr. J.-C.
"apocope",                      #  apocopefuné                         apocopefunés
"apposition",                   # En apposition                        (En apposition)

"attention",                    #                                      
"au pluriel uniquement",        #  au pluriel uniquemen                au pluriel uniquement
"au pluriel uniquement",        #  au pluriel uniquementCatégorie:Mots au pluriel uniquement en françai  au pluriel uniquementCatégorie:Mots au pluriel uniquement en français
"au singulier uniquement",      #  au singulier uniquementCatégorie:Mots au singulier uniquement en françai  au singulier uniquementCatégorie:Mots au singulier uniquement en français
"avant 1835",                   # Archaïque, orthographe d’avant 1835  (Archaïque, orthographe d’avant 1835)Catégorie:français moderne d’avant 1835
"c",                            #  commu                               commun
"cf",                           #  → voir cathode à émission de cham   → voir cathode à émission de champ
"cit_réf ",                     #  Encyclopédie Universelle, « finsenthérapie », dans Encyclopédie Universelle, 2012 → consulter cet ouvrag  Encyclopédie Universelle, « finsenthérapie », dans Encyclopédie Universelle, 2012 → consulter cet ouvrage
"cit_réf",                      #  Jeune Afrique, 7 mars 201           Jeune Afrique, 7 mars 2013
"Citation/Lionel Naccache/Le Nouvel Inconscient/2009", # Lionel Naccache, Le Nouvel Inconscient : Freud, le Christophe Colomb des neurosciences, Odile Jacob, 2009, page 38  — (Lionel Naccache, Le Nouvel Inconscient : Freud, le Christophe Colomb des neurosciences, Odile Jacob, 2009, page 38)
"clé de tri",                   #                                      
"comparatif de",                #  Comparatif de bon marchéCatégorie:Adjectifs comparatifs en françai  Comparatif de bon marchéCatégorie:Adjectifs comparatifs en français
"composé de",                   #  Catégorie:Compositions en français composé de -et, -ette et -e  Catégorie:Compositions en français composé de -et, -ette et -er
"conj",                         # voir la conjugaison                  1ᵉʳ groupe (voir la conjugaison)Catégorie:Verbes du premier groupe en français Catégorie:Wiktionnaire:Conjugaisons manquantes en français
"conjugaison",                  # voir la conjugaison                  1ᵉʳ groupe (voir la conjugaison)Catégorie:Verbes du premier groupe en français Catégorie:Wiktionnaire:Conjugaisons manquantes en français
"couleur",                      #  #723e6                              #723e64
"date",                         # 2008                                 (2008)
"de",                           #  alleman                             allemand
"ébauche-déf",                  # //dummy.host/index.php?title=finit%C3%A9simal&action=edit Ajouter  Définition manquante ou à compléter. (//dummy.host/index.php?title=finit%C3%A9simal&action=edit Ajouter)Catégorie:Wiktionnaire:Définitions manquantes en français
"ébauche-étym",                 #  Étymologie manquante ou incomplète. Si vous la connaissez, vous pouvez l’ajouter //dummy.host/w/index.php?title=Zelenska&action=edit en cliquant ici.Catégorie:Wiktionnaire:Étymologies manquantes en françai  Étymologie manquante ou incomplète. Si vous la connaissez, vous pouvez l’ajouter //dummy.host/w/index.php?title=Zelenska&action=edit en cliquant ici.Catégorie:Wiktionnaire:Étymologies manquantes en français
"ébauche",                      #  Catégorie:Wiktionnaire:Ébauches en françai  Catégorie:Wiktionnaire:Ébauches en français
"épithète",                     # Employé comme épithète               (Employé comme épithète)
"équiv-pour",                   # pour une femme, on dit : développeuse ; pour un homme, on dit : développeur  (pour une femme, on dit : développeuse ; pour un homme, on dit : développeur)Catégorie:Wiktionnaire:Pages à créer
"étyl",                         #  latin Fratres ArvalesCatégorie:Mots en français issus d’un mot en lati  latin Fratres ArvalesCatégorie:Mots en français issus d’un mot en latin
"exemple",                      # François Mauriac, Un adolescent d’autrefois, Flammarion, 1969, pages 215-216  La contrition parfaite n’est pas inaccessible comme on nous le fait croire, et réservée aux saints ; elle est à notre portée dans la mesure où l’est le royaume de Dieu : c’est le sésame qui en ouvre nécessairement la porte. » — (François Mauriac, Un adolescent d’autrefois, Flammarion, 1969, pages 215-216)Catégorie:Exemples en français
"exemple\n",                    # Gloria Faccanoni, M33 - Analyse numérique - Recueil d’exercices corrigés et aide-mémoire, 2015, p.21, accédé le 10.12.2022 → lire en ligne  Lorsque a > 0 est donné, on veut calculer sa valeur réciproque 1/a. — (Gloria Faccanoni, M33 - Analyse numérique - Recueil d’exercices corrigés et aide-mémoire, 2015, p.21, accédé le 10.12.2022 → lire en ligne)Catégorie:Exemples en français
"exemple\n",                    # selon le modèle théorique utilisé    En traçant la cadence de désintégration en tant que fonction de la valeur inverse du carré de la largeur de la région masse (selon le modèle théorique utilisé), il apparaît que l’on peut obtenir la longévité du porteur minoritaire ainsi que la constante de diffusion du matériau N. Une comparaison avec d’autres méthodes confirme l’utilité de cette méthode. — (J.L. Lindström, Flash X-ray irradiation of P-N junctions: A method to measure minority carrier lifetimes, diffusion constants and generation constants (résumé en français), Solid-State Electronics, vol. 14, N°9, pp. 827-833 → lire en ligne)Catégorie:Exemples en français
"f",                            #  fémini                              féminin
"féminin",                      #  fémini                              féminin
"forme pronominale",            #  Forme pronominale de recalotte      Forme pronominale de recalotter
"fplur",                        #  féminin plurie                      féminin pluriel
"fr-accord-rég",                #                                      
"fr-inv",                       #                                      
"fr-rég",                       #                                      
"fr",                           #  françai                             français
"fsing",                        #  féminin singulie                    féminin singulier
"graphie",                      #  ‹ –                                 ‹ – ›
"i",                            #  intransitifCatégorie:Verbes intransitifs en françai  intransitifCatégorie:Verbes intransitifs en français
"ibid",                         # ibid.                                — (ibid.)
"impers",                       #  impersonnelCatégorie:Verbes impersonnels en françai  impersonnelCatégorie:Verbes impersonnels en français
"in",                           #                                      ₈
"incise",                       #  — généralement en bois              — généralement en bois —
"ind",                          #  indonésie                           indonésien
"invar",                        #  invariabl                           invariable
"invariable",                   #  invariabl                           invariable
"invisible",                    #                                      
"ISBN",                         #  ISBN 2-84172-350-x ISBN invalideCatégorie:Pages avec ISBN invalid  ISBN 2-84172-350-x ISBN invalideCatégorie:Pages avec ISBN invalide
"ISBN",                         #  ISBN 978-2-87505-087-               ISBN 978-2-87505-087-8
"l",                            #  supermunicipa                       supermunicipal
"Lien 639-3",                   #  Documentation for ISO 639 identifier: def, SIL International, 202  Documentation for ISO 639 identifier: def, SIL International, 2023
"lien brisé",                   # (//web.archive.org/web/*/http://www.oulala.net/Portail/article.php3?id_article=1299 Archive • //archive.wikiwix.com/cache/?url=http://www.oulala.net/Portail/article.php3?id_article=1299 Wikiwix • Que faire ?  « source » ^((//web.archive.org/web/*/http://www.oulala.net/Portail/article.php3?id_article=1299 Archive • //archive.wikiwix.com/cache/?url=http://www.oulala.net/Portail/article.php3?id_article=1299 Wikiwix • Que faire ?)). Consulté le 2014-02-06Catégorie:Pages contenant un lien brisé
"lien pronominal",              # pronominal : s’engainer              (pronominal : s’engainer)Catégorie:Verbes pronominaux en français
"Lien web ",                    #  Callac - À Callac, Clique et cueillette, une nouvelle formule de vente à la librairie sur Le Telegramme, 06 novembre 2020. Consulté le 11 novembre 202  Callac - À Callac, Clique et cueillette, une nouvelle formule de vente à la librairie sur Le Telegramme, 06 novembre 2020. Consulté le 11 novembre 2020
"lien web",                     #  Les maîtres du désert sur /www.lemonde.fr, 07 avril 198  Les maîtres du désert sur /www.lemonde.fr, 07 avril 1981
"lien web\n",                   #  article R4227-39 du Code du travail sur Légifrance, 2008-03-07. Consulté le 2018-06-1  article R4227-39 du Code du travail sur Légifrance, 2008-03-07. Consulté le 2018-06-15
"lien",                         #  oppos                               opposé
"lire en ligne",                #  [La carte postale ne fait plus recette, article Du Parisien, du 23/08/2011 lire en ligne  [La carte postale ne fait plus recette, article Du Parisien, du 23/08/2011 lire en ligne]
"lire en ligne",                # page consultée le 24 octobre 2010    [texte intégral (page consultée le 24 octobre 2010)]
"m",                            #  masculi                             masculin
"mf ?",                         # l’usage hésite                       masculin ou féminin (l’usage hésite)Catégorie:Mots parfois masculins ou féminins en français
"mf",                           #  masculin et féminin identique       masculin et féminin identiques
"Modèle:Accord des couleurs",   #  Voir la note sur les accords grammaticaux des noms de couleurs employés comme noms ou adjectifs  Voir la note sur les accords grammaticaux des noms de couleurs employés comme noms ou adjectifs.
"Modèle:Citation/Daniel Nayeri/Brigade des crimes imaginaires/2012", # Daniel Nayeri, Coco et Cloclo, dans Brigade des crimes imaginaires et autres histoires fantastiques et déglinguées, traduit de l’anglais par Valérie Le Plouhinec, Hélium, 2008, page 335  — (Daniel Nayeri, Coco et Cloclo, dans Brigade des crimes imaginaires et autres histoires fantastiques et déglinguées, traduit de l’anglais par Valérie Le Plouhinec, Hélium, 2008, page 335)
"modèle:n-uple/exemple",        # a₁,a₂,…,aₙ                           Pour n > 0, si nous notons a₁ le premier élément, a₂ le deuxième élément, …, aₙ le nᵉ élément, le n-uple s’écrit : (a₁,a₂,…,aₙ) et le 0-uple s’écrit ( ).
"mot-valise",                   #  Mot-valisesamanch                   Mot-valisesamanche
"mplur",                        #  masculin plurie                     masculin pluriel
"msing",                        #  masculin singulie                   masculin singulier
"n",                            #  neutr                               neutre
"non standard",                 #  Il s’agit d’un terme utilisé qui n’est pas d’un usage standard.Catégorie:Termes non standards en françai  Il s’agit d’un terme utilisé qui n’est pas d’un usage standard.Catégorie:Termes non standards en français
"note",                         #  Note                                Note :
"ortho1990",                    # orthographe rectifiée de 1990        (orthographe rectifiée de 1990)
"ouvrage",                      #  Jean Baptiste Pierre Antoine de Monet de Lamarck, méthodique : Botanique, Jean Louis Marie Poire  Jean Baptiste Pierre Antoine de Monet de Lamarck, méthodique : Botanique, Jean Louis Marie Poiret
"Ouvrage",                      #  traduit par Claude Bertrand, La France de Vichy 1940-1944, préf. de Stanley Hoffmann, Éditions du Seuil, collection « L'Univers historique », Paris, 1973, page 5  traduit par Claude Bertrand, La France de Vichy 1940-1944, préf. de Stanley Hoffmann, Éditions du Seuil, collection « L'Univers historique », Paris, 1973, page 55
"ouvrage",                      # « Il était une fois… le Petit Maghreb de Montréal »  Bochra Manaï, Maghrébins de Montréal, chapitre IV (« Il était une fois… le Petit Maghreb de Montréal »), Les Presses de l'Université de Montréal, collection « Pluralismes », Montréal, 2018, page 92
"ouvrage\n', <PREFORMATTED(){} ' | titre = Histoire des oracles\n | auteur = ', <LINK(['w:Bernard Le Bouyer de Fontenelle", #  Bernard Le Bouyer de Fontenelle, des oracles, 172  Bernard Le Bouyer de Fontenelle, des oracles, 1728
"ouvrage\n",                    #  Marc Lachièze-Rey, Edgard Gunzig, Le Rayonnement cosmologique : Trace de l'Univers primordial, Masson, collection « De caelo », Paris, 1995, ISBN 2-225-84924-2, page avant-propo  Marc Lachièze-Rey, Edgard Gunzig, Le Rayonnement cosmologique : Trace de l'Univers primordial, Masson, collection « De caelo », Paris, 1995, ISBN 2-225-84924-2, page avant-propos
"p",                            #  plurie                              pluriel
"pc",                           #  ii                                  iii
"périodique ",                  #  « Les découvertes de la chronobiologie », dans Le Point, nᵒ 2320, 23 février 2017, page 48-5  « Les découvertes de la chronobiologie », dans Le Point, nᵒ 2320, 23 février 2017, page 48-51
"petites capitales",            #  balay-ion                           balay-ions
"peu attesté",                  #  Ce terme est très peu attesté.Catégorie:Termes peu attestés en françai  Ce terme est très peu attesté.Catégorie:Termes peu attestés en français
"phon",                         #  [j                                  [j]
"pluriel",                      #  plurie                              pluriel
"préciser",                     # définition à préciser ou à vérifier  (définition à préciser ou à vérifier)Catégorie:Pages à vérifier en français
"prnl",                         #  pronomina                           pronominal
"prnl",                         #  pronominalCatégorie:Verbes pronominaux en françai  pronominalCatégorie:Verbes pronominaux en français
"pron-API",                     #  [k                                  [k]
"prononciation",                #  \ɛ̃                                 \ɛ̃\
"R:LarousseXIXe",               #  Pierre Larousse, Grand dictionnaire universel du XIXᵉ siècle, 1866-1877 → consulter cet ouvrag  Pierre Larousse, Grand dictionnaire universel du XIXᵉ siècle, 1866-1877 → consulter cet ouvrage
"R:Littré",                     #  « livet », dans Émile Littré, Dictionnaire de la langue française, 1872–1877 → consulter cet ouvrag  « livet », dans Émile Littré, Dictionnaire de la langue française, 1872–1877 → consulter cet ouvrage
"R:Nicot1606",                  #  « reblandir », dans Jean Nicot, Thresor de la langue françoyse, 1606 → consulter cet ouvrag  « reblandir », dans Jean Nicot, Thresor de la langue françoyse, 1606 → consulter cet ouvrage
"R:Pauleau",                    #  Christine Pauleau, Le français de Nouvelle-Calédonie, EDICEF, 1995, ISBN 9782841290239, page 43  Christine Pauleau, Le français de Nouvelle-Calédonie, EDICEF, 1995, ISBN 9782841290239, page 43.
"R:Trévoux",                    #  « ACHE », dans [Jésuites de] Trévoux, Dictionnaire universel françois et latin, 1704–1771 → consulter cet ouvrag  « ACHE », dans [Jésuites de] Trévoux, Dictionnaire universel françois et latin, 1704–1771 → consulter cet ouvrage
"re",                           #  ʳ                                   ʳᵉ
"réciproque",                   #  réciproqu                           réciproque
"réciproque",                   #  réciproqueCatégorie:Verbes réciproques en françai  réciproqueCatégorie:Verbes réciproques en français
"réciproque2",                  # Réciproque                           (Réciproque)Catégorie:Verbes réciproques en français
"recons",                       #  *patt-Catégorie:Étymologies en français incluant une reconstructio  *patt-Catégorie:Étymologies en français incluant une reconstruction
"réf ?",                        # Référence nécessaire                 ^(Référence nécessaire)Catégorie:Références nécessaires en français
"réf?",                         # Référence nécessaire                 ^(Référence nécessaire)Catégorie:Références nécessaires en français
"référence nécessaire",         # Référence nécessaire                 ^(Référence nécessaire)Catégorie:Références nécessaires sans langue précisée
"réfl",                         #  réfléch                             réfléchi
"réfl",                         #  réfléchiCatégorie:Verbes réflexifs en françai  réfléchiCatégorie:Verbes réflexifs en français
"réfléchi",                     # Réfléchi                             (Réfléchi)Catégorie:Verbes réflexifs en français
"réflexif",                     # Réfléchi                             (Réfléchi)Catégorie:Verbes réflexifs en français
"réfnéc",                       # Référence nécessaire                 ^(Référence nécessaire)Catégorie:Références nécessaires en français
"refnec",                       # Référence nécessaire                 ^(Référence nécessaire)Catégorie:Références nécessaires sans langue précisée
"rire",                         #                                      
"s",                            #  singulie                            singulier
"sic !",                        # [sic : gibbsitogélite]               ^([sic : gibbsitogélite])
"SIC",                          # [sic]                                ^([sic])
"siècle",                       # XVIIᵉ siècle – fr                    (XVIIᵉ siècle – fr)
"smcp",                         #  vi                                  vii
"source ",                      # Jean Sellier, Histoire des langues et des peuples qui les parlent, 2020, La Découverte, page 338  — (Jean Sellier, Histoire des langues et des peuples qui les parlent, 2020, La Découverte, page 338)
"source?",                      # Référence nécessaire                 ^(Référence nécessaire)Catégorie:Références nécessaires en français
"source",                       # André Obey, Loire, 1933              — (André Obey, Loire, 1933)
"source",                       # Article Médicament générique sur l’encyclopédie Wikipédia Catégorie:Pages liées à Wikipédia en français  — (Article Médicament générique sur l’encyclopédie Wikipédia Catégorie:Pages liées à Wikipédia en français)
"sp",                           #  singulier et pluriel identique      singulier et pluriel identiques
"superlatif de",                #  Superlatif de fidèleCatégorie:Adjectifs superlatifs en françai  Superlatif de fidèleCatégorie:Adjectifs superlatifs en français
"T",                            #  AllemandCatégorie:Traductions en alleman  AllemandCatégorie:Traductions en allemand
"t",                            #  transitifCatégorie:Verbes transitifs en françai  transitifCatégorie:Verbes transitifs en français
"Temps géologiques",            #  382,7 ± 1,                          382,7 ± 1,6
"tr-dir",                       #  transitif directCatégorie:Verbes transitifs en françai  transitif directCatégorie:Verbes transitifs en français
"tr-indir",                     #  transitif indirectCatégorie:Verbes transitifs en françai  transitif indirectCatégorie:Verbes transitifs en français
"trad+",                        # tr                                   ilçe (tr)
"tradit",                       # orthographe traditionnelle           (orthographe traditionnelle)
"usage",                        #  Note d’usage                        Note d’usage :
"Variante de",                  #  Variante de franc-maçonn            Variante de franc-maçonne
"variante de",                  #  Variante de source à émission de cham  Variante de source à émission de champ
"variante ortho de ",           #  Variante orthographique de débecte  Variante orthographique de débecter
"Variante ortho de",            #  Variante orthographique de hosann   Variante orthographique de hosanna
"variante ortho de",            #  Variante orthographique de mespe    Variante orthographique de mesper
"variante ortho de",            # « monseigneur »                      Variante orthographique de Mᵍʳ (« monseigneur »)
"variante orthographique de",   #  Variante orthographique de calfouett  Variante orthographique de calfouette
"vérifier",                     #  Catégorie:Pages à vérifier sans langue précisé  Catégorie:Pages à vérifier sans langue précisée
"voir thésaurus",               #  |Aide sur le thésaurus cardinal figure dans les recueils de vocabulaire en français ayant pour thème : mathématiques, théorie des ensembles  |Aide sur le thésaurus cardinal figure dans les recueils de vocabulaire en français ayant pour thème : mathématiques, théorie des ensembles.
"voir-conj",                    # se conjugue → voir la conjugaison de être  (se conjugue → voir la conjugaison de être)
"voir",                         #  Voir aussi : Sapindacea             Voir aussi : Sapindaceae
"W",                            #  Établissements sociaux et médico-sociau  Établissements sociaux et médico-sociaux
"W",                            # LFSS                                 loi de financement de la Sécurité sociale (LFSS)
"wd",                           # dans la base de données Wikidata     Pierre-Louis ^(dans la base de données Wikidata)
"Wikipédia",                    # escalade                             bloc (escalade) sur l’encyclopédie Wikipédia Catégorie:Pages liées à Wikipédia en français
"Wikisource",                   #  La Fille Élisa dans la bibliothèque Wikisource Catégorie:Pages liées à Wikisource en françai  La Fille Élisa dans la bibliothèque Wikisource Catégorie:Pages liées à Wikisource en français
"WP",                           #  sac vocal sur l’encyclopédie Wikipédia Catégorie:Pages liées à Wikipédia en françai  sac vocal sur l’encyclopédie Wikipédia Catégorie:Pages liées à Wikipédia en français
"wp",                           # catégorie                            Somme_(catégorie) sur l’encyclopédie Wikipédia Catégorie:Pages liées à Wikipédia en français
"WS",                           #  Hannappes dans la bibliothèque Wikisource Catégorie:Pages liées à Wikisource en françai  Hannappes dans la bibliothèque Wikisource Catégorie:Pages liées à Wikisource en français
"ws",                           #  l’Andromaque de Racin               l’Andromaque de Racine
"wsp",                          #  Artemisia absinthiu                 Artemisia absinthium
"WSP",                          #  Odonata sur Wikispecies Catégorie:Pages liées à Wikispecies en françai  Odonata sur Wikispecies Catégorie:Pages liées à Wikispecies en français
]