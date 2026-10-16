# Which prompts make the cut. The aim: questions anyone can have a go at ("Name a song by Queen"),
# with deep answer lists so the rare picks are still there. Niche questions ("Name a Swiss canton",
# "Name a song by Sufjan Stevens") are dropped even if their data is good.
import re

FAMILIES = [
    (r"^Name a song by (.+)$", """ABBA; AC/DC; Adele; Aerosmith; Ariana Grande; Avril Lavigne; Backstreet Boys; Bee Gees; Beyoncé; Billie Eilish;
        Billy Joel; Blondie; Bob Dylan; Bob Marley; Bon Jovi; Britney Spears; Bruce Springsteen; Bruno Mars; BTS; Celine Dion; Cher;
        Christina Aguilera; Coldplay; David Bowie; Destiny's Child; Dolly Parton; Drake; Dua Lipa; Eagles; Ed Sheeran; Elton John;
        Elvis Presley; Eminem; Fleetwood Mac; Foo Fighters; Frank Sinatra; George Michael; Green Day; Guns N' Roses; Imagine Dragons;
        Jay-Z; Johnny Cash; Justin Bieber; Justin Timberlake; Kanye West; Katy Perry; Kendrick Lamar; Kylie Minogue; Lady Gaga;
        Led Zeppelin; Linkin Park; Madonna; Mariah Carey; Maroon 5; Metallica; Michael Jackson; Miley Cyrus; Nirvana; Oasis;
        Olivia Rodrigo; One Direction; Phil Collins; Pink; Pink Floyd; Post Malone; Prince; Queen; Radiohead; Red Hot Chili Peppers;
        Rihanna; Robbie Williams; Sabrina Carpenter; Shakira; Snoop Dogg; Spice Girls; Stevie Wonder; Taylor Swift; The Beach Boys;
        The Beatles; The Killers; The Police; The Rolling Stones; The Weeknd; The Who; Tina Turner; U2; Whitney Houston; Arctic Monkeys;
        Bad Bunny; Billie Holiday; Daft Punk; Kiss; Iron Maiden; Black Sabbath; Usher; 50 Cent; Tupac Shakur; Selena Gomez;
        Simon & Garfunkel; Ozzy Osbourne; Janet Jackson; Lionel Richie; Neil Diamond; Kelly Clarkson; Gwen Stefani; No Doubt; Blink-182;
        Weezer; R.E.M.; Pearl Jam; The Cure; Depeche Mode; Duran Duran; Def Leppard; Journey; Toto; Earth, Wind & Fire; Marvin Gaye;
        Aretha Franklin; Ray Charles; Louis Armstrong; The Doors; Jimi Hendrix; The Kinks; Kate Bush; Sting; Genesis; Tears for Fears;
        Pet Shop Boys; Take That; Westlife; Little Mix; Girls Aloud; Lana Del Rey; Lorde; Sia; Sam Smith; Shawn Mendes; Lil Wayne;
        Nicki Minaj; Travis Scott; Doja Cat; SZA; Avicii; David Guetta; Gorillaz; Blur; Paramore; My Chemical Romance; Fall Out Boy;
        Panic! at the Disco; Twenty One Pilots; System of a Down; Rage Against the Machine; Slipknot; Rammstein; Evanescence; Nickelback;
        The Cranberries; The Strokes; The White Stripes; Kings of Leon; John Lennon; Paul McCartney; Cher; Enrique Iglesias; Ricky Martin;
        Jennifer Lopez; Christina Aguilera; Kenny Rogers; Garth Brooks; Shania Twain; Willie Nelson; Roy Orbison; Chuck Berry; Buddy Holly;
        James Brown; Diana Ross; The Supremes; Barbra Streisand; Ella Fitzgerald; Nina Simone; Bee Gees; Snow Patrol; Coldplay"""),
    (r"^Name an album by (.+)$", """ABBA; AC/DC; Adele; Beyoncé; Bob Dylan; Coldplay; David Bowie; Drake; Elton John; Elvis Presley; Eminem;
        Fleetwood Mac; Green Day; Kanye West; Lady Gaga; Led Zeppelin; Madonna; Metallica; Michael Jackson; Nirvana; Oasis; Pink Floyd;
        Prince; Queen; Radiohead; Rihanna; Taylor Swift; The Beatles; The Rolling Stones; U2; Bruce Springsteen; Guns N' Roses; Mariah Carey"""),
    (r"^Name a film directed by (.+)$", """Alfred Hitchcock; Christopher Nolan; Clint Eastwood; David Fincher; Francis Ford Coppola; George Lucas;
        Guy Ritchie; Hayao Miyazaki; James Cameron; Martin Scorsese; Michael Bay; Peter Jackson; Quentin Tarantino; Ridley Scott;
        Robert Zemeckis; Ron Howard; Stanley Kubrick; Steven Spielberg; Tim Burton; Wes Anderson; Woody Allen; Charlie Chaplin;
        M. Night Shyamalan; Sam Raimi; Denis Villeneuve; Guillermo del Toro; Spike Lee; Danny Boyle; Taika Waititi; Zack Snyder"""),
    (r"^Name a film starring (.+)$", """Adam Sandler; Al Pacino; Angelina Jolie; Anthony Hopkins; Arnold Schwarzenegger; Audrey Hepburn;
        Ben Stiller; Brad Pitt; Bruce Willis; Cameron Diaz; Cate Blanchett; Chris Hemsworth; Christian Bale; Clint Eastwood; Daniel Craig;
        Denzel Washington; Dwayne Johnson; Eddie Murphy; Emma Thompson; George Clooney; Harrison Ford; Hugh Grant; Hugh Jackman;
        Jack Nicholson; Jackie Chan; Jason Statham; Jennifer Aniston; Jennifer Lawrence; Jim Carrey; Johnny Depp; Julia Roberts;
        Keanu Reeves; Kate Winslet; Leonardo DiCaprio; Margot Robbie; Marilyn Monroe; Mark Wahlberg; Matt Damon; Meryl Streep;
        Morgan Freeman; Natalie Portman; Nicole Kidman; Robert De Niro; Robert Downey Jr.; Robin Williams; Ryan Gosling; Ryan Reynolds;
        Samuel L. Jackson; Sandra Bullock; Scarlett Johansson; Sean Connery; Sylvester Stallone; Tom Cruise; Tom Hanks; Tom Hardy;
        Vin Diesel; Will Ferrell; Will Smith; Zendaya; Hugh Jackman; Russell Crowe; Mel Gibson; Michael Caine; Judi Dench; Ian McKellen;
        Bruce Lee; Shah Rukh Khan; Timothée Chalamet; Cillian Murphy; Pedro Pascal; Jamie Lee Curtis; Owen Wilson; Kevin Costner"""),
    (r"^Name a work by (.+)$", """Agatha Christie; Arthur Conan Doyle; C. S. Lewis; Charles Dickens; Dr. Seuss; Edgar Allan Poe; Enid Blyton;
        Ernest Hemingway; F. Scott Fitzgerald; George Orwell; George R. R. Martin; H. G. Wells; J. K. Rowling; J. R. R. Tolkien;
        Jules Verne; Leo Tolstoy; Mark Twain; Oscar Wilde; Roald Dahl; Stephen King; Terry Pratchett; William Shakespeare; John Grisham;
        Michael Crichton; Ian Fleming; Rick Riordan; John Steinbeck; Lewis Carroll; Robert Louis Stevenson; Beatrix Potter; Isaac Asimov;
        Haruki Murakami; Neil Gaiman; Fyodor Dostoevsky; James Patterson; Judy Blume; Anthony Horowitz; Jacqueline Wilson"""),
    (r"^Name an artwork by (.+)$", "Michelangelo; Frida Kahlo; Johannes Vermeer; Gustav Klimt"),
    (r"^Name a piece of music composed by (.+)$", """Wolfgang Amadeus Mozart; Ludwig van Beethoven; Johann Sebastian Bach;
        Pyotr Ilyich Tchaikovsky; Antonio Vivaldi; Andrew Lloyd Webber; Frédéric Chopin; Giuseppe Verdi; Giacomo Puccini"""),
    (r"^Name a film scored by (.+)$", "Hans Zimmer; John Williams; Danny Elfman; Ennio Morricone"),
    (r"^Name someone who has (?:played|driven) for (.+)$", """Ferrari; Arsenal; Chelsea; Liverpool; Manchester City; Manchester United;
        Tottenham Hotspur; Everton; Newcastle United; West Ham United; Aston Villa; Leeds United; Barcelona; Real Madrid; Atlético Madrid;
        Bayern Munich; Borussia Dortmund; Juventus; AC Milan; Inter Milan; Paris Saint-Germain; Celtic; Rangers; LA Galaxy; Inter Miami;
        Los Angeles Lakers; Chicago Bulls; Boston Celtics; Golden State Warriors; Miami Heat; New York Knicks; Dallas Cowboys;
        New England Patriots; Green Bay Packers; Kansas City Chiefs; New York Yankees; Boston Red Sox; Los Angeles Dodgers;
        the England national team; the Brazil national team; the Argentina national team; the France national team;
        the Germany national team; the Italy national team; the Spain national team; the Netherlands national team;
        the Portugal national team; the United States men's national team; the Scotland national team; the Wales national team;
        the Republic of Ireland national team; the England cricket team; the India national cricket team; the Australia national cricket team;
        the New Zealand national rugby union team"""),
    (r"^Name a character from (.+)$", """A Song of Ice and Fire; Harry Potter; The Simpsons; Star Wars; Lord of the Rings; Pokémon;
        SpongeBob SquarePants; Family Guy; Futurama; The Office; Breaking Bad; Stranger Things; Doctor Who; Star Trek; Scooby-Doo;
        Peanuts; Sesame Street; Mickey Mouse universe; X-Men; Naruto; One Piece; Dragon Ball; Mortal Kombat; Super Smash Bros.;
        Final Fantasy; Grey's Anatomy; The Sopranos; Avatar: The Last Airbender; Thomas & Friends; The Adventures of Tintin;
        Asterix; EastEnders; Neighbours; Coronation Street"""),
    (r"^Name something from the (.+) series$", """James Bond; Star Wars; Marvel Cinematic Universe; Super Mario; Legend of Zelda; Pokémon;
        Sonic the Hedgehog; Mario Kart; Jurassic Park; Shrek; Indiana Jones; FIFA; Sims; Final Fantasy; Mortal Kombat; Need for Speed;
        Star Trek; Terminator; Alien; Tomb Raider; Crash Bandicoot; Resident Evil; Doctor Who; Godzilla; Kirby; Tekken; Fallout;
        Elder Scrolls; Battlefield; Far Cry"""),
    (r"^Name a city or town in (.+)$", """the US; the UK; France; Germany; Italy; Spain; Japan; China; India; Brazil; Canada; Australia;
        Mexico; Russia; the Netherlands; Ireland; New Zealand; South Africa; Greece; Turkey; Egypt; Switzerland; Poland; Argentina;
        South Korea; Belgium; Thailand; Austria; Portugal; Sweden; Norway"""),
    (r"^Name an? (.+) dish or food$", """Chinese; French; Indian; Italian; Japanese; Mexican; Thai; Korean; Greek; Spanish; American;
        British; German; Vietnamese; Turkish; Australian"""),
    (r"^Name an? (.+) car model$", """BMW; Ferrari; Ford; Honda; Toyota; Volkswagen; Mercedes-Benz; Porsche; Audi; Nissan; Lamborghini;
        Volvo; Mazda; Hyundai; Fiat; Jaguar; Aston Martin; Subaru; Kia; Renault; Dodge; Mitsubishi; Holden; Chevrolet; Jeep"""),
    (r"^Name a TV show that aired on (.+)$", """HBO; Netflix; BBC One; ABC; NBC; CBS; Fox; Disney Channel; Nickelodeon; Cartoon Network;
        MTV; Channel 4; ITV; Disney+; Amazon Prime Video; Comedy Central"""),
    (r"^Name a video game developed by (.+)$", "Nintendo; Sega; Ubisoft; Electronic Arts; Square Enix; Capcom; Valve; Sony; Activision; Rockstar Games"),
    (r"^Name a game released for the (.+)$", """PlayStation; PlayStation 2; PlayStation 3; PlayStation 4; Wii; Nintendo 64; Game Boy; Nintendo DS;
        Xbox 360; Nintendo Entertainment System; Super Nintendo Entertainment System; GameCube; Game Boy Advance; Sega Genesis; Nintendo Switch"""),
    (r"^Name a river in (.+)$", "the US; the UK; Australia; France; Germany; Canada"),
    (r"^Name a university in (.+)$", "the US; the UK; Australia; Canada"),
    (r"^Name a mountain in (.+)$", ""),
    (r"^Name an island belonging to (.+)$", "the UK; the US; Greece; Italy; Japan; Australia"),
    (r"^Name an? (.+) film$", """Pixar; Walt Disney Animation Studios; Studio Ghibli; DreamWorks Animation; Marvel Studios; Illumination;
        Lucasfilm; Aardman; A24; horror; comedy; science fiction; western; war; romance; superhero; crime; fantasy; thriller; musical;
        action; animated; disaster; sports; spy; heist; zombie; mystery; drama; biographical; historical; adventure; slasher;
        romantic comedy; Christmas; dystopian; documentary; martial arts; coming-of-age"""),
]

