cmake_minimum_required(VERSION 3.0.2)
project(thmho_ngsi_converter_bringup)

find_package(catkin REQUIRED COMPONENTS
  rospy
)

catkin_package(
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)