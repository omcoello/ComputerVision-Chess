from services.controller import GameController

def main():
    controller = GameController(device_index=1, debug=True)
    controller.run()

if __name__ == "__main__":
    main()
