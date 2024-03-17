import json
import spacy
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Load the narrative from the JSON file
with open("static/public/ensonya_story_sessions.json", "r", encoding='utf-8') as file:
    campaign_data = json.load(file)

# Load an English model in spaCy
nlp = spacy.load("en_core_web_lg")
# Create a directed graph
G = nx.DiGraph()
character_connections = defaultdict(lambda: defaultdict(int))
# Initialize the SentimentIntensityAnalyzer
sentiment_analyzer = SentimentIntensityAnalyzer()
# establish atlas
character_atlas = {}

# Define a mapping of nicknames to full names
nickname_mapping = {
    "Zelutig 'The Uncut' Stonecock": ['Zelutig "The Uncut" Stonecock', "Zel", "Zelutig", "The Uncut", "barbarian"],
    'Zyntripetal Force': ['Zyntripetal Force', "Zyn", "Zyntripetal", "Dragonborn Ascendant", "dragonborn", "monk"],
    'Ipsaleth Gelordio': ['Ipsaleth Gelordio', "Ip", "Ipsaleth", "death cleric", "cleric of luck", "the coin", "necromancy", "luck"],
    'Bruce McSnout': ['Thrymheim', "Bruce", "Roo", "McSnout", "dragon"],
    'Granny Martha': ['Granny Marth', "The Hag", "Martha"],
    'Sonya': ['Sonya', "Ice Goddess", "Goddess", "Ice Temple", "Ice Trials"],
    'Soranu': ['Soranu', "Soranu The Wise", "dragon"],
    'Durkin': ['Durkin Firestride', "Durkin", "bard"],
    'Bartholomew': ['Bartholomew Beakfolk', "Bart", "Bartholomew", "Beakfolk"],
    'Brok the Poet': ['Brok the Poet', "Brok", "goblin", "bard"],
    'V-Man':['Vecna', 'V-Man', "Mr V", "Mr. V", "thay"],
    "Szass Tam":["Szass", "Szass Tam", "Archlich", "Thay"],
    "Astralos": ['Astralos', "Ancient Dragon", "dragon"],
    "Tymora": ["Tymora", "Lady of Luck", "God of Luck", "Goddess of Luck", "luck"],
    "Eldrithan Zephyrus":["Eldie","Eldrithan","Eldrithan Zephyrus"],
    "Scjauron":["Scjauron", "Who?", "dragonborn"],
    "Seraphina Eldertide": ["Seraphina", "Serpahine", "Eldertide", "Seraphina Eldertide", "Archmage", "wizard's tower", "Elderspire", "arcane quarters"],
    "Supreme Necroflayers":["Supreme Necroflayer", "necroflayer", "thay", "supreme"],
    "Empowered Necroflayers":["Empowered Necroflayers", "necroflayer", "thay"],
    "Lesser Necroflayers":["Lesser Necroflayers", "necroflayer", "thay"],
    "Zethul": ["Zethul", "dragonborn", "draconic"],
    "Mycellia": ["Mycellia", "Myconid"],
    "Gran Daño": ["Gran Dano", "Gran Daño", "Eldric", "Frostforge", "frost wizard", "wizard"],
    "Malachar": ["Malachar", "devil", "overseer of punishment"],
    "Kaelen Silverveil": ["Kaelen", "Paladin of Sonya", "Silverveil", "Kaelen Silverveil"],
    "Sylvara": ["Sylvara", "Stormscale", "dragon"],
    "Dorgrim Bonecleaver": ["Dorgrim", "Bonecleaver"],
    "Wøli":["Wøli", "Woli", "divine purpose", "frostheart"],
    "Zel's Goblins": ["Battle Hardened Goblins", "Zelutig's Goblins", "the goblins", "goblins", "goblin"],
    "Nadaal": ["Nadal", "Nadaal", "rogue"],
    "Neopheles": ['Neopheles', "Nocturnam"],
    "Velindra Zethar":["Velindra",'Zethar',"Vel", "Shar"],
    "Kral'Gathar":["Kral","Gathar", "githyanki", "general"],
    "Zephryn": ["Zephryn", "the girl", "divine purpose", "sonya's daughter"],
    "Thrain Ironfist": ["Thrain", "Ironfist"],
    "Elystria": ["Elystria", "The nature spirit", "protector of the reach"],
    "Thistle": ["Thistle", "Thistle the Wise"],
    "Draco Iflem": ["Draco", "Iflem", "draco Iflem"],
    "Grakka Stonecock": ["Grakka", "Stonecock"],
    "Giant Black Serpent": ["Giant Serpent", "Black Serpent"],
    "Durkin Firestride": ["Durkin","Firestride","Tiefling Bard"],
    "Sel'Thar": ["Sel'thar", "Shadowstride", "Gith Rogue", "Ghaik Rogue"],
    "Gralk": ["Gralk", "Goblin Leader"],
    "Thayan Soldiers": ["Thayan Soldier", "Thay Soldiers", "Thayans"],
    "Thayan Acolytes": ["Thayan Acolytes", "Thay Acolyte"],
    "James Marco Marco": ["James", "Marco Marco", "Marco", "Fashion Designer", "Thayan Leiutenant", "clothes", "craftsman"],
    "Myconids": ["Myconid", "Myconids"],
    "Mindless Goliaths": ["Mindless Goliaths", "rogue goliaths", "rogue goliath", "draco iflem"],
    "Tadpoled Serpents": ["Tadpoled Serpents", "Serpents"],
    "Bug Bears": ["Bugbear", "bugbears", "bug bear"],
    "Worgs": ["Worg", "worgs"],
    "Lathander": ["God of Light", "Lathander"],
    "Tyr": ["Tyr", "God of Justice", "balance in imbalance"],
    "Tiamat": ["Dragon God", "Tiamat", "balance in imbalance"],
    "Shar": ["Lady of Loss", "Lady of Darkness", "Shar", "of loss"],
    "Prince Torrek IX": ["The Prince", "Prince", "prince torrek"],
    "Astrid":["Paladin of Shar", "Shar's Chosen", "Astrid"]
}

