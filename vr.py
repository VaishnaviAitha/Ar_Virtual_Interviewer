import cv2
import numpy as np

class SimpleVRConverter:
    def __init__(self, camera_source=0):
        """
        Initialize the VR converter
        
        Parameters:
        camera_source: 0 for default webcam, 1 for second camera,
                      or 'path/to/video.mp4' for video file
        """
        self.camera_source = camera_source
        self.cap = None
        
        # VR settings
        self.depth = 40          # 3D depth effect (0-100)
        self.convergence = 0.5   # Where objects converge (0-1)
        self.enable_3d = True    # Enable 3D effect
        
        # Initialize camera
        self.setup_camera()
        
        # Setup display windows
        self.setup_windows()
        
    def setup_camera(self):
        """Setup camera based on source type"""
        try:
            # Check if it's a file path or camera index
            if isinstance(self.camera_source, str):
                self.cap = cv2.VideoCapture(self.camera_source)
                print(f"Loading video: {self.camera_source}")
            else:
                self.cap = cv2.VideoCapture(self.camera_source)
                print(f"Using camera index: {self.camera_source}")
            
            if not self.cap.isOpened():
                raise Exception(f"Cannot open camera/video: {self.camera_source}")
                
            # Test capture
            ret, test_frame = self.cap.read()
            if not ret:
                raise Exception("Cannot read from camera/video")
                
            print(f"Camera resolution: {test_frame.shape[1]}x{test_frame.shape[0]}")
            
        except Exception as e:
            print(f"Error setting up camera: {e}")
            print("\nTrying different camera indices...")
            self.try_different_cameras()
    
    def try_different_cameras(self):
        """Try different camera indices if default fails"""
        for i in range(5):  # Try first 5 camera indices
            self.cap = cv2.VideoCapture(i)
            if self.cap.isOpened():
                print(f"Found camera at index {i}")
                ret, frame = self.cap.read()
                if ret:
                    print(f"Successfully opened camera {i}")
                    self.camera_source = i
                    return
            self.cap.release()
        
        print("No camera found! Using test pattern instead.")
        self.camera_source = 'test_pattern'
    
    def setup_windows(self):
        """Create display windows and controls"""
        # Create windows
        cv2.namedWindow('VR Output (Side-by-Side)', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Original Feed', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Controls', cv2.WINDOW_NORMAL)
        
        # Set window positions
        cv2.moveWindow('VR Output (Side-by-Side)', 50, 50)
        cv2.moveWindow('Original Feed', 700, 50)
        cv2.moveWindow('Controls', 50, 550)
        
        # Create trackbars in Controls window
        cv2.createTrackbar('3D Depth', 'Controls', self.depth, 100, self.on_depth_change)
        cv2.createTrackbar('Convergence', 'Controls', int(self.convergence*100), 100, self.on_convergence_change)
        cv2.createTrackbar('3D On/Off', 'Controls', 1, 1, self.on_3d_toggle)
        cv2.createTrackbar('Brightness', 'Controls', 50, 100, self.on_brightness_change)
        
        # Add text instructions
        self.instructions = [
            "CONTROLS:",
            "Q - Quit",
            "S - Save screenshot",
            "V - Start/Stop recording",
            "Space - Pause/Resume",
            "F - Fullscreen toggle",
            "+/- - Adjust depth",
            "[/] - Adjust convergence"
        ]
    
    def on_depth_change(self, val):
        """Callback for depth trackbar"""
        self.depth = val
    
    def on_convergence_change(self, val):
        """Callback for convergence trackbar"""
        self.convergence = val / 100.0
    
    def on_3d_toggle(self, val):
        """Callback for 3D toggle"""
        self.enable_3d = bool(val)
    
    def on_brightness_change(self, val):
        """Callback for brightness adjustment"""
        self.brightness = val - 50  # Center at 0
    
    def create_test_pattern(self):
        """Create a test pattern when no camera is available"""
        # Create a colorful test pattern
        height, width = 480, 640
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw grid
        for i in range(0, width, 40):
            cv2.line(frame, (i, 0), (i, height), (100, 100, 100), 1)
        for i in range(0, height, 40):
            cv2.line(frame, (0, i), (width, i), (100, 100, 100), 1)
        
        # Draw center cross
        cv2.line(frame, (width//2, 0), (width//2, height), (0, 255, 0), 2)
        cv2.line(frame, (0, height//2), (width, height//2), (0, 255, 0), 2)
        
        # Draw depth test object
        center = (width//2, height//2)
        cv2.circle(frame, center, 50, (255, 0, 0), -1)  # Blue circle
        
        # Add text
        cv2.putText(frame, "VR TEST PATTERN", (width//4, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, "Connect a camera for live feed", (width//6, height-50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        return frame
    
    def create_vr_frame(self, frame):
        """
        Convert normal frame to VR side-by-side view
        
        Args:
            frame: Input BGR frame from camera
        
        Returns:
            VR frame in side-by-side format
        """
        if self.camera_source == 'test_pattern':
            frame = self.create_test_pattern()
        
        h, w = frame.shape[:2]
        
        if not self.enable_3d:
            # Just duplicate frame for both eyes (no 3D)
            vr_frame = np.hstack([frame, frame])
        else:
            # Apply brightness adjustment if needed
            if hasattr(self, 'brightness'):
                frame = cv2.convertScaleAbs(frame, alpha=1.0, beta=self.brightness)
            
            # Calculate shift based on depth setting
            shift = int((self.depth / 100.0) * (w / 10))
            
            # Create left eye view (shifted right)
            left_eye = np.roll(frame, -shift, axis=1)
            # Fill the gap created by roll
            left_eye[:, -shift:] = 0
            
            # Create right eye view (shifted left)
            right_eye = np.roll(frame, shift, axis=1)
            # Fill the gap
            right_eye[:, :shift] = 0
            
            # Apply convergence (adjust horizontal alignment)
            conv_shift = int(shift * (self.convergence - 0.5) * 2)
            left_eye = np.roll(left_eye, -conv_shift, axis=1)
            right_eye = np.roll(right_eye, conv_shift, axis=1)
            
            # Combine side-by-side
            vr_frame = np.hstack([left_eye, right_eye])
        
        # Add VR guides and info
        vr_frame = self.add_vr_overlay(vr_frame)
        
        return vr_frame
    
    def add_vr_overlay(self, frame):
        """Add VR guides and information overlay"""
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # Center separation line
        cv2.line(overlay, (w//2, 0), (w//2, h), (0, 255, 0), 2)
        
        # Add crosshairs for each eye
        left_center = (w//4, h//2)
        right_center = (3*w//4, h//2)
        
        for center in [left_center, right_center]:
            # Crosshair
            cv2.line(overlay, (center[0]-20, center[1]), 
                    (center[0]+20, center[1]), (0, 0, 255), 2)
            cv2.line(overlay, (center[0], center[1]-20), 
                    (center[0], center[1]+20), (0, 0, 255), 2)
            
            # Circle around crosshair
            cv2.circle(overlay, center, 30, (255, 0, 0), 2)
        
        # Add text info
        info_y = 30
        cv2.putText(overlay, "LEFT EYE", (20, info_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(overlay, "RIGHT EYE", (w//2 + 20, info_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add settings info
        settings_text = f"Depth: {self.depth} | Convergence: {self.convergence:.2f} | 3D: {'ON' if self.enable_3d else 'OFF'}"
        cv2.putText(overlay, settings_text, (20, h-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)
        
        # Add keyboard shortcuts
        shortcuts = "Q:Quit  S:Save  Space:Pause  F:Fullscreen"
        cv2.putText(overlay, shortcuts, (w-400, h-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return overlay
    
    def update_controls_window(self):
        """Update the controls window with current settings"""
        controls_img = np.zeros((200, 400, 3), dtype=np.uint8)
        
        # Title
        cv2.putText(controls_img, "VR CONVERTER CONTROLS", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Display current settings
        y_pos = 60
        for i, line in enumerate(self.instructions):
            cv2.putText(controls_img, line, (10, y_pos + i*25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add current values
        values_y = 200
        cv2.putText(controls_img, f"Current Depth: {self.depth}", (10, values_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(controls_img, f"Current Convergence: {self.convergence:.2f}", (10, values_y+25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return controls_img
    
    def save_screenshot(self, frame, vr_frame):
        """Save current frames to file"""
        timestamp = cv2.getTickCount()
        cv2.imwrite(f"screenshot_original_{timestamp}.jpg", frame)
        cv2.imwrite(f"screenshot_vr_{timestamp}.jpg", vr_frame)
        print(f"Screenshots saved with timestamp: {timestamp}")
    
    def run(self):
        """Main loop to run the VR converter"""
        print("\n" + "="*50)
        print("VR CONVERTER STARTED")
        print("="*50)
        print("\nInstructions:")
        for line in self.instructions:
            print(f"  {line}")
        print("\nPress 'Q' to quit")
        
        recording = False
        video_writer = None
        paused = False
        
        while True:
            if not paused:
                # Capture frame
                if self.camera_source == 'test_pattern':
                    frame = self.create_test_pattern()
                else:
                    ret, frame = self.cap.read()
                    if not ret:
                        print("Cannot read frame. Restarting capture...")
                        self.cap.release()
                        self.setup_camera()
                        continue
                
                # Mirror the frame (more natural)
                frame = cv2.flip(frame, 1)
            
            # Create VR frame
            vr_frame = self.create_vr_frame(frame)
            
            # Update controls window
            controls_img = self.update_controls_window()
            
            # Display all windows
            cv2.imshow('VR Output (Side-by-Side)', vr_frame)
            cv2.imshow('Original Feed', frame)
            cv2.imshow('Controls', controls_img)
            
            # Handle recording
            if recording:
                video_writer.write(vr_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):  # Quit
                break
            elif key == ord('s'):  # Save screenshot
                self.save_screenshot(frame, vr_frame)
            elif key == ord('v'):  # Start/stop recording
                if not recording:
                    # Start recording
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    height, width = vr_frame.shape[:2]
                    video_writer = cv2.VideoWriter(f'vr_output_{cv2.getTickCount()}.avi', 
                                                  fourcc, 20.0, (width, height))
                    recording = True
                    print("Started recording...")
                else:
                    # Stop recording
                    recording = False
                    video_writer.release()
                    print("Recording saved.")
            elif key == ord(' '):  # Space bar to pause
                paused = not paused
                print(f"Paused: {paused}")
            elif key == ord('f'):  # Toggle fullscreen
                cv2.setWindowProperty('VR Output (Side-by-Side)', 
                                     cv2.WND_PROP_FULLSCREEN, 
                                     cv2.WINDOW_FULLSCREEN ^ cv2.getWindowProperty('VR Output (Side-by-Side)', cv2.WND_PROP_FULLSCREEN))
            elif key == ord('+'):  # Increase depth
                self.depth = min(100, self.depth + 5)
                cv2.setTrackbarPos('3D Depth', 'Controls', self.depth)
            elif key == ord('-'):  # Decrease depth
                self.depth = max(0, self.depth - 5)
                cv2.setTrackbarPos('3D Depth', 'Controls', self.depth)
            elif key == ord(']'):  # Increase convergence
                self.convergence = min(1.0, self.convergence + 0.05)
                cv2.setTrackbarPos('Convergence', 'Controls', int(self.convergence*100))
            elif key == ord('['):  # Decrease convergence
                self.convergence = max(0.0, self.convergence - 0.05)
                cv2.setTrackbarPos('Convergence', 'Controls', int(self.convergence*100))
        
        # Cleanup
        if recording and video_writer:
            video_writer.release()
        
        if self.cap and isinstance(self.camera_source, int):
            self.cap.release()
        
        cv2.destroyAllWindows()
        print("\nVR Converter stopped.")

# Main execution
if __name__ == "__main__":
    import sys
    
    print("="*50)
    print("SIMPLE VR CONVERTER")
    print("="*50)
    print("\nChoose camera source:")
    print("  0 - Default webcam")
    print("  1 - Second camera")
    print("  2 - Third camera")
    print("  path/to/video.mp4 - Video file")
    print("\nPress Enter to use default (0) or specify:")
    
    # Get user input
    user_input = input("Camera source [0]: ").strip()
    
    if user_input == "":
        source = 0
    elif user_input.isdigit():
        source = int(user_input)
    else:
        source = user_input  # Assume it's a file path
    
    # Create and run VR converter
    try:
        vr_converter = SimpleVRConverter(camera_source=source)
        vr_converter.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying with default camera...")
        vr_converter = SimpleVRConverter(camera_source=0)
        vr_converter.run()