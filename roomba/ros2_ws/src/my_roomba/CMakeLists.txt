cmake_minimum_required(VERSION 3.8)
project(my_roomba)

find_package(ament_cmake REQUIRED)

# Copy these folders into the install space so launch files can find them
install(DIRECTORY launch urdf config worlds
  DESTINATION share/${PROJECT_NAME})

ament_package()