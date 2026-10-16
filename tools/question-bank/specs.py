# Prompt specs. Each spec: prompt text + a SPARQL fragment binding ?item.
HUMAN_TYPES = ["Q5"]
GROUP_TYPES = ["Q215380", "Q5741069", "Q216337", "Q641066", "Q9212979", "Q2088357"]
ARTIST_TYPES = HUMAN_TYPES + GROUP_TYPES

def kinds(q):   # instances or subclasses (kinds of cheese, kinds of bread)
    return f"?item (wdt:P31|wdt:P279)/wdt:P279* wd:{q}."
def inst(q):
    return f"?item wdt:P31 wd:{q}."
def inst_sub(q):
    return f"?item wdt:P31/wdt:P279* wd:{q}."

S = []
def add(prompt, where, **kw):
    S.append(dict(prompt=prompt, where=where, **kw))

# ---------- Food & drink ----------
for p, q in [("Name a cheese", "Q10943"), ("Name a type of bread", "Q7802"), ("Name a pasta shape", "Q178"),
             ("Name a sausage", "Q131419"), ("Name a cake", "Q13276"), ("Name a cookie or biscuit", "Q13266"),
             ("Name a dessert", "Q182940"), ("Name a soup", "Q41415"), ("Name a sauce", "Q178359"),
             ("Name a salad", "Q9266"), ("Name a sandwich", "Q28803"), ("Name a dumpling", "Q1404232"),
             ("Name a cocktail", "Q134768"), ("Name a liqueur", "Q178780"), ("Name a pastry", "Q477248"),
             ("Name a sweet or candy", "Q185583"), ("Name a spice", "Q42527"), ("Name a herb", "Q207123"),
             ("Name a fruit", "Q3314483"), ("Name a vegetable", "Q11004"), ("Name a nut", "Q11009"),
             ("Name a type of pizza", "Q177"), ("Name a curry", "Q81938"), ("Name a coffee drink", "Q8486"),
             ("Name a type of tea", "Q6097"), ("Name a beer style", "Q44"), ("Name a wine", "Q282"),
             ("Name a cut of beef", "Q1371853"), ("Name a breakfast food", "Q1352767"), ("Name a pie", "Q13360264"),
             ("Name a noodle dish", "Q192874"), ("Name a rice dish", "Q2269709"), ("Name a stew", "Q178359x"),
             ("Name a condiment", "Q2596997"), ("Name a soft drink", "Q147538"), ("Name a whisky", "Q281"),
             ("Name a seafood dish", "Q1517248"), ("Name a mushroom you can eat", "Q654236"), ("Name a pudding", "Q13261"),
             ("Name a flatbread", "Q666242"), ("Name a street food", "Q1201902"), ("Name a fermented food", "Q1435347"),
             ("Name a type of chocolate", "Q195"), ("Name a snack food", "Q749316"), ("Name a doughnut", "Q192783"),
             ("Name an ice cream flavour or dessert", "Q13233"), ("Name a pancake", "Q44541"), ("Name a porridge", "Q216163")]:
    add(p, kinds(q), limit=500, minsl=2)
S[:] = [s for s in S if not s["where"].endswith("x.")]
add("Name a grape variety used for wine", inst("Q10978"), limit=500, minsl=2)
add("Name a breakfast cereal", inst_sub("Q215035"), limit=400, minsl=1)
add("Name a fast food chain", inst_sub("Q18509232"), limit=500, minsl=3)
add("Name a restaurant chain", inst_sub("Q18534714"), limit=500, minsl=3)
add("Name a chocolate bar brand", inst_sub("Q1500032"), limit=400, minsl=1)
add("Name a beer brand", inst("Q10838"), limit=500, minsl=2)

CUISINES = ["Japan", "China", "India", "Italy", "France", "Mexico", "Thailand", "South Korea", "Vietnam", "Spain", "Greece",
            "Turkey", "Germany", "United Kingdom", "United States of America", "Brazil", "Peru", "Indonesia", "Philippines",
            "Malaysia", "Russia", "Poland", "Lebanon", "Morocco", "Ethiopia", "Nigeria", "Iran", "Portugal", "Hungary",
            "Austria", "Sweden", "Argentina", "Israel", "Pakistan", "Georgia", "Ukraine", "Sri Lanka", "Singapore", "Australia", "Canada"]
DEMONYM = {"Japan": "Japanese", "China": "Chinese", "India": "Indian", "Italy": "Italian", "France": "French", "Mexico": "Mexican",
           "Thailand": "Thai", "South Korea": "Korean", "Vietnam": "Vietnamese", "Spain": "Spanish", "Greece": "Greek", "Turkey": "Turkish",
           "Germany": "German", "United Kingdom": "British", "United States of America": "American", "Brazil": "Brazilian", "Peru": "Peruvian",
           "Indonesia": "Indonesian", "Philippines": "Filipino", "Malaysia": "Malaysian", "Russia": "Russian", "Poland": "Polish",
           "Lebanon": "Lebanese", "Morocco": "Moroccan", "Ethiopia": "Ethiopian", "Nigeria": "Nigerian", "Iran": "Persian",
           "Portugal": "Portuguese", "Hungary": "Hungarian", "Austria": "Austrian", "Sweden": "Swedish", "Argentina": "Argentine",
           "Israel": "Israeli", "Pakistan": "Pakistani", "Georgia": "Georgian", "Ukraine": "Ukrainian", "Sri Lanka": "Sri Lankan",
           "Singapore": "Singaporean", "Australia": "Australian", "Canada": "Canadian"}
COUNTRY_TYPES = ["Q3624078", "Q6256"]
for c in CUISINES:
    d = DEMONYM[c]
    add(f"Name {'an' if d[0] in 'AEIOU' else 'a'} {d} dish or food", "?item wdt:P495 wd:{C}; (wdt:P31|wdt:P279)/wdt:P279* wd:Q746549.", limit=400, minsl=1, resolve={"C": (c, COUNTRY_TYPES)})

# ---------- Animals ----------
def taxon(q, rank=None):
    r = f" ?item wdt:P105 wd:{rank}." if rank else ""
    return f"?item wdt:P171+ wd:{q}.{r} ?item wdt:P225 ?tn. ?item rdfs:label ?en. FILTER(lang(?en)='en' && LCASE(STR(?en)) != LCASE(?tn))"
for p, q, rank, lim in [("Name a mammal", "Q7377", "Q7432", 600), ("Name a bird", "Q5113", "Q7432", 600), ("Name a reptile", "Q10811", "Q7432", 400),
                        ("Name a snake", "Q2102", "Q7432", 400), ("Name a shark", "Q7372", "Q7432", 300), ("Name an insect", "Q1390", None, 500),
                        ("Name a butterfly or moth", "Q28319", None, 400), ("Name a primate", "Q7380", None, 300), ("Name a member of the cat family", "Q25265", None, 200),
                        ("Name a whale or dolphin", "Q160", None, 200), ("Name an amphibian", "Q10908", None, 300), ("Name a spider", "Q1357", None, 300),
                        ("Name a fish", "Q127282", "Q7432", 600), ("Name a beetle", "Q22671", None, 300), ("Name a parrot", "Q31431", None, 250),
                        ("Name a bird of prey", "Q21140", None, 250), ("Name a rodent", "Q10850", None, 300), ("Name a marsupial", "Q25336", None, 250),
                        ("Name a crustacean", "Q25364", None, 300), ("Name a mollusc", "Q25326", None, 300), ("Name a lizard", "Q15879", None, 300),
                        ("Name a deer or antelope", "Q7363", None, 300), ("Name a duck, goose or swan", "Q25432", None, 250), ("Name an owl", "Q25263", None, 200),
                        ("Name a bat", "Q28425", None, 250), ("Name a turtle or tortoise", "Q223044", None, 250), ("Name a frog or toad", "Q53636", None, 250),
                        ("Name a tree", "Q25314", "Q7432", 500), ("Name a flowering plant", "Q25314", None, 600), ("Name a cactus or succulent", "Q14560", None, 250),
                        ("Name a palm tree", "Q15041", None, 200), ("Name a rose or relative of the rose", "Q46299", None, 300), ("Name an orchid", "Q25308", None, 250)]:
    add(p, taxon(q, rank), limit=lim, minsl=5)
add("Name a dinosaur", "?item wdt:P171+ wd:Q430; wdt:P105 wd:Q34740.", limit=500, minsl=2)
add("Name a dog breed", inst("Q39367"), limit=500, minsl=2)
add("Name a cat breed", inst("Q43577"), limit=200, minsl=1)
add("Name a horse breed", inst("Q1160573"), limit=400, minsl=2)
add("Name a cattle breed", inst("Q16889133"), limit=300, minsl=2)
add("Name a chicken breed", inst("Q4141838"), limit=300, minsl=2)
add("Name a Pokémon", inst("Q3966183"), limit=1100, minsl=1)
add("Name a legendary or mythical creature", inst_sub("Q2239243"), limit=500, minsl=5)
add("Name an extinct animal", "?item wdt:P141 wd:Q237350; wdt:P31 wd:Q16521. ?item wdt:P225 ?tn. ?item rdfs:label ?en. FILTER(lang(?en)='en' && LCASE(STR(?en)) != LCASE(?tn))", limit=400, minsl=3)
add("Name an endangered animal", "?item wdt:P141 wd:Q11394; wdt:P31 wd:Q16521. ?item wdt:P171+ wd:Q729. ?item wdt:P225 ?tn. ?item rdfs:label ?en. FILTER(lang(?en)='en' && LCASE(STR(?en)) != LCASE(?tn))", limit=400, minsl=5)

# ---------- Geography ----------
SOV = "?item wdt:P31 wd:Q3624078. FILTER NOT EXISTS { ?item wdt:P576 [] }"
add("Name a country", SOV, limit=300, minsl=1, kind="country")
for p, q in [("Name a country in Africa", "Q15"), ("Name a country in Asia", "Q48"), ("Name a country in Europe", "Q46"),
             ("Name a country in South America", "Q18"), ("Name a country in North America", "Q49"), ("Name a country in Oceania", "Q538")]:
    add(p, SOV + f" ?item wdt:P30 wd:{q}.", limit=100, minsl=1, kind="country", min=10)
