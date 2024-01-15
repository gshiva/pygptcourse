# System Design Documentation

## Overview

This document provides an overview of the design and architecture of the camera control and face detection system, including the t-shirt launcher control mechanism. It includes UML class diagrams and sequence diagrams to illustrate the relationships and interactions between various components.

## Class Diagram

The following class diagram represents the structure of the system, showing classes, their methods, and relationships.

```mermaid

classDiagram
    class CameraControl {
        -start()
        -move_camera()
        -move_camera_to_center()
        -check_and_move_camera()
        -launch_if_aligned()
        -stop()
    }
    class CameraManager {
        -start()
        -stop()
    }
    class OpenTelemetryCredentials {
        -is_configured()
    }
    class FaceDetector {
        -load_and_encode_faces()
        -detect_faces()
    }
    class ImageLoader {
        -get_full_image_path()
    }
    class FileSystemImageLoader {
        -get_full_image_path()
    }
    class AbstractLauncher {
        -send_command()
        -start()
        -stop()
        -fire()
        -move()
        -close()
    }
    class Launcher {
        -start()
        -stop()
        -read_process()
        -read()
        -send_command()
        -move()
        -fire()
        -close()
    }
    class SimulatedLauncher {
        -send_command()
        -start()
        -stop()
        -fire()
        -move()
        -close()
    }
    class DummyMetric {
        -add()
        -get_count()
    }
    class OpenTelemetryHandler {
        <<decorator>>
        -_initialize_dummy_metrics()
        -trace()
    }
    CameraControl --> CameraManager: Uses
    FaceDetector --> ImageLoader: Uses
    FileSystemImageLoader ..|> ImageLoader: Inherits
    Launcher ..|> AbstractLauncher: Inherits
    SimulatedLauncher ..|> AbstractLauncher: Inherits
    OpenTelemetryHandler --> OpenTelemetryCredentials: Uses
```

## Sequence Diagram

The sequence diagram below shows the interactions between the classes during the operation of the system.

```mermaid
sequenceDiagram
    participant Main
    participant CameraControl
    participant CameraManager
    participant OpenTelemetryCredentials
    participant FaceDetector
    participant ImageLoader
    participant AbstractLauncher
    Main->>OpenTelemetryCredentials: Creates instance
    Main->>CameraControl: Creates instance
    Main->>CameraManager: Creates instance
    Main->>FaceDetector: Creates instance
    Main->>ImageLoader: Creates instance
    Main->>AbstractLauncher: Creates instance (Launcher/SimulatedLauncher)
    loop Camera Operations
        CameraControl->>CameraManager: start()
        CameraControl->>CameraManager: stop()
    end
    loop Face Detection
        FaceDetector->>ImageLoader: get_full_image_path()
        FaceDetector->>FaceDetector: load_and_encode_faces()
        FaceDetector->>FaceDetector: detect_faces()
    end
    loop T-Shirt Launching
        CameraControl->>AbstractLauncher: move()
        CameraControl->>AbstractLauncher: fire()
        CameraControl->>AbstractLauncher: stop()
    end

```
