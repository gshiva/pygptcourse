# pygptcourse

Face detection, tracking using USB micro T-Shirt launcher and RaspberryPi camera module to demonstrate how ChatGPT can speed up development and writing clean and SOLID code.

## Documentation generated for T-Shirt Launcher Project by ChatGPT

The following documentation was 95% generated by ChatGPT after copy/pasting the main.py, tracker.py and tshirt_launcher.py code
To see the prompts used, see <https://chat.openai.com/share/e71885d2-8639-409d-bf7a-2809801135f0>

## Micro T-Shirt Launcher

This repository contains Python code for launching micro T-Shirts to a particular person identified through face recognition. The launcher positions itself using it's pan and tilt capabilities to launch the micro T-Shirt towards the identified person's location. The micro T-Shirt launcher does not launch T-Shirt if the person is not in the pre-loaded facial image set. The ability to develop, test and debug the launcher and facial recognition functionality independently is present.

## Requirements

- Python 3.x
- PyUSB library
- Poetry > 1.5.X

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/gshiva/pygptcourse.git
   ```

1. Install the required dependencies:

   ```bash
   # if poetry is not installed
   # curl -sSL https://install.python-poetry.org | python3 -
   poetry install
   ```

   1. Windows:
   Most likely you will run into `No backend available` errors.

   ```bash
      raise NoBackendError('No backend available')
      usb.core.NoBackendError: No backend available
   ```

   Follow the instructions in [AdaFruit's instruction for fixing `no backend error`](https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/windows#test-pyusb-and-pyftdi-3041697). It involves downloading [libusb](https://sourceforge.net/projects/libusb/) and copying it to `C:\Windows\System32\` directory.

   1. Mac:
   Most likely you will run into `No backend available` errors.

   Follow the instructions in [stack overflow article](https://stackoverflow.com/questions/70729330/python-on-m1-mbp-trying-to-connect-to-usb-devices-nobackenderror-no-backend-a) and run the following.

   ```bash
   brew install libusb
   # The above is not sufficient. The libraries installed by brew is not visible to pyusb.
   # Run the following to make the library available
   ln -s /opt/homebrew/lib ~/lib
   ```

1. Connect the T-Shirt launcher via USB.

## Usage

### Using main.py with both the Tracker and T-Shirt Launcher Functionality

The `main.py` script integrates the functionalities of both the tracker and the T-Shirt launcher. It allows for automated control of the T-Shirt launcher based on the face recognition and tracking system.

To use `main.py`:

1. Ensure all prerequisites and setup steps mentioned above are completed.

1. Run `main.py` in the activated Poetry virtual environment to start the integrated system:

   ```bash
   sudo poetry run python main.py
   ```

This script will utilize the camera to detect and track faces, and control the T-Shirt launcher based on the tracked positions.

### Running `tracker.py` Face Recognition Functionality Standalone

If you do not have the USB micro T-Shirt launcher available or you want to test the facial recognition on a different machine, you can do so.

For debugging and testing the camera based facial recognition system:

#### Setup

- Ensure that the images used for face recognition (`shiva_face.jpg`, `adil_face.jpg`, or similar) are in the project directory.
- Verify that `tracker.py` is configured with the correct paths to these images.

#### Running the Script

- Activate the Poetry virtual environment and run the facial recognition system:

  ```bash
  poetry run python tracker.py
  ```

Press `q` on the Video Window to quit.

#### Observation

Running the tracker should show a window similar to below. On the console, you should see simulated commands that moves the launcher device right/left/up/down based on where the identified face is.

![Sample Face Recognition Screenshot](./docs/facial_recognition.png).

Sample output on the console:

```bash
Previous position: [13, 2] Calculated current position: [13, 2], Direction: None, Duration: 0
Nothing to do. Current position: [13, 2] is the same as the previous position [13, 2].
Previous position: [13, 2] Calculated current position: [10, 4], Direction: RIGHT, Duration: 1.0
Moving to position: [10, 4], Direction: RIGHT, Duration: 1.0
```

### Running `tshirt_launcher.py` Launcher Pan/Tilt Functionality Standalone

To use the T-Shirt launcher, execute the `tshirt_launcher.py` script. Make sure you have sufficient permissions to access USB devices.

```bash
sudo poetry run python tshirt_launcher.py
```

The launcher can be controlled using the following commands:

- Move Up: `u`
- Move Down: `d`
- Stop: `s`
- Move Left: `l`
- Move Right: `r`
- Fire: `f`

Enter the command followed by a delay (in seconds) to control the launcher's movements. For example, to move the launcher to the right for 2 seconds, use the command `r 2`. To fire a T-Shirt, use the command `f`.

The launcher's current state is displayed as a prompt, indicating the availability of movement options. For example, if the launcher is capable of moving left and right, the prompt will show `L R` as options.

**Handling Limits:**

The T-Shirt launcher has certain limits in its movement range. The program detects these limits and handles them appropriately. The limits and their respective time limits are as follows:

- `RIGHT_LIMIT`: The launcher has reached the rightmost limit. The maximum time to move from right to left is approximately 26 seconds.
- `LEFT_LIMIT`: The launcher has reached the leftmost limit. The maximum time to move from left to right is approximately 26 seconds.
- `UP_LIMIT`: The launcher has reached the uppermost limit. The maximum time to move from up to down is approximately 4 seconds.
- `DOWN_LIMIT`: The launcher has reached the lowermost limit. The maximum time to move from down to up is approximately 4 seconds.
- `FIRE_COMPLETED`: A previous fire command has been completed.

When any of these limits are reached, the program takes the following actions:

- If the launcher is commanded to move in a direction that corresponds to a limit, the program sends a `STOP` command to halt the movement.
- If a fire command has been completed (`FIRE_COMPLETED` is `True`), the program waits for 1 second and sends a `STOP` command to reset the launcher.

Example usage:

```bash
L R U D F>> r 26
Sending command r
... (launcher moves to the right for approximately 26 seconds)
All the way right. Sending STOP
```

To quit the program, enter `quit`.

## Troubleshooting

If you encounter any issues with the USB device, try detaching the kernel driver before using the launcher:

```python
launcher.detach_kernel_driver()
```

### Setting Breakpoints in Visual Studio Code

To debug `tracker.py` using Visual Studio Code:

#### Setup Visual Studio Code with Poetry

- Open the project folder in Visual Studio Code.
- Ensure the Python extension is installed.
- Configure the Python interpreter to use the virtual environment created by Poetry:
  - Open the Command Palette (Ctrl+Shift+P) and type "Python: Select Interpreter".
  - Choose the interpreter that corresponds to your project's Poetry environment.

#### Setting Breakpoints

- Open `tracker.py` in Visual Studio Code.
- Click on the left margin next to the line number where you want to set a breakpoint.

#### Running the Script with Debugging

- Go to the "Run" panel in Visual Studio Code.
- Click on "Start Debugging" (or press F5) to start the script with the debugger attached.
- The execution will pause when it hits the breakpoint, allowing you to inspect variables and step through the code.

### Code Duplication between `main.py` and `tracker.py`

In this version of the code, an astute reader may notice code duplication between `main.py` and `tracker.py`. The face tracking code and `move_camera` function code is copy/pasted from `tracker.py` to `main.py`. It was done both by accident and intention. The initial implementation of tracker.py was focused on developing the OpenCV functionality on a machine that did not have the USB device attached. Once the testing was complete, it was easier to copy/paste code rather than a modular integration. It was supposed to be a temporary solution. Life intervenes and is present for months now. Repackaging the accidental tech-debt as intentional, this would be a scenario very common in software where the 'temporary' solution becomes 'permanent'. More fixes are done to now 'permanent' solution 'just for this release' resulting in spaghetti code that nobody wants to touch. In the next iterations we will see how ChatGPT can help in refactoring code safely.

#### Code Duplication Rationale

- `main.py` includes sections of code copied from `tracker.py`. This was initially for quick integration, allowing `main.py` to handle face tracking along with the T-Shirt launcher control.
- This also highlights tech debt problem that teams run into when implementing code under tight deadlines. Duplicated code makes it very hard to keep the different versions in `tracker.py` and `main.py` in sync. Testing is harder and so is bug fixing.
- This approach established a working system, with plans to refactor and optimize in subsequent phases.

## Credits

This code is based on the original source available at [https://github.com/hovren/pymissile](https://github.com/hovren/pymissile).

## License

This project is licensed under the [Apache License 2.0](LICENSE).