add("Name a capital city", "?c wdt:P31 wd:Q3624078; wdt:P36 ?item. FILTER NOT EXISTS { ?c wdt:P576 [] }", limit=300, minsl=1)
add("Name a European capital city", "?c wdt:P31 wd:Q3624078; wdt:P30 wd:Q46; wdt:P36 ?item. FILTER NOT EXISTS { ?c wdt:P576 [] }", limit=100, minsl=1, min=15)
add("Name an Asian capital city", "?c wdt:P31 wd:Q3624078; wdt:P30 wd:Q48; wdt:P36 ?item. FILTER NOT EXISTS { ?c wdt:P576 [] }", limit=100, minsl=1, min=15)
add("Name an African capital city", "?c wdt:P31 wd:Q3624078; wdt:P30 wd:Q15; wdt:P36 ?item. FILTER NOT EXISTS { ?c wdt:P576 [] }", limit=100, minsl=1, min=15)
add("Name a US state", inst("Q35657"), limit=60, minsl=1, kind="state", min=10)
add("Name a US state capital", "?s wdt:P31 wd:Q35657; wdt:P36 ?item.", limit=60, minsl=1, min=10)
add("Name a county in England", inst("Q180673"), limit=60, minsl=1, min=10)
add("Name a London borough", inst("Q211690"), limit=40, minsl=1, min=10)
add("Name a Japanese prefecture", inst("Q50337"), limit=60, minsl=1, min=10)
add("Name a Canadian province or territory", "{ ?item wdt:P31 wd:Q11828004 } UNION { ?item wdt:P31 wd:Q9357527 }", limit=20, minsl=1, min=10)
add("Name an Australian state or territory", "{ ?item wdt:P31 wd:Q5852411 } UNION { ?item wdt:P31 wd:Q14192252 }", limit=20, minsl=1, min=6)
add("Name a state of India", inst("Q13390680"), limit=40, minsl=1, min=10)
add("Name a state of Mexico", inst("Q15149663"), limit=40, minsl=1, min=10)
add("Name a state of Brazil", inst("Q485258"), limit=40, minsl=1, min=10)
add("Name a German state", inst("Q1221156"), limit=20, minsl=1, min=10)
add("Name a region of Italy", inst("Q16110"), limit=30, minsl=1, min=10)
add("Name a Spanish province", inst("Q162620"), limit=60, minsl=1, min=10)
add("Name a Swiss canton", inst("Q23058"), limit=30, minsl=1, min=10)
add("Name a county of Ireland", inst("Q179872"), limit=40, minsl=1, min=10)
add("Name a Chinese province", inst("Q1615742"), limit=40, minsl=1, min=10)
add("Name a Scottish council area", inst("Q15060255"), limit=40, minsl=1, min=10)
add("Name a French department", inst("Q6465"), limit=120, minsl=1, min=10)
add("Name a Russian federal subject", "?item wdt:P31/wdt:P279* wd:Q43263.", limit=100, minsl=1, min=10)
add("Name a US national park", inst("Q34918"), limit=100, minsl=1)
for p, q in [("Name a river", "Q4022"), ("Name a mountain", "Q8502"), ("Name a volcano", "Q8072"), ("Name an island", "Q23442"),
             ("Name a lake", "Q23397"), ("Name a desert", "Q8514"), ("Name a sea", "Q165"), ("Name a waterfall", "Q34038"),
             ("Name a mountain range", "Q46831"), ("Name a skyscraper", "Q11303"), ("Name a famous bridge", "Q12280"),
             ("Name a museum", "Q33506"), ("Name a castle", "Q23413"), ("Name a stadium", "Q483110"), ("Name a palace", "Q16560"),
             ("Name a cathedral", "Q2977"), ("Name an airport", "Q1248784"), ("Name a university", "Q3918"), ("Name a peninsula", "Q34763"),
             ("Name a bay or gulf", "Q39594"), ("Name a strait", "Q37901"), ("Name a glacier", "Q35666"), ("Name a canyon", "Q150784"),
             ("Name a cave", "Q35509"), ("Name a ski resort", "Q130003"), ("Name a theme park", "Q2416723"), ("Name a zoo", "Q43501"),
             ("Name a lighthouse", "Q39715"), ("Name a temple", "Q44539"), ("Name a mosque", "Q32815"), ("Name a monument", "Q4989906"),
             ("Name a famous tower", "Q12518"), ("Name an archipelago", "Q33837"), ("Name a dam", "Q12323"), ("Name a racecourse or race circuit", "Q2338524")]:
    add(p, inst_sub(q), limit=600, minsl=8)
add("Name a UNESCO World Heritage Site", "?item wdt:P1435 wd:Q9259.", limit=700, minsl=10)
add("Name a city that has hosted the Olympics", "?g wdt:P31/wdt:P279* wd:Q5389; wdt:P276 ?item. ?item wdt:P31/wdt:P279* wd:Q486972.", limit=80, minsl=1)
add("Name a London Underground station", "?item wdt:P31/wdt:P279* wd:Q928830; wdt:P16 wd:Q20075.", limit=300, minsl=1)
add("Name a Paris Métro station", "?item wdt:P31/wdt:P279* wd:Q928830; wdt:P16 wd:Q50716.", limit=320, minsl=1)
CITY_COUNTRIES = ["United States of America", "United Kingdom", "France", "Germany", "Italy", "Spain", "Japan", "People's Republic of China", "India",
                  "Brazil", "Canada", "Australia", "Mexico", "Russia", "Netherlands", "Belgium", "Switzerland", "Austria", "Sweden", "Norway",
                  "Poland", "Portugal", "Greece", "Turkey", "Egypt", "Nigeria", "South Africa", "Argentina", "Chile", "Colombia", "Peru",
                  "Indonesia", "Philippines", "Vietnam", "Thailand", "South Korea", "Pakistan", "Iran", "Israel", "Ireland", "New Zealand",
                  "Denmark", "Finland", "Ukraine", "Morocco", "Kenya", "Saudi Arabia", "Malaysia", "Czech Republic", "Hungary", "Romania",
                  "Scotland", "Wales", "England", "Bangladesh", "Algeria", "Venezuela", "Cuba", "Croatia", "Serbia", "Bulgaria", "Iraq", "Syria"]
CITY_NAME = {"United States of America": "the US", "United Kingdom": "the UK", "People's Republic of China": "China", "Netherlands": "the Netherlands",
             "Philippines": "the Philippines", "Czech Republic": "the Czech Republic"}
for c in CITY_COUNTRIES:
    sub = c in ("Scotland", "Wales", "England")
    where = ("?item wdt:P131+ wd:{C}; " if sub else "?item wdt:P17 wd:{C}; ") + "wdt:P31/wdt:P279* wd:Q486972; wdt:P1082 ?pop. FILTER(?pop >= 15000)"
    add(f"Name a city or town in {CITY_NAME.get(c, c)}", where, limit=600, minsl=3, resolve={"C": (c, COUNTRY_TYPES + ["Q3336843", "Q6256"])})
for c in ["United States of America", "United Kingdom", "Canada", "Australia", "France", "Germany", "Italy", "Spain", "Japan", "India", "People's Republic of China", "Brazil"]:
    add(f"Name a river in {CITY_NAME.get(c, c)}", "?item wdt:P17 wd:{C}; wdt:P31/wdt:P279* wd:Q4022.", limit=400, minsl=4, resolve={"C": (c, COUNTRY_TYPES)})
    add(f"Name a university in {CITY_NAME.get(c, c)}", "?item wdt:P17 wd:{C}; wdt:P31/wdt:P279* wd:Q3918.", limit=500, minsl=6, resolve={"C": (c, COUNTRY_TYPES)})
for c in ["United States of America", "United Kingdom", "France", "Italy", "Greece", "Japan", "Canada", "Australia", "Spain", "Germany", "Switzerland", "Norway"]:
    add(f"Name a mountain in {CITY_NAME.get(c, c)}", "?item wdt:P17 wd:{C}; wdt:P31/wdt:P279* wd:Q8502.", limit=400, minsl=4, resolve={"C": (c, COUNTRY_TYPES)})
    add(f"Name an island belonging to {CITY_NAME.get(c, c)}", "?item wdt:P17 wd:{C}; wdt:P31/wdt:P279* wd:Q23442.", limit=400, minsl=5, resolve={"C": (c, COUNTRY_TYPES)})

# ---------- Science & nature ----------
add("Name a chemical element", inst("Q11344"), limit=130, minsl=1, kind="element")
add("Name a moon in the solar system", "?item wdt:P31/wdt:P279* wd:Q2537; wdt:P397 ?p. ?p wdt:P397 wd:Q525.", limit=200, minsl=3)
add("Name a constellation", inst("Q8928"), limit=100, minsl=1)
add("Name a star (in space)", inst_sub("Q523"), limit=400, minsl=15)
add("Name a galaxy", inst_sub("Q318"), limit=300, minsl=8)
add("Name a comet or asteroid", "{ ?item wdt:P31/wdt:P279* wd:Q3559 } UNION { ?item wdt:P31/wdt:P279* wd:Q3863 }", limit=300, minsl=10)
add("Name a spacecraft or space probe", "{ ?item wdt:P31/wdt:P279* wd:Q26529 } UNION { ?item wdt:P31/wdt:P279* wd:Q40218 }", limit=400, minsl=12)
add("Name a bone in the human body", kinds("Q265868"), limit=300, minsl=5)
add("Name a muscle in the human body", kinds("Q7365"), limit=300, minsl=5)
add("Name an organ of the human body", kinds("Q712378"), limit=300, minsl=15)
add("Name a disease", kinds("Q12136"), limit=600, minsl=30)
add("Name an infectious disease", kinds("Q18123741"), limit=500, minsl=15)
add("Name a medication", inst_sub("Q12140"), limit=500, minsl=30)
add("Name a vitamin", kinds("Q34956"), limit=60, minsl=5, min=10)
add("Name a hormone", kinds("Q11364"), limit=200, minsl=10)
add("Name an amino acid", inst_sub("Q8066"), limit=120, minsl=10, min=15)
add("Name a mineral", inst_sub("Q7946"), limit=500, minsl=10)
add("Name a gemstone", kinds("Q83437"), limit=300, minsl=4)
add("Name a type of rock", kinds("Q8063"), limit=300, minsl=12)
add("Name a unit of measurement", inst_sub("Q47574"), limit=500, minsl=15)
add("Name a geometric shape", kinds("Q815741"), limit=400, minsl=12)
add("Name a polygon", kinds("Q37555"), limit=100, minsl=8)
add("Name a mathematical theorem", inst_sub("Q65943"), limit=400, minsl=10)
add("Name a paradox", inst_sub("Q170584"), limit=200, minsl=5)
add("Name a logical fallacy", inst_sub("Q186150"), limit=200, minsl=4)
add("Name a phobia", inst_sub("Q175854"), limit=200, minsl=3)
add("Name a cognitive bias", inst_sub("Q1127759"), limit=200, minsl=4)
add("Name an elementary or subatomic particle", kinds("Q43116"), limit=150, minsl=15)
add("Name a programming language", inst_sub("Q9143"), limit=600, minsl=10)
add("Name an operating system", inst_sub("Q9135"), limit=400, minsl=10)
add("Name a web browser", inst_sub("Q6368"), limit=200, minsl=5)
add("Name a social media platform", inst_sub("Q3220391"), limit=300, minsl=10)
add("Name a cryptocurrency", inst_sub("Q13479982"), limit=200, minsl=5)
add("Name a video game console", inst_sub("Q8076"), limit=300, minsl=8)
add("Name a smartphone model", inst_sub("Q22645"), limit=400, minsl=15)
add("Name a computer virus or piece of malware", inst_sub("Q14001"), limit=200, minsl=8)
add("Name a type of cloud", kinds("Q8074"), limit=120, minsl=5)
add("Name a weather phenomenon", kinds("Q11663"), limit=200, minsl=20)
add("Name a named hurricane or tropical cyclone", inst_sub("Q8092"), limit=500, minsl=10)
add("Name a famous earthquake", inst_sub("Q7944"), limit=400, minsl=15)
add("Name a geological period or era", "{ ?item wdt:P31 wd:Q392928 } UNION { ?item wdt:P31 wd:Q630830 } UNION { ?item wdt:P31 wd:Q688113 }", limit=200, minsl=10)
add("Name a branch of science", kinds("Q2465832"), limit=500, minsl=40)
add("Name a sense or sensory system", kinds("Q11208"), limit=100, minsl=8, min=10)
add("Name an acid", kinds("Q11158"), limit=300, minsl=15)
add("Name an alloy", kinds("Q37756"), limit=200, minsl=8)
add("Name a type of fabric or textile", kinds("Q28823"), limit=400, minsl=10)
add("Name a colour", inst("Q1075"), limit=400, minsl=10)
add("Name a renewable or fossil energy source", kinds("Q12705"), limit=100, minsl=15, min=10)
add("Name a blood type, cell or blood component", kinds("Q7873"), limit=100, minsl=10, min=10)
add("Name a type of cell in the body", kinds("Q189118"), limit=300, minsl=10)

