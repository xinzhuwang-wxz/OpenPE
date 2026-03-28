"""Pipeline class for chaining processes together with true streaming"""

import threading
import queue
import io
from typing import List, Union
from .process import Process
from .streams import InputStream, OutputStream, ErrorStream
from .control_flow import ControlFlowException


class StreamingPipeline:
    """
    True streaming pipeline implementation

    Processes run in parallel threads with streaming I/O between them.
    This prevents memory exhaustion on large data sets.
    """

    def __init__(self, processes: List[Process]):
        """
        Initialize a streaming pipeline

        Args:
            processes: List of Process objects to chain together
        """
        self.processes = processes
        self.exit_codes = []
        self.threads = []
        self.pipes = []  # Queue-based pipes between processes

    def execute(self) -> int:
        """
        Execute the entire pipeline with true streaming

        All processes run in parallel threads, connected by queues.
        Data flows through the pipeline in chunks without full buffering.

        Returns:
            Exit code of the last process
        """
        if not self.processes:
            return 0

        # Special case: single process (no piping needed)
        if len(self.processes) == 1:
            return self.processes[0].execute()

        # Create pipes (queues) between processes
        self.pipes = [queue.Queue(maxsize=10) for _ in range(len(self.processes) - 1)]
        self.exit_codes = [None] * len(self.processes)

        # Create wrapper streams that read from/write to queues
        for i, process in enumerate(self.processes):
            # Set up stdin: read from previous process's queue
            if i > 0:
                process.stdin = StreamingInputStream(self.pipes[i - 1])

            # Set up stdout: write to next process's queue
            if i < len(self.processes) - 1:
                process.stdout = StreamingOutputStream(self.pipes[i])

        # Start all processes in parallel threads
        for i, process in enumerate(self.processes):
            thread = threading.Thread(
                target=self._execute_process,
                args=(i, process),
                name=f"Process-{i}-{process.command}"
            )
            thread.start()
            self.threads.append(thread)

        # Wait for all processes to complete
        for thread in self.threads:
            thread.join()

        # Return exit code of last process
        return self.exit_codes[-1] if self.exit_codes else 0

    def _execute_process(self, index: int, process: Process):
        """
        Execute a single process in a thread

        Args:
            index: Process index in the pipeline
            process: Process object to execute
        """
        try:
            exit_code = process.execute()
            self.exit_codes[index] = exit_code
        except KeyboardInterrupt:
            # Let KeyboardInterrupt propagate for proper Ctrl-C handling
            raise
        except ControlFlowException:
            # Let control flow exceptions propagate
            raise
        except Exception as e:
            process.stderr.write(f"Pipeline error: {e}\n")
            self.exit_codes[index] = 1
        finally:
            # Signal EOF to next process by properly closing stdout
            # This ensures any buffered data is flushed before EOF
            if index < len(self.processes) - 1:
                if isinstance(process.stdout, StreamingOutputStream):
                    process.stdout.close()  # flush remaining buffer and send EOF
                else:
                    self.pipes[index].put(None)  # EOF marker


class StreamingInputStream(InputStream):
    """Input stream that reads from a queue in chunks"""

    def __init__(self, pipe: queue.Queue):
        super().__init__(None)
        self.pipe = pipe
        self._buffer = io.BytesIO()
        self._eof = False

    def read(self, size: int = -1) -> bytes:
        """Read from the queue-based pipe"""
        if size == -1:
            # Read all available data
            chunks = []
            while not self._eof:
                chunk = self.pipe.get()
                if chunk is None:  # EOF
                    self._eof = True
                    break
                chunks.append(chunk)
            return b''.join(chunks)
        else:
            # Read specific number of bytes
            data = b''
            while len(data) < size and not self._eof:
                # Check if we have buffered data
                buffered = self._buffer.read(size - len(data))
                if buffered:
                    data += buffered
                    if len(data) >= size:
                        break

                # Get more data from queue
                chunk = self.pipe.get()
                if chunk is None:  # EOF
                    self._eof = True
                    break

                # Put in buffer
                self._buffer = io.BytesIO(chunk)

            return data

    def readline(self) -> bytes:
        """Read a line from the pipe"""
        line = []
        while not self._eof:
            byte = self.read(1)
            if not byte:
                break
            line.append(byte)
            if byte == b'\n':
                break
        return b''.join(line)

    def readlines(self) -> list:
        """Read all lines from the pipe"""
        lines = []
        while not self._eof:
            line = self.readline()
            if not line:
                break
            lines.append(line)
        return lines


class StreamingOutputStream(OutputStream):
    """Output stream that writes to a queue in chunks"""

    def __init__(self, pipe: queue.Queue, chunk_size: int = 8192):
        super().__init__(None)
        self.pipe = pipe
        self.chunk_size = chunk_size
        self._buffer = io.BytesIO()

    def write(self, data: Union[bytes, str]) -> int:
        """Write data to the queue-based pipe"""
        if isinstance(data, str):
            data = data.encode('utf-8')

        # Write to buffer
        self._buffer.write(data)

        # Flush chunks if buffer is large enough
        buffer_size = self._buffer.tell()
        if buffer_size >= self.chunk_size:
            self.flush()

        return len(data)

    def flush(self):
        """Flush buffered data to the queue"""
        self._buffer.seek(0)
        data = self._buffer.read()
        if data:
            self.pipe.put(data)
        self._buffer = io.BytesIO()

    def close(self):
        """Close the stream and flush remaining data"""
        self.flush()
        self.pipe.put(None)  # EOF marker


class Pipeline:
    """
    Hybrid pipeline implementation

    Uses streaming for pipelines that may have large data.
    Falls back to buffered execution for compatibility.
    """

    def __init__(self, processes: List[Process]):
        """
        Initialize a pipeline

        Args:
            processes: List of Process objects to chain together
        """
        self.processes = processes
        self.exit_codes = []
        self.use_streaming = len(processes) > 1  # Use streaming for multi-process pipelines

    def execute(self) -> int:
        """
        Execute the entire pipeline

        Automatically chooses between streaming and buffered execution.

        Returns:
            Exit code of the last process
        """
        if not self.processes:
            return 0

        # Use streaming pipeline for multi-process pipelines
        if self.use_streaming:
            streaming_pipeline = StreamingPipeline(self.processes)
            exit_code = streaming_pipeline.execute()
            self.exit_codes = streaming_pipeline.exit_codes
            return exit_code

        # Single process: execute directly (buffered)
        if not self.processes:
            return 0

        self.exit_codes = []

        # Execute processes in sequence, piping output to next input
        for i, process in enumerate(self.processes):
            # If this is not the first process, connect previous stdout to this stdin
            if i > 0:
                prev_process = self.processes[i - 1]
                prev_output = prev_process.get_stdout()
                process.stdin = InputStream.from_bytes(prev_output)

            # Execute the process
            exit_code = process.execute()
            self.exit_codes.append(exit_code)

        # Return exit code of last process
        return self.exit_codes[-1] if self.exit_codes else 0

    def get_stdout(self) -> bytes:
        """Get final stdout from the last process"""
        if not self.processes:
            return b''
        return self.processes[-1].get_stdout()

    def get_stderr(self) -> bytes:
        """Get combined stderr from all processes"""
        stderr_data = b''
        for process in self.processes:
            stderr_data += process.get_stderr()
        return stderr_data

    def get_exit_code(self) -> int:
        """Get exit code of the last process"""
        return self.exit_codes[-1] if self.exit_codes else 0

    def __repr__(self):
        pipeline_str = ' | '.join(str(p) for p in self.processes)
        return f"Pipeline({pipeline_str})"