DROP = """badminton player; ballet dancer; bassist; biathlete; biologist; bodybuilder; Booker Prize winner; Booker Prize-winning novel;
    Brazilian Série A club; cattle breed; chess opening; chicken breed; Chinese emperor; Chinese province; comic book artist;
    computer scientist; computer virus or piece of malware; conductor; container; county of Ireland; dam; discus thrower;
    EFL Championship club; Eredivisie club; economist; engineer; Fields Medal winner; fencer; fermented food; French department;
    French president; geological period or era; German state; glacier; handball player; historian; Holy Roman Emperor; illustrator;
    Japanese prefecture; Japanese prime minister; jockey; journalist; judoka; lighthouse; literary genre; long jumper; marathon runner;
    middle-distance runner; military officer; mosque; motorcycle racer; mountaineer; Nobel Prize in Economics winner;
    Nobel Prize in Chemistry winner; Nobel Prize in Medicine winner; Paris Métro station; peninsula; photographer; porridge;
    Primeira Liga club; Pulitzer Prize for Fiction winner; Pulitzer-winning novel; racecourse or race circuit; rally driver;
    record producer; region of Italy; rower; Russian federal subject; saxophonist; Scottish council area; screenwriter; snowboarder;
    sociologist; songwriter; Spanish monarch; Spanish province; speed skater; state of Brazil; state of Mexico; strait;
    style of country music; style of jazz; subgenre of electronic music; subgenre of hip hop; subgenre of punk rock; style of pop music;
    Swiss canton; table tennis player; theologian; track cyclist; triathlete; triple jumper; Turing Award winner; type of cell in the body;
    US Secretary of State; violinist; volleyball player; weightlifter; archer; acid; alloy; animator; archipelago; opera singer;
    film producer; rose or relative of the rose; orchid; yoga posture; type of dance music; mollusc; crustacean; MLS team;
    Palme d'Or winning film; logical fallacy; mathematical theorem; polygon; poetic form; type of chocolate;
    elementary or subatomic particle; bay or gulf; video game designer; science fiction writer; cartoonist; type of rock;
    type of cloud; hormone; Hindu deity; cut of beef; grape variety used for wine; beer style; liqueur"""

_drop = {d.strip() for d in DROP.split(";") if d.strip()}
_fam = [(re.compile(rx), {x.strip() for x in allow.split(";") if x.strip()}) for rx, allow in FAMILIES]

def keep(prompt):
    for rx, allow in _fam:
        m = rx.match(prompt)
        if m: return m.group(1) in allow
    return re.sub(r"^Name (a|an) ", "", prompt) not in _drop