# ---------- People by occupation ----------
OCC = [("painter", "Q1028181"), ("sculptor", "Q1281618"), ("classical composer", "Q36834"), ("poet", "Q49757"), ("novelist", "Q6625963"),
       ("playwright", "Q214917"), ("philosopher", "Q4964182"), ("physicist", "Q169470"), ("chemist", "Q593644"), ("mathematician", "Q170790"),
       ("astronomer", "Q11063"), ("inventor", "Q205375"), ("astronaut", "Q11631"), ("architect", "Q42973"), ("fashion designer", "Q3501317"),
       ("chef", "Q3499072"), ("magician", "Q148401"), ("comedian", "Q245068"), ("rapper", "Q2252262"), ("DJ", "Q130857"),
       ("film director", "Q2526255"), ("guitarist", "Q855091"), ("drummer", "Q386854"), ("pianist", "Q486748"), ("opera singer", "Q2865819"),
       ("conductor", "Q158852"), ("photographer", "Q33231"), ("economist", "Q188094"), ("psychologist", "Q212980"), ("explorer", "Q11900058"),
       ("YouTuber", "Q17125263"), ("fashion model", "Q3357567"), ("ballet dancer", "Q805221"), ("cartoonist", "Q1114448"),
       ("comic book artist", "Q715301"), ("tennis player", "Q10833314"), ("golfer", "Q13156709"), ("Formula One driver", "Q10841764"),
       ("boxer", "Q11338576"), ("chess player", "Q10873124"), ("cyclist", "Q2309784"), ("sprinter", "Q4009406"), ("swimmer", "Q10843402"),
       ("figure skater", "Q13219587"), ("professional wrestler", "Q13474373"), ("mixed martial artist", "Q11607585"),
       ("basketball player", "Q3665646"), ("American football player", "Q19204627"), ("baseball player", "Q10871364"),
       ("ice hockey player", "Q11774891"), ("footballer", "Q937857"), ("cricketer", "Q12299841"), ("rugby union player", "Q14089670"),
       ("snooker player", "Q17165321"), ("skier", "Q4144610"), ("biologist", "Q864503"), ("historian", "Q201788"), ("sociologist", "Q2306091"),
       ("singer", "Q177220"), ("actor", "Q33999"), ("film producer", "Q3282637"), ("television presenter", "Q947873"), ("journalist", "Q1930187"),
       ("saxophonist", "Q12800682"), ("violinist", "Q1259917"), ("bassist", "Q584301"), ("songwriter", "Q753110"), ("record producer", "Q183945"),
       ("theologian", "Q1234713"), ("military officer", "Q189290"), ("engineer", "Q81096"), ("entrepreneur", "Q131524"), ("computer scientist", "Q82594"),
       ("animator", "Q266569"), ("video game designer", "Q3630699"), ("screenwriter", "Q28389"), ("illustrator", "Q644687"), ("children's author", "Q4853732"),
       ("science fiction writer", "Q18844224"), ("crime writer", "Q6051619"), ("darts player", "Q19799599"), ("jockey", "Q846750"), ("gymnast", "Q16947675"),
       ("skateboarder", "Q17125263x"), ("surfer", "Q13561328"), ("rock climber", "Q9149093"), ("volleyball player", "Q15117302"), ("handball player", "Q12840545"),
       ("badminton player", "Q13141064"), ("table tennis player", "Q13382519"), ("darts player", "Q19799599x"), ("racing cyclist", "Q15117395"),
       ("NASCAR driver", "Q15958185"), ("rally driver", "Q10842936"), ("motorcycle racer", "Q3014296"), ("sumo wrestler", "Q15982795"),
       ("marathon runner", "Q13382460"), ("high jumper", "Q13381753"), ("long jumper", "Q13381428"), ("pole vaulter", "Q13848274"),
       ("discus thrower", "Q13381689"), ("speed skater", "Q10866633"), ("biathlete", "Q16029547"), ("snowboarder", "Q15709642"), ("fencer", "Q13381863"),
       ("judoka", "Q6665249"), ("rower", "Q13382576"), ("archer", "Q13382355"), ("weightlifter", "Q13381376"), ("triathlete", "Q15306067")]
seen_occ = set()
for name, q in OCC:
    if q.endswith("x") or q in seen_occ: continue
    seen_occ.add(q)
    a = "an" if name[0].lower() in "aeiou" else "a"
    big = q in ("Q177220", "Q33999", "Q937857", "Q1930187", "Q82955")
    stem = {"classical composer": "composer", "film director": "director", "fashion model": "model", "comic book artist": "comic", "Formula One driver": "racing|driver",
            "professional wrestler": "wrestl", "mixed martial artist": "martial|MMA|fighter", "American football player": "football", "ice hockey player": "hockey",
            "footballer": "football|soccer", "rugby union player": "rugby", "children's author": "writer|author|novelist", "science fiction writer": "writer|author|novelist",
            "crime writer": "writer|author|novelist", "racing cyclist": "cycl", "NASCAR driver": "racing|driver|NASCAR", "motorcycle racer": "motorcycl|racer",
            "television presenter": "presenter|host|broadcaster", "record producer": "producer", "video game designer": "game", "military officer": "officer|general|admiral|military|soldier",
            "computer scientist": "computer", "opera singer": "opera|soprano|tenor|baritone|mezzo|bass", "ballet dancer": "ballet|dancer"}.get(name, name.split()[-1][:-2] if name.endswith("er") else name.split()[-1])
    add(f"Name {a} {name}", f"?item wdt:P31 wd:Q5; wdt:P106 wd:{q}.", limit=700, minsl=25 if big else 8, kind="person", desc=stem)

# ---------- Office holders & award winners ----------
for p, q in [("Name a US president", "Q11696"), ("Name a British prime minister", "Q14211"), ("Name a Roman emperor", "Q842606"),
             ("Name a pope", "Q19546"), ("Name an Egyptian pharaoh", "Q37110"), ("Name a US vice president", "Q11699"),
             ("Name a German chancellor", "Q4970706"), ("Name a UN Secretary-General", "Q81066"), ("Name a French president", "Q191954"),
             ("Name a Canadian prime minister", "Q839078"), ("Name an Australian prime minister", "Q319145"), ("Name a monarch of England", "Q18810062"),
             ("Name a US Secretary of State", "Q14213"), ("Name a Chief Justice or Supreme Court justice of the US", "Q11201"),
             ("Name a Holy Roman Emperor", "Q181765"), ("Name a Russian tsar or emperor", "Q12097"), ("Name a Chinese emperor", "Q268218"),
             ("Name a king of France", "Q3439798"), ("Name a mayor of London or New York", "Q11653"), ("Name a Prime Minister of India", "Q192711"),
             ("Name a President of Russia or the Soviet leader", "Q218295"), ("Name a Japanese prime minister", "Q274948"), ("Name a Spanish monarch", "Q18235919"),
             ("Name a Doctor Who actor (the Doctor)", "Q2316941")]:
    add(p, f"?item wdt:P39 wd:{q}.", limit=300, minsl=1, kind="person", min=10)
for p, q in [("Name a Nobel Prize in Literature winner", "Q37922"), ("Name a Nobel Prize in Physics winner", "Q38104"), ("Name a Nobel Peace Prize winner", "Q35637"),
             ("Name a Nobel Prize in Chemistry winner", "Q44585"), ("Name a Nobel Prize in Medicine winner", "Q80061"), ("Name a Nobel Prize in Economics winner", "Q47170"),
             ("Name a Best Actor Oscar winner", "Q103916"), ("Name a Best Actress Oscar winner", "Q103618"), ("Name a Best Director Oscar winner", "Q103360"),
             ("Name a Best Supporting Actor Oscar winner", "Q106291"), ("Name a Best Supporting Actress Oscar winner", "Q106301"),
             ("Name a Ballon d'Or winner", "Q166177"), ("Name a Pulitzer Prize for Fiction winner", "Q833633"), ("Name a Booker Prize winner", "Q160082"),
             ("Name a Fields Medal winner", "Q28835"), ("Name a Turing Award winner", "Q185667"), ("Name a Grammy Best New Artist winner", "Q935843"),
             ("Name a Time Person of the Year", "Q190961")]:
    add(p, f"?item wdt:P166 wd:{q}; wdt:P31 wd:Q5.", limit=300, minsl=1, kind="person", min=15)
add("Name a Best Picture Oscar winner", "?item wdt:P166 wd:Q102427.", limit=150, minsl=1)
add("Name a Palme d'Or winning film", "?item wdt:P166 wd:Q179808.", limit=150, minsl=1)
add("Name a Eurovision-winning song", "?item wdt:P166 wd:Q276."+"", limit=100, minsl=1, min=15)
add("Name a Pulitzer-winning novel", "?item wdt:P166 wd:Q833633; wdt:P31/wdt:P279* wd:Q7725634.", limit=150, minsl=1, min=15)
add("Name a Booker Prize-winning novel", "?item wdt:P166 wd:Q160082; wdt:P31/wdt:P279* wd:Q7725634.", limit=150, minsl=1, min=15)
add("Name a Game of the Year winner", "?item wdt:P166 ?a. ?a wdt:P31/wdt:P279* wd:Q4672301. ?item wdt:P31 wd:Q7889.", limit=200, minsl=5)

