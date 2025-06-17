import argparse

def main():
    parser = argparse.ArgumentParser(description="CLI entry point.")
    parser.add_argument("--name", type=str, help="Your name")
    args = parser.parse_args()
    print(f"Hello, {args.name}!")

if __name__ == "__main__":
    main()
