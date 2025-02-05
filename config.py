import random
import locale

TOKEN = ''
GRAPH_DPI = 200
ENABLE_GRAPH = True

MINIGAME_TIME = 15
MINIGAME_SPEED = 0.75
MINIGAME_COUNTDOWN = 3

TRIVIA_TIME = 10
TRIVIA_COUNTDOWN = 3

PUBLIC_STATS = True    #whether or not anybody can view anybody elses stats, or just their own

BRISTOL_STOOL_CHART = {
    1: "Separate hard lumps, like nuts (hard to pass)",
    2: "Sausage-shaped but lumpy",
    3: "Like a sausage but with cracks on the surface",
    4: "Like a sausage or snake, smooth and soft",
    5: "Soft blobs with clear-cut edges (passed easily)",
    6: "Fluffy pieces with ragged edges, a mushy stool",
    7: "Watery, no solid pieces (entirely liquid)"
}

POOP_SYNONYMS = [
    "poop",
    "poopoo",
    "shit",
    "dung",
    "doo-doo",
    "stool",
    "dropping",
    "ass biscuit",
    "dookie",
    "butt brownie",
    "hot sloppy",
    "dump",
    "doody",
    "boom boom",
    "shid",
    "hot sloppy",
    "dookie"
]

LOVE_EMOJIS = [
    "🥰",
    "😍",
    "😘",
    "💖",
    "💗",
    "💕",
    "🫶",
    "💝",
    "💋"
]

RATING_ADVICE = {
    1: f"Go to the ass doctor :(",
    2: f"Be nice to your {random.choice(POOP_SYNONYMS)} hole! It's been through a lot.",
    3: f"I hope your next {random.choice(POOP_SYNONYMS)} is better",
    4: f"Perhaps a diet change, for your health.",
    5: f"Stay hydrated and take care of yourself.",
    6: f"You're doing well, but there's room for improvement.",
    7: f"Nice {random.choice(POOP_SYNONYMS)}! Keep it up.",
    8: f"You're doing great! Keep it up. {random.choice(LOVE_EMOJIS)}",
    9: f"Almost perfect! Keep up the good work. {random.choice(LOVE_EMOJIS)}",
    10: f"Perfect {random.choice(POOP_SYNONYMS)}! You're a pro. {random.choice(LOVE_EMOJIS)}"
}

RATING_EMOJIS = {
    1: "😭",
    2: "🥺",
    3: "😟",
    4: "😞",
    5: "😊",
    6: "😊",
    7: "😬",
    8: "😃",
    9: "😁",
    10: "🤩"
}

JUST_POOPED_TITLE = [
    f"Good job king {random.choice(LOVE_EMOJIS)}",
    f"You did good pretty boi {random.choice(LOVE_EMOJIS)}",
    "Well done mommy!",
    f"Great work daddy! {random.choice(LOVE_EMOJIS)}",
    "Your parents are proud of you!",
    f"Wipe until clean! {random.choice(LOVE_EMOJIS)}",
    "Excellent job little buddy!",
    "You're my lil star!",
    f"Remember to wipe! {random.choice(LOVE_EMOJIS)}"
]

MINIGAME_WIN_TITLE = [
    "You saved the village!",
    f"Good job King {random.choice(LOVE_EMOJIS)}",
    f"Handle me like that, daddy {random.choice(LOVE_EMOJIS)}",
    "Keep it up!"
]

MINIGAME_LOSE_TITLE = [
    "Try harder, scrub",
    "What a stinker",
    "This is why your dad left for milk!",
    "Get your head in the game",
    "Look alive soldier!"
]

TRIVIA_QUESTIONS = [
    {
        "question": f"What is the world record for the largest {random.choice(POOP_SYNONYMS)} ever recorded?",
        "choices": ["12 pounds", "10 feet long", "26 pounds", "5 feet wide"],
        "answer":  "C"
    },
    {
        "question": f"In which country is the invention of toilet paper most commonly attributed to?",
        "choices": ["China", "United States", "France", "England"],
        "answer":  "A"
    },
    {
        "question": f"What is the average amount of time a person spends on the toilet per year?",
        "choices": ["30 hours", "48 hours", "200 hours", "300 hours"],
        "answer":  "C"
    },
    {
        "question": f"Which animal is known to have the largest poop in relation to its body size?",
        "choices": ["Elephant", "Blue Whale", "Hippo", "Kangaroo"],
        "answer":  "D"
    },
    {
        "question": f"In ancient Rome, what was commonly used as a cleaning material after using the toilet?",
        "choices": ["Sand", "Wool", "Rag on a stick", "Leaves"],
        "answer":  "C"
    },
    {
        "question": f"Which type of bacteria is most responsible for producing the gases in human farts?",
        "choices": ["E. coli", "Lactobacillus", "Bifidobacteria", "Methanogens"],
        "answer":  "D"
    },
    {
        "question": f"What is the scientific term for the act of farding?",
        "choices": ["Flatulism", "Defecation", "Evacuation", "Peristalsis"],
        "answer":  "A"
    },
    {
        "question": f"What was the first brand of toilet paper to be perforated for easy tearing?",
        "choices": ["Charmin", "Scott", "Cottonelle", "Northern"],
        "answer":  "B"
    },
    {
        "question": f"Which famous artist created a painting titled ''The Toilet'' in the early 20th century?",
        "choices": ["Pablo Picasso", "Marcel Duchamp", "Salvador Dalí", "Andy Warhol"],
        "answer":  "B"
    },
    {
        "question": f"The average person produces how many pounds of poop each year?",
        "choices": ["10 pounds", "100 pounds", "200 pounds", "500 pounds"],
        "answer":  "C"
    },
    
    
]