# ---------- Mythology & religion ----------
add("Name a Greek god or goddess", "{ ?item wdt:P31/wdt:P279* wd:Q22989102 } UNION { ?item wdt:P31/wdt:P279* wd:Q178885; wdt:P1080 wd:Q34726 }", limit=300, minsl=4)
add("Name a Roman god or goddess", "{ ?item wdt:P31/wdt:P279* wd:Q11688446 } UNION { ?item wdt:P31/wdt:P279* wd:Q178885; wdt:P1080 wd:Q122173 }", limit=300, minsl=4)
add("Name a Norse god or goddess", "{ ?item wdt:P31/wdt:P279* wd:Q16513881 } UNION { ?item wdt:P31/wdt:P279* wd:Q178885; wdt:P1080 wd:Q128285 }", limit=300, minsl=3)
add("Name an Egyptian god or goddess", "{ ?item wdt:P31/wdt:P279* wd:Q146083 } UNION { ?item wdt:P31/wdt:P279* wd:Q178885; wdt:P1080 wd:Q57225 }", limit=300, minsl=3)
add("Name a Hindu deity", "{ ?item wdt:P31/wdt:P279* wd:Q979507 } UNION { ?item wdt:P31/wdt:P279* wd:Q178885; wdt:P1080 wd:Q211392 }", limit=300, minsl=5)
add("Name a figure from Greek mythology", "?item wdt:P1080 wd:Q34726.", limit=600, minsl=6)
add("Name a figure from the Bible", "{ ?item wdt:P1441 wd:Q1845 } UNION { ?item wdt:P1441 wd:Q19786 } UNION { ?item wdt:P1441 wd:Q18813 }", limit=500, minsl=8)
add("Name a book of the Bible", "?item wdt:P31/wdt:P279* wd:Q49616; wdt:P361 ?b. VALUES ?b { wd:Q1845 wd:Q19786 wd:Q18813 wd:Q41490 }", limit=100, minsl=1, min=15)
add("Name a saint", "?item wdt:P31 wd:Q5; wdt:P411 wd:Q43115.", limit=600, minsl=20, kind="person")
add("Name a religion", kinds("Q9174"), limit=400, minsl=20)
add("Name a holiday or festival", "{ ?item wdt:P31/wdt:P279* wd:Q1445650 } UNION { ?item wdt:P31/wdt:P279* wd:Q132241 }", limit=600, minsl=20)
add("Name a fairy tale", inst_sub("Q699"), limit=300, minsl=5)

# ---------- Arts, entertainment ----------
for p, q, ms in [("Name a musical instrument", "Q34379", 5), ("Name a music genre", "Q188451", 15), ("Name a dance", "Q11639", 8),
                 ("Name a sport", "Q349", 15), ("Name a martial art", "Q11417", 4), ("Name a board game", "Q131436", 5), ("Name a card game", "Q142714", 4),
                 ("Name an art movement", "Q968159", 10), ("Name an architectural style", "Q32880", 10), ("Name a language", "Q34770", 30),
                 ("Name a writing system or alphabet", "Q8192", 15), ("Name a currency", "Q8142", 15), ("Name an item of clothing", "Q11460", 15),
                 ("Name a hat", "Q80151", 4), ("Name a type of shoe", "Q22676", 5), ("Name a piece of furniture", "Q14745", 8), ("Name a tool", "Q39546", 15),
                 ("Name a hairstyle", "Q1149207", 4), ("Name a type of boat or ship", "Q1229765", 10), ("Name a vehicle", "Q42889", 20),
                 ("Name a type of aircraft", "Q11436", 15), ("Name a weapon", "Q728", 15), ("Name a firearm", "Q12796", 10), ("Name a knot", "Q1078765", 3),
                 ("Name a poetic form", "Q1191125", 3), ("Name a literary genre", "Q223393", 15), ("Name a film genre", "Q201658", 10),
                 ("Name a toy", "Q11422", 10), ("Name a kitchen utensil or appliance", "Q3773693", 5), ("Name a container", "Q987767", 15),
                 ("Name a household appliance", "Q212920", 8), ("Name a game played with a ball", "Q2736", 10), ("Name a water sport", "Q216048", 5),
                 ("Name a winter sport", "Q204686", 5), ("Name a combat sport", "Q2468833", 5), ("Name a team sport", "Q216048x", 5),
                 ("Name a gymnastics or skating move", "Q1194952", 2), ("Name a chess opening", "Q103632", 3), ("Name a yoga posture", "Q2457048", 2),
                 ("Name a cheese dish or fondue", "Q12152x", 2), ("Name a dog sport or activity", "Q3253290", 2), ("Name a type of dance music", "Q1640319", 4),
                 ("Name a style of jazz", "Q8341x", 4), ("Name a subgenre of rock music", "Q11399x", 4), ("Name a subgenre of hip hop", "Q11401x", 3),
                 ("Name a subgenre of electronic music", "Q9778x", 3), ("Name a subgenre of heavy metal", "Q38848x", 3)]:
    if q.endswith("x"):
        continue
    add(p, kinds(q), limit=500, minsl=ms)
for p, q in [("Name a style of jazz", "Q8341"), ("Name a subgenre of rock music", "Q11399"), ("Name a subgenre of hip hop", "Q11401"),
             ("Name a subgenre of electronic music", "Q9778"), ("Name a subgenre of heavy metal", "Q38848"), ("Name a style of country music", "Q83440"),
             ("Name a subgenre of punk rock", "Q3071"), ("Name a style of pop music", "Q37073")]:
    add(p, f"?item wdt:P279+ wd:{q}.", limit=300, minsl=3)
add("Name a team sport", "?item wdt:P31/wdt:P279* wd:Q216048.", limit=300, minsl=5)
add("Name an Olympic sport", "?item wdt:P31/wdt:P279* wd:Q212434.", limit=300, minsl=5)
add("Name a famous painting", inst("Q3305213"), limit=600, minsl=20)
add("Name a famous sculpture", inst_sub("Q860861"), limit=400, minsl=15)
add("Name a classic novel", inst("Q8261"), limit=800, minsl=30)
add("Name a poem", inst_sub("Q5185279"), limit=500, minsl=10)
add("Name a book series", inst_sub("Q277759"), limit=600, minsl=10)
add("Name a manga", inst_sub("Q21198342"), limit=600, minsl=10)
add("Name an anime series", inst_sub("Q63952888"), limit=700, minsl=10)
add("Name a Broadway or West End musical", inst_sub("Q2743"), limit=600, minsl=6)
add("Name an opera", inst_sub("Q1344"), limit=600, minsl=6)
add("Name a ballet", inst_sub("Q1546797x"), limit=300, minsl=4)
S.pop()
add("Name a ballet", inst_sub("Q2627975"), limit=300, minsl=4)
add("Name a newspaper", inst_sub("Q11032"), limit=600, minsl=15)
add("Name a magazine", inst_sub("Q41298"), limit=600, minsl=12)
add("Name a comic strip", inst_sub("Q838795"), limit=400, minsl=6)
add("Name a comic book series", inst_sub("Q14406742"), limit=500, minsl=8)
add("Name a superhero", inst_sub("Q188784"), limit=600, minsl=5)
add("Name a supervillain", inst_sub("Q1144010"), limit=500, minsl=3)
add("Name a fictional detective", "?item wdt:P31/wdt:P279* wd:Q95074; wdt:P106 wd:Q842782.", limit=300, minsl=3)
add("Name a fictional dog", inst_sub("Q21070598"), limit=300, minsl=3)
add("Name a fictional cat", inst_sub("Q21070568"), limit=300, minsl=3)
add("Name a fictional robot", inst_sub("Q2552305"), limit=300, minsl=3)
add("Name a fictional wizard or witch", "{ ?item wdt:P31/wdt:P279* wd:Q15730398 } UNION { ?item wdt:P31/wdt:P279* wd:Q95074; wdt:P106 wd:Q338269 }", limit=300, minsl=3)
add("Name a fictional vampire", inst_sub("Q16975488"), limit=300, minsl=3)
add("Name an animated character", inst_sub("Q15711870"), limit=700, minsl=10)
add("Name a Disney character", "?item wdt:P31/wdt:P279* wd:Q95074. { ?item wdt:P1080 ?u. ?u wdt:P272 wd:Q191224 } UNION { ?item wdt:P1441 ?w. ?w wdt:P272 ?s. VALUES ?s { wd:Q191224 wd:Q1047410 wd:Q127552 } }", limit=600, minsl=3)
add("Name a video game character", inst_sub("Q1569167"), limit=700, minsl=8)
add("Name a mascot", inst_sub("Q431603"), limit=400, minsl=5)
add("Name a puppet or Muppet", inst_sub("Q18710149"), limit=300, minsl=3)
add("Name a famous ship", "?item wdt:P31/wdt:P279* wd:Q11446; wikibase:sitelinks ?s2. FILTER(?s2 > 15)", limit=500, minsl=15)
add("Name a famous racehorse", inst_sub("Q10855242"), limit=300, minsl=4)
add("Name a famous animal", inst_sub("Q26401003"), limit=400, minsl=6)
add("Name a national anthem", inst_sub("Q23691"), limit=400, minsl=10)
add("Name a Christmas song", "?item wdt:P136 wd:Q1062400.", limit=400, minsl=2)
add("Name a Christmas film", "?item wdt:P136 wd:Q1146335.", limit=400, minsl=2)
add("Name a nursery rhyme", inst_sub("Q4295957"), limit=300, minsl=2)
add("Name a famous speech", inst_sub("Q861911"), limit=300, minsl=6)
add("Name a famous diamond", inst_sub("Q11416x"), limit=100, minsl=3)
S.pop()

# Film / TV
add("Name a film", inst("Q11424"), limit=900, minsl=60)
add("Name an animated film", inst_sub("Q202866"), limit=800, minsl=15)
for g, q in [("horror", "Q200092"), ("comedy", "Q157443"), ("science fiction", "Q471839"), ("western", "Q172980"), ("war", "Q369747"),
             ("romance", "Q1054574"), ("superhero", "Q1535153"), ("crime", "Q959790"), ("fantasy", "Q157394"), ("thriller", "Q2484376"),
             ("musical", "Q842256"), ("action", "Q188473"), ("documentary", "Q93204"), ("disaster", "Q846544"), ("sports", "Q1196408"),
             ("spy", "Q2297927"), ("heist", "Q496523"), ("zombie", "Q1342372"), ("teen", "Q1146335x"), ("martial arts", "Q1167921"), ("mystery", "Q1200678"),
             ("drama", "Q130232"), ("biographical", "Q645928"), ("historical", "Q17013749"), ("noir", "Q185867"), ("adventure", "Q319221"), ("animated", "Q202866x"),
             ("coming-of-age", "Q1361932"), ("slasher", "Q853630"), ("monster", "Q1342372x"), ("psychological thriller", "Q20442589"), ("satire", "Q2973181"),
             ("romantic comedy", "Q860626"), ("road", "Q1361932x"), ("space opera", "Q752285"), ("cyberpunk", "Q204225"), ("dystopian", "Q20656232")]:
    if q.endswith("x"): continue
    a = "an" if g[0] in "aeiou" else "a"
    add(f"Name {a} {g} film", f"?item wdt:P31 wd:Q11424; wdt:P136 wd:{q}.", limit=700, minsl=8)
