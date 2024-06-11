# Nicholas Moreland
# 1001886051

import numpy as np


class KalmanFilter(object):

    def __init__(self, x_initial, v_initial, dt, a_var, x_std, y_std):
        # Initial position and velocity
        self.a_var = a_var

        # Initial state variable
        self.x = np.matrix([[0], [0], [0], [0]])

        # Control variable
        self.u = np.matrix([[x_initial], [v_initial]])

        # Time step
        self.dt = dt

        # Initial state transition matrix
        self.A = np.matrix([[1, 0, self.dt, 0],
                           [0, 1, 0, self.dt],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])

        # Initial control matrix
        self.B = np.matrix([[(self.dt**2)/2, 0],
                            [0, (self.dt**2)/2],
                            [self.dt, 0],
                            [0, self.dt]])

        # Initial transition matrix
        self.H = np.matrix([[1, 0, 0, 0],
                            [0, 1, 0, 0]])

        # Initial Process Noise Covariance
        self.Q = np.matrix([[(self.dt**4)/4, 0, (self.dt**3)/2, 0],
                            [0, (self.dt**4)/4, 0, (self.dt**3)/2],
                            [(self.dt**3)/2, 0, self.dt**2, 0],
                            [0, (self.dt**3)/2, 0, self.dt**2]]) * a_var**2

        # Initial Measurement Noise Covariance
        self.R = np.matrix([[x_std**2, 0],
                           [0, y_std**2]])

        # Covariance Matrix
        self.P = np.identity(self.A.shape[1])

    # Predict the state
    def predict(self):
        # x_k = A_kx*x+_k-1 + B_k*u_k
        x_new = np.dot(self.A, self.x) + np.dot(self.B, self.u)

        # sigma_k = A_k * P+_k-1 * (A_k)^T + Q
        P_new = np.dot(np.dot(self.A, self.P), self.A.T) + self.Q

        # Update the state
        self.P = P_new
        self.x = x_new

        # Return the predicted state
        return self.x[0:2]

    # Update the state
    def update(self, z):
        # S = HPH' + R
        S = self.H * self.P * self.H.T + self.R

        # K = PH'inv(S)
        K = self.P * self.H.T * np.linalg.pinv(S)

        # x = x + Ky
        x_update = self.x + K*(z - (self.H*self.x))

        # P = (I-KH)P
        P_update = (np.identity(self.H.shape[1]) - K*self.H)*self.P

        # Update the state
        self.P = P_update
        self.x = x_update

        # Return the updated state
        return self.x[0]
