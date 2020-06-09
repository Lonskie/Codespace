def main():
    name = input("What's your name: ")
    print(f"Goodbye, {name}.")

    return 0

if __name__ == "__main__":
    status = main()
    if status != 0:
        print(f"Error: Exit status ({status}).")
        exit(status)