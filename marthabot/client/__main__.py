import asyncio


# from client import Client
from client import localization_client

# from client import movement_client
# from client import streaming_client

# from utils.custom_logger import setup_logging

# log = setup_logging(__name__)

import logging

logging.basicConfig()


def main():
    # ctype = input("Choose your client, 'main','pose','movement','streaming'\n")
    localization_client.main()

    # if ctype == "":
    #     Client.main()
    # elif ctype == "main":
    #     Client.main()
    # elif ctype == "pose":
    #     localization_client.main()
    # elif ctype == "movement":
    #     movement_client.main()
    # elif ctype == "streaming":
    #     streaming_client.main([])


if __name__ == "__main__":
    main()
