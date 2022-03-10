#!/usr/bin/env python3
import rospy
from nav_msgs.msg import OccupancyGrid
from scipy.sparse import csr_matrix
import numpy as np
import requests
import time
from datetime import datetime
import sys


class HeatmapSaver():
    """API to save the Occupancy grid messages to mongoDB 
    """
    def __init__(self):
        self.urlsparse = 'http://localhost:5000/insert'
        self.heatmap_subscriber = rospy.Subscriber(
            "/costmap_generator/costmap/costmap", OccupancyGrid, self.save_heatmap)
        costmap = rospy.wait_for_message("/map", OccupancyGrid, timeout=100)
        self.width = costmap.info.width
        self.height = costmap.info.height
        self.size = (self.height, self.width)
        self.mask = np.array(costmap.data).reshape(self.size).astype(bool)
        self.mask = (~self.mask).astype(int)
        self.mask = csr_matrix(self.mask)
        body = {
            'name': 'base_mask',
            'width': self.width,
            'height': self.height,
            'indices': self.mask.indices.tolist(),
            'indptr': self.mask.indptr.tolist(),
        }
        requests.post(self.urlsparse, json=body)
        self.mask = self.mask.toarray()

    def save_heatmap(self, msg):
        """Send OccupancyGrid message via Flask endpoint

        Args:
            msg (OccupancyGrid): OccupancyGrid
        """
        data = np.array(msg.data).reshape(self.size)
        try:
            masked_data = csr_matrix(data * self.mask)
            date = datetime.now().isoformat()
            body_csr = {
                'date': date,
                'indices': masked_data.indices.tolist(),
                'indptr': masked_data.indptr.tolist(),
            }
            requests.post(self.urlsparse, json=body_csr)
            print(f"Inserted registry at {date}")
        except Exception as e:
            print(e)


if __name__ == '__main__':
    rospy.init_node('heatmap_saver', anonymous=True)
    heatmap = HeatmapSaver()
    time.sleep(5)
    rospy.spin()
