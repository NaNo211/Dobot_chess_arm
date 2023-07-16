import cv2
import numpy as np

class camera_cal:
    def __init__(self,img):
        self.img = img
        self.dict = {}
        self.inverse = {}
    def callibrate(self):
        # Define the number of inner corners (squares) in the chessboard
        num_corners_x = 7
        num_corners_y = 7

        # Initialize the object points, which are the coordinates of the chessboard corners in the real world
        object_points = np.zeros((num_corners_x * num_corners_y, 3), np.float32)
        object_points[:, :2] = np.mgrid[0:num_corners_x, 0:num_corners_y].T.reshape(-1, 2)

        # Initialize the arrays that will store the detected corners in the images
        object_points_list = []  # 3D points in real world space
        image_points_list = []  # 2D points in image plane

        # Load the chessboard images
        images = self.img
        # images = [cv2.imread(r'C:\Users\AAST\Desktop\chess _project_dont_touch\CameraCalibration 2\images/img12.png')]

        # Find the chessboard corners in each image
        for image in images:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, (num_corners_x, num_corners_y), None)

            # If the corners are found, add the object points and image points to the lists
            if ret:
                object_points_list.append(object_points)
                image_points_list.append(corners)

        # Calibrate the camera using the detected corners
        ret, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors = cv2.calibrateCamera(
            object_points_list, image_points_list, gray.shape[::-1], None, None
        )

        # Define the coordinate system for each corner in the chessboard
        square_size = 2.5  # The size of each square in centimeters
        chessboard_corners = np.zeros((num_corners_x * num_corners_y, 3), np.float32)
        chessboard_corners[:, :2] = np.mgrid[0:num_corners_x, 0:num_corners_y].T.reshape(-1, 2) * square_size

        # Transform the 2D image coordinates of each corner into 3D world coordinates
        for image, corners in zip(images, image_points_list):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            ret, rvecs, tvecs = cv2.solvePnP(chessboard_corners, corners, camera_matrix, distortion_coefficients)

            # Define the coordinate system for each corner
            for i in range(num_corners_x):
                for j in range(num_corners_y):
                    corner_3d = np.array([i * square_size, j * square_size, 0]).reshape(-1, 3)
                    corner_2d, _ = cv2.projectPoints(corner_3d,rvecs, tvecs, camera_matrix, distortion_coefficients)
                    # Transform the corner from the camera coordinate system to the world coordinate system
                    corner_3d_world = cv2.Rodrigues(rvecs)[0].T @ (corner_3d.T - tvecs)
                    # print(f'Corner ({i}, {j}): {corner_3d_world.squeeze()}')
                    self.dict[(i,j)] = corner_3d_world.squeeze()
                    self.inverse[(num_corners_x-i-1,num_corners_y-j-1)] = corner_3d_world.squeeze()
        return self.dict , self.inverse