import React, { useState, useEffect, useRef } from 'react';
import FileTree from './components/FileTree';
import Editor from './components/Editor';
import Terminal from './components/Terminal';
import MenuBar from './components/MenuBar';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [savedContent, setSavedContent] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [currentPath, setCurrentPath] = useState('/');
  const [currentDirectory, setCurrentDirectory] = useState('/');
  const [sidebarWidth, setSidebarWidth] = useState(250);
  const [terminalHeight, setTerminalHeight] = useState(250);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [showNewFileDialog, setShowNewFileDialog] = useState(false);
  const wsRef = useRef(null);
  const editorRef = useRef(null);
  const fileInputRef = useRef(null);
  const isResizingSidebar = useRef(false);
  const isResizingTerminal = useRef(false);

  // Check if file is a text file based on extension
  const isTextFile = (filename) => {
    const textExtensions = [
      'txt', 'md', 'json', 'xml', 'html', 'css', 'js', 'jsx', 'ts', 'tsx',
      'py', 'java', 'c', 'cpp', 'h', 'hpp', 'cs', 'php', 'rb', 'go', 'rs',
      'sh', 'bash', 'yaml', 'yml', 'toml', 'ini', 'cfg', 'conf',
      'sql', 'log', 'csv', 'tsv', 'svg', 'vue', 'scss', 'sass', 'less',
      'gitignore', 'dockerfile', 'makefile', 'readme'
    ];

    const ext = filename.split('.').pop().toLowerCase();
    return textExtensions.includes(ext) || !filename.includes('.');
  };

  const handleFileSelect = async (file) => {
    // Update current directory based on selected item
    if (file.type === 'directory') {
      setCurrentDirectory(file.path);
    } else {
      // For files, set current directory to parent directory
      const parentDir = file.path.substring(0, file.path.lastIndexOf('/')) || '/';
      setCurrentDirectory(parentDir);
    }

    if (file.type === 'file') {
      // Check if it's a text file
      if (!isTextFile(file.name)) {
        // Non-text file, trigger download
        const downloadUrl = `/api/files/download?path=${encodeURIComponent(file.path)}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = file.name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        return;
      }

      // Text file, display in editor
      setSelectedFile(file);
      // Fetch file content from API
      try {
        const response = await fetch(`/api/files/read?path=${encodeURIComponent(file.path)}`);
        const data = await response.json();
        const content = data.content || '';
        setFileContent(content);
        setSavedContent(content);
        setHasUnsavedChanges(false);
      } catch (error) {
        console.error('Error reading file:', error);
        setFileContent('');
        setSavedContent('');
        setHasUnsavedChanges(false);
      }
    }
  };

  const handleContentChange = (content) => {
    setFileContent(content);
    setHasUnsavedChanges(content !== savedContent);
  };

  const handleFileSave = async (content) => {
    if (!selectedFile) return;

    try {
      const response = await fetch('/api/files/write', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          path: selectedFile.path,
          content: content,
        }),
      });

      if (response.ok) {
        // Update saved content and reset unsaved changes flag
        setSavedContent(content);
        setHasUnsavedChanges(false);
      } else {
        console.error('Error saving file:', await response.text());
      }
    } catch (error) {
      console.error('Error saving file:', error);
    }
  };

  const handleNewFile = async (filePath) => {
    try {
      // Create empty file
      await fetch('/api/files/write', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          path: filePath,
          content: '',
        }),
      });

      // Select the newly created file
      const fileName = filePath.split('/').pop();
      setSelectedFile({
        name: fileName,
        path: filePath,
        type: 'file'
      });
      setFileContent('');
      setSavedContent('');
      setHasUnsavedChanges(false);

      // Trigger file tree refresh
      setRefreshTrigger(prev => prev + 1);
    } catch (error) {
      console.error('Error creating file:', error);
      alert('Failed to create file: ' + error.message);
    }
  };

  const handleMenuSave = () => {
    if (editorRef.current) {
      editorRef.current.save();
    }
  };

  const handleUpload = async (files) => {
    if (!files || files.length === 0) return;

    let successCount = 0;
    let failCount = 0;

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('directory', currentDirectory);

        const response = await fetch('/api/files/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const data = await response.json();
          alert(`Failed to upload ${file.name}: ${data.error}`);
          failCount++;
        } else {
          successCount++;
        }
      } catch (error) {
        alert(`Failed to upload ${file.name}: ${error.message}`);
        failCount++;
      }
    }

    // Trigger a refresh of the file tree
    if (successCount > 0) {
      setRefreshTrigger(prev => prev + 1);
    }

    alert(`Uploaded ${successCount} file(s) to ${currentDirectory}${failCount > 0 ? ` (${failCount} failed)` : ''}`);
  };

  // Handle sidebar resize
  const handleSidebarMouseDown = (e) => {
    isResizingSidebar.current = true;
    e.preventDefault();
  };

  const handleMouseMove = (e) => {
    if (isResizingSidebar.current) {
      const newWidth = e.clientX;
      if (newWidth >= 150 && newWidth <= 600) {
        setSidebarWidth(newWidth);
      }
    }
    if (isResizingTerminal.current) {
      const newHeight = window.innerHeight - e.clientY;
      if (newHeight >= 100 && newHeight <= window.innerHeight - 200) {
        setTerminalHeight(newHeight);
      }
    }
  };

  const handleMouseUp = () => {
    isResizingSidebar.current = false;
    isResizingTerminal.current = false;
  };

  // Handle terminal resize
  const handleTerminalMouseDown = (e) => {
    isResizingTerminal.current = true;
    e.preventDefault();
  };

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Check if Ctrl (or Cmd on Mac) is pressed
      if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
          case 'n':
            e.preventDefault();
            setShowNewFileDialog(true);
            break;
          case 's':
            e.preventDefault();
            if (selectedFile && hasUnsavedChanges) {
              handleMenuSave();
            }
            break;
          case 'd':
            e.preventDefault();
            if (selectedFile) {
              handleDownload();
            }
            break;
          case 'u':
            e.preventDefault();
            fileInputRef.current?.click();
            break;
          default:
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [selectedFile, hasUnsavedChanges]);

  const handleDownload = () => {
    if (!selectedFile) return;
    const downloadUrl = `/api/files/download?path=${encodeURIComponent(selectedFile.path)}`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = selectedFile.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="app">
      <MenuBar
        onNewFile={handleNewFile}
        onSave={handleMenuSave}
        onUpload={handleUpload}
        onDownload={handleDownload}
        currentFile={selectedFile}
        currentDirectory={currentDirectory}
        hasUnsavedChanges={hasUnsavedChanges}
        showNewFileDialog={showNewFileDialog}
        onShowNewFileDialog={setShowNewFileDialog}
        fileInputRef={fileInputRef}
      />
      <div className="app-body">
        <div className="sidebar" style={{ width: `${sidebarWidth}px` }}>
          <div className="sidebar-header">Explorer</div>
          <FileTree
            currentPath={currentPath}
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            wsRef={wsRef}
            refreshTrigger={refreshTrigger}
          />
        </div>
        <div className="resizer resizer-vertical" onMouseDown={handleSidebarMouseDown}></div>
        <div className="main-content">
          <div className="editor-container" style={{ height: `calc(100% - ${terminalHeight}px)` }}>
            <Editor
              ref={editorRef}
              file={selectedFile}
              content={fileContent}
              onSave={handleFileSave}
              onChange={handleContentChange}
            />
          </div>
          <div className="resizer resizer-horizontal" onMouseDown={handleTerminalMouseDown}></div>
          <div className="terminal-container" style={{ height: `${terminalHeight}px` }}>
            <Terminal wsRef={wsRef} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
