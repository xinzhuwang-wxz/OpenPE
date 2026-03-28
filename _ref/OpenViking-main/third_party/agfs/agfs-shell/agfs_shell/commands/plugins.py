"""
PLUGINS command - manage AGFS plugins.
"""

import os
from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('plugins')
def cmd_plugins(process: Process) -> int:
    """
    Manage AGFS plugins

    Usage: plugins <subcommand> [arguments]

    Subcommands:
        list [-v]         List all plugins (builtin and external)
        load <path>       Load external plugin from AGFS or HTTP(S)
        unload <path>     Unload external plugin

    Options:
        -v                Show detailed configuration parameters

    Path formats for load:
        <relative_path>    - Load from AGFS (relative to current directory)
        <absolute_path>    - Load from AGFS (absolute path)
        http(s)://<url>    - Load from HTTP(S) URL

    Examples:
        plugins list                                  # List all plugins
        plugins list -v                               # List with config details
        plugins load /mnt/plugins/myplugin.so         # Load from AGFS (absolute)
        plugins load myplugin.so                      # Load from current directory
        plugins load ../plugins/myplugin.so           # Load from relative path
        plugins load https://example.com/myplugin.so  # Load from HTTP(S)
        plugins unload /mnt/plugins/myplugin.so       # Unload plugin
    """
    if not process.filesystem:
        process.stderr.write("plugins: filesystem not available\n")
        return 1

    # No arguments - show usage
    if len(process.args) == 0:
        process.stderr.write("Usage: plugins <subcommand> [arguments]\n")
        process.stderr.write("\nSubcommands:\n")
        process.stderr.write("  list           - List all plugins (builtin and external)\n")
        process.stderr.write("  load <path>    - Load external plugin\n")
        process.stderr.write("  unload <path>  - Unload external plugin\n")
        process.stderr.write("\nPath formats for load:\n")
        process.stderr.write("  <relative_path>  - Load from AGFS (relative to current directory)\n")
        process.stderr.write("  <absolute_path>  - Load from AGFS (absolute path)\n")
        process.stderr.write("  http(s)://<url>  - Load from HTTP(S) URL\n")
        process.stderr.write("\nExamples:\n")
        process.stderr.write("  plugins list\n")
        process.stderr.write("  plugins load /mnt/plugins/myplugin.so         # Absolute path\n")
        process.stderr.write("  plugins load myplugin.so                      # Current directory\n")
        process.stderr.write("  plugins load ../plugins/myplugin.so           # Relative path\n")
        process.stderr.write("  plugins load https://example.com/myplugin.so  # HTTP(S) URL\n")
        return 1

    # Handle plugin subcommands
    subcommand = process.args[0].lower()

    if subcommand == "load":
        if len(process.args) < 2:
            process.stderr.write("Usage: plugins load <path>\n")
            process.stderr.write("\nPath formats:\n")
            process.stderr.write("  <relative_path>  - Load from AGFS (relative to current directory)\n")
            process.stderr.write("  <absolute_path>  - Load from AGFS (absolute path)\n")
            process.stderr.write("  http(s)://<url>  - Load from HTTP(S) URL\n")
            process.stderr.write("\nExamples:\n")
            process.stderr.write("  plugins load /mnt/plugins/myplugin.so        # Absolute path\n")
            process.stderr.write("  plugins load myplugin.so                     # Current directory\n")
            process.stderr.write("  plugins load ../plugins/myplugin.so          # Relative path\n")
            process.stderr.write("  plugins load https://example.com/myplugin.so # HTTP(S) URL\n")
            return 1

        path = process.args[1]

        # Determine path type
        is_http = path.startswith('http://') or path.startswith('https://')

        # Process path based on type
        if is_http:
            # HTTP(S) URL: use as-is, server will download it
            library_path = path
        else:
            # AGFS path: resolve relative paths and add agfs:// prefix
            # Resolve relative paths to absolute paths
            if not path.startswith('/'):
                # Relative path - resolve based on current working directory
                cwd = getattr(process, 'cwd', '/')
                path = os.path.normpath(os.path.join(cwd, path))
            library_path = f"agfs://{path}"

        try:
            # Load the plugin
            result = process.filesystem.client.load_plugin(library_path)
            plugin_name = result.get("plugin_name", "unknown")
            process.stdout.write(f"Loaded external plugin: {plugin_name}\n")
            process.stdout.write(f"  Source: {path}\n")
            return 0
        except Exception as e:
            error_msg = str(e)
            process.stderr.write(f"plugins load: {error_msg}\n")
            return 1

    elif subcommand == "unload":
        if len(process.args) < 2:
            process.stderr.write("Usage: plugins unload <library_path>\n")
            return 1

        library_path = process.args[1]

        try:
            process.filesystem.client.unload_plugin(library_path)
            process.stdout.write(f"Unloaded external plugin: {library_path}\n")
            return 0
        except Exception as e:
            error_msg = str(e)
            process.stderr.write(f"plugins unload: {error_msg}\n")
            return 1

    elif subcommand == "list":
        try:
            # Check for verbose flag
            verbose = '-v' in process.args[1:] or '--verbose' in process.args[1:]

            # Use new API to get detailed plugin information
            plugins_info = process.filesystem.client.get_plugins_info()

            # Separate builtin and external plugins
            builtin_plugins = [p for p in plugins_info if not p.get('is_external', False)]
            external_plugins = [p for p in plugins_info if p.get('is_external', False)]

            # Display builtin plugins
            if builtin_plugins:
                process.stdout.write(f"Builtin Plugins: ({len(builtin_plugins)})\n")
                for plugin in sorted(builtin_plugins, key=lambda x: x.get('name', '')):
                    plugin_name = plugin.get('name', 'unknown')
                    mounted_paths = plugin.get('mounted_paths', [])
                    config_params = plugin.get('config_params', [])

                    if mounted_paths:
                        mount_list = []
                        for mount in mounted_paths:
                            path = mount.get('path', '')
                            config = mount.get('config', {})
                            if config:
                                mount_list.append(f"{path} (with config)")
                            else:
                                mount_list.append(path)
                        process.stdout.write(f"  {plugin_name:20} -> {', '.join(mount_list)}\n")
                    else:
                        process.stdout.write(f"  {plugin_name:20} (not mounted)\n")

                    # Show config params if verbose and available
                    if verbose and config_params:
                        process.stdout.write(f"    Config parameters:\n")
                        for param in config_params:
                            req = "*" if param.get('required', False) else " "
                            name = param.get('name', '')
                            ptype = param.get('type', '')
                            default = param.get('default', '')
                            desc = param.get('description', '')
                            default_str = f" (default: {default})" if default else ""
                            process.stdout.write(f"      {req} {name:20} {ptype:10} {desc}{default_str}\n")

                process.stdout.write("\n")

            # Display external plugins
            if external_plugins:
                process.stdout.write(f"External Plugins: ({len(external_plugins)})\n")
                for plugin in sorted(external_plugins, key=lambda x: x.get('name', '')):
                    plugin_name = plugin.get('name', 'unknown')
                    library_path = plugin.get('library_path', '')
                    mounted_paths = plugin.get('mounted_paths', [])
                    config_params = plugin.get('config_params', [])

                    # Extract just the filename for display
                    filename = os.path.basename(library_path) if library_path else plugin_name
                    process.stdout.write(f"  {filename}\n")
                    process.stdout.write(f"    Plugin name: {plugin_name}\n")

                    if mounted_paths:
                        mount_list = []
                        for mount in mounted_paths:
                            path = mount.get('path', '')
                            config = mount.get('config', {})
                            if config:
                                mount_list.append(f"{path} (with config)")
                            else:
                                mount_list.append(path)
                        process.stdout.write(f"    Mounted at: {', '.join(mount_list)}\n")
                    else:
                        process.stdout.write(f"    (Not currently mounted)\n")

                    # Show config params if verbose and available
                    if verbose and config_params:
                        process.stdout.write(f"    Config parameters:\n")
                        for param in config_params:
                            req = "*" if param.get('required', False) else " "
                            name = param.get('name', '')
                            ptype = param.get('type', '')
                            default = param.get('default', '')
                            desc = param.get('description', '')
                            default_str = f" (default: {default})" if default else ""
                            process.stdout.write(f"      {req} {name:20} {ptype:10} {desc}{default_str}\n")
            else:
                process.stdout.write("No external plugins loaded\n")

            return 0
        except Exception as e:
            error_msg = str(e)
            process.stderr.write(f"plugins list: {error_msg}\n")
            return 1

    else:
        process.stderr.write(f"plugins: unknown subcommand: {subcommand}\n")
        process.stderr.write("\nUsage:\n")
        process.stderr.write("  plugins list                             - List all plugins\n")
        process.stderr.write("  plugins load <library_path|url>          - Load external plugin\n")
        process.stderr.write("  plugins unload <library_path>            - Unload external plugin\n")
        return 1
