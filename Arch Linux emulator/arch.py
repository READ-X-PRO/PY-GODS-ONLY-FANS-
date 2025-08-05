import os
import re
from datetime import datetime

class FileSystemNode:
    def __init__(self, name, is_dir=True, content=None):
        self.name = name
        self.is_dir = is_dir
        self.content = content if not is_dir else ""
        self.children = {} if is_dir else None
        self.parent = None

class ArchLinuxEmulator:
    def __init__(self):
        self.root = FileSystemNode("/")
        self.current_dir = self.root
        self.hostname = "arch-emulator"
        self.username = "user"
        self.init_filesystem()
    
    def init_filesystem(self):
        # Create essential directories
        etc = self.create_node("etc", parent=self.root)
        self.create_node("pacman.conf", parent=etc, is_dir=False, content="# Pacman configuration file")
        
        home = self.create_node("home", parent=self.root)
        user_home = self.create_node(self.username, parent=home)
        
        # Create user files
        self.create_node(".bashrc", parent=user_home, is_dir=False, content="alias ls='ls --color=auto'")
        self.create_node("hello.txt", parent=user_home, is_dir=False, content="Welcome to Arch Linux Emulator!")
        
        # Set current directory to user home
        self.current_dir = user_home
    
    def create_node(self, name, parent, is_dir=True, content=""):
        node = FileSystemNode(name, is_dir, content)
        node.parent = parent
        parent.children[name] = node
        return node

    def get_path(self, node=None):
        if not node:
            node = self.current_dir
        
        segments = []
        current = node
        while current and current != self.root:
            segments.append(current.name)
            current = current.parent
        
        path = "/" + "/".join(reversed(segments))
        return path if path else "/"

    def resolve_path(self, path):
        if path.startswith("/"):
            current = self.root
        else:
            current = self.current_dir
        
        parts = [p for p in path.split("/") if p]
        
        for part in parts:
            if part == "..":
                if current.parent:
                    current = current.parent
            elif part == ".":
                continue
            elif current.is_dir and part in current.children:
                current = current.children[part]
            else:
                return None
        return current

    def execute(self, command):
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return ""
        
        cmd = cmd_parts[0]
        args = cmd_parts[1:]
        
        if cmd == "ls":
            return self.cmd_ls(args)
        elif cmd == "cd":
            return self.cmd_cd(args)
        elif cmd == "pwd":
            return self.cmd_pwd()
        elif cmd == "echo":
            return self.cmd_echo(args)
        elif cmd == "cat":
            return self.cmd_cat(args)
        elif cmd == "mkdir":
            return self.cmd_mkdir(args)
        elif cmd == "touch":
            return self.cmd_touch(args)
        elif cmd == "pacman":
            return self.cmd_pacman(args)
        elif cmd == "exit":
            return "exit"
        elif cmd == "clear":
            return "\n" * 100  # Simulate screen clear
        else:
            return f"{cmd}: command not found"

    def cmd_ls(self, args):
        target_path = args[0] if args else "."
        resolved = self.resolve_path(target_path)

        if not resolved:
            return f"ls: cannot access '{target_path}': No such file or directory"
        
        if resolved.is_dir:
            return " ".join(resolved.children.keys())
        else:
            return resolved.name

    def cmd_cd(self, args):
        if not args:
            # Go to user's home directory by default
            target_path = f"/home/{self.username}"
        else:
            target_path = args[0]
        
        target = self.resolve_path(target_path)
        
        if not target:
            return f"cd: no such file or directory: {target_path}"
        if not target.is_dir:
            return f"cd: not a directory: {target_path}"
        
        self.current_dir = target
        return ""

    def cmd_pwd(self):
        return self.get_path()

    def cmd_echo(self, args):
        text_parts = []
        redirect_file = None
        
        redirect_index = -1
        if ">" in args:
            redirect_index = args.index(">")
            
        if redirect_index != -1:
            if redirect_index + 1 >= len(args):
                return "bash: syntax error near unexpected token `newline'"
            redirect_file = args[redirect_index + 1]
            text_parts = args[:redirect_index]
        else:
            text_parts = args

        output = " ".join(text_parts)
        if redirect_file:
            target = self.resolve_path(redirect_file)
            if target and target.is_dir:
                return f"echo: {redirect_file}: Is a directory"
            
            # Handle path to create the file
            path_parts = redirect_file.split('/')
            filename = path_parts[-1]
            parent_path = "/".join(path_parts[:-1])

            if parent_path:
                 parent = self.resolve_path(parent_path)
            else:
                 parent = self.current_dir

            if not parent or not parent.is_dir:
                return f"echo: cannot create file '{redirect_file}': No such file or directory"
            
            if filename in parent.children:
                # Overwrite existing file
                parent.children[filename].content = output
            else:
                # Create new file
                self.create_node(filename, parent, is_dir=False, content=output)
            return ""
        
        return output

    def cmd_cat(self, args):
        if not args:
            return "cat: missing operand"
        
        outputs = []
        for path in args:
            target = self.resolve_path(path)
            if not target:
                outputs.append(f"cat: {path}: No such file or directory")
            elif target.is_dir:
                outputs.append(f"cat: {path}: Is a directory")
            else:
                outputs.append(target.content)
        return "\n".join(outputs)

    def _create_from_path(self, path, is_dir):
        """Helper function for mkdir and touch to resolve paths and create nodes."""
        if not path:
            op = "mkdir" if is_dir else "touch"
            return f"{op}: missing operand"
            
        # Correctly determine the parent directory and the name of the new node
        path_parts = path.rstrip('/').split('/')
        node_name = path_parts[-1]
        
        if len(path_parts) > 1:
            parent_path_str = "/".join(path_parts[:-1])
            if path.startswith('/') and not parent_path_str:
                parent_path_str = '/' # Handle root case like /newdir
        else:
            parent_path_str = '.' # Relative to current dir

        parent = self.resolve_path(parent_path_str)

        if not parent or not parent.is_dir:
            return f"mkdir: cannot create directory ‘{path}’: No such file or directory"

        if node_name in parent.children:
            if not (not is_dir and not parent.children[node_name].is_dir): # allow touch on existing file
                 return f"mkdir: cannot create directory ‘{path}’: File exists"
            return "" # Silently succeed if 'touch'ing an existing file

        self.create_node(node_name, parent, is_dir=is_dir)
        return ""

    def cmd_mkdir(self, args):
        if not args:
            return "mkdir: missing operand"
        
        for path in args:
            result = self._create_from_path(path, is_dir=True)
            if result:
                return result
        return ""

    def cmd_touch(self, args):
        if not args:
            return "touch: missing operand"
        
        for path in args:
            result = self._create_from_path(path, is_dir=False)
            if result:
                return result
        return ""

    def cmd_pacman(self, args):
        if not args:
            return "pacman: no operation specified (use -h for help)"
        
        # Prioritize Syu over S
        if "-Syu" in args:
            return ":: Synchronizing package databases...\n:: Starting full system upgrade...\n there is nothing to do"
        elif "-S" in args:
            package_index = -1
            try:
                package_index = args.index("-S") + 1
            except (ValueError, IndexError):
                 return "error: option '-S' requires a target"
            
            if package_index >= len(args):
                return "error: option '-S' requires a target"
            
            packages = args[package_index:]
            return f"resolving dependencies...\nlooking for conflicting packages...\n\nPackages ({len(packages)})  {'  '.join(packages)}\n\nTotal Installed Size:  0.00 MiB\n\n:: Proceed with installation? [Y/n] \n:: (1/{len(packages)}) Checking keys in keyring\n:: (1/{len(packages)}) Checking package integrity\n:: (1/{len(packages)}) Loading package files\n:: (1/{len(packages)}) Checking for file conflicts\n:: (1/{len(packages)}) Checking available disk space\n:: Installing {' '.join(packages)}..."
        else:
            return f"pacman: invalid option '{args[0]}'"

    def get_prompt(self):
        home_path = f"/home/{self.username}"
        current_path_str = self.get_path()
        
        if current_path_str.startswith(home_path):
            display_path = "~" + current_path_str[len(home_path):]
        else:
            display_path = current_path_str
            
        return f"[{self.username}@{self.hostname} {display_path}]$ "

def main():
    emulator = ArchLinuxEmulator()
    print("Welcome to Arch Linux Emulator (type 'exit' to quit)")
    
    while True:
        try:
            command = input(emulator.get_prompt())
            result = emulator.execute(command)
            if result == "exit":
                break
            if result:
                print(result)
        except KeyboardInterrupt:
            print("^C")
            continue
        except EOFError:
            print("exit")
            break

if __name__ == "__main__":
    main()