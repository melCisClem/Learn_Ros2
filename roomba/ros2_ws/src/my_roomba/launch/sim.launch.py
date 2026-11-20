import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('my_roomba')

    # Read the robot description file into a string
    with open(os.path.join(pkg, 'urdf', 'roomba.urdf')) as f:
        robot_description = f.read()

    # 1. Start Gazebo with our room (-r = start running, not paused)
    world = os.path.join(pkg, 'worlds', 'test_room.sdf')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': f'-r {world}'}.items(),
    )

    # 2. Publish the robot description + the fixed parts of the TF tree
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
        output='screen',
    )

    # 3. Put the robot into Gazebo
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_roomba', '-z', '0.06'],
        output='screen',
    )

    # 4. Connect Gazebo topics <-> ROS topics
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(pkg, 'config', 'bridge.yaml'),
            'use_sim_time': True,
        }],
        output='screen',
    )

    return LaunchDescription([gazebo, robot_state_publisher, spawn, bridge])