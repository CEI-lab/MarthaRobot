"""
  Connection configuration details
"""

# client.py
host = '192.168.0.191'
command_port = 65432
bytes_per_packet = 4096
response_port = 28200


# streaming_client.py
ports = {"rs": 1024, "tof": 1025, "ext": 1028}
mc_ip_address = '224.0.0.1'
streaming_chunk_size = 4096
