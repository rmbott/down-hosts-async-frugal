import time
from asyncping3 import ping
import asyncio

# Takes a list of IPs and returns a list of IPs that are down.
# Pings are done in asyncronous batches. If all hosts are up, the number of 
# batches = 1. If one or more hosts are down, the number of 
# batches = "batches". Unless all down hosts turn out to be up on retry. In 
# that case, the number of batches will be less than "batches".

async def tf_ping(host:str) -> bool:
    response = await ping(host)
    if type(response) is float:
        return True # asyncping3.ping returns responsetime floats for successful pings
    if response is None:
        return False # asyncping3.ping returns None for timeouts
    if response is False:
        return response  # asyncping3.ping returns False for resolution errors

async def batch(hosts:list)-> list:
    if len(hosts) <= 0:
        return []
    ping_tasks = []
    for ip in hosts:
        ping_tasks.append(asyncio.create_task(tf_ping(ip)))
    results = await asyncio.gather(*ping_tasks)
    if False in results:
        return [d[0] for d in zip(hosts, results) if d[1] == False]
    else:
        return []

async def down(down_hosts:list, batches:int=2)->list:
        for i in range(0, batches):
            # false negatives (down hosts that are now up on retry) get dropped as this iterates
            down_hosts = await batch(down_hosts)
        return down_hosts

async def main():
    good_ips = ['8.8.8.8', '1.1.1.1']
    bad_ips = ['8.8.1.1', '256.256.256.256']
    ips = good_ips + bad_ips
    start_time = time.time()
    down_hosts = await down(ips)
    print(f'Down Hosts: {down_hosts}')
    print(f'--- {time.time() - start_time} seconds ---')


asyncio.run(main())