for dec in range(1920, 2030, 10):
    add(f"Name a film from the {dec}s", f"?item wdt:P31 wd:Q11424; wdt:P577 ?d. FILTER(YEAR(?d) >= {dec} && YEAR(?d) < {dec+10})", limit=700, minsl=30 if dec >= 1960 else 15)
for dec in range(1950, 2030, 10):
    add(f"Name a hit song from the {dec}s", f"?item wdt:P31 ?t. VALUES ?t {{ wd:Q7366 wd:Q134556 }} ?item wdt:P577 ?d. FILTER(YEAR(?d) >= {dec} && YEAR(?d) < {dec+10})", limit=800, minsl=12)
    add(f"Name an album from the {dec}s", f"?item wdt:P31 ?t. VALUES ?t {{ wd:Q482994 wd:Q208569 }} ?item wdt:P577 ?d. FILTER(YEAR(?d) >= {dec} && YEAR(?d) < {dec+10})", limit=800, minsl=15)
for dec in range(1950, 2030, 10):
    add(f"Name a TV series that started in the {dec}s", f"?item wdt:P31 wd:Q5398426; wdt:P580 ?d. FILTER(YEAR(?d) >= {dec} && YEAR(?d) < {dec+10})", limit=700, minsl=12)
for dec in range(1980, 2030, 10):
    add(f"Name a video game from the {dec}s", f"?item wdt:P31 wd:Q7889; wdt:P577 ?d. FILTER(YEAR(?d) >= {dec} && YEAR(?d) < {dec+10})", limit=800, minsl=15)
add("Name a TV sitcom", "?item wdt:P31 wd:Q5398426; wdt:P136 wd:Q170238.", limit=700, minsl=6)
add("Name a reality TV show", "?item wdt:P31/wdt:P279* wd:Q5398426; wdt:P136 wd:Q182415.", limit=500, minsl=6)
add("Name a TV game show", "{ ?item wdt:P31/wdt:P279* wd:Q5398426; wdt:P136 wd:Q20190959 } UNION { ?item wdt:P31 wd:Q20190959 }", limit=500, minsl=6)
add("Name an animated TV series", inst_sub("Q581714"), limit=800, minsl=10)
add("Name a soap opera", "?item wdt:P136 wd:Q23739.", limit=400, minsl=6)
add("Name a talk show", "?item wdt:P136 wd:Q622812.", limit=400, minsl=5)
add("Name a TV drama series", "?item wdt:P31 wd:Q5398426; wdt:P136 wd:Q1366112.", limit=700, minsl=12)
add("Name a science fiction TV series", "?item wdt:P31 wd:Q5398426; wdt:P136 wd:Q336059.", limit=500, minsl=8)
add("Name a crime TV series", "?item wdt:P31 wd:Q5398426; wdt:P136 ?g. VALUES ?g { wd:Q9335577 wd:Q959790 wd:Q1550211 }", limit=600, minsl=10)
add("Name a children's TV show", "?item wdt:P31/wdt:P279* wd:Q5398426; wdt:P136 wd:Q1104295x.", limit=500, minsl=6)
S.pop()
add("Name a TV series", inst("Q5398426"), limit=900, minsl=40)
add("Name a video game", inst("Q7889"), limit=900, minsl=40)
add("Name a video game franchise", inst_sub("Q7058673"), limit=600, minsl=10)
add("Name a fighting game", "?item wdt:P31 wd:Q7889; wdt:P136 wd:Q846224.", limit=500, minsl=6)
add("Name a role-playing video game", "?item wdt:P31 wd:Q7889; wdt:P136 wd:Q744038.", limit=700, minsl=10)
add("Name a first-person shooter", "?item wdt:P31 wd:Q7889; wdt:P136 wd:Q185029.", limit=700, minsl=10)
add("Name a platform game", "?item wdt:P31 wd:Q7889; wdt:P136 wd:Q828322.", limit=700, minsl=10)
add("Name a racing video game", "?item wdt:P31 wd:Q7889; wdt:P136 wd:Q860750.", limit=600, minsl=8)
add("Name a puzzle video game", "?item wdt:P31 wd:Q7889; wdt:P136 wd:Q54767.", limit=600, minsl=8)
add("Name a strategy video game", "?item wdt:P31 wd:Q7889; wdt:P136 ?g. VALUES ?g { wd:Q4103 wd:Q4369 wd:Q1203590 wd:Q1688220 }", limit=600, minsl=8)
add("Name a survival horror game", "?item wdt:P31 wd:Q7889; wdt:P136 wd:Q1129348.", limit=400, minsl=6)
add("Name a sports video game", "?item wdt:P31 wd:Q7889; wdt:P136 wd:Q868217.", limit=600, minsl=6)
add("Name an arcade game", "?item wdt:P31 wd:Q7889; wdt:P400 wd:Q192851.", limit=600, minsl=6)
add("Name a mobile game", "?item wdt:P31 wd:Q7889; wdt:P400 ?pl. VALUES ?pl { wd:Q48493 wd:Q94 }", limit=600, minsl=10)
for console in ["Nintendo Entertainment System", "Super Nintendo Entertainment System", "Nintendo 64", "GameCube", "Wii", "Nintendo Switch", "Game Boy",
                "Nintendo DS", "PlayStation", "PlayStation 2", "PlayStation 3", "PlayStation 4", "Xbox", "Xbox 360", "Sega Genesis", "Dreamcast", "Game Boy Advance", "Atari 2600"]:
    add(f"Name a game released for the {console}", "?item wdt:P31 wd:Q7889; wdt:P400 wd:{C}.", limit=700, minsl=6, resolve={"C": (console, ["Q8076", "Q62008942", "Q17589470"])})

# ---------- Brands / companies ----------
add("Name a car brand", "{ ?item wdt:P31/wdt:P279* wd:Q786820 } UNION { ?item wdt:P31 wd:Q17085090x }", limit=600, minsl=10)
add("Name an airline", inst_sub("Q46970"), limit=600, minsl=15)
add("Name a fashion house or clothing brand", "{ ?item wdt:P31/wdt:P279* wd:Q1618899 } UNION { ?item wdt:P31/wdt:P279* wd:Q431289; wdt:P452 wd:Q11460 }", limit=500, minsl=8)
add("Name a supermarket chain", inst_sub("Q18043413"), limit=400, minsl=5)
add("Name a department store", inst_sub("Q216107"), limit=400, minsl=6)
add("Name a video game company", inst_sub("Q210167"), limit=600, minsl=15)
add("Name a record label", inst_sub("Q18127"), limit=600, minsl=10)
add("Name a film studio", inst_sub("Q375336"), limit=500, minsl=10)
add("Name a tech company", "?item wdt:P31/wdt:P279* wd:Q4830453; wdt:P452 ?ind. VALUES ?ind { wd:Q880371 wd:Q11661 wd:Q1622444 wd:Q638608 wd:Q21129801 }", limit=600, minsl=25)
add("Name a bank", inst_sub("Q22687"), limit=600, minsl=15)
add("Name a toy company or toy brand", "?item wdt:P452 wd:Q1137109.", limit=400, minsl=5)
add("Name a sportswear brand", "?item wdt:P452 wd:Q1149652x.", limit=400, minsl=5)
S.pop()
add("Name a hotel chain", inst_sub("Q1631129"), limit=300, minsl=5)
add("Name a TV channel", inst_sub("Q2001305"), limit=700, minsl=15)
add("Name a streaming service", inst_sub("Q15590336x"), limit=200, minsl=5)
S.pop()
add("Name a motorcycle manufacturer", inst_sub("Q936518"), limit=300, minsl=5)
add("Name a watch brand", "?item wdt:P452 wd:Q1066186.", limit=300, minsl=4)
add("Name a camera manufacturer", "?item wdt:P1056 wd:Q15328.", limit=300, minsl=5)
add("Name a Formula One team or constructor", inst_sub("Q10497835"), limit=300, minsl=3)
CAR_MAKERS = ["Ford Motor Company", "Toyota", "BMW", "Mercedes-Benz", "Volkswagen", "Ferrari", "Porsche", "Honda", "Chevrolet", "Nissan", "Audi",
              "Lamborghini", "Fiat", "Renault", "Peugeot", "Volvo Cars", "Hyundai Motor Company", "Mazda", "Jaguar Cars", "Land Rover", "Aston Martin",
              "Tesla, Inc.", "Dodge", "Jeep", "Subaru", "Kia", "Rolls-Royce Motor Cars", "Citroën", "Mitsubishi Motors", "Alfa Romeo", "Opel", "Škoda Auto",
              "SEAT", "Lotus Cars", "Cadillac", "Buick", "Pontiac", "Lexus", "Bentley", "Maserati", "Bugatti", "Mini", "Saab Automobile", "Suzuki", "Lada", "Vauxhall Motors"]
for m in CAR_MAKERS:
    nm = m.replace(" Motor Company", "").replace(", Inc.", "").replace(" Cars", "").replace(" Motors", "").replace(" Auto", "").replace(" Automobile", "")
    add(f"Name a {nm} car model", "?item wdt:P176 wd:{C}; wdt:P31/wdt:P279* wd:Q3231690.", limit=400, minsl=2, resolve={"C": (m, ["Q786820", "Q4830453", "Q431289", "Q167270", "Q6881511", "Q891723"])})

# ---------- Sports teams ----------
def league(q): return f"?item wdt:P118 wd:{q}. FILTER NOT EXISTS {{ ?item wdt:P576 [] }}"
for p, q in [("Name an NBA team", "Q155223"), ("Name an NFL team", "Q1215884"), ("Name an MLB team", "Q1163715"), ("Name an NHL team", "Q1215892"),
             ("Name an MLS team", "Q18543")]:
    add(p, league(q) + " ?item wdt:P31/wdt:P279* wd:Q12973014.", limit=60, minsl=1, min=15)
