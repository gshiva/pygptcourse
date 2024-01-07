import logging
import time

from pygptcourse.otel_decorators import otel_handler
from pygptcourse.tshirt_launcher import (
    DOWN,
    LEFT,
    RIGHT,
    STOP,
    UP,
    Launcher,
    SimulatedLauncher,
)

logger = logging.getLogger(__name__)


class CameraControl:
    TOTAL_TIME_LR = 26
    TOTAL_TIME_TB = 4
    IMAGE_WIDTH = 640
    IMAGE_HEIGHT = 480
    TIME_INCREMENT = 0.1
    TOLERANCE = IMAGE_HEIGHT / (4 * 2)  # for 480, it is 60
    launch_count = 0

    @otel_handler.trace
    def __init__(self, simulation_mode=False):
        self.simulation_mode = simulation_mode
        logger.warning("Starting initialization of Launcher")
        self.launcher = Launcher() if not simulation_mode else SimulatedLauncher()
        logger.error("Finished initialization of Launcher")
        self.current_camera_position = [self.TOTAL_TIME_LR, self.TOTAL_TIME_TB]

    @otel_handler.trace
    def start(self):
        if not self.launcher.running:
            logger.info("Starting launcher...")
            self.launcher.start()

    @otel_handler.trace
    def move_camera(self, direction, duration):
        cmd = STOP
        prev_current_camera_position = self.current_camera_position.copy()
        logger.info(f"Previous camera position: {prev_current_camera_position}")

        # Update the current position based on the direction
        if direction == "LEFT":
            self.current_camera_position[0] -= duration
            cmd = LEFT
        elif direction == "RIGHT":
            self.current_camera_position[0] += duration
            cmd = RIGHT
        elif direction == "UP":
            self.current_camera_position[1] -= duration
            cmd = UP
        elif direction == "DOWN":
            self.current_camera_position[1] += duration
            cmd = DOWN

        # Ensure the current position is within the image bounds
        self.current_camera_position[0] = max(
            0, min(self.current_camera_position[0], self.TOTAL_TIME_LR)
        )
        self.current_camera_position[1] = max(
            0, min(self.current_camera_position[1], self.TOTAL_TIME_TB)
        )

        logger.info(
            f"Previous position: {prev_current_camera_position}, "
            f"Calculated current position: {self.current_camera_position}, "
            f"Direction: {direction}, "
            f"Duration: {duration}"
        )

        if prev_current_camera_position == self.current_camera_position:
            logger.info(
                f"Nothing to do. Current position: {self.current_camera_position} "
                f"is same as previous position {prev_current_camera_position}."
            )
            return
        logger.info(
            f"Moving to position: {self.current_camera_position}, Direction: {direction}, Duration: {duration}"
        )
        self.launcher.move(cmd, duration)

    @otel_handler.trace
    def move_camera_to_center(self):
        logger.info("Moving camera to center")
        # Move to bottom left (0, TOTAL_TIME_TB)
        self.move_camera("LEFT", self.TOTAL_TIME_LR)
        time.sleep(0.1)
        self.move_camera("DOWN", self.TOTAL_TIME_TB)
        time.sleep(0.1)
        # Ensure it goes down
        self.current_camera_position[1] = 0
        self.move_camera("DOWN", self.TOTAL_TIME_TB)
        # Set the current position to bottom left
        self.current_camera_position = [0, self.TOTAL_TIME_TB]
        # Move to the center (TOTAL_TIME_LR/2, TOTAL_TIME_TB/2)
        self.move_camera("RIGHT", self.TOTAL_TIME_LR / 2)
        self.move_camera("UP", self.TOTAL_TIME_TB / 2)

    @otel_handler.trace
    def check_and_move_camera(self, face_center):
        dx = face_center[0] - (self.IMAGE_WIDTH / 2)
        dy = face_center[1] - (self.IMAGE_HEIGHT / 2)

        moving = False
        if dx > self.TOLERANCE:
            self.move_camera("RIGHT", self.TIME_INCREMENT)
            moving = True
        elif dx < -self.TOLERANCE:
            self.move_camera("LEFT", self.TIME_INCREMENT)
            moving = True

        if dy > self.TOLERANCE:
            self.move_camera("DOWN", self.TIME_INCREMENT)
            moving = True
        elif dy < -self.TOLERANCE:
            self.move_camera("UP", self.TIME_INCREMENT)
            moving = True

        return moving

    @otel_handler.trace
    def launch_if_aligned(self, face_center):
        moving = self.check_and_move_camera(face_center)
        if not moving:
            self.launcher.fire()
            self.launch_count += 1
        else:
            logger.info("Target not aligned. Holding launch.")

    @otel_handler.trace
    def stop(self):
        self.launcher.running = False
        self.launcher.close()
