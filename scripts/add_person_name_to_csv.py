"""
Add a 'personName' column with realistic names for each sender (nameOrig).
First pass: collect unique nameOrig and assign each a deterministic name.
Second pass: write CSV with personName column.
"""
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = PROJECT_ROOT / "AIML Dataset.csv"
OUTPUT_CSV = PROJECT_ROOT / "AIML Dataset_with_person_name.csv"
CHUNK_SIZE = 100_000

# Large name lists so we get many unique "First Last" combinations (deterministic per account ID)
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
    "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
    "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa", "Timothy", "Deborah",
    "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon", "Jeffrey", "Laura", "Ryan", "Cynthia",
    "Jacob", "Kathleen", "Gary", "Amy", "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna",
    "Stephen", "Brenda", "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra", "Frank",
    "Rachel", "Alexander", "Catherine", "Patrick", "Carolyn", "Jack", "Janet", "Dennis", "Ruth", "Jerry",
    "Maria", "Tyler", "Heather", "Aaron", "Diane", "Jose", "Virginia", "Adam", "Julie", "Nathan",
    "Joyce", "Zachary", "Victoria", "Henry", "Olivia", "Douglas", "Kelly", "Peter", "Lauren", "Kyle",
    "Christina", "Noah", "Joan", "Ethan", "Evelyn", "Jeremy", "Judith", "Walter", "Megan", "Christian",
    "Andrea", "Keith", "Cheryl", "Roger", "Hannah", "Terry", "Jacqueline", "Austin", "Martha", "Sean",
    "Gloria", "Gerald", "Teresa", "Carl", "Ann", "Dylan", "Sara", "Harold", "Madison", "Jordan",
    "Frances", "Jesse", "Kathryn", "Bryan", "Janice", "Lawrence", "Jean", "Arthur", "Abigail", "Gabriel",
    "Alice", "Bruce", "Judy", "Logan", "Sophia", "Albert", "Grace", "Willie", "Denise", "Alan",
    "Amber", "Eugene", "Doris", "Russell", "Marilyn", "Vincent", "Danielle", "Philip", "Beverly", "Bobby",
    "Isabella", "Johnny", "Theresa", "Bradley", "Diana", "Roy", "Natalie", "Ralph", "Brittany", "Eugene",
    "Diana", "Wayne", "Marie", "Billy", "Kayla", "Howard", "Alexis", "Louis", "Lori", "Harry",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
    "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez",
    "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes",
    "Gonzales", "Fisher", "Vasquez", "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton",
    "Graham", "Reynolds", "Griffin", "Wallace", "West", "Cole", "Hayes", "Chavez", "Gibson", "Bryant",
    "Ellis", "Stevens", "Murray", "Ford", "Marshall", "Owens", "McDonald", "Harrison", "Ruiz", "Kennedy",
    "Wells", "Alvarez", "Woods", "Mcdonald", "Hart", "Hanson", "Daniels", "Palmer", "Mills", "Nichols",
    "Grant", "Knight", "Ferguson", "Rose", "Stone", "Hawkins", "Dunn", "Perkins", "Hudson", "Spencer",
    "Gardner", "Stephens", "Payne", "Pierce", "Berry", "Matthews", "Arnold", "Wagner", "Willis", "Ray",
    "Watkins", "Olson", "Carroll", "Duncan", "Snyder", "Hart", "Cunningham", "Bradley", "Lane", "Andrews",
    "Ruiz", "Harper", "Fox", "Riley", "Armstrong", "Carpenter", "Weaver", "Greene", "Lawrence", "Elliott",
    "Chavez", "Sims", "Austin", "Peters", "Kelley", "Franklin", "Lawson", "Fields", "Gutierrez", "Ryan",
    "Schmidt", "Carr", "Vasquez", "Castillo", "Wheeler", "Larson", "Carlson", "Harper", "George", "Romero",
    "Lane", "Holmes", "Johnston", "Johnston", "Banks", "Meyer", "Bishop", "Mccoy", "Howell", "Alvarez",
    "Moreno", "Fuller", "West", "Lynch", "Dean", "Gilbert", "Garrett", "Romero", "Warren", "Oliver",
    "Medina", "Daniels", "Kim", "Rice", "Schultz", "Jacobs", "Erickson", "Willis", "Hansen", "Osborne",
]


def get_name_for_id(account_id: str, seen_count: int) -> str:
    """Return a deterministic 'First Last' name for the given account ID."""
    s = str(account_id).strip()
    h = abs(hash(s)) % (2**31)
    fi = h % len(FIRST_NAMES)
    li = (h // len(FIRST_NAMES)) % len(LAST_NAMES)
    return f"{FIRST_NAMES[fi]} {LAST_NAMES[li]}"


def main():
    if not INPUT_CSV.exists():
        print(f"Error: {INPUT_CSV} not found.")
        sys.exit(1)

    print("Pass 1: Collecting unique sender accounts (nameOrig)...")
    unique_orig = set()
    for chunk in pd.read_csv(INPUT_CSV, chunksize=CHUNK_SIZE, usecols=["nameOrig"]):
        for v in chunk["nameOrig"].astype(str).str.strip():
            unique_orig.add(v)
    print(f"  Found {len(unique_orig):,} unique accounts.")

    print("Assigning names to each account...")
    id_to_name = {}
    for i, uid in enumerate(sorted(unique_orig)):
        id_to_name[uid] = get_name_for_id(uid, i)
        if (i + 1) % 50_000 == 0:
            print(f"  Assigned {i + 1:,} names...")

    print(f"\nPass 2: Writing CSV with personName column to {OUTPUT_CSV}...")
    first_chunk = True
    total_rows = 0
    for chunk in pd.read_csv(INPUT_CSV, chunksize=CHUNK_SIZE):
        chunk["personName"] = chunk["nameOrig"].astype(str).str.strip().map(lambda x: id_to_name.get(x, x))
        if first_chunk:
            chunk.to_csv(OUTPUT_CSV, index=False, mode="w")
            first_chunk = False
        else:
            chunk.to_csv(OUTPUT_CSV, index=False, mode="a", header=False)
        total_rows += len(chunk)
        if total_rows % 500_000 == 0:
            print(f"  Written {total_rows:,} rows...")

    print(f"Done. Total rows: {total_rows:,}")
    print(f"New file: {OUTPUT_CSV}")
    print("Backend is already set to use this file (DATA_PATH). Restart backend to pick up the new names.")


if __name__ == "__main__":
    main()