for p, q in [("Name a club that has played in the Premier League", "Q9448"), ("Name a club that has played in La Liga", "Q324867"),
             ("Name a club that has played in Serie A", "Q15804"), ("Name a club that has played in the Bundesliga", "Q82595"),
             ("Name a club that has played in Ligue 1", "Q13394"), ("Name a club that has played in the Eredivisie", "Q207815"),
             ("Name a club that has played in the Scottish Premiership", "Q1129245"), ("Name a club that has played in the EFL Championship", "Q19510"),
             ("Name a club that has played in the Primeira Liga", "Q182994"), ("Name a club that has played in the Brazilian Série A", "Q206813")]:
    add(p, f"?item wdt:P118 wd:{q}.", limit=200, minsl=1, min=15)
add("Name a national football team", inst("Q6979593"), limit=250, minsl=10)
add("Name an IPL cricket team", "?item wdt:P118 wd:Q1199893x.", limit=30, minsl=1)
S.pop()
add("Name a college football or basketball school (NCAA Division I)", "?item wdt:P31/wdt:P279* wd:Q3918; wdt:P17 wd:Q30; wdt:P1534 ?x.", limit=10, minsl=1)
S.pop()
CLUBS = ["Manchester United F.C.", "Liverpool F.C.", "Arsenal F.C.", "Chelsea F.C.", "Manchester City F.C.", "Tottenham Hotspur F.C.", "Everton F.C.",
         "Newcastle United F.C.", "Aston Villa F.C.", "West Ham United F.C.", "Leeds United F.C.", "Real Madrid CF", "FC Barcelona", "Atlético Madrid",
         "FC Bayern Munich", "Borussia Dortmund", "Juventus FC", "AC Milan", "Inter Milan", "AS Roma", "SSC Napoli", "Paris Saint-Germain FC",
         "Olympique de Marseille", "AFC Ajax", "PSV Eindhoven", "S.L. Benfica", "FC Porto", "Celtic F.C.", "Rangers F.C.", "Boca Juniors",
         "Club Atlético River Plate", "Santos FC", "Clube de Regatas do Flamengo", "LA Galaxy", "Inter Miami CF", "Sevilla FC", "Valencia CF",
         "Olympique Lyonnais", "Bayer 04 Leverkusen", "Lazio", "Fiorentina", "Galatasaray S.K.", "Fenerbahçe S.K.",
         "England national football team", "Brazil national football team", "Argentina national football team", "France national football team",
         "Germany national football team", "Italy national football team", "Spain national football team", "Netherlands national football team",
         "Portugal national football team", "United States men's national soccer team", "Scotland national football team", "Wales national football team",
         "Republic of Ireland national football team", "Mexico national football team", "Belgium national football team",
         "Los Angeles Lakers", "Boston Celtics", "Chicago Bulls", "Golden State Warriors", "New York Knicks", "Miami Heat", "San Antonio Spurs",
         "Dallas Cowboys", "New England Patriots", "Green Bay Packers", "Pittsburgh Steelers", "San Francisco 49ers", "Kansas City Chiefs",
         "New York Yankees", "Boston Red Sox", "Los Angeles Dodgers", "Chicago Cubs", "St. Louis Cardinals",
         "Montreal Canadiens", "Toronto Maple Leafs", "Detroit Red Wings", "New Zealand national rugby union team", "England national rugby union team",
         "Australia national cricket team", "England cricket team", "India national cricket team", "Mercedes-AMG Petronas F1 Team", "Scuderia Ferrari", "McLaren"]
CLUB_TYPES = ["Q476028", "Q12973014", "Q847017", "Q6979593", "Q13393265", "Q17156793", "Q13027888", "Q1076486", "Q10517054", "Q4498974", "Q20639856", "Q2485182", "Q1194951", "Q1803226"]
for c in CLUBS:
    nm = c.replace(" F.C.", "").replace(" FC", "").replace(" CF", "").replace(" S.K.", "").replace("FC ", "").replace("AFC ", "").replace("SSC ", "").replace("S.L. ", "")
    nm = nm.replace("Club Atlético ", "").replace("Clube de Regatas do ", "").replace("-AMG Petronas F1 Team", "").replace("Scuderia ", "")
    nm = nm.replace("national football team", "national team").replace("men's national soccer team", "men's national team")
    verb = "driven for" if c in ("Mercedes-AMG Petronas F1 Team", "Scuderia Ferrari", "McLaren") else "played for"
    add(f"Name someone who has {verb} {'the ' if 'national' in nm or c in ('England cricket team',) else ''}{nm}",
        "?item wdt:P54 wd:{C}; wdt:P31 wd:Q5.", limit=700, minsl=3, kind="person", resolve={"C": (c, CLUB_TYPES)})

# ---------- Works by creators ----------
ARTISTS = ["Taylor Swift", "The Beatles", "Michael Jackson", "Madonna", "Elvis Presley", "Queen", "The Rolling Stones", "Beyoncé", "Rihanna",
           "Drake", "Eminem", "Kanye West", "Lady Gaga", "Ed Sheeran", "Adele", "Bruno Mars", "Katy Perry", "Britney Spears", "Justin Bieber",
           "Ariana Grande", "Billie Eilish", "Dua Lipa", "The Weeknd", "Coldplay", "U2", "Oasis", "Radiohead", "Led Zeppelin", "Pink Floyd",
           "David Bowie", "Elton John", "Prince", "Whitney Houston", "Mariah Carey", "Celine Dion", "ABBA", "Bob Dylan", "Bruce Springsteen",
           "Nirvana", "Metallica", "AC/DC", "Guns N' Roses", "Red Hot Chili Peppers", "Green Day", "Linkin Park", "Foo Fighters", "Arctic Monkeys",
           "The Killers", "Muse", "Blur", "The Smiths", "The Cure", "Depeche Mode", "Pet Shop Boys", "Duran Duran", "Kylie Minogue", "Spice Girls",
           "Take That", "One Direction", "Backstreet Boys", "NSYNC", "Destiny's Child", "TLC", "Janet Jackson", "Stevie Wonder", "Marvin Gaye",
           "Aretha Franklin", "Ray Charles", "Frank Sinatra", "Johnny Cash", "Dolly Parton", "Shania Twain", "Garth Brooks", "Kenny Rogers",
           "Fleetwood Mac", "Eagles", "The Beach Boys", "The Doors", "Jimi Hendrix", "The Who", "The Kinks", "Black Sabbath", "Iron Maiden",
           "Bon Jovi", "Aerosmith", "Kiss", "Van Halen", "Def Leppard", "Journey", "Toto", "Billy Joel", "Phil Collins", "Genesis", "Sting", "The Police",
           "Lionel Richie", "George Michael", "Wham!", "Tina Turner", "Cher", "Bee Gees", "Earth, Wind & Fire", "Kendrick Lamar", "Jay-Z", "Nicki Minaj",
           "Snoop Dogg", "50 Cent", "Tupac Shakur", "The Notorious B.I.G.", "Outkast", "Missy Elliott", "Travis Scott", "Post Malone", "Harry Styles",
           "Olivia Rodrigo", "Sabrina Carpenter", "Doja Cat", "SZA", "Lana Del Rey", "Lorde", "Sia", "Shakira", "Jennifer Lopez", "Christina Aguilera",
           "Pink", "Avril Lavigne", "Kelly Clarkson", "Miley Cyrus", "Selena Gomez", "Demi Lovato", "Usher", "Chris Brown", "Justin Timberlake",
           "Maroon 5", "Imagine Dragons", "OneRepublic", "Coldplay", "BTS", "Blackpink", "Bad Bunny", "Daft Punk", "Calvin Harris", "David Guetta",
           "Avicii", "The Chemical Brothers", "Gorillaz", "Paul McCartney", "John Lennon", "Bob Marley", "Neil Young", "Simon & Garfunkel",
           "Paul Simon", "Joni Mitchell", "Leonard Cohen", "Tom Petty", "R.E.M.", "Pearl Jam", "Soundgarden", "Weezer", "Blink-182", "Paramore",
           "My Chemical Romance", "Fall Out Boy", "The Strokes", "The White Stripes", "Kings of Leon", "Florence and the Machine", "Amy Winehouse",
           "Robbie Williams", "Girls Aloud", "Little Mix", "Sugababes", "Kate Bush", "Elvis Costello", "The Clash", "Sex Pistols", "Ramones",
           "Talking Heads", "Blondie", "Roxy Music", "T. Rex", "Slade", "The Jam", "Madness", "UB40", "Eurythmics", "Tears for Fears", "Simple Minds",
           "Erasure", "New Order", "Joy Division", "The Stone Roses", "Pulp", "Suede", "Manic Street Preachers", "Stereophonics", "Travis",
           "Snow Patrol", "Kasabian", "Franz Ferdinand", "Bloc Party", "Glass Animals", "Chappell Roan", "Charli XCX", "Megan Thee Stallion",
           "Cardi B", "Lil Wayne", "Lil Nas X", "Mac Miller", "J. Cole", "Tyler, the Creator", "Frank Ocean", "Childish Gambino", "Lizzo",
           "Halsey", "Camila Cabello", "Shawn Mendes", "Lewis Capaldi", "Sam Smith", "George Ezra", "Stormzy", "Dave", "Skepta", "Ella Fitzgerald",
           "Louis Armstrong", "Miles Davis", "Nina Simone", "Billie Holiday", "Chuck Berry", "Little Richard", "Buddy Holly", "Roy Orbison",
           "Cliff Richard", "Tom Jones", "Dusty Springfield", "Barbra Streisand", "Neil Diamond", "Barry Manilow", "Carpenters", "The Supremes",
           "The Temptations", "Diana Ross", "Smokey Robinson", "Otis Redding", "James Brown", "Sam Cooke", "Al Green", "Hozier", "Noah Kahan",
           "Zach Bryan", "Morgan Wallen", "Luke Combs", "Carrie Underwood", "Tim McGraw", "Kacey Musgraves", "Willie Nelson", "Hank Williams",
           "Patsy Cline", "Loretta Lynn", "Reba McEntire", "Rammstein", "Scorpions", "a-ha", "Roxette", "Europe", "Ace of Base", "Björk",
           "Enya", "The Cranberries", "Sinéad O'Connor", "The Pogues", "Thin Lizzy", "Westlife", "Boyzone", "The Corrs", "Sufjan Stevens",
           "Vampire Weekend", "Arcade Fire", "LCD Soundsystem", "Tame Impala", "The 1975", "Bastille", "Twenty One Pilots", "Panic! at the Disco",
           "Ozzy Osbourne", "Slipknot", "System of a Down", "Rage Against the Machine", "Tool", "Korn", "Limp Bizkit", "Evanescence", "Nickelback",
           "Creed", "Matchbox Twenty", "Goo Goo Dolls", "No Doubt", "Gwen Stefani", "Alanis Morissette", "Sheryl Crow", "Norah Jones", "John Legend",
           "Alicia Keys", "Mary J. Blige", "Lauryn Hill", "Fugees", "Wu-Tang Club", "Wu-Tang Clan", "Run-DMC", "Beastie Boys", "Public Enemy",
           "Dr. Dre", "Ice Cube", "N.W.A", "Busta Rhymes", "Pharrell Williams", "Nelly", "Ludacris", "T-Pain", "Akon", "Sean Paul", "Shaggy",
           "Pitbull", "Enrique Iglesias", "Ricky Martin", "Marc Anthony", "Gloria Estefan", "Juanes", "Karol G", "J Balvin", "Rosalía",
           "Stray Kids", "Twice", "Seventeen", "Big Bang", "Girls' Generation", "Exo", "NewJeans"]
