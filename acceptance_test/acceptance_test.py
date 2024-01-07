import csv
import datetime
import hashlib

# The list of test cases for acceptance with instructions and expected results
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
        "name": "Camera Movement Response",
        "instructions": (
            "Simulate face movement in the camera's view and observe the "
            "camera's movement. The camera should move correspondingly to keep "
            "the face centered."
        ),
        "expected_result": (
            "The camera should track the face, moving correspondingly to keep "
            "the face centered in the frame."
        ),
    },
    {
        "name": "System Integration with Real Hardware",
        "instructions": (
            "Set up the system with the actual hardware and observe it operating "
            "in real-time. Verify that the system performs reliably without "
            "integration issues."
        ),
        "expected_result": (
            "The system should perform reliably, detecting faces and controlling "
            "the camera smoothly, with no hardware integration issues."
        ),
    },
    {
        "name": "User Interaction and Control",
        "instructions": (
            "Interact with the system's user interface to change settings or "
            "modes. Verify that the system responds correctly to these inputs."
        ),
        "expected_result": (
            "The system should reflect changes immediately and behave according "
            "to the new settings."
        ),
    },
    {
        "name": "Performance Under Load",
        "instructions": (
            "Feed the system with continuous input or high volume of data. Check "
            "the system's performance for latency and accuracy without crashing "
            "or errors."
        ),
        "expected_result": (
            "The system should maintain a consistent detection rate and latency "
            "within acceptable bounds."
        ),
    },
    {
        "name": "Failure and Recovery",
        "instructions": (
            "Introduce failures like obstructed camera view or extreme lighting "
            "conditions. Verify that the system either recovers gracefully or "
            "provides clear error messages."
        ),
        "expected_result": (
            "The system should alert the user of the obstruction and attempt to "
            "resume normal operation once the obstruction is cleared."
        ),
    },
    {
        "name": "Compliance and Security",
        "instructions": (
            "Review the system's handling of data and user information. Verify "
            "that it complies with relevant security standards and laws."
        ),
        "expected_result": (
            "The system should encrypt sensitive data, ensure user data privacy, "
            "and allow users to control their data as per compliance standards."
        ),
    },
    {
        "name": "Face Recognition and Launch Triggering",
        "instructions": (
            "Place a recognized face in the camera's view and keep it stationary. "
            "Observe if the T-shirt is launched."
        ),
        "expected_result": (
            "The system should identify the face and trigger a T-shirt launch."
        ),
    },
    {
        "name": "Non-Recognition and No Launch",
        "instructions": (
            "Introduce an unrecognized face or object into the camera's view. "
            "Ensure it remains stationary."
        ),
        "expected_result": (
            "The system should not recognize the face/object, and no T-shirt "
            "launch should occur."
        ),
    },
    {
        "name": "Movement and Launch Cancellation",
        "instructions": (
            "Start with a recognized face in a stationary position. After "
            "identification, move it out of the position."
        ),
        "expected_result": (
            "The system should cancel the T-shirt launch as soon as the face moves "
            "from its recognized position."
        ),
    },
    {
        "name": "Observability and Monitoring",
        "instructions": (
            "Ensure that the .env file is populated with the right values"
            " for Grafana Cloud Integration.\n"
            "See .env.example on the values that need to be set.\n"
            "Start with a recognized face in a stationary position. After "
            "identification, move it out of the position."
        ),
        "expected_result": (
            "On the Explore tab in Grafana Cloud, you should be able to see:\n"
            "faces_detected metric in grafanacloud-*-prom\n"
            "traces and spans in grafanacloud-*-traces\n"
            "logs in grafanacloud-*-logs\n"
        ),
    },
]


def write_results_to_csv(file_name, test_name, result, notes):
    """Writes the test results to a CSV file."""
    with open(file_name, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, test_name, result, notes])


def generate_sha256_checksum(file_name):
    """Generates a SHA256 checksum of the file."""
    with open(file_name, "rb") as f:
        _bytes = f.read()  # read entire file as bytes
        return hashlib.sha256(_bytes).hexdigest()


def get_validated_input(prompt, valid_responses):
    """Asks user for input and ensures it's valid based on given valid responses."""
    user_input = input(prompt).strip().lower()
    while user_input not in valid_responses:
        print(
            "Invalid input. Please enter one of the following: "
            + ", ".join(valid_responses)
        )
        user_input = input(prompt).strip().lower()
    return user_input


def main():
    # Generate unique file names with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_csv = f"acceptance_tests_{timestamp}.csv"
    checksum_file = f"acceptance_tests_checksum_{timestamp}.txt"

    # Create and initialize the CSV file with headers
    with open(log_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "test_name", "result", "notes"])

    print("Starting Acceptance Testing Session")

    for test in test_cases:
        print("\n-----------------------------------")
        print(f"Test: {test['name']}")
        print("Instructions:", test["instructions"])
        print("Expected Result:", test["expected_result"])

        # Validate user input for pass/fail
        result = get_validated_input(
            "Enter 'p' for pass or 'f' for fail: ", ["p", "pass", "f", "fail"]
        )
        notes = input("Notes (optional): ").strip()

        # Write the results to CSV
        write_results_to_csv(
            log_csv, test["name"], result.upper()[0], notes
        )  # 'P' or 'F'

    # Generate and save SHA256 checksum
    checksum = generate_sha256_checksum(log_csv)
    with open(checksum_file, "w") as f:
        f.write("SHA256 Checksum: " + checksum + "\n")

    print("\nTesting session complete. Results logged in:", log_csv)
    print("Integrity checksum saved in:", checksum_file)


if __name__ == "__main__":
    main()
