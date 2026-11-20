# Roomba (ROS 2 Jazzy + Gazebo)

A simulated roomba in a small room: differential drive, a 360° lidar, and a
node that wanders around and avoids obstacles.

## What's in here

```
roomba/
├── Dockerfile / compose.yaml      # ROS 2 Jazzy + Gazebo + Nav2 + SLAM container
└── ros2_ws/src/
    ├── my_roomba/                 # the robot + world
    │   ├── urdf/roomba.urdf       # robot body, wheels, lidar, Gazebo plugins
    │   ├── worlds/test_room.sdf   # the room (4 walls + a box)
    │   ├── config/bridge.yaml     # Gazebo <-> ROS topic bridge
    │   └── launch/sim.launch.py   # starts everything
    └── roomba_brain/              # Python package
        └── roomba_brain/wanderer.py   # drives using /scan -> /cmd_vel
```

## 0. Work inside WSL

Run every command in this guide in a **WSL (Ubuntu) terminal**, not PowerShell. The real
project lives in the WSL filesystem, and the container mounts it from there:

```
/Learn_Ros2/roomba/ros2_ws   ->   /ros2_ws  (inside the container)
```

Open a WSL terminal: start **Ubuntu** from the Start menu, or run `wsl` in PowerShell.

Open VS Code in WSL:

```bash
cd ~/Learn_Ros2
code .
```

The first time, VS Code installs its WSL server. You need the **WSL** extension
(by Microsoft) on the Windows side. The bottom-left corner of the window should show
`WSL: Ubuntu`. If it doesn't, press `Ctrl+Shift+P` and run **WSL: Reopen Folder in WSL**.
The integrated terminal (`Ctrl+\``) then is a WSL terminal, so you can run every command below there.

Docker Desktop must be running, with WSL integration enabled for your distro
(Docker Desktop -> Settings -> Resources -> WSL integration).

## 1. Start the container

In the WSL terminal, from the `roomba/` folder (`cd ~/Learn_Ros2/roomba`):

```bash
docker compose up -d --build     # first time (or after changing the Dockerfile)
docker exec -it roomba bash      # open a shell inside
```

Every extra terminal needs its own `docker exec -it roomba bash`.
On Windows/WSL, delete the `/dev/dri` lines in `compose.yaml` if they cause errors.

## 2. Build (inside the container)

```bash
cd /ros2_ws
colcon build --symlink-install
source install/setup.bash
```

Re-run `source install/setup.bash` in every new terminal.

## 3. Run the simulation

Terminal 1, the sim (Gazebo + bridge + robot):

```bash
ros2 launch my_roomba sim.launch.py
```

Terminal 2, the wanderer:

```bash
ros2 run roomba_brain wanderer
```

Manual driving instead of the wanderer:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## 4. Check it works

```bash
ros2 topic list            # expect /scan /odom /cmd_vel /tf /joint_states /clock
ros2 topic hz /scan        # ~10 Hz
ros2 topic echo /cmd_vel   # what the wanderer is sending
rviz2                      # fixed frame = odom; add LaserScan (/scan), RobotModel, TF
```

## Do I need to rebuild?

Because we build with `--symlink-install`:

| Change | What to do |
|---|---|
| Edit `wanderer.py` | Ctrl+C, then `ros2 run roomba_brain wanderer` |
| Edit `test_room.sdf`, `roomba.urdf`, `bridge.yaml` | Ctrl+C, then `ros2 launch my_roomba sim.launch.py` |
| Add a new file, node, or edit `setup.py`, `package.xml`, `CMakeLists.txt` | `cd /ros2_ws && colcon build --symlink-install && source install/setup.bash`, then run the node/launch again |

## Common edits

- **Room size:** for a room `S` metres across, north/south walls sit at `y = ±S/2`
  with size `S+0.1 x 0.1`; east/west at `x = ±S/2` with size `0.1 x S+0.1`.
  Change both `<collision>` and `<visual>` sizes. Keep the room above ~2 m.
- **Box position:** the `box` link's `<pose>` in `test_room.sdf` (`x y z roll pitch yaw`).
  The roomba spawns at `(0, 0)` facing +x, so `1 0 0.2` puts it directly ahead.
- **Wanderer tuning:** parameters `stop_distance`, `forward_speed`, `turn_speed`,
  `front_half_angle`, for example:
  `ros2 param set /wanderer stop_distance 0.6`

## Troubleshooting

- **`/scan` missing from `ros2 topic list`:** check each entry in `config/bridge.yaml`
  starts with `- ` (a missing dash silently merges it into the previous entry), then
  relaunch. Also confirm the world has the Sensors plugin (`ogre2`) and the sim is not paused.
- **`NameError: qos_profile_sensor_data`:** add `from rclpy.qos import qos_profile_sensor_data`.
- **Subscriber never fires on `/scan`:** QoS mismatch. Use `qos_profile_sensor_data`.
- **`ros2 topic list` empty in a new terminal:** you are not inside the container
  (`docker exec -it roomba bash`), or you forgot to source the workspace.
- **Code isn't in your Windows checkout:** the container mounts the WSL copy
  (`/home/clem/Learn_Ros2/roomba/ros2_ws`). Edit and commit from there (see section 0).
- **`code .` not found in WSL:** install VS Code on Windows and the WSL extension, then
  reopen the WSL terminal.
- **`docker: command not found` in WSL:** start Docker Desktop and enable WSL integration.
