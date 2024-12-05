from _assets.dlib_typing import _dlib_pybind11

from typing import Sequence, Tuple, Any
from itertools import combinations
from screeninfo import Monitor
from cv2 import VideoCapture
import numpy as np
import screeninfo
import dlib
import json
import cv2
import os


class GazeOTS:
    """
    ## Gaze Off-the-Shelf

    Object for calculating user gaze position. Utilizes shape predictor from dlib

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    def __init__(self) -> None:
        self.cwd = os.getcwd()
        self.cap: VideoCapture = cv2.VideoCapture(0)

        self.detector: _dlib_pybind11.fhog_object_detector = dlib.get_frontal_face_detector()
        self.predictor: _dlib_pybind11.shape_predictor = dlib.shape_predictor(os.path.join(self.cwd, '_assets/shape_predictor.dat'))

        # Screen properties
        screen: Monitor = screeninfo.get_monitors()[0]
        self.width: int = screen.width
        self.height: int = screen.height

        # Webcam properties
        webcam: Tuple[bool, Sequence] = self.cap.read()
        self.webcam_width: int = webcam[1].shape[1]
        self.webcam_height: int = webcam[1].shape[0]

        # Calibration dot
        self.dot_radius = round(max([self.width, self.height]) / 100)

        # Top left, top right, bottom left, bottom right, center points on screen (in px)
        self.calibration_points: Sequence[Tuple[int, int]] = [
            (self.dot_radius, self.dot_radius), 
            (self.width - self.dot_radius, self.dot_radius), 
            (self.dot_radius, self.height - self.dot_radius), 
            (self.width - self.dot_radius, self.height - self.dot_radius), 
            (self.width // 2, self.height // 2)
        ]

        # Initial gaze locatino
        self.gaze_x = 0
        self.gaze_y = 0

        self.run()
    
    def run(self) -> None:
        """
        ## Run

        Runs calibration sequence and creates display with live gaze tracking

        Parameters
        ----------
        None
        
        Returns
        -------
        None
            Runs method to display gaze tracking
        """
        calibration_files = os.listdir(os.path.join(self.cwd, '_assets/calibration_files'))
        predicted_file = f"s{self.width}_s{self.height}_w{self.webcam_width}_w{self.webcam_height}.json"

        if predicted_file in calibration_files:
            recalibrate = input("Do you want to recalibrate? (y/n): ")
            while recalibrate != "y" and recalibrate != "n":
                recalibrate = input("Please only enter y or n: ")
            if recalibrate == "y":
                recalibrate = True
            else:
                recalibrate = False
        
        if predicted_file in calibration_files and not recalibrate:
            with open(f"{os.path.join(self.cwd, '_assets/calibration_files/')}{predicted_file}", "r") as infile:
                calibration_dict = json.load(fp=infile)

            self.gaze_points = calibration_dict["gaze_points"]
            self.transform = np.array(calibration_dict["transform"])

        else:
            self.gaze_points = self.__calibrate()
            self.transform = self.average_trans
            calibration_dict = {
                "calibration_points": self.calibration_points,
                "gaze_points": self.gaze_points,
                "transform": [[float(x) for x in self.transform[0]], [float(x) for x in self.transform[1]]]
            }

            with open(f"{os.path.join(self.cwd, '_assets/calibration_files/')}s{self.width}_s{self.height}_w{self.webcam_width}_w{self.webcam_height}.json", "w") as outfile:
                json.dump(obj=calibration_dict, fp=outfile)

    def __calibrate(self) -> Sequence[Tuple[int, int]]:
        """
        ## Calibrate

        Calibrates for a given screen and webcam

        Parameters
        ----------
        None

        Returns
        -------
        Sequence[Tuple[int, int]]
            Recorded gaze points for known screen positions
        """
        # Black screen
        frame = np.zeros((self.height, self.width, 3))

        # Calibration window
        cv2.namedWindow("Calibration", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Calibration", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # Calculate scaling for display text (accounts for different display resolutions)
        line1_text = "Turn your head to stare at each dot for two seconds."
        line2_text = "Press spacebar to record calibration point."
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        font_thickness = font_scale * 2

        while True:
            text_size = cv2.getTextSize(text=line1_text, fontFace=font, fontScale=font_scale, thickness=font_thickness)[0]
            if self.width > text_size[0] > self.width * 0.75:
                break
            elif self.width < text_size[0]:
                font_scale -= 0.1
                font_thickness = round(font_scale * 2)
            elif self.width * 0.75 > text_size[0]:
                font_scale += 0.1
                font_thickness = round(font_scale * 2)

        # Set up display text
        line1_size = cv2.getTextSize(text=line1_text, fontFace=font, fontScale=font_scale, thickness=font_thickness)[0]
        line2_size = cv2.getTextSize(text=line2_text, fontFace=font, fontScale=font_scale, thickness=font_thickness)[0]

        line1_origin = (round(self.calibration_points[-1][0] - line1_size[0] / 2),
                        round(self.calibration_points[-1][1] - line1_size[1]))
        line2_origin = (round(self.calibration_points[-1][0] - line2_size[0] / 2),
                        round(self.calibration_points[-1][1] + line2_size[1]))
    
        # Collect points
        gaze_points = []
        for point in self.calibration_points:
            x, y = point
            frame = np.zeros((self.height, self.width, 3))

            cv2.putText(img=frame, text=line1_text, org=line1_origin, fontFace=font, fontScale=font_scale, 
                        color=(255, 255, 255), thickness=font_thickness, lineType=cv2.FILLED)
            cv2.putText(img=frame, text=line2_text, org=line2_origin, fontFace=font, fontScale=font_scale, 
                        color=(255, 255, 255), thickness=font_thickness, lineType=cv2.FILLED)
            
            cv2.circle(img=frame, center=(x, y), radius=self.dot_radius, color=(0, 255, 0), thickness=-1)            
            cv2.imshow("Calibration", frame)

            # Wait for user to capture image (spacebar)
            while True:
                _, webcam_frame = self.cap.read()
                webcam_frame = cv2.flip(webcam_frame, 1)

                key = cv2.waitKey(1) & 0xFF
                if key == 32:  # Spacebar
                    # Detect faces and eyes for gaze tracking
                    gray = cv2.cvtColor(webcam_frame, cv2.COLOR_BGR2GRAY)
                    faces = self.detector(gray)

                    for face in faces:
                        gaze_x, gaze_y = self.__gaze_location(frame=webcam_frame, gray=gray, face=face)

                        # Clamp bounds on screen
                        gaze_x = max(0, min(self.width - 1, gaze_x))
                        gaze_y = max(0, min(self.height - 1, gaze_y))

                        # Store gaze point
                        gaze_points.append((gaze_x, gaze_y))
                    break
                
                frame = np.zeros((self.height, self.width, 3))

            # Clear screen
            frame = np.zeros((self.height, self.width, 3))
            cv2.imshow("Calibration", frame)

        # Remove window
        cv2.destroyWindow("Calibration")
        return gaze_points

    def track_gaze(self) -> None:
        """
        ## Track Gaze

        Tracks user gaze and shows live results

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Create a black screen
        gaze_screen = np.zeros((self.height, self.width, 3))

        # Show gaze tracking
        cv2.namedWindow("Gaze Tracking", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Gaze Tracking", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while True:
            _, webcam_frame = self.cap.read()
            webcam_frame = cv2.flip(webcam_frame, 1)

            # Detect faces
            gray = cv2.cvtColor(webcam_frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)

            for face in faces:
                transformed_point = cv2.transform(np.array([[self.__gaze_location(frame=webcam_frame, gray=gray, face=face)]], \
                                                           dtype=np.float32), self.transform)
                gaze_x, gaze_y = transformed_point[0][0]
            
            gaze_screen = np.zeros((self.height, self.width, 3))

            # Draw dot at gaze location
            cv2.circle(gaze_screen, (round(gaze_x), round(gaze_y)), self.dot_radius, (0, 255, 0), -1)

            # Display gaze screen
            cv2.imshow("Gaze Tracking", gaze_screen)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

    def __gaze_location(self, frame: Sequence, gray: Sequence, face: Any) -> Tuple[int, int]:
        """
        ## Gaze Location

        Calculates gaze location from a frame, normalized frame, and face object

        Parameters
        ----------
        frame : Sequence
            Captured frame
        gray : Sequence
            Normalized frame
        face : Any
            Face object

        Returns
        -------
        Tuple[int, int]
            Gaze location in webcam reference frame
        """
        landmarks = self.predictor(gray, face)

        # Eye landmarks from dlib
        left_eye = landmarks.part(36), landmarks.part(39)
        right_eye = landmarks.part(42), landmarks.part(45)

        # Center of each eye
        left_eye_center = (((left_eye[0].x + left_eye[1].x) / 2), ((left_eye[0].y + left_eye[1].y) / 2))
        right_eye_center = (((right_eye[0].x + right_eye[1].x) / 2), ((right_eye[0].y + right_eye[1].y) / 2))

        # Average of centers
        face_center_x = ((left_eye_center[0] + right_eye_center[0]) / 2)
        face_center_y = ((left_eye_center[1] + right_eye_center[1]) / 2)

        # Map the eye center position to screen space
        gaze_x = round((face_center_x / frame.shape[1]) * self.width)
        gaze_y = round((face_center_y / frame.shape[0]) * self.height)

        return (gaze_x, gaze_y)

    def __calculate_transformation_matrix(self, calibration_points: Sequence[Tuple[int, int]], gaze_points: Sequence[Tuple[int, int]]) -> Sequence[Sequence[float]]:
        """
        ## Calculate Transformation Matrix

        Creates transformation matrix to map inputs to outputs.
        Note that inputs must be a matrix of shape 2 x 3.

        Parameters
        ----------
        calibration_points : Sequence[Tuple[int, int]]
            Known points displayed on screen
        gaze_points : Sequence[Tuple[int, int]]
            Known points from calibration sequence

        Returns
        -------
        Sequence[Sequence[float]]
            Transformation matrix
        """
        src_pts = np.array([list(x) for x in gaze_points], dtype=np.float32)
        dst_pts = np.array([list(x) for x in calibration_points], dtype=np.float32)

        # Affine transformation matrix
        matrix = cv2.getAffineTransform(src_pts, dst_pts)
        return matrix

    @property
    def gaze_location(self) -> Tuple[int, int]:
        """
        ## Gaze Location

        Attribute giving current gaze location

        Parameters
        ----------
        None

        Returns
        -------
        Tuple[int, int]
            Current gaze location in px
        """
        _, webcam_frame = self.cap.read()
        webcam_frame = cv2.flip(webcam_frame, 1)

        # Detect faces
        gray = cv2.cvtColor(webcam_frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        for face in faces:
            transformed_point = cv2.transform(np.array([[self.__gaze_location(frame=webcam_frame, gray=gray, face=face)]], \
                                                        dtype=np.float32), self.transform)
            gaze_x, gaze_y = transformed_point[0][0]

        if faces:
            self.gaze_x = gaze_x
            self.gaze_y = gaze_y
            return (gaze_x, gaze_y)
        
        else:
            return (self.gaze_x, self.gaze_y)
    
    @property
    def average_trans(self) -> Sequence:
        """
        ## Average Transformation Matrix

        Average transformation matrix for converting from snapshot resolution to display resolution

        Returns
        -------
        Sequence
            Average transformation matrix
        """
        # Converts from screen webcam snapshots to screen position
        calib_comb = list(combinations(iterable=self.calibration_points, r=3))
        gaze_comb = list(combinations(iterable=self.gaze_points, r=3))

        trans_mats = []
        
        try:
            for i in range(len(calib_comb)):
                trans_mat = self.__calculate_transformation_matrix(calibration_points=calib_comb[i], gaze_points=gaze_comb[i])
                trans_mats.append(trans_mat)

            average_trans_mat = sum(trans_mats) / len(trans_mats)
        except IndexError:
            raise Exception("Please check your lighting. There was an issue extracting facial features.")

        return average_trans_mat
    
if __name__ == "__main__":
    test_gaze = GazeOTS()
    test_gaze.track_gaze()
    while True:
        print(test_gaze.gaze_location, end="\r")