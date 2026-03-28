import unittest
import tempfile
import os
from unittest.mock import Mock, MagicMock
from agfs_shell.builtins import BUILTINS
from agfs_shell.process import Process
from agfs_shell.streams import InputStream, OutputStream, ErrorStream

class TestBuiltins(unittest.TestCase):
    def create_process(self, command, args, input_data=""):
        stdin = InputStream.from_string(input_data)
        stdout = OutputStream.to_buffer()
        stderr = ErrorStream.to_buffer()
        return Process(command, args, stdin, stdout, stderr)

    def test_echo(self):
        cmd = BUILTINS['echo']
        
        # Test basic echo
        proc = self.create_process("echo", ["hello", "world"])
        self.assertEqual(cmd(proc), 0)
        self.assertEqual(proc.get_stdout(), b"hello world\n")

        # Test empty echo
        proc = self.create_process("echo", [])
        self.assertEqual(cmd(proc), 0)
        self.assertEqual(proc.get_stdout(), b"\n")

    def test_cat_stdin(self):
        cmd = BUILTINS['cat']
        input_data = "line1\nline2\n"
        proc = self.create_process("cat", [], input_data)
        self.assertEqual(cmd(proc), 0)
        self.assertEqual(proc.get_stdout(), input_data.encode('utf-8'))

    def test_cat_file(self):
        cmd = BUILTINS['cat']
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test.txt")
            with open(filename, "w") as f:
                f.write("file content")
            
            proc = self.create_process("cat", [filename])
            self.assertEqual(cmd(proc), 0)
            self.assertEqual(proc.get_stdout(), b"file content")

    def test_grep(self):
        cmd = BUILTINS['grep']
        input_data = "apple\nbanana\ncherry\n"
        
        # Match found
        proc = self.create_process("grep", ["pp"], input_data)
        self.assertEqual(cmd(proc), 0)
        self.assertEqual(proc.get_stdout(), b"apple\n")

        # No match
        proc = self.create_process("grep", ["xyz"], input_data)
        self.assertEqual(cmd(proc), 1)
        self.assertEqual(proc.get_stdout(), b"")

        # Missing pattern
        proc = self.create_process("grep", [], input_data)
        self.assertEqual(cmd(proc), 2)
        self.assertIn(b"missing pattern", proc.get_stderr())

    def test_wc(self):
        cmd = BUILTINS['wc']
        input_data = "one two\nthree\n"
        # 2 lines, 3 words, 14 bytes
        
        # Default (all)
        proc = self.create_process("wc", [], input_data)
        self.assertEqual(cmd(proc), 0)
        self.assertEqual(proc.get_stdout(), b"2 3 14\n")

        # Lines only
        proc = self.create_process("wc", ["-l"], input_data)
        self.assertEqual(cmd(proc), 0)
        self.assertEqual(proc.get_stdout(), b"2\n")

    def test_head(self):
        cmd = BUILTINS['head']
        input_data = "\n".join([f"line{i}" for i in range(20)]) + "\n"
        
        # Default 10 lines
        proc = self.create_process("head", [], input_data)
        self.assertEqual(cmd(proc), 0)
        output = proc.get_stdout().decode('utf-8').splitlines()
        self.assertEqual(len(output), 10)
        self.assertEqual(output[0], "line0")
        self.assertEqual(output[-1], "line9")

        # Custom lines
        proc = self.create_process("head", ["-n", "5"], input_data)
        self.assertEqual(cmd(proc), 0)
        output = proc.get_stdout().decode('utf-8').splitlines()
        self.assertEqual(len(output), 5)

    def test_tail(self):
        cmd = BUILTINS['tail']
        input_data = "\n".join([f"line{i}" for i in range(20)]) + "\n"
        
        # Default 10 lines
        proc = self.create_process("tail", [], input_data)
        self.assertEqual(cmd(proc), 0)
        output = proc.get_stdout().decode('utf-8').splitlines()
        self.assertEqual(len(output), 10)
        self.assertEqual(output[0], "line10")
        self.assertEqual(output[-1], "line19")

    def test_sort(self):
        cmd = BUILTINS['sort']
        input_data = "c\na\nb\n"
        
        # Normal sort
        proc = self.create_process("sort", [], input_data)
        self.assertEqual(cmd(proc), 0)
        self.assertEqual(proc.get_stdout(), b"a\nb\nc\n")

        # Reverse sort
        proc = self.create_process("sort", ["-r"], input_data)
        self.assertEqual(cmd(proc), 0)
        self.assertEqual(proc.get_stdout(), b"c\nb\na\n")

    def test_uniq(self):
        cmd = BUILTINS['uniq']
        input_data = "a\na\nb\nb\nc\n"
        
        proc = self.create_process("uniq", [], input_data)
        self.assertEqual(cmd(proc), 0)
        self.assertEqual(proc.get_stdout(), b"a\nb\nc\n")

    def test_tr(self):
        cmd = BUILTINS['tr']
        input_data = "hello"
        
        # Translate
        proc = self.create_process("tr", ["el", "ip"], input_data)
        self.assertEqual(cmd(proc), 0)
        self.assertEqual(proc.get_stdout(), b"hippo")

        # Error cases
        proc = self.create_process("tr", ["a"], input_data)
        self.assertEqual(cmd(proc), 1)
        self.assertIn(b"missing operand", proc.get_stderr())

    def test_ls_multiple_files(self):
        """Test ls command with multiple file arguments (like from glob expansion)"""
        cmd = BUILTINS['ls']

        # Create a mock filesystem
        mock_fs = Mock()

        # Mock get_file_info to return file info for each path
        def mock_get_file_info(path):
            # Simulate file metadata
            if path.endswith('.txt'):
                return {
                    'name': os.path.basename(path),
                    'isDir': False,
                    'size': 100,
                    'modTime': '2025-11-23T12:00:00Z',
                    'mode': 'rw-r--r--'
                }
            else:
                raise Exception(f"No such file: {path}")

        mock_fs.get_file_info = mock_get_file_info

        # Test with multiple file paths (simulating glob expansion like 'ls *.txt')
        proc = self.create_process("ls", [
            "/test/file1.txt",
            "/test/file2.txt",
            "/test/file3.txt"
        ])
        proc.filesystem = mock_fs

        exit_code = cmd(proc)
        self.assertEqual(exit_code, 0)

        # Check output contains all files
        output = proc.get_stdout().decode('utf-8')
        self.assertIn('file1.txt', output)
        self.assertIn('file2.txt', output)
        self.assertIn('file3.txt', output)

        # Verify each file listed once
        self.assertEqual(output.count('file1.txt'), 1)
        self.assertEqual(output.count('file2.txt'), 1)
        self.assertEqual(output.count('file3.txt'), 1)

    def test_ls_mixed_files_and_dirs(self):
        """Test ls command with mix of files and directories"""
        cmd = BUILTINS['ls']

        # Create a mock filesystem
        mock_fs = Mock()

        # Mock get_file_info to return file/dir info
        def mock_get_file_info(path):
            if path == "/test/dir1":
                return {
                    'name': 'dir1',
                    'isDir': True,
                    'size': 0,
                    'modTime': '2025-11-23T12:00:00Z'
                }
            elif path.endswith('.txt'):
                return {
                    'name': os.path.basename(path),
                    'isDir': False,
                    'size': 100,
                    'modTime': '2025-11-23T12:00:00Z'
                }
            else:
                raise Exception(f"No such file: {path}")

        # Mock list_directory for the directory
        def mock_list_directory(path):
            if path == "/test/dir1":
                return [
                    {'name': 'subfile1.txt', 'isDir': False, 'size': 50},
                    {'name': 'subfile2.txt', 'isDir': False, 'size': 60}
                ]
            else:
                raise Exception(f"Not a directory: {path}")

        mock_fs.get_file_info = mock_get_file_info
        mock_fs.list_directory = mock_list_directory

        # Test with mix of file and directory
        proc = self.create_process("ls", [
            "/test/file1.txt",
            "/test/dir1"
        ])
        proc.filesystem = mock_fs

        exit_code = cmd(proc)
        self.assertEqual(exit_code, 0)

        # Check output
        output = proc.get_stdout().decode('utf-8')
        # File should be listed
        self.assertIn('file1.txt', output)
        # Directory contents should be listed
        self.assertIn('subfile1.txt', output)
        self.assertIn('subfile2.txt', output)

    def test_rm_with_glob_pattern(self):
        """Test rm command with glob pattern (simulating shell glob expansion)"""
        cmd = BUILTINS['rm']

        # Create a mock filesystem
        mock_fs = Mock()
        mock_client = Mock()
        mock_fs.client = mock_client

        # Track which files were deleted
        deleted_files = []

        def mock_rm(path, recursive=False):
            deleted_files.append((path, recursive))

        mock_client.rm = mock_rm

        # Test rm with multiple files (simulating glob expansion of '23_11_2025*')
        # This simulates what should happen when the shell expands the glob pattern
        proc = self.create_process("rm", [
            "/test/23_11_2025_11_43_05.wav",
            "/test/23_11_2025_11_43_36.wav",
            "/test/23_11_2025_11_44_11.wav"
        ])
        proc.filesystem = mock_fs

        exit_code = cmd(proc)
        self.assertEqual(exit_code, 0)

        # Verify all files were deleted
        self.assertEqual(len(deleted_files), 3)
        self.assertIn(('/test/23_11_2025_11_43_05.wav', False), deleted_files)
        self.assertIn(('/test/23_11_2025_11_43_36.wav', False), deleted_files)
        self.assertIn(('/test/23_11_2025_11_44_11.wav', False), deleted_files)

    def test_cp_with_glob_pattern(self):
        """Test cp command with glob pattern (simulating shell glob expansion)"""
        cmd = BUILTINS['cp']

        # Create a mock filesystem
        mock_fs = Mock()

        # Track which files were copied
        copied_files = []

        def mock_read_file(path, stream=False):
            return b"file contents"

        def mock_write_file(path, data, append=False):
            copied_files.append((path, data))

        def mock_get_file_info(path):
            # Mock /dest/ as a directory
            if path == '/dest' or path == '/dest/':
                return {'name': 'dest', 'isDir': True, 'size': 0}
            # Mock source files as regular files
            return {'name': os.path.basename(path), 'isDir': False, 'size': 100}

        mock_fs.read_file = mock_read_file
        mock_fs.write_file = mock_write_file
        mock_fs.get_file_info = mock_get_file_info

        # Test cp with multiple source files (simulating glob expansion like 'cp *.txt /dest/')
        proc = self.create_process("cp", [
            "/test/file1.txt",
            "/test/file2.txt",
            "/test/file3.txt",
            "/dest/"
        ])
        proc.filesystem = mock_fs
        proc.cwd = "/test"

        exit_code = cmd(proc)
        self.assertEqual(exit_code, 0)

        # Verify all files were copied
        self.assertEqual(len(copied_files), 3)

        # Check that the destination paths are correct
        copied_paths = [path for path, _ in copied_files]
        self.assertIn('/dest/file1.txt', copied_paths)
        self.assertIn('/dest/file2.txt', copied_paths)
        self.assertIn('/dest/file3.txt', copied_paths)

    def test_cp_with_local_prefix(self):
        """Test cp command with local: prefix to ensure it doesn't get path-resolved"""
        import tempfile
        import shutil

        cmd = BUILTINS['cp']

        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()

        try:
            # Create a mock filesystem
            mock_fs = Mock()

            def mock_read_file(path, stream=False):
                if stream:
                    # Return an iterable of chunks
                    return [b"file contents chunk 1", b"file contents chunk 2"]
                return b"file contents"

            def mock_get_file_info(path):
                return {'name': os.path.basename(path), 'isDir': False, 'size': 100}

            mock_fs.read_file = mock_read_file
            mock_fs.get_file_info = mock_get_file_info

            # Test download: cp <agfs_path> local:./
            # The local:./ should be resolved to current directory, not treated as AGFS path
            proc = self.create_process("cp", [
                "/s3fs/test/file.wav",
                f"local:{temp_dir}/"
            ])
            proc.filesystem = mock_fs
            proc.cwd = "/s3fs/aws/dongxu/omi-recording/raw/2025/11/23/16"

            exit_code = cmd(proc)
            self.assertEqual(exit_code, 0)

            # Verify file was downloaded to local directory
            downloaded_file = os.path.join(temp_dir, "file.wav")
            self.assertTrue(os.path.exists(downloaded_file))

        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir)

    def test_date(self):
        """Test date command calls system date and returns output"""
        cmd = BUILTINS['date']

        # Test basic date command (no arguments)
        proc = self.create_process("date", [])
        exit_code = cmd(proc)
        self.assertEqual(exit_code, 0)

        # Output should contain date/time information (not empty)
        output = proc.get_stdout().decode('utf-8')
        self.assertTrue(len(output) > 0)

        # Test date with format argument
        proc = self.create_process("date", ["+%Y"])
        exit_code = cmd(proc)
        self.assertEqual(exit_code, 0)

        # Should return current year (4 digits + newline)
        output = proc.get_stdout().decode('utf-8').strip()
        self.assertTrue(output.isdigit())
        self.assertEqual(len(output), 4)

if __name__ == '__main__':
    unittest.main()
