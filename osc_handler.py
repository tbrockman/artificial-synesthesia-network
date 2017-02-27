import OSC

class OSCHandler:

    def __init__(self, ip, port):
        c = OSC.OSCClient()
        c.connect((ip, port))   # connect to SuperCollider
        self.client = c

    def sendMessage(self, address, message):
        oscmsg = OSC.OSCMessage()
        oscmsg.setAddress(address)
        oscmsg.append(message)
        self.client.send(oscmsg)
