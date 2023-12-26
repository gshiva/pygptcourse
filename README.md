# pygptcourse

Face detection, tracking using USB micro T-Shirt launcher and RaspberryPi camera module to demonstrate how ChatGPT can speed up development and writing clean and SOLID code.

## Documentation generated for T-Shirt Launcher Project by ChatGPT

The following documentation was 95% generated by ChatGPT after copy/pasting the main.py, tracker.py and tshirt_launcher.py code
To see the prompts used, see <https://chat.openai.com/share/e71885d2-8639-409d-bf7a-2809801135f0>

## Micro T-Shirt Launcher

This repository contains Python code for launching micro T-Shirts to a particular person identified through face recognition.
The launcher positions itself using it's pan and tilt capabilities to launch the micro T-Shirt towards the identified person's location.
The micro T-Shirt launcher does not launch T-Shirt if the person is not in the pre-loaded facial image set.
The ability to develop, test and debug the launcher and facial recognition functionality independently is present.

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

   1. Raspberry Pi:
      Most likely you will run into `KeyRing` errors when installing over ssh on raspberry pi.

      To get around it:

      ```shell
      export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
      poetry install
      ```

      should work. See [github issue](https://github.com/python-poetry/poetry/issues/1917) for further details.

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

### Running Face Recognition Functionality Standalone

If you do not have the USB micro T-Shirt launcher available or you want to test the facial recognition on a different machine, you can do so.

For debugging and testing the camera based facial recognition system:

#### Setup

- Ensure that the images used for face recognition (`shiva_face.jpg`, `adil_face.jpg`, or similar) are in the project directory.
- Verify that `main.py` is configured with the correct paths to these images.

#### Running the Script

- Activate the Poetry virtual environment and run the facial recognition system:

  ```bash
  poetry run python main.py --simulate
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

### Running Automated Tests

#### Overview

Automated tests are essential for ensuring the quality and reliability of our application. They cover unit tests, integration tests, and system tests, each designed to validate different aspects of the system. Follow the instructions below to run these tests.

#### Prerequisites

- Ensure poetry is installed and properly set up on your system.

#### Running the Tests

1. **Navigate to the Project Root:**
   Open a terminal and navigate to the root directory of the project.

2. **Run the test:**

   ```shell
   poetry run pytest
   ```

   Alternatively, if the tests are categorized or you want to run a specific set, you can specify the path:

After running the tests, observe the output in the terminal for the results, including passed, failed, and possibly skipped tests.
For detailed results, most test runners offer options to generate reports in various formats.

Run a Specific Test:
Use pytest to run a specific test file or even a single test case within a file. Here's the general structure:

```shell
poetry run pytest tests/path/to/test_file.py::test_class_name::test_function_name
```

Replace `path/to/test_file.py` with the relative path to the test file you want to run.
Replace the `test_class_name` with the specific test class name you want to run.
Replace `test_function_name` with the specific test function you want to execute. If you want to run all tests in a file, just omit ``::test_function_name`.

For example, to run a test named `test_load_and_encode_faces` under the class `TestFaceDetector` in a file located at `tests/test_unit_face_detector.py`, you would use:

```shell
poetry run pytest tests/test_unit_face_detector.py::TestFaceDetector::test_load_and_encode_faces
```

### Running Acceptance Tests

#### Acceptance Tests Overview

`acceptance_test_runner.py` script is part of our quality assurance process. This script facilitates manual acceptance testing by guiding users through predefined test cases, ensuring that our application meets all requirements and works as expected in real-world scenarios when installed at the customer site.

#### Features of the Acceptance Test Runner

- **Input Validation:** Ensures that test results are accurately recorded by accepting only specific inputs ('p', 'P', 'pass', 'Pass', 'PASS' for passing and similar variations for failing).
- **CSV Output:** Results are logged into a CSV file, `acceptance_tests_TIMESTAMP.csv`, making it easy to review and parse test outcomes.
- **Checksum for Integrity:** A SHA256 checksum is generated for the CSV log and saved in a separate file, `acceptance_tests_checksum_TIMESTAMP.txt`, ensuring the integrity of the test results.
- **Unique Timestamps:** Each test session's results are stored in uniquely named files, preventing overwriting and making each test run distinguishable.

#### Running the Acceptance Tests

1. **Activate the Virtual Environment:**
   Ensure Poetry's virtual environment is activated to access all dependencies:

   ```shell
   poetry shell
   ```

   **Execute the Script:**

   Navigate to the acceptance_test directory and run:

   ```shell
   python acceptance_test_runner.py
   ```

### Adding or Modifying Test Cases

To maintain and update the acceptance tests as your application evolves, you can directly modify the `test_cases` list in the `acceptance_test_runner.py` script. Here's how:

#### Editing the `test_cases` List

1. **Find the `test_cases` List:**
   Open the `acceptance_test_runner.py` script and locate the `test_cases` list. It starts with an opening square bracket `[` and ends with a closing square bracket `]`.

1. **Adding a New Test Case:**
   Directly add a new dictionary to the `test_cases` list for each new test case. Ensure each dictionary contains the 'name', 'instructions', and 'expected_result' keys.

   **From:**

   ```python
   test_cases = [
      {
        "name": "Face Detection Accuracy",
        "instructions": (
            "Present various images to the system with different lighting, "
            "distances, and orientations. Verify the system accurately detects "
            "faces in each image."
        ),
        "expected_result": (
            "The system should detect faces in at least 95% of the cases across "
            "all conditions."
        ),
      },
   ]
   ```

**To:**

```python
test_cases = [
      {
        "name": "Face Detection Accuracy",
        "instructions": (
            "Present various images to the system with different lighting, "
            "distances, and orientations. Verify the system accurately detects "
            "faces in each image."
        ),
        "expected_result": (
            "The system should detect faces in at least 95% of the cases across "
            "all conditions."
        ),
      },
      {
      "name": "New Test Case",
      "instructions": "Instructions for the new test case.",
      "expected_result": "Expected outcome or behavior for the new test case."
      },
      # Add more test cases as needed
]
```

**Note:**

For `flake8` to pass ensure that each line is less than `120` characters. You can do that by enclosing your string using `(` and `)`.

1. **Removing an Existing Test Case:**

To remove a test case, simply delete the entire dictionary entry for that test case from the test_cases list.

Before Deletion:

```python
test_cases = [
{ ... }, # Some test case
{
"name": "Obsolete Test Case",
"instructions": "Old instructions.",
"expected_result": "Old expected result."
},
{ ... } # Other test cases
]
```

After Deletion:

```python
test_cases = [
{ ... }, # Some test case
# The obsolete test case has been removed
{ ... } # Other test cases
]
```

**Best Practices:**

- Clear and Descriptive: Make sure each test case is clearly described with explicit instructions and expected results.
- Validation: After editing, ensure the script still runs without syntax errors. This might include checking for missing commas, brackets, or quotation marks.
- Documentation: Document any changes made to the test cases via commit messages, including why a test was added or removed, to maintain a clear history of the test suite evolution.

## Credits

This code is based on the original source available at [https://github.com/hovren/pymissile](https://github.com/hovren/pymissile).

## License

This project is licensed under the [Apache License 2.0](LICENSE).
