// Prompt bank. Each round picks 7 of these at random.
//
// To add a prompt, append an object with a `prompt` and an `answers` map of tiers.
// Each answer string can list aliases separated by "|" — the first one is shown to the player.
// Matching already ignores case, accents, punctuation, spacing, "the", and simple plurals,
// and forgives small typos, so you don't need to list those variants.
//
// Tiers (points): plankton 10 · tooClever 15 · schooler 30 · rare 60 · deepCut 85 · gem 100
// `gem` should hold exactly one answer: the hidden "one in a krillion".

window.KRILLION_PROMPTS = [
  {
    prompt: "Name a noodle dish",
    answers: {
      plankton: ["Spaghetti", "Ramen", "Pad thai", "Lasagna|lasagne", "Mac and cheese|macaroni and cheese|mac n cheese|macaroni cheese", "Chow mein", "Lo mein", "Pho", "Spaghetti bolognese|spag bol|bolognese"],
      tooClever: ["Udon", "Soba", "Laksa", "Pad see ew", "Japchae|chapchae"],
      schooler: ["Fettuccine alfredo|alfredo", "Carbonara|spaghetti carbonara", "Singapore noodles|singapore mei fun", "Dan dan noodles|dan dan mian", "Yakisoba", "Chicken noodle soup", "Drunken noodles|pad kee mao", "Beef noodle soup", "Pancit", "Mee goreng|mi goreng", "Char kway teow|char kuey teow", "Bun cha", "Chow fun|beef chow fun|ho fun", "Tsukemen", "Cacio e pepe", "Spaghetti and meatballs", "Glass noodles|cellophane noodles", "Rice noodles", "Pasta salad", "Ravioli", "Tagliatelle"],
      rare: ["Khao soi", "Biang biang noodles|biangbiang", "Naengmyeon|naengmyun", "Jajangmyeon|jjajangmyeon", "Kalguksu", "Mohinga", "Hokkien mee", "Wonton noodles|wonton mee", "Lagman|laghman", "Champon|chanpon", "Hiyashi chuka", "Bun bo hue", "Cao lau", "Mee siam", "Mee rebus", "Khanom chin", "Kuy teav|kuyteav", "Ants climbing a tree", "Zhajiangmian|zha jiang mian", "Kitsune udon", "Tantanmen", "Lanzhou beef noodles|lanzhou lamian|lamian", "Spaetzle|spätzle", "Kugel|lokshen kugel|noodle kugel", "Haluski", "Pastitsio", "Yaki udon", "Mazemen", "Bun rieu", "Mi quang"],
      deepCut: ["Mee pok", "Lor mee", "Bakmi", "Mie aceh", "Ash reshteh|reshteh", "Fideua|fideuà", "Sopa de fideo|fideo", "Kasespatzle|käsespätzle", "Cold sesame noodles|sesame noodles", "Crossing the bridge noodles|guoqiao mixian", "Hot dry noodles|reganmian", "Ohn no khao swe", "Hu tieu", "Kesme", "Makaronia", "Pancit canton", "Pancit malabon"],
      gem: ["Saimin"],
    },
  },
  {
    prompt: "Name a fruit",
    answers: {
      plankton: ["Apple", "Banana", "Orange", "Strawberry", "Grape", "Watermelon", "Pineapple", "Mango", "Pear", "Peach", "Cherry", "Lemon", "Blueberry"],
      tooClever: ["Dragon fruit|pitaya", "Durian", "Lychee|litchi", "Kumquat", "Star fruit|carambola", "Passion fruit"],
      schooler: ["Kiwi|kiwifruit", "Plum", "Raspberry", "Blackberry", "Lime", "Grapefruit", "Apricot", "Coconut", "Pomegranate", "Papaya", "Cantaloupe", "Honeydew", "Nectarine", "Fig", "Avocado", "Tomato", "Cranberry", "Tangerine", "Clementine", "Melon", "Date", "Guava", "Persimmon", "Mandarin", "Satsuma"],
      rare: ["Jackfruit", "Rambutan", "Mangosteen", "Quince", "Gooseberry", "Elderberry", "Loquat", "Feijoa", "Tamarind", "Longan", "Kiwano|horned melon", "Cherimoya|custard apple", "Ugli fruit", "Salak|snake fruit", "Mulberry", "Blackcurrant|currant|redcurrant", "Physalis|cape gooseberry|goldenberry", "Yuzu", "Soursop|guanabana", "Boysenberry", "Cloudberry", "Pomelo", "Olive", "Plantain", "Sapodilla", "Acai|açaí", "Damson", "Greengage"],
      deepCut: ["Medlar", "Jabuticaba", "Ackee", "Cupuacu|cupuaçu", "Miracle fruit|miracle berry", "Buddha's hand", "Finger lime", "Marula", "Lucuma", "Santol", "Langsat", "Bilberry", "Lingonberry", "Salmonberry", "Huckleberry", "Jujube", "Aronia|chokeberry", "Sea buckthorn", "Bael", "Wood apple", "Black sapote", "Mamey|mamey sapote", "Noni", "Rose apple|wax apple", "Salal", "Cornelian cherry"],
      gem: ["Pawpaw"],
    },
  },
  {
    prompt: "Name a dog breed",
    answers: {
      plankton: ["Labrador|labrador retriever|lab", "Golden retriever", "German shepherd", "Poodle", "Chihuahua", "Bulldog|english bulldog", "Beagle", "Pug", "Husky|siberian husky", "Dachshund|sausage dog|wiener dog"],
      tooClever: ["Shiba inu|shiba", "Corgi|welsh corgi|pembroke welsh corgi", "Basenji", "Xoloitzcuintli|xolo", "Shar pei"],
      schooler: ["Rottweiler", "Boxer", "Great dane", "Border collie", "Yorkshire terrier|yorkie", "Doberman|dobermann|doberman pinscher", "Shih tzu", "Cocker spaniel", "Pomeranian", "French bulldog|frenchie", "Dalmatian", "Greyhound", "Maltese", "Saint bernard|st bernard", "Bichon frise|bichon", "Jack russell|jack russell terrier", "Labradoodle", "Cockapoo", "Bernese mountain dog", "Collie|rough collie", "Schnauzer", "Akita", "Chow chow", "Whippet", "Pit bull|pitbull|american pit bull terrier", "Australian shepherd|aussie", "Mastiff", "Bloodhound", "Newfoundland", "Samoyed", "Malamute|alaskan malamute", "Staffordshire bull terrier|staffy|staffie", "Cavalier king charles spaniel|cavalier", "Boston terrier", "Bull terrier", "Weimaraner", "Vizsla", "Springer spaniel", "Basset hound", "Westie|west highland terrier|west highland white terrier", "Scottish terrier|scottie", "Goldendoodle"],
      rare: ["Komondor", "Puli", "Borzoi", "Saluki", "Afghan hound", "Rhodesian ridgeback", "Pharaoh hound", "Leonberger", "Tibetan mastiff", "Keeshond", "Schipperke", "Bedlington terrier", "Affenpinscher", "Lhasa apso", "Briard", "Bouvier des flandres", "Irish wolfhound", "Scottish deerhound|deerhound", "Cane corso", "Dogue de bordeaux", "Anatolian shepherd", "Kuvasz", "Chinese crested", "Norwegian elkhound", "Finnish spitz", "Havanese", "Coton de tulear", "Dandie dinmont terrier", "Portuguese water dog", "Papillon", "Great pyrenees", "Brittany|brittany spaniel", "Airedale|airedale terrier"],
      deepCut: ["Lagotto romagnolo", "Catalburun", "Mudi", "Azawakh", "Bergamasco", "Otterhound", "Sloughi", "Stabyhoun", "Kooikerhondje|nederlandse kooikerhondje", "Cesky terrier", "Glen of imaal terrier", "Thai ridgeback", "Kai ken", "Jindo|korean jindo", "Peruvian inca orchid", "Pumi", "Karelian bear dog", "Swedish vallhund", "Mexican hairless", "Bracco italiano", "Spinone|italian spinone", "Kerry blue terrier", "Hovawart", "Telomian"],
      gem: ["Norwegian lundehund|lundehund"],
    },
  },
  {
    prompt: "Name a country in Africa",
    answers: {
      plankton: ["Egypt", "Nigeria", "South Africa", "Kenya", "Morocco", "Ethiopia"],
      tooClever: ["Madagascar", "Burkina Faso", "Djibouti", "Eswatini|swaziland", "Cape Verde|cabo verde"],
      schooler: ["Ghana", "Tanzania", "Uganda", "Algeria", "Libya", "Tunisia", "Sudan", "Somalia", "Zimbabwe", "Zambia", "Senegal", "Republic of the Congo|congo|congo brazzaville", "DR Congo|democratic republic of the congo|drc|congo kinshasa|zaire", "Cameroon", "Ivory Coast|cote d'ivoire", "Angola", "Mozambique", "Namibia", "Botswana", "Rwanda", "Mali", "Chad", "Niger"],
      rare: ["Malawi", "Burundi", "Eritrea", "South Sudan", "Benin", "Togo", "Sierra Leone", "Liberia", "Guinea", "Gabon", "Mauritania", "Lesotho", "The Gambia|gambia", "Mauritius", "Seychelles", "Central African Republic|car", "Equatorial Guinea"],
      deepCut: ["Guinea-Bissau", "Comoros"],
      gem: ["São Tomé and Príncipe|sao tome|sao tome and principe"],
    },
  },
  {
    prompt: "Name a musical instrument",
    answers: {
      plankton: ["Guitar", "Piano", "Drums|drum|drum kit", "Violin", "Flute", "Trumpet"],
      tooClever: ["Theremin", "Didgeridoo", "Ukulele", "Kazoo", "Triangle", "Sitar"],
      schooler: ["Saxophone|sax", "Cello", "Clarinet", "Harp", "Trombone", "Bass guitar|bass|electric bass", "Tuba", "Oboe", "Xylophone", "Harmonica", "Accordion", "Banjo", "Keyboard", "Tambourine", "Organ", "Recorder", "Viola", "French horn|horn", "Double bass|upright bass|contrabass", "Bagpipes", "Cymbals", "Synthesizer|synth", "Mandolin", "Bassoon", "Piccolo", "Glockenspiel", "Bongos", "Maracas", "Timpani|kettle drum", "Cowbell", "Marimba", "Castanets", "Snare drum|snare", "Fiddle", "Electric guitar", "Acoustic guitar"],
      rare: ["Harpsichord", "Lute", "Dulcimer", "Zither", "Bouzouki", "Balalaika", "Steel drum|steelpan|steel pan", "Kalimba|thumb piano|mbira", "Tabla", "Djembe", "Ocarina", "Celesta", "Euphonium", "Sousaphone", "Oud", "Koto", "Shamisen", "Erhu", "Hurdy-gurdy", "Cajon|cajón", "Vibraphone", "Pan flute|panpipes", "Washboard", "Melodica", "Harmonium", "Cornet", "Flugelhorn", "Contrabassoon", "Lyre", "Gong", "Tin whistle|penny whistle", "Bodhran|bodhrán", "Clavichord", "Spinet", "Conga|congas", "Tubular bells|chimes"],
      deepCut: ["Nyckelharpa", "Handpan|hang|hang drum", "Sarangi", "Guzheng", "Pipa", "Kora", "Shakuhachi", "Crwth", "Sackbut", "Serpent", "Ophicleide", "Theorbo", "Cimbalom", "Hammered dulcimer", "Gamelan", "Santoor|santur", "Rebab", "Duduk", "Kantele", "Bandoneon|bandoneón", "Ondes martenot", "Waterphone", "Tromba marina", "Cuica|cuíca", "Berimbau", "Launeddas", "Sheng", "Dizi", "Crumhorn", "Rackett", "Mellotron", "Stylophone"],
      gem: ["Glass harmonica|armonica"],
    },
  },
  {
    prompt: "Name a cheese",
    answers: {
      plankton: ["Cheddar", "Mozzarella", "Parmesan|parmigiano reggiano|parmigiano", "Brie", "Swiss", "Feta", "Gouda"],
      tooClever: ["Halloumi", "Gruyère|gruyere", "Manchego", "Stilton", "Roquefort", "Burrata"],
      schooler: ["Camembert", "Blue cheese|bleu cheese", "Ricotta", "Provolone", "Edam", "Monterey Jack|jack", "Pepper jack", "Colby", "American cheese|american", "Cream cheese", "Cottage cheese", "Emmental|emmentaler|emmenthal", "Gorgonzola", "Mascarpone", "Goat cheese|chevre|chèvre", "Havarti", "Paneer", "Pecorino|pecorino romano", "Wensleydale", "Red Leicester", "String cheese", "Muenster|munster", "Queso fresco", "Colby jack", "Double Gloucester"],
      rare: ["Taleggio", "Comté|comte", "Raclette", "Reblochon", "Fontina", "Asiago", "Jarlsberg", "Lancashire", "Caerphilly", "Cheshire", "Port Salut", "Limburger", "Brunost|gjetost|brown cheese", "Oaxaca|queso oaxaca", "Cotija", "Manouri", "Kefalotyri", "Scamorza", "Stracciatella", "Boursin", "Mimolette", "Époisses|epoisses", "Leerdammer", "Danish blue", "Cambozola", "Tilsit", "Quark", "Labneh", "Provola", "Grana padano", "Queso blanco", "Neufchâtel|neufchatel"],
      deepCut: ["Vacherin|vacherin mont d'or", "Tête de Moine|tete de moine", "Stinking Bishop", "Shropshire blue", "Cornish Yarg|yarg", "Beaufort", "Morbier", "Langres", "Saint-Nectaire", "Valençay|valencay", "Idiazabal|idiazábal", "Mahón|mahon", "Torta del Casar", "Caciocavallo", "Bryndza", "Oscypek", "Sbrinz", "Appenzeller", "Pule", "Cheese curds|squeaky cheese", "Leipäjuusto|juustoleipa|bread cheese", "Chhena", "Cabrales", "Ossau-Iraty", "Brillat-Savarin", "Livarot", "Munster-géromé"],
      gem: ["Casu marzu"],
    },
  },
  {
    prompt: "Name a bird",
    answers: {
      plankton: ["Eagle", "Robin", "Pigeon", "Sparrow", "Crow", "Owl", "Parrot", "Penguin", "Flamingo", "Chicken", "Duck", "Swan", "Seagull|gull", "Hawk", "Blue jay"],
      tooClever: ["Dodo", "Kiwi", "Emu", "Ostrich", "Toucan", "Albatross", "Puffin", "Peacock|peafowl|peahen"],
      schooler: ["Cardinal", "Hummingbird", "Pelican", "Woodpecker", "Falcon|peregrine falcon", "Vulture", "Heron", "Stork", "Crane", "Goose", "Turkey", "Raven", "Magpie", "Blackbird", "Starling", "Finch", "Canary", "Cockatoo", "Macaw", "Budgie|parakeet|budgerigar", "Wren", "Kingfisher", "Swallow", "Dove", "Cuckoo", "Condor", "Osprey", "Quail", "Pheasant", "Kookaburra", "Lovebird", "Mockingbird", "Oriole", "Bluebird", "Goldfinch", "Thrush", "Nightingale", "Lark|skylark", "Partridge", "Grouse", "Cormorant", "Ibis", "Roadrunner", "Blue tit|tit|great tit", "Chickadee", "Kestrel", "Buzzard", "Bald eagle", "Jay", "Mallard"],
      rare: ["Hoopoe", "Cassowary", "Rhea", "Shoebill", "Kakapo|kākāpō", "Secretary bird", "Lyrebird", "Bird of paradise", "Quetzal", "Hornbill", "Frigatebird", "Booby|blue-footed booby", "Spoonbill|roseate spoonbill", "Nuthatch", "Treecreeper", "Warbler", "Wagtail", "Bittern", "Curlew", "Plover", "Sandpiper", "Avocet", "Oystercatcher", "Kea", "Tui", "Bowerbird", "Nightjar", "Whip-poor-will", "Grebe", "Loon", "Harrier", "Merlin", "Goshawk", "Kite|red kite", "Egret", "Ptarmigan", "Capercaillie", "Corncrake", "Dipper", "Jacana", "Tanager", "Waxwing", "Cowbird", "Grackle", "Meadowlark", "Moorhen", "Coot", "Kittiwake", "Gannet", "Petrel", "Shearwater", "Tern", "Auk|razorbill", "Skua"],
      deepCut: ["Potoo", "Oilbird", "Kagu", "Takahe|takahē", "Sunbittern", "Motmot", "Umbrellabird", "Cock-of-the-rock", "Frogmouth|tawny frogmouth", "Lammergeier|bearded vulture", "Turaco", "Oxpecker", "Honeyguide", "Wallcreeper", "Bee-eater", "Roller", "Mousebird", "Shrike", "Firecrest", "Goldcrest", "Dunnock", "Smew", "Hammerkop", "Sungrebe", "Limpkin", "Anhinga", "Tropicbird", "Pitta", "Bellbird", "Wryneck", "Chough"],
      gem: ["Hoatzin|stinkbird"],
    },
  },
  {
    prompt: "Name a vegetable",
    answers: {
      plankton: ["Carrot", "Broccoli", "Potato", "Lettuce", "Tomato", "Onion", "Cucumber", "Corn|sweetcorn", "Peas", "Spinach", "Celery", "Cabbage"],
      tooClever: ["Kohlrabi", "Romanesco", "Okra", "Bok choy|pak choi|bok choi", "Artichoke", "Kale"],
      schooler: ["Cauliflower", "Bell pepper|pepper|capsicum", "Zucchini|courgette", "Eggplant|aubergine", "Asparagus", "Green beans|string beans", "Sweet potato", "Mushroom", "Garlic", "Beetroot|beet", "Radish", "Brussels sprouts|brussel sprouts|sprouts", "Leek", "Butternut squash|squash", "Pumpkin", "Turnip", "Parsnip", "Yam", "Chard|swiss chard", "Arugula|rocket", "Watercress", "Shallot", "Spring onion|scallion|green onion", "Fennel", "Endive", "Jalapeño|jalapeno", "Chili|chilli|chile", "Cassava|yuca", "Edamame", "Bean sprouts", "Snow peas|mangetout|sugar snap peas|snap peas", "Broad beans|fava beans", "Runner beans", "Ginger", "Iceberg lettuce", "Red onion"],
      rare: ["Rutabaga|swede", "Jicama", "Celeriac", "Salsify", "Daikon|mooli", "Taro", "Lotus root", "Burdock|gobo", "Sunchoke|jerusalem artichoke", "Bitter melon|bitter gourd|karela", "Chayote|choko", "Tomatillo", "Radicchio", "Gai lan|chinese broccoli|kai lan", "Napa cabbage|chinese cabbage", "Mizuna", "Broccoli rabe|rapini", "Purslane", "Sorrel", "Fiddleheads|fiddlehead fern", "Samphire|sea beans", "Cardoon", "Nopales|nopal|cactus paddle", "Water chestnut", "Bamboo shoots", "Collard greens|collards", "Mustard greens", "Dandelion greens", "Horseradish", "Wasabi", "Tenderstem|broccolini", "Kabocha", "Delicata squash", "Spaghetti squash", "Turnip greens"],
      deepCut: ["Oca", "Ulluco", "Scorzonera|black salsify", "Crosne|chinese artichoke", "Celtuce|stem lettuce", "Malabar spinach", "Chaya", "Yacon|yacón", "Mashua", "Sea kale", "Good King Henry", "Alexanders", "Hamburg parsley|parsley root", "Tindora|ivy gourd", "Drumstick|moringa", "Agretti", "Puntarelle", "Ensete", "Kohlrabi greens", "Arracacha", "Chicory root", "Winged bean"],
      gem: ["Skirret"],
    },
  },
  {
    prompt: "Name a board game",
    answers: {
      plankton: ["Monopoly", "Chess", "Scrabble", "Checkers|draughts", "Clue|cluedo", "Risk", "The Game of Life|life|game of life", "Sorry!|sorry", "Candy Land|candyland", "Connect Four|connect 4"],
      tooClever: ["Catan|settlers of catan", "Go|weiqi|baduk", "Backgammon", "Ticket to Ride", "Mahjong|mah jong|mahjongg"],
      schooler: ["Battleship", "Trivial Pursuit", "Operation", "Guess Who", "Mouse Trap|mousetrap", "Snakes and Ladders|chutes and ladders", "Pictionary", "Ludo", "Parcheesi|pachisi", "Trouble|frustration", "Stratego", "Othello|reversi", "Mancala", "Carcassonne", "Pandemic", "Hungry Hungry Hippos", "Payday|pay day", "Upwords", "Blokus", "Rummikub", "Chinese Checkers", "Cranium", "Diplomacy", "Mastermind", "Labyrinth", "Axis and Allies|axis & allies", "Dominoes", "Hotels", "Escape from Colditz"],
      rare: ["Wingspan", "Azul", "Splendor", "Terraforming Mars", "Gloomhaven", "Twilight Imperium", "Power Grid", "Agricola", "Puerto Rico", "7 Wonders|seven wonders", "Codenames", "Dixit", "Small World", "King of Tokyo", "Scythe", "Everdell", "Betrayal at House on the Hill|betrayal", "Arkham Horror", "Eldritch Horror", "Dead of Winter", "Cosmic Encounter", "Root", "Spirit Island", "Brass|brass birmingham|brass lancashire", "Castles of Burgundy", "Le Havre", "Caylus", "Tigris and Euphrates|tigris & euphrates", "Acquire", "Shogi", "Xiangqi|chinese chess", "Nine Men's Morris|nine mens morris", "Pente", "Hive", "Onitama", "Quoridor", "Abalone", "Santorini", "Kingdomino", "Patchwork", "Camel Up", "Takenoko", "Mysterium", "Sagrada", "Photosynthesis", "El Grande", "Through the Ages", "Mage Knight", "War of the Ring", "HeroQuest|hero quest", "Talisman", "Survive: Escape from Atlantis|survive|escape from atlantis", "Fireball Island", "Dark Tower", "Twister"],
      deepCut: ["Hnefatafl|tafl|tablut", "Senet", "Royal Game of Ur|game of ur|ur", "Mehen", "Twixt", "Hex", "Tak", "GIPF", "YINSH", "ZÈRTZ|zertz", "Arimaa", "Fanorona", "Bao", "Oware|awale|awari", "Alquerque", "Surakarta", "Konane", "Mu torere", "Game of the Goose|game of goose", "Kriegspiel", "Chaturanga", "Liubo", "Patolli", "Puluc", "Halma", "Fox and Geese", "Kalah"],
      gem: ["Crokinole"],
    },
  },
  {
    prompt: "Name a sea creature",
    answers: {
      plankton: ["Shark", "Whale", "Dolphin", "Octopus", "Jellyfish", "Crab", "Starfish|sea star", "Fish", "Lobster", "Seal", "Sea turtle|turtle", "Shrimp|prawn"],
      tooClever: ["Anglerfish", "Narwhal", "Blobfish", "Mantis shrimp", "Krill", "Giant squid"],
      schooler: ["Seahorse", "Squid", "Clownfish", "Stingray|ray", "Manta ray|manta", "Sea urchin|urchin", "Eel", "Orca|killer whale", "Blue whale", "Humpback whale|humpback", "Walrus", "Sea lion", "Sea otter|otter", "Tuna", "Salmon", "Cod", "Coral", "Oyster", "Clam", "Mussel", "Barnacle", "Sea cucumber", "Pufferfish|blowfish", "Swordfish", "Hammerhead shark|hammerhead", "Great white shark|great white", "Manatee", "Plankton", "Sea anemone|anemone", "Barracuda", "Marlin", "Mackerel", "Sardine", "Anchovy", "Herring", "Halibut", "Flounder", "Beluga", "Sperm whale", "Lionfish", "Moray eel|moray", "Scallop", "Hermit crab", "Cuttlefish", "Nautilus", "Tiger shark", "Bull shark"],
      rare: ["Dugong", "Vaquita", "Coelacanth", "Oarfish", "Ocean sunfish|sunfish|mola|mola mola", "Sea pig", "Sea butterfly", "Siphonophore", "Portuguese man o' war|man o war|portuguese man of war", "Box jellyfish", "Nudibranch|sea slug", "Sea spider", "Giant isopod|isopod", "Frilled shark", "Goblin shark", "Megamouth shark|megamouth", "Whale shark", "Basking shark", "Wobbegong", "Sawfish", "Sea dragon|leafy sea dragon|weedy sea dragon", "Pipefish", "Gulper eel|pelican eel", "Viperfish", "Fangtooth", "Hatchetfish", "Lanternfish", "Dumbo octopus", "Vampire squid", "Colossal squid", "Mimic octopus", "Blue-ringed octopus", "Cone snail", "Lamprey|sea lamprey", "Hagfish", "Triggerfish", "Parrotfish", "Grouper", "Wrasse", "Remora", "Flying fish", "Needlefish", "Pilot whale", "Bowhead whale", "Minke whale", "Porpoise", "Elephant seal", "Leopard seal", "Horseshoe crab", "Japanese spider crab|spider crab", "Sea squirt|tunicate", "Sea sponge|sponge", "Crinoid|sea lily", "Brittle star", "Sand dollar", "Chiton", "Limpet", "Abalone", "Conch", "Cowrie", "Sea angel", "Gray whale|grey whale", "Right whale", "Fin whale", "Sea snake", "Mudskipper"],
      deepCut: ["Barreleye", "Yeti crab", "Pompeii worm", "Bone-eating worm|osedax|zombie worm", "Christmas tree worm", "Bobbit worm", "Giant tube worm|tube worm", "Stargazer", "Wolf eel", "Lumpsucker|lumpfish", "Sea toad", "Tripod fish", "Cookiecutter shark", "Greenland shark", "Sixgill shark", "Chimaera|ghost shark|ratfish", "Black swallower", "Stoplight loosejaw", "Sea pen", "Salp", "Comb jelly|ctenophore", "Pyrosome", "Blue dragon|glaucus|glaucus atlanticus", "Sea mouse", "Feather star", "Firefly squid", "Telescope octopus", "Cock-eyed squid", "Spookfish", "Dragonfish", "Hairy frogfish|frogfish", "Peacock mantis shrimp", "Pistol shrimp"],
      gem: ["Sarcastic fringehead|fringehead"],
    },
  },
];
