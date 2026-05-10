#!/bin/bash


#  source /opt/ros/humble/setup.bash
#    colcon build
#   source install/setup.bash
#  ros2 run ros_nodes ear_node

set -eo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACKAGE_NAME="ros_nodes"
LAUNCH_FILE="tim_bot.launch.py"
START_EAR="${START_EAR:-true}"

source_if_exists() {
  local setup_file="$1"
  if [[ -f "$setup_file" ]]; then
    # shellcheck disable=SC1090
    source "$setup_file"
    return 0
  fi
  return 1
}

if [[ -n "${TIM_BOT_ROS_SETUP:-}" ]]; then
  source_if_exists "$TIM_BOT_ROS_SETUP" || {
    echo "TIM_BOT_ROS_SETUP points to a missing file: $TIM_BOT_ROS_SETUP" >&2
    exit 1
  }
else
  source_if_exists "$ROOT_DIR/install/setup.bash" \
    || source_if_exists "$ROOT_DIR/../install/setup.bash" \
    || source_if_exists "$ROOT_DIR/install/setup.zsh" \
    || source_if_exists "$ROOT_DIR/../install/setup.zsh" \
    || true
fi

if ! command -v ros2 >/dev/null 2>&1; then
  echo "ros2 is not on PATH. Source your ROS 2 / workspace setup and rerun." >&2
  exit 1
fi

exec ros2 launch "$PACKAGE_NAME" "$LAUNCH_FILE" "start_ear:=$START_EAR"