ARTISTS = list(dict.fromkeys(ARTISTS))
SONG = "VALUES ?t { wd:Q7366 wd:Q134556 wd:Q105543609 } ?item wdt:P31 ?t."
for a in ARTISTS:
    add(f"Name a song by {a}", "?item wdt:P175 wd:{C}. " + SONG, limit=500, minsl=1, resolve={"C": (a, ARTIST_TYPES)})
ALBUM_ARTISTS = ARTISTS[:150]
for a in ALBUM_ARTISTS:
    add(f"Name an album by {a}", "?item wdt:P175 wd:{C}. VALUES ?t { wd:Q482994 wd:Q208569 wd:Q209939 wd:Q222910 } ?item wdt:P31 ?t.", limit=300, minsl=1, min=12, resolve={"C": (a, ARTIST_TYPES)})

DIRECTORS = ["Steven Spielberg", "Alfred Hitchcock", "Stanley Kubrick", "Martin Scorsese", "Quentin Tarantino", "Christopher Nolan", "Ridley Scott",
             "James Cameron", "Tim Burton", "Woody Allen", "Clint Eastwood", "Francis Ford Coppola", "David Fincher", "Wes Anderson", "Coen brothers",
             "Joel Coen", "Spike Lee", "Ron Howard", "Robert Zemeckis", "John Carpenter", "Wes Craven", "Sam Raimi", "Peter Jackson", "Guillermo del Toro",
             "Denis Villeneuve", "Danny Boyle", "Guy Ritchie", "Michael Bay", "Zack Snyder", "J. J. Abrams", "George Lucas", "Brian De Palma",
             "Oliver Stone", "Ang Lee", "Hayao Miyazaki", "Akira Kurosawa", "Ingmar Bergman", "Federico Fellini", "Pedro Almodóvar", "Billy Wilder",
             "John Ford", "Howard Hawks", "Orson Welles", "David Lynch", "Terry Gilliam", "Richard Linklater", "Paul Thomas Anderson", "Sofia Coppola",
             "Greta Gerwig", "Jordan Peele", "Ridley Scott", "Tony Scott", "Steven Soderbergh", "Rob Reiner", "John Hughes", "Chris Columbus",
             "Mel Brooks", "John Landis", "Ivan Reitman", "Richard Curtis", "Edgar Wright", "Taika Waititi", "M. Night Shyamalan", "Darren Aronofsky",
             "Baz Luhrmann", "Kathryn Bigelow", "Sergio Leone", "Roman Polanski", "Werner Herzog", "Jean-Luc Godard", "François Truffaut", "Satyajit Ray",
             "Wong Kar-wai", "Bong Joon-ho", "Park Chan-wook", "Zhang Yimou", "John Woo", "Luc Besson", "Paul Verhoeven", "David Cronenberg",
             "Michael Mann", "Ken Loach", "Mike Leigh", "Danny DeVito", "Penny Marshall", "Nora Ephron", "Garry Marshall", "Frank Capra", "Charlie Chaplin",
             "Buster Keaton", "Sidney Lumet", "Lars von Trier", "Yorgos Lanthimos", "Ari Aster", "Robert Altman", "Jim Jarmusch", "Rob Zombie", "Joe Dante"]
DIRECTORS = list(dict.fromkeys(DIRECTORS))
for d in DIRECTORS:
    add(f"Name a film directed by {d}", "?item wdt:P57 wd:{C}; wdt:P31/wdt:P279* wd:Q11424.", limit=200, minsl=1, min=10, resolve={"C": (d, HUMAN_TYPES + ["Q1141470"])})
ACTORS = ["Tom Hanks", "Meryl Streep", "Leonardo DiCaprio", "Brad Pitt", "Tom Cruise", "Julia Roberts", "Denzel Washington", "Robert De Niro",
          "Al Pacino", "Jack Nicholson", "Harrison Ford", "Johnny Depp", "Morgan Freeman", "Samuel L. Jackson", "Will Smith", "Nicole Kidman",
          "Scarlett Johansson", "Keanu Reeves", "Sandra Bullock", "Matt Damon", "George Clooney", "Cate Blanchett", "Kate Winslet", "Christian Bale",
          "Arnold Schwarzenegger", "Sylvester Stallone", "Bruce Willis", "Jim Carrey", "Robin Williams", "Eddie Murphy", "Adam Sandler", "Ben Stiller",
          "Will Ferrell", "Jennifer Aniston", "Cameron Diaz", "Drew Barrymore", "Reese Witherspoon", "Natalie Portman", "Anne Hathaway", "Emma Stone",
          "Ryan Gosling", "Ryan Reynolds", "Dwayne Johnson", "Jason Statham", "Vin Diesel", "Hugh Jackman", "Robert Downey Jr.", "Chris Hemsworth",
          "Chris Evans", "Mark Wahlberg", "Jake Gyllenhaal", "Joaquin Phoenix", "Daniel Day-Lewis", "Gary Oldman", "Anthony Hopkins", "Michael Caine",
          "Judi Dench", "Helen Mirren", "Maggie Smith", "Emma Thompson", "Hugh Grant", "Colin Firth", "Ralph Fiennes", "Benedict Cumberbatch",
          "Tom Hardy", "Daniel Craig", "Pierce Brosnan", "Sean Connery", "Roger Moore", "Ian McKellen", "Patrick Stewart", "Kevin Costner",
          "Kevin Bacon", "Kevin Spacey", "Mel Gibson", "Russell Crowe", "Cary Grant", "James Stewart", "Humphrey Bogart", "Audrey Hepburn",
          "Marilyn Monroe", "Katharine Hepburn", "Bette Davis", "Elizabeth Taylor", "Marlon Brando", "Paul Newman", "Clint Eastwood", "John Wayne",
          "Gene Hackman", "Dustin Hoffman", "Michael Douglas", "Jeff Bridges", "Bill Murray", "Steve Martin", "Owen Wilson", "Seth Rogen",
          "Jonah Hill", "Zendaya", "Timothée Chalamet", "Florence Pugh", "Margot Robbie", "Jennifer Lawrence", "Viola Davis", "Halle Berry",
          "Angelina Jolie", "Charlize Theron", "Michelle Pfeiffer", "Sigourney Weaver", "Jamie Lee Curtis", "Whoopi Goldberg", "Goldie Hawn",
          "Shah Rukh Khan", "Amitabh Bachchan", "Jackie Chan", "Bruce Lee", "Jet Li", "Toshiro Mifune", "Gérard Depardieu", "Penélope Cruz",
          "Antonio Banderas", "Javier Bardem", "Cillian Murphy", "Pedro Pascal", "Idris Elba", "Michael B. Jordan", "Oscar Isaac", "Adam Driver"]
ACTORS = list(dict.fromkeys(ACTORS))
for a in ACTORS:
    add(f"Name a film starring {a}", "?item wdt:P161 wd:{C}; wdt:P31/wdt:P279* wd:Q11424.", limit=300, minsl=2, min=15, resolve={"C": (a, HUMAN_TYPES)})
AUTHORS = ["Stephen King", "Charles Dickens", "William Shakespeare", "Jane Austen", "Agatha Christie", "J. K. Rowling", "Roald Dahl", "Mark Twain",
           "Ernest Hemingway", "F. Scott Fitzgerald", "George Orwell", "Leo Tolstoy", "Fyodor Dostoevsky", "Virginia Woolf", "Thomas Hardy",
           "Oscar Wilde", "H. G. Wells", "Jules Verne", "Arthur Conan Doyle", "J. R. R. Tolkien", "C. S. Lewis", "Terry Pratchett", "Neil Gaiman",
           "Margaret Atwood", "Toni Morrison", "John Steinbeck", "William Faulkner", "Kurt Vonnegut", "Ray Bradbury", "Isaac Asimov",
           "Philip K. Dick", "Ursula K. Le Guin", "Michael Crichton", "Dan Brown", "John Grisham", "Haruki Murakami", "Gabriel García Márquez",
           "Salman Rushdie", "Kazuo Ishiguro", "Ian McEwan", "Charlotte Brontë", "Edgar Allan Poe", "Herman Melville", "Victor Hugo", "Alexandre Dumas",
           "Émile Zola", "Franz Kafka", "James Joyce", "Samuel Beckett", "Henrik Ibsen", "Anton Chekhov", "Tennessee Williams", "Arthur Miller",
           "Enid Blyton", "Dr. Seuss", "Beatrix Potter", "Judy Blume", "Rick Riordan", "Suzanne Collins", "George R. R. Martin", "Brandon Sanderson",
           "Anne Rice", "Ian Fleming", "John le Carré", "Lee Child", "James Patterson", "Danielle Steel", "Nora Roberts", "P. G. Wodehouse",
           "Evelyn Waugh", "Graham Greene", "Aldous Huxley", "D. H. Lawrence", "E. M. Forster", "Daphne du Maurier", "Ruth Rendell", "Ken Follett",
           "Cormac McCarthy", "Philip Roth", "John Updike", "Jonathan Franzen", "David Walliams", "Jacqueline Wilson", "Anthony Horowitz",
           "Michael Morpurgo", "Rudyard Kipling", "Robert Louis Stevenson", "Lewis Carroll", "Douglas Adams", "Arthur C. Clarke", "Frank Herbert",
           "Robert A. Heinlein", "Iain Banks", "Hilary Mantel", "Sally Rooney", "Colleen Hoover", "Raymond Chandler", "Dashiell Hammett", "Patricia Highsmith"]
AUTHORS = list(dict.fromkeys(AUTHORS))
for a in AUTHORS:
    add(f"Name a work by {a}", "?item wdt:P50 wd:{C}; wdt:P31/wdt:P279* wd:Q7725634.", limit=300, minsl=1, min=12, resolve={"C": (a, HUMAN_TYPES)})
for a in ["Vincent van Gogh", "Pablo Picasso", "Claude Monet", "Leonardo da Vinci", "Rembrandt", "Salvador Dalí", "Michelangelo", "Johannes Vermeer",
          "Frida Kahlo", "Andy Warhol", "J. M. W. Turner", "Edgar Degas", "Pierre-Auguste Renoir", "Paul Cézanne", "Henri Matisse", "Gustav Klimt",
          "Caravaggio", "Raphael", "Sandro Botticelli", "Edvard Munch", "René Magritte", "Francisco Goya", "Diego Velázquez", "Edward Hopper",
          "Jackson Pollock", "Peter Paul Rubens", "Titian", "Albrecht Dürer", "John Constable", "Paul Gauguin"]:
    add(f"Name an artwork by {a}", "?item wdt:P170 wd:{C}; wdt:P31/wdt:P279* wd:Q838948.", limit=400, minsl=2, min=12, resolve={"C": (a, HUMAN_TYPES)})
