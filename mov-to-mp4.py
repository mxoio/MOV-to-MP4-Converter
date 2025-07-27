#!/usr/bin/env python3
"""
MOV to MP4 Converter Script with GUI File Manager
Converts MOV files to MP4 format using FFmpeg with file dialog interface.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import sys
from pathlib import Path

class VideoConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MOV to MP4 Converter")
        self.root.geometry("600x400")
        
        # Variables
        self.selected_files = []
        self.output_directory = ""
        self.conversion_in_progress = False
        
        self.setup_ui()
        self.check_ffmpeg()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File selection
        ttk.Label(main_frame, text="Select MOV files to convert:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="Browse Files", command=self.select_files).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(file_frame, text="Clear Selection", command=self.clear_files).grid(row=0, column=1)
        
        # File list
        self.file_listbox = tk.Listbox(main_frame, height=8)
        self.file_listbox.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Output directory
        ttk.Label(main_frame, text="Output directory:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.output_label = ttk.Label(output_frame, text="Same as source files", foreground="gray")
        self.output_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        ttk.Button(output_frame, text="Choose Directory", command=self.select_output_dir).grid(row=0, column=1)
        
        # Quality settings
        quality_frame = ttk.LabelFrame(main_frame, text="Quality Settings", padding="5")
        quality_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(quality_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W)
        self.quality_var = tk.StringVar(value="high")
        quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var, 
                                   values=["high", "medium", "low", "custom"], state="readonly")
        quality_combo.grid(row=0, column=1, padx=(5, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to convert")
        self.status_label.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Convert button
        self.convert_button = ttk.Button(main_frame, text="Convert Files", command=self.start_conversion)
        self.convert_button.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def check_ffmpeg(self):
        """Check if FFmpeg is installed."""
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Common FFmpeg paths to check (prioritizing bundled version)
        ffmpeg_paths = [
            os.path.join(script_dir, "ffmpeg", "ffmpeg.exe"),  # Bundled with project
            os.path.join(script_dir, "ffmpeg", "ffmpeg"),      # Unix-style bundled
            "ffmpeg",  # If in PATH
            r"C:\ProgramData\chocolatey\lib\ffmpeg-full\tools\ffmpeg\bin\ffmpeg.exe",
            r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe",
        ]
        
        self.ffmpeg_path = None
        for path in ffmpeg_paths:
            try:
                subprocess.run([path, "-version"], stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL, check=True)
                self.ffmpeg_path = path
                print(f"Found FFmpeg at: {path}")
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if not self.ffmpeg_path:
            messagebox.showerror("FFmpeg Not Found", 
                               "FFmpeg is required for video conversion.\n\n"
                               "Please install FFmpeg:\n"
                               "- Windows: choco install ffmpeg-full\n"
                               "- macOS: brew install ffmpeg\n"
                               "- Linux: sudo apt install ffmpeg")
            self.root.quit()
    
    def select_files(self):
        """Open file dialog to select MOV files."""
        file_paths = filedialog.askopenfilenames(
            title="Select MOV files to convert",
            filetypes=[
                ("MOV files", "*.mov *.MOV"),
                ("All video files", "*.mov *.MOV *.mp4 *.MP4 *.avi *.AVI"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            self.selected_files = list(file_paths)
            self.update_file_list()
    
    def clear_files(self):
        """Clear selected files."""
        self.selected_files = []
        self.update_file_list()
    
    def update_file_list(self):
        """Update the file listbox."""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.selected_files:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            self.file_listbox.insert(tk.END, f"{file_name} ({file_size:.1f} MB)")
    
    def select_output_dir(self):
        """Select output directory."""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_directory = directory
            self.output_label.config(text=f"Output: {directory}", foreground="black")
        else:
            self.output_directory = ""
            self.output_label.config(text="Same as source files", foreground="gray")
    
    def get_ffmpeg_params(self, quality):
        """Get FFmpeg parameters based on quality setting."""
        params = {
            "high": ["-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "192k"],
            "medium": ["-c:v", "libx264", "-crf", "23", "-c:a", "aac", "-b:a", "128k"],
            "low": ["-c:v", "libx264", "-crf", "28", "-c:a", "aac", "-b:a", "96k"],
            "custom": ["-c:v", "libx264", "-crf", "20", "-c:a", "copy"]  # Copy audio
        }
        return params.get(quality, params["medium"])
    
    def convert_video(self, input_path, output_path, quality):
        """Convert a single video file."""
        ffmpeg_params = self.get_ffmpeg_params(quality)
        
        cmd = [self.ffmpeg_path, "-i", input_path] + ffmpeg_params + ["-y", output_path]
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                     universal_newlines=True)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                return True, "Success"
            else:
                return False, stderr
        except Exception as e:
            return False, str(e)
    
    def start_conversion(self):
        """Start the conversion process in a separate thread."""
        if not self.selected_files:
            messagebox.showwarning("No Files Selected", "Please select MOV files to convert.")
            return
        
        if self.conversion_in_progress:
            messagebox.showinfo("Conversion In Progress", "Please wait for the current conversion to complete.")
            return
        
        # Start conversion in separate thread
        self.conversion_in_progress = True
        self.convert_button.config(state="disabled")
        thread = threading.Thread(target=self.conversion_worker)
        thread.daemon = True
        thread.start()
    
    def conversion_worker(self):
        """Worker thread for video conversion."""
        total_files = len(self.selected_files)
        successful_conversions = 0
        failed_conversions = []
        
        for i, input_path in enumerate(self.selected_files):
            # Update status
            file_name = os.path.basename(input_path)
            self.status_label.config(text=f"Converting: {file_name}")
            
            # Determine output path
            if self.output_directory:
                output_dir = self.output_directory
            else:
                output_dir = os.path.dirname(input_path)
            
            # Create output filename
            input_name = os.path.splitext(file_name)[0]
            output_path = os.path.join(output_dir, f"{input_name}.mp4")
            
            # Convert video
            success, message = self.convert_video(input_path, output_path, self.quality_var.get())
            
            if success:
                successful_conversions += 1
            else:
                failed_conversions.append((file_name, message))
            
            # Update progress
            progress = ((i + 1) / total_files) * 100
            self.progress_var.set(progress)
            self.root.update_idletasks()
        
        # Show results
        result_msg = f"Conversion completed!\n\n"
        result_msg += f"Successfully converted: {successful_conversions}/{total_files} files"
        
        if failed_conversions:
            result_msg += f"\n\nFailed conversions:"
            for file_name, error in failed_conversions:
                result_msg += f"\n- {file_name}: {error[:100]}..."
        
        messagebox.showinfo("Conversion Results", result_msg)
        
        # Reset UI
        self.conversion_in_progress = False
        self.convert_button.config(state="normal")
        self.status_label.config(text="Ready to convert")
        self.progress_var.set(0)
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

def command_line_converter():
    """Command line version of the converter."""
    if len(sys.argv) < 2:
        print("Usage: python mov_to_mp4.py <input_files...> [--output <directory>] [--quality <high|medium|low>]")
        return
    
    input_files = []
    output_dir = None
    quality = "medium"
    i = 1
    
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--output" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        elif arg == "--quality" and i + 1 < len(sys.argv):
            quality = sys.argv[i + 1]
            i += 2
        else:
            input_files.append(arg)
            i += 1
    
    # Check FFmpeg
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_paths = [
        os.path.join(script_dir, "ffmpeg", "ffmpeg.exe"),  # Bundled with project
        os.path.join(script_dir, "ffmpeg", "ffmpeg"),      # Unix-style bundled
        "ffmpeg",  # If in PATH
        r"C:\ProgramData\chocolatey\lib\ffmpeg-full\tools\ffmpeg\bin\ffmpeg.exe",
        r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe",
    ]
    
    ffmpeg_path = None
    for path in ffmpeg_paths:
        try:
            subprocess.run([path, "-version"], stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, check=True)
            ffmpeg_path = path
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    if not ffmpeg_path:
        print("Error: FFmpeg is not installed or not found")
        print("Please ensure FFmpeg executables are in the 'ffmpeg' folder or install FFmpeg system-wide")
        return
    
    converter = VideoConverter()
    
    for input_file in input_files:
        if not os.path.exists(input_file):
            print(f"Error: File not found: {input_file}")
            continue
        
        if output_dir:
            output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + ".mp4")
        else:
            output_path = os.path.splitext(input_file)[0] + ".mp4"
        
        print(f"Converting: {input_file} -> {output_path}")
        success, message = converter.convert_video(input_file, output_path, quality)
        
        if success:
            print(f"✓ Successfully converted: {os.path.basename(input_file)}")
        else:
            print(f"✗ Failed to convert {os.path.basename(input_file)}: {message}")

def main():
    """Main function."""
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        # Command line mode
        command_line_converter()
    else:
        # GUI mode
        app = VideoConverter()
        app.run()

if __name__ == "__main__":
    main()