# Assuming your nickname_mapping dictionary is defined here

# Flatten the nickname to canonical name mapping for direct lookup
nickname_to_canonical = {}
for canonical, nicknames in nickname_mapping.items():
    for nickname in nicknames:
        nickname_to_canonical[nickname.lower()] = canonical

# Function to identify and extract actions from text data related to characters
def extract_actions(doc):
    character_actions = defaultdict(list)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            char_name = nickname_to_canonical.get(ent.text.lower())
            if char_name:
                for token in ent.root.head.children:
                    if token.pos_ == "VERB":
                        character_actions[char_name].append(token.lemma_)
    return character_actions

def update_character_connections_with_sentiment(doc, chapter_character_actions):
    # Assume chapter_character_actions is a dict mapping character names to lists of actions
    
    for sent in doc.sents:
        characters_in_sent = set()
        for ent in sent.ents:
            canonical_name = nickname_to_canonical.get(ent.text.lower())
            if canonical_name:
                characters_in_sent.add(canonical_name)
        
        sentiment_score = sentiment_analyzer.polarity_scores(sent.text)['compound']

        for char1 in characters_in_sent:
            for char2 in characters_in_sent:
                if char1 != char2:
                    action_key = tuple(sorted([char1, char2]))  # Make sure to create a consistent key
                    
                    character_connections[action_key]['weight'] += 1
                    character_connections[action_key]['cumulative_sentiment'] += sentiment_score
                    
                    # Here's the new part: we accumulate actions for both characters
                    actions_1 = chapter_character_actions.get(char1, [])
                    actions_2 = chapter_character_actions.get(char2, [])
                    combined_actions = list(set(actions_1 + actions_2))  # Remove duplicates
                    character_connections[action_key]['actions'].extend(combined_actions)
                    # Remove duplicates after combination
                    character_connections[action_key]['actions'] = list(set(character_connections[action_key]['actions']))

