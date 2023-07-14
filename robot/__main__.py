from robot.HSIMaster import HSIMaster

if __name__ == "__main__":
    obj = HSIMaster()
    obj.initializeCommandRegistry()
    obj.startSystem()
