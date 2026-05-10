import audioop
import os
import select
import sys
import tempfile
import threading
import time
from typing import Optional
import wave

import pyaudio
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from ros_nodes.gpt import strigalize_verb


# just vibecoded the new TTS, need to test it. will throw error in docker container.


class EarNode(Node):
    def __init__(self):
        super().__init__("ear_node")
        self.user_command_pub = self.create_publisher(String, "/user_command", 10)
        self._running = True
        self._stdin_is_tty = sys.stdin.isatty()
        self._prompt_needs_render = True
        self._audio = None
        self._sample_rate = int(os.getenv("TIM_BOT_MIC_SAMPLE_RATE", "16000"))
        self._chunk_size = int(os.getenv("TIM_BOT_MIC_CHUNK_SIZE", "1024"))
        self._channels = 1
        self._sample_width = 2
        self._start_threshold = int(os.getenv("TIM_BOT_MIC_START_THRESHOLD", "700"))
        self._silence_threshold = int(os.getenv("TIM_BOT_MIC_SILENCE_THRESHOLD", "500"))
        self._silence_seconds = float(os.getenv("TIM_BOT_MIC_SILENCE_SECONDS", "1.2"))
        self._max_record_seconds = float(os.getenv("TIM_BOT_MIC_MAX_RECORD_SECONDS", "8.0"))

        self.get_logger().info("EarNode initiated.")
        if self._stdin_is_tty:
            self.get_logger().info("Type commands and press Enter. Ctrl+C to quit.")
            self.input_thread = threading.Thread(target=self._read_terminal_loop, name="ear-stdin")
            self.input_thread.start()
        else:
            self.input_thread = None
            self.get_logger().warn(
                "stdin is not interactive; publish to /user_command or run `ros2 run ros_nodes ear_node`."
            )

    def _publish_user_command(self, text: str) -> None:
        msg = String()
        msg.data = text
        self.user_command_pub.publish(msg)
        self.get_logger().info(f"Published user_command_text: {text}")

    def _open_mic_stream(self):
        if self._audio is None:
            self._audio = pyaudio.PyAudio()
        return self._audio.open(
            format=pyaudio.paInt16,
            channels=self._channels,
            rate=self._sample_rate,
            input=True,
            frames_per_buffer=self._chunk_size,
        )

    def _record_microphone_command(self) -> Optional[str]:
        stream = self._open_mic_stream()
        frames = []
        heard_speech = False
        silent_chunks = 0
        max_chunks = max(1, int(self._max_record_seconds * self._sample_rate / self._chunk_size))
        silence_limit = max(1, int(self._silence_seconds * self._sample_rate / self._chunk_size))

        self.get_logger().info("Listening for spoken command...")

        try:
            for _ in range(max_chunks):
                if not self._running or not rclpy.ok():
                    return None

                chunk = stream.read(self._chunk_size, exception_on_overflow=False)
                level = audioop.rms(chunk, self._sample_width)

                if not heard_speech:
                    if level < self._start_threshold:
                        continue
                    heard_speech = True

                frames.append(chunk)
                if level < self._silence_threshold:
                    silent_chunks += 1
                else:
                    silent_chunks = 0

                if silent_chunks >= silence_limit:
                    break
        finally:
            stream.stop_stream()
            stream.close()

        if not frames:
            return None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_path = temp_audio.name

        try:
            with wave.open(temp_path, "wb") as wav_file:
                wav_file.setnchannels(self._channels)
                wav_file.setsampwidth(self._sample_width)
                wav_file.setframerate(self._sample_rate)
                wav_file.writeframes(b"".join(frames))
            transcript = strigalize_verb(temp_path).strip()
            return transcript or None
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def listen_from_microphone(self) -> Optional[str]:
        try:
            text = self._record_microphone_command()
        except Exception as exc:
            self.get_logger().error(f"Microphone capture failed: {exc}")
            return None

        if not text:
            return None

        self._publish_user_command(text)
        return text

    def _read_terminal_loop(self):
        while self._running and rclpy.ok():
            try:
                if self._prompt_needs_render:
                    print("Command for TIM: > ", end="", flush=True)
                    self._prompt_needs_render = False

                ready, _, _ = select.select([sys.stdin], [], [], 0.2)
                if not ready:
                    continue

                text = sys.stdin.readline()
            except EOFError:
                break
            except OSError:
                break

            if not text:
                time.sleep(0.1)
                continue

            text = text.strip()
            self._prompt_needs_render = True

            if not text:
                continue

            self._publish_user_command(text)

    def destroy_node(self):
        self._running = False
        if self.input_thread is not None and self.input_thread.is_alive():
            self.input_thread.join(timeout=1.0)
        if self._audio is not None:
            self._audio.terminate()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = EarNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