for a in ["Wolfgang Amadeus Mozart", "Ludwig van Beethoven", "Johann Sebastian Bach", "Pyotr Ilyich Tchaikovsky", "Frédéric Chopin", "Giuseppe Verdi",
          "Richard Wagner", "Giacomo Puccini", "Antonio Vivaldi", "George Frideric Handel", "Claude Debussy", "Igor Stravinsky", "Johannes Brahms",
          "Franz Schubert", "Gustav Mahler", "Sergei Rachmaninoff", "Franz Liszt", "Joseph Haydn", "Felix Mendelssohn", "Robert Schumann",
          "Edward Elgar", "Antonín Dvořák", "Maurice Ravel", "Sergei Prokofiev", "Dmitri Shostakovich", "Gioachino Rossini", "Andrew Lloyd Webber",
          "Stephen Sondheim", "Hans Zimmer", "John Williams", "Ennio Morricone", "Danny Elfman", "Howard Shore", "Leonard Bernstein"]:
    film = a in ("Hans Zimmer", "John Williams", "Ennio Morricone", "Danny Elfman", "Howard Shore")
    nofilm = "" if film else " FILTER NOT EXISTS { ?item wdt:P31/wdt:P279* wd:Q11424 } FILTER NOT EXISTS { ?item wdt:P31/wdt:P279* wd:Q15416 }"
    add(f"Name a piece of music composed by {a}" if not film else f"Name a film scored by {a}", "?item wdt:P86 wd:{C}." + nofilm, limit=500, minsl=2, min=12, resolve={"C": (a, HUMAN_TYPES)})
for a in ["Hayao Miyazaki"]:
    pass

STUDIOS = [("Pixar", "Pixar"), ("Walt Disney Animation Studios", "Walt Disney Animation Studios"), ("Studio Ghibli", "Studio Ghibli"),
           ("DreamWorks Animation", "DreamWorks Animation"), ("A24", "A24"), ("Marvel Studios", "Marvel Studios"), ("Hammer", "Hammer Film Productions"),
           ("Aardman", "Aardman Animations"), ("Illumination", "Illumination"), ("Blue Sky Studios", "Blue Sky Studios"), ("Blumhouse", "Blumhouse Productions"),
           ("Lucasfilm", "Lucasfilm"), ("Ealing Studios", "Ealing Studios"), ("Laika", "Laika"), ("Amblin Entertainment", "Amblin Entertainment"),
           ("Working Title", "Working Title Films"), ("New Line Cinema", "New Line Cinema"), ("Legendary", "Legendary Entertainment")]
for nm, label in STUDIOS:
    add(f"Name a {nm} film", "?item wdt:P272 wd:{C}; wdt:P31/wdt:P279* wd:Q11424.", limit=300, minsl=2, min=10, resolve={"C": (label, ["Q4830453", "Q375336", "Q1762059", "Q10689397", "Q2085381", "Q43229"])})
NETWORKS = ["HBO", "Netflix", "BBC One", "BBC Two", "ITV", "Channel 4", "AMC", "FX", "NBC", "CBS", "American Broadcasting Company", "Fox Broadcasting Company",
            "Adult Swim", "Cartoon Network", "Nickelodeon", "Disney Channel", "Apple TV+", "Amazon Prime Video", "Hulu", "MTV", "Comedy Central",
            "Showtime", "The CW", "PBS", "Disney+", "Sky One", "CBBC", "Fuji TV", "TV Tokyo", "Channel 5"]
NET_NAME = {"American Broadcasting Company": "ABC", "Fox Broadcasting Company": "Fox"}
for n in NETWORKS:
    add(f"Name a TV show that aired on {NET_NAME.get(n, n)}", "?item wdt:P449 wd:{C}; wdt:P31/wdt:P279* wd:Q5398426.", limit=600, minsl=3, resolve={"C": (n, ["Q2001305", "Q15265344", "Q1153191", "Q15590336", "Q1616075", "Q43229", "Q4830453", "Q7725310"])})
PUBLISHERS = ["Nintendo", "Sega", "Ubisoft", "Electronic Arts", "Square Enix", "Capcom", "Bethesda Softworks", "Valve Corporation", "Rockstar Games",
              "Blizzard Entertainment", "Sony Interactive Entertainment", "Konami", "Bandai Namco Entertainment", "Activision", "Atari, Inc.", "Microsoft",
              "Namco", "Taito", "Epic Games", "Bungie", "id Software", "FromSoftware", "Naughty Dog", "BioWare", "Rare", "Insomniac Games", "THQ"]
for pub in PUBLISHERS:
    nm = pub.replace(" Corporation", "").replace(", Inc.", "").replace(" Softworks", "").replace(" Interactive Entertainment", "").replace(" Entertainment", "")
    add(f"Name a video game developed by {nm}", "?item wdt:P178 wd:{C}; wdt:P31 wd:Q7889.", limit=600, minsl=5, resolve={"C": (pub, ["Q4830453", "Q210167", "Q1137109", "Q891723", "Q6881511", "Q783794", "Q43229"])})
SERIES = ["Super Mario", "The Legend of Zelda", "Pokémon", "Final Fantasy", "Call of Duty", "Grand Theft Auto", "Assassin's Creed", "Sonic the Hedgehog",
          "Mega Man", "Resident Evil", "Metal Gear", "Kirby", "Donkey Kong", "Fire Emblem", "Street Fighter", "Mortal Kombat", "Tekken", "Halo",
          "The Elder Scrolls", "Fallout", "Castlevania", "Metroid", "Mario Kart", "Star Wars", "James Bond", "Harry Potter", "Marvel Cinematic Universe",
          "Star Trek", "Tomb Raider", "Crash Bandicoot", "Need for Speed", "FIFA", "Madden NFL", "Dragon Quest", "Kingdom Hearts", "Persona",
          "Silent Hill", "Battlefield", "Far Cry", "The Sims", "SimCity", "Civilization", "Warcraft", "Diablo", "Doom", "Gran Turismo",
          "Animal Crossing", "Splatoon", "Yakuza", "Hitman", "Prince of Persia", "Spyro", "Ratchet & Clank", "Uncharted", "God of War",
          "Pirates of the Caribbean", "Fast & Furious", "Rocky", "Mission: Impossible", "Jurassic Park", "Toy Story", "Shrek", "Alien",
          "Friday the 13th", "Halloween", "A Nightmare on Elm Street", "Saw", "Scream", "Planet of the Apes", "Godzilla", "Indiana Jones",
          "Die Hard", "Terminator", "The Matrix", "X-Men", "Despicable Me", "Ice Age", "Carry On", "Doctor Who"]
for s in SERIES:
    add(f"Name something from the {s[4:] if s.startswith('The ') else s} series", "{ ?item wdt:P179 wd:{C} } UNION { ?item wdt:P8345 wd:{C}; wdt:P31/wdt:P279* ?ty. VALUES ?ty { wd:Q7889 wd:Q11424 wd:Q7725634 wd:Q5398426 } }", limit=500, minsl=1, min=15, resolve={"C": (s, ["Q7058673", "Q196600", "Q24856", "Q1667921", "Q277759", "Q7725310", "Q117467246", "Q5398426"])})
FRANCHISES = ["Harry Potter", "The Simpsons", "Star Wars", "Marvel Universe", "DC Universe", "Middle-earth", "A Song of Ice and Fire", "Star Trek",
              "Doctor Who", "Friends", "The Office", "Family Guy", "SpongeBob SquarePants", "South Park", "Futurama", "Looney Tunes", "Super Mario",
              "The Legend of Zelda", "Sonic the Hedgehog", "Street Fighter", "Mortal Kombat", "Final Fantasy", "X-Men", "Batman", "Spider-Man", "Transformers",
              "Teenage Mutant Ninja Turtles", "Naruto", "One Piece", "Dragon Ball", "Sailor Moon", "Breaking Bad", "The Sopranos", "Stranger Things",
              "Winnie-the-Pooh", "Peanuts", "Sesame Street", "The Muppets", "Overwatch", "League of Legends", "Coronation Street", "EastEnders",
              "Neighbours", "Thomas & Friends", "Pokémon", "Disney Princess", "Chronicles of Narnia", "Discworld", "His Dark Materials", "The Wire",
              "Grey's Anatomy", "Seinfeld", "Twin Peaks", "Buffy the Vampire Slayer", "Battlestar Galactica", "Lost", "Mad Men", "Downton Abbey",
              "Sherlock Holmes", "Dune", "The Hunger Games", "Twilight", "Arthurian legend", "Robin Hood", "Asterix", "The Adventures of Tintin",
              "Archie Comics", "Gundam", "Bleach", "Attack on Titan", "My Hero Academia", "Jujutsu Kaisen", "Fullmetal Alchemist", "Hunter × Hunter",
              "Mobile Suit Gundam", "Fire Emblem", "Kingdom Hearts", "Persona", "Genshin Impact", "Fortnite", "Minecraft", "The Witcher",
              "Mass Effect", "Dragon Age", "BioShock", "Halo", "Gears of War", "The Last of Us", "Red Dead", "Grand Theft Auto", "Metal Gear",
              "Resident Evil", "Tekken", "Super Smash Bros.", "Animal Crossing", "Kirby", "Metroid", "Star Fox", "Banjo-Kazooie", "Crash Bandicoot",
              "Spyro", "Rayman", "Mega Man", "Castlevania", "Bluey", "Peppa Pig", "Paw Patrol", "Adventure Time", "Avatar: The Last Airbender",
              "Gravity Falls", "Rick and Morty", "Bob's Burgers", "King of the Hill", "American Dad!", "Scooby-Doo", "The Flintstones", "The Jetsons",
              "Tom and Jerry", "Mickey Mouse universe", "Lord of the Rings"]
FRANCHISES = list(dict.fromkeys(FRANCHISES))
for f in FRANCHISES:
    add(f"Name a character from {f}", "{ ?item wdt:P1080 wd:{C} } UNION { ?item wdt:P1441 wd:{C} } UNION { ?item wdt:P8345 wd:{C} } ?item wdt:P31/wdt:P279* wd:Q95074.",
        limit=600, minsl=1, min=15, resolve={"C": (f, ["Q559618", "Q196600", "Q7725634", "Q5398426", "Q11424", "Q7058673", "Q1667921", "Q7889", "Q24856", "Q838795", "Q1004", "Q14406742", "Q21198342", "Q63952888", "Q277759", "Q15416", "Q581714"])})
