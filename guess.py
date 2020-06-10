import random

lower, upper = 1, 500

print(f"i am thinking of a random number between {lower} and {upper}.")

rnd = random.randint(lower, upper)
guesses = 0

while True:
    try:
        guess = int(input("Guess: "))
        guesses = guesses + 1
    except:
        print("That's not a valid number...")
        continue

    if guess < rnd:
        print("Nope. A little higher")
    elif guess > rnd:
        print("Nope. A little lower")
    else:
        print(f"That is right! You got it in only {guesses} guesses!")
        break
    
