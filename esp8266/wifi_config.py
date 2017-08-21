import network

SSID = 'Kalte Fusion'
PASSWORD = 'ceil7VieF5sae5woh1ohleowahsuaw'

wlan_client  = network.WLAN(network.STA_IF)
wlan_client.active(True)
print('connecting to network', SSID, '...')
wlan_client.connect(SSID, PASSWORD)

while not wlan_client.isconnected():
    ...

ip, subnet, gateway, dns = wlan_client.ifconfig()
print('network config:', ip, subnet, gateway, dns)