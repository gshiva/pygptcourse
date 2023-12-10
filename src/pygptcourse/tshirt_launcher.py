# original source from https://github.com/hovren/pymissile
#!/usr/bin/env python3
# encoding: utf8
import time
import threading

import usb.core
import usb.util

VENDOR = 0x1941
PRODUCT = 0x8021

RIGHT = 8
LEFT = 4
STOP = 15
FIRE = 16
DOWN = 2
UP = 1


class Launcher(object):
    def __init__(self):
        dev = usb.core.find(idVendor=VENDOR, idProduct=PRODUCT)

        if dev is None:
            raise Exception("Could not find USB device")

        try:
            dev.detach_kernel_driver(0)
            print("Device unregistered")
        except Exception:
            print("Already unregistered")

        dev.reset()
        self.dev = dev
        self.dev.set_configuration()
        self.cfg = dev.get_active_configuration()
        self.intf = self.cfg[(0, 0)]
        self.fire_start_time = time.time()

        usb.util.claim_interface(self.dev, self.intf)

        self.ep = usb.util.find_descriptor(
            self.intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress)
            == usb.util.ENDPOINT_IN,
        )

        self.send_command(0)

        self.running = False
        self.firing = False

        self.state = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "fire": False,
        }

    #        try:
    #            self.dev.reset()
    #        except usb.core.USBError, e:
    #            print("RESET ERROR", e)

    def start(self):
        self.running = True
        self.t = threading.Thread(target=self.read_process)
        self.t.start()
        self.running = True

    def stop(self):
        self.running = False
        print("Stopping the thread")
        self.t.stop()
        print("Thread stopped")

    def read_process(self):
        abort_fire = False
        fire_complete_time = time.time()
        while self.running:
            time.sleep(0.1)
            if self.firing and abort_fire:
                if time.time() - fire_complete_time > 10.0:
                    print("Aborting fire")
                    self.send_command(0)
                    self.firing = False
                    abort_fire = False

            data = self.read(8)
            # print(data)
            if data:
                a, b = data[:2]
                # the data value looks like this: array('B', [0, 24, 0, 0, 0, 0, 0, 0])
                # the above line takes the first 2 bytes of the array
                # assigns them to a and b
                # b has the values for RIGHT_LIMIT, LEFT_LIMIT, FIRE_COMPLETED
                # a has the values for UP_LIMIT, DOWN_LIMIT
                # when the a or b matches the following values shown in the table
                # they are set to true
                #
                # | Variable        | b (base 10)           | a (base 10)  |
                # | ------------- |:-------------:| -----:|
                # | RIGHT_LIMIT      | 24 | - |
                # | LEFT_LIMIT      | 20      |   - |
                # | FIRE_COMPLETED | 128      |    - |
                # | UP_LIMIT | -      |    128 |
                # | DOWN_LIMIT | -      |    64 |
                RIGHT_LIMIT = (b & 0x08) != 0
                LEFT_LIMIT = (b & 0x04) != 0
                FIRE_COMPLETED = (b & 0x80) != 0
                UP_LIMIT = (a & 0x80) != 0
                DOWN_LIMIT = (a & 0x40) != 0

                self.state["up"] = UP_LIMIT
                self.state["down"] = DOWN_LIMIT
                self.state["left"] = LEFT_LIMIT
                self.state["right"] = RIGHT_LIMIT
                self.state["fire"] = FIRE_COMPLETED

                if LEFT_LIMIT and self.command == LEFT:
                    print("All the way left. Sending STOP")
                    self.send_command(STOP)
                elif RIGHT_LIMIT and self.command == RIGHT:
                    print("All the way right. Sending STOP")
                    self.send_command(STOP)
                elif UP_LIMIT and self.command == UP:
                    print("All the way up. Sending STOP")
                    self.send_command(STOP)
                elif DOWN_LIMIT and self.command == DOWN:
                    print("All the way down. Sending STOP")
                    self.send_command(STOP)

                if FIRE_COMPLETED and self.firing:
                    fire_complete_time = time.time()
                    print(
                        f"Firing completed in {fire_complete_time-self.fire_start_time} seconds."
                    )
                    time.sleep(
                        5.0
                    )  # waiting too short of a time causes the next firing to end too fast
                    print("Fire completed. Sending 0")
                    self.send_command(0)
                    self.firing = False
        self.close()
        print("THREAD STOPPED")

    def read(self, length):
        try:
            return self.ep.read(length)
        except usb.core.USBError:
            return None

    def send_command(self, command):
        try:
            self.command = command
            self.dev.ctrl_transfer(0x21, 0x09, 0x200, 0, [command])
        except usb.core.USBError as e:
            print("SEND ERROR", e)

    def move(self, command, duration):
        try:
            self.send_command(command)
            time.sleep(duration)
            self.send_command(STOP)
        except usb.core.USBError as e:
            print("SEND ERROR", e)

    # added to see if this would fix the overheating problem
    # after the program exits when connected to a Mac
    def close(self):
        print("Closing connection")
        usb.util.dispose_resources(self.dev)


# // Control of the launcher works on a binary code – see the table below for an explanation
# //
# // | 16 | 8 | 4 | 2 | 1 |
# // |——|—|—|—|—|
# // | 0 | 0 | 0 | 0 | 1 | 1 – Up
# // | 0 | 0 | 0 | 1 | 0 | 2 – Down
# // | 0 | 0 | 0 | 1 | 1 | 3 – nothing
# // | 0 | 0 | 1 | 0 | 0 | 4 – Left
# // | 0 | 0 | 1 | 0 | 1 | 5 – Up / Left
# // | 0 | 0 | 1 | 1 | 0 | 6 – Down / left
# // | 0 | 0 | 1 | 1 | 1 | 7 – Slow left
# // | 0 | 1 | 0 | 0 | 0 | 8 – Right
# // | 0 | 1 | 0 | 0 | 1 | 9 – Up / Right
# // | 0 | 1 | 0 | 1 | 0 | 10 – Down / Right
# // | 0 | 1 | 0 | 1 | 1 | 11 – Slow Right
# // | 0 | 1 | 1 | 0 | 0 | 12 – nothing
# // | 0 | 1 | 1 | 0 | 1 | 13 – Slow Up
# // | 0 | 1 | 1 | 1 | 0 | 14 – Slow Down
# // | 0 | 1 | 1 | 1 | 1 | 15 – Stop
# // | 1 | 0 | 0 | 0 | 0 | 16 – Fire
# //
# // | Fire |RT |LT |DN |UP |

# Max Range in seconds for launcher
# Right<->Left Max Range = 26
# Up<->Down Max Range = 4

if __name__ == "__main__":
    launcher = Launcher()

    launcher.start()

    print("Starting command loop")
    while True:
        prompt = "{} {} {} {} {}".format(
            "L" if launcher.state["left"] else " ",
            "R" if launcher.state["right"] else " ",
            "U" if launcher.state["up"] else " ",
            "D" if launcher.state["down"] else " ",
            "F" if launcher.state["fire"] else " ",
        )
        try:
            s = input("{}>> ".format(prompt)).strip()
            print(f"Received command {s}")
            cmd, delay = s.split()
            delay = float(delay)
        except EOFError:
            cmd = "quit"
        except ValueError:
            cmd = s
            delay = 0

        if cmd == "quit":
            break

        if cmd in "rlud" and delay > 0:
            print(f"Sending command {cmd}")
            if cmd == "r":
                launcher.send_command(RIGHT)
            if cmd == "l":
                launcher.send_command(LEFT)
            if cmd == "u":
                if launcher.state["up"]:
                    delay = 0
                else:
                    launcher.send_command(UP)
            if cmd == "d":
                launcher.send_command(DOWN)

            time.sleep(delay)
            launcher.send_command(STOP)

        if cmd == "f":
            launcher.firing = True
            launcher.fire_start_time = time.time()
            launcher.send_command(FIRE)

    launcher.running = False

    launcher.close()

    print("Done")
