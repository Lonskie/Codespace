def say(what_to_say):
    import subprocess
    proc = subprocess.Popen(['espeak', '-ven-rp+f5', '-s180', what_to_say],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    out, err = proc.communicate()
    return (proc.returncode, out, err)

def sayp(message, end="\n"):
    print(message, end=end)
    return say(message)

def sayi(message="input> "):
    sayp(message, end='')
    return input()

sayp("You walk in to a store, and you try to buy some beer (because it is Christmas)")

name = sayi("What is your name? ")

sayp(f"Your name is {name}, huh? Very well.")

age = int(sayi("What is your age, then: "))

if age > 18:
    sayp("You're over over 18 old, huh! Wow you're old. The beer will be £12.99.")
else:
    sayp(f"You're {age} years old, thats pretty young.and also you are not allowed to have the beer so get out of here!.")
