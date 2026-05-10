# `ros_nodes`

ROS 2 Python package for Tim's runtime nodes.

## Intended layout

- Node implementations live only in `ros_nodes/`.
- `setup.py` exposes each node as a ROS 2 console script.
- `launch/tim_bot.launch.py` is the canonical multi-node startup path.
- `start_all_nodes.sh` is a thin convenience wrapper around `ros2 launch`.

## Running

Build in a ROS 2 workspace with `colcon`, source the workspace, then launch:

```bash
ros2 launch ros_nodes tim_bot.launch.py start_ear:=true
```

For convenience, from this directory:

```bash
./start_all_nodes.sh
```

If your workspace setup file is not in a standard relative location, set `TIM_BOT_ROS_SETUP` before running:

```bash
TIM_BOT_ROS_SETUP=/path/to/install/setup.bash ./start_all_nodes.sh
```

## Notes

- Do not commit `venv/`, `build/`, `install/`, `log/`, or `.env` from this package.
- Prefer ROS parameters, launch arguments, and package entry points over direct `python file.py` execution.