character_connections = defaultdict(lambda: {'weight': 0, 'cumulative_sentiment': 0.0, 'actions': []})
campaign_character_actions = defaultdict(list)

# Load the narrative from the JSON file
with open("static/public/ensonya_story_sessions.json", "r", encoding='utf-8') as file:
    campaign_data = json.load(file)

# Process each chapter in the campaign data
for session in campaign_data:
    for chapter in session.get('chapters', []):
        doc = nlp(chapter.get('content', ''))
        chapter_character_actions = extract_actions(doc)
        update_character_connections_with_sentiment(doc, chapter_character_actions)
        for character, actions in chapter_character_actions.items():
            campaign_character_actions[character].extend(actions)

character_atlas = {}
for character, actions in campaign_character_actions.items():
    if character not in character_atlas:
        character_atlas[character] = {'actions': actions, 'connections': {}}
    for (char1, char2), connection_info in character_connections.items():
        if character == char1 or character == char2:
            other_character = char2 if character == char1 else char1
            avg_sentiment = connection_info['cumulative_sentiment'] / connection_info['weight']
            character_atlas[character]['connections'][other_character] = {
                'weight': connection_info['weight'],
                'avg_sentiment': avg_sentiment,
                'actions': connection_info['actions']
            }
def getCharacterAtlas():
    return character_atlas


def getCharacterObjFromText(message):
    message = message.lower()
    character_atlas = getCharacterAtlas()
    relevantPeople = []
    for character, data in character_atlas.items():
        characterMentioned = False
        if character.lower() in message:
            characterMentioned = True
        actions = data['actions']
        actionMentioned = False
        connectionActionMentioned = False
        for o in actions:
            if o.lower() in message:
                actionMentioned = True
        for connection, connection_info in data['connections'].items():
            connection_weight = connection_info['weight']
            connection_sentiment = connection_info['avg_sentiment']
            connection_actions = connection_info['actions']
            for o in connection_actions:
                if o.lower() in message:
                    connectionActionMentioned = True

        if(connectionActionMentioned or actionMentioned or characterMentioned):
            relevantPeople.append({"name":character, "actions":actions, "connections":data['connections']})

    return relevantPeople

# Visualization removed for brevity - please refer to the previous detailed visualization steps.

# print(json.dumps(character_atlas, indent=4))

# Visualization part

# Create a new directed graph
'''
G = nx.DiGraph()

# Add nodes, edges with weights and sentiments
for character, data in character_atlas.items():
    G.add_node(character)
    for connected_character, info in data['connections'].items():
        # Add an edge with weight and sentiment
        G.add_edge(character, connected_character, weight=info['weight'], sentiment=info['avg_sentiment'])

# Define positions for the nodes
pos = nx.spring_layout(G)

# Draw the network
for edge in G.edges(data=True):
    # Map the sentiment value to a color
    if edge[2]['sentiment'] > 0:
        edge_color = "green"
    elif edge[2]['sentiment'] < 0:
        edge_color = "red"
    else:
        edge_color = "gray"
    
    # Normalize weight for visualization purposes
    normalized_weight = edge[2]['weight'] / max(info['weight'] for _, _, info in G.edges(data=True)) * 10
    
    # Draw the edge with specified color and normalized weight as thickness
    nx.draw_networkx_edges(G, pos, edgelist=[(edge[0], edge[1])], width=normalized_weight, alpha=0.5, edge_color=edge_color)

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='skyblue')

# Draw node labels
nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

# Remove axes
plt.axis('off')

# Set title and show plot
plt.title("Character Connections Mind Map with Sentiment", fontsize=16)
plt.tight_layout()
plt.show()
'''