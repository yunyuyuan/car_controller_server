import bluetooth


class BthClient(object):
    def __init__(self, just_connect=False):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock.bind(("", bluetooth.PORT_ANY))
        self.server_sock.listen(1)
        print("listen")

        uuid = "00001101-0000-1000-8000-00805F9B34FB"

        bluetooth.advertise_service(self.server_sock, "CarServer",
                                    service_id=uuid,
                                    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE])
        print("advertise")
        self.just_connect = just_connect
        if not just_connect:
            from car_control import CarController
            import subprocess

            subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscan'])
            self.controller = CarController()

    def run(self):
        while 1:
            client_sock, address = self.server_sock.accept()
            print("Accepted connection from ", address)
            while 1:
                try:
                    data = eval(bytes.decode(client_sock.recv(1024), 'utf-8'))
                    print(data)
                    if not self.just_connect:
                        self.controller.parse_req(data)
                except SyntaxError:
                    pass
                except bluetooth.btcommon.BluetoothError:
                    break
