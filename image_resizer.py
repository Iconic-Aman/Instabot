import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
import os
import keyboard
import time
import pyperclip
from io import BytesIO
import cv2
import numpy as np

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer to 1:1")
        # Set window to full screen
        self.root.state('zoomed')  # This will maximize the window
        # self.root.geometry("1400x1400")  # Remove this line as we're using full screen
        
        # Create output directory with specific path
        self.output_dir = r"C:\Users\raunak\Desktop\LEETCODE"  # Replace this with your desired path
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Variables
        self.original_images = []
        self.resized_images = []
        self.image_paths = []
        self.screenshot_shortcut = "ctrl+shift+s"  # Full screenshot shortcut
        self.partial_screenshot_shortcut = "ctrl+shift+a"  # Partial screenshot shortcut
        self.current_full_screenshot = None
        self.current_cv_image = None
        
        # Create GUI elements
        self.create_widgets()
        
        # Set up keyboard shortcuts
        keyboard.add_hotkey(self.screenshot_shortcut, self.take_screenshot)
        keyboard.add_hotkey(self.partial_screenshot_shortcut, self.take_partial_screenshot)
        
    def create_widgets(self):
        # Main container frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for buttons
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=10)
        
        # Upload button
        self.upload_btn = tk.Button(top_frame, text="Upload Images", command=self.upload_images)
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        # Paste button
        self.paste_btn = tk.Button(top_frame, text="Paste from Clipboard", command=self.paste_from_clipboard)
        self.paste_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        self.reset_btn = tk.Button(top_frame, text="Reset", command=self.reset_application, bg='red', fg='white')
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Download button
        self.download_btn = tk.Button(top_frame, text="Download All Resized Images", command=self.download_images)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        self.download_btn.config(state=tk.DISABLED)
        
        # Shortcut info label
        shortcuts_frame = tk.Frame(top_frame)
        shortcuts_frame.pack(side=tk.RIGHT, padx=5)
        
        # full_shortcut_label = tk.Label(shortcuts_frame, text=f"Full Screenshot: {self.screenshot_shortcut.upper()}")
        # full_shortcut_label.pack()
        
        partial_shortcut_label = tk.Label(shortcuts_frame, text=f"Partial Screenshot: {self.partial_screenshot_shortcut.upper()}")
        partial_shortcut_label.pack()
        
        # Create canvas and scrollbar for multiple images
        self.canvas = tk.Canvas(main_frame)
        self.scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def upload_images(self):
        file_paths = filedialog.askopenfilenames(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if file_paths:
            self.image_paths = file_paths
            self.original_images = []
            self.resized_images = []
            
            # Clear previous images
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # Process each image
            for file_path in file_paths:
                original_image = Image.open(file_path)
                self.original_images.append(original_image)
                
                # Create frame for each image pair
                image_pair_frame = tk.Frame(self.scrollable_frame)
                image_pair_frame.pack(pady=10)
                
                # Original image label
                original_label = tk.Label(image_pair_frame, text="Original")
                original_label.pack(side=tk.LEFT, padx=10)
                
                # Resized image label
                resized_label = tk.Label(image_pair_frame, text="Resized (1:1)")
                resized_label.pack(side=tk.LEFT, padx=10)
                
                # Display original image
                self.display_image(original_image, original_label)
                
                # Resize and display
                resized_image = self.resize_image(original_image)
                self.resized_images.append(resized_image)
                self.display_image(resized_image, resized_label)
            
            # Enable download button
            self.download_btn.config(state=tk.NORMAL)
    
    def resize_image(self, image):
        # Get the maximum dimension for the square
        max_dim = max(image.size)
        # Stretch the image to square dimensions
        return image.resize((max_dim, max_dim), Image.Resampling.LANCZOS)
    
    def display_image(self, image, label):
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate display size based on screen size
        if label.master.winfo_parent() == self.scrollable_frame.winfo_id():  # If it's a pasted image
            # For pasted images, use the original image size
            display_size = image.size
        else:
            display_size = (600, 600)  # Smaller size for partial screenshots
        
        display_image = image.copy()
        # Only resize if the image is larger than screen
        if display_size[0] > screen_width or display_size[1] > screen_height:
            display_image.thumbnail((screen_width, screen_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(display_image)
        
        # Update label
        label.config(image=photo)
        label.image = photo
    
    def download_images(self):
        if self.resized_images:
            try:
                for i, (image, path) in enumerate(zip(self.resized_images, self.image_paths)):
                    # Create new filename with _resized suffix
                    filename = os.path.basename(path)
                    name, ext = os.path.splitext(filename)
                    new_path = os.path.join(self.output_dir, f"{name}_resized{ext}")
                    
                    # Save the image
                    image.save(new_path)
                
                messagebox.showinfo("Success", f"{len(self.resized_images)} images saved successfully in the 'resized_images' folder!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save images: {str(e)}")

    def take_screenshot(self):
        # Minimize the window to take screenshot
        self.root.withdraw()
        time.sleep(0.5)  # Give time for window to minimize
        
        # Take screenshot
        screenshot = ImageGrab.grab()
        
        # Show the window again
        self.root.deiconify()
        
        # Save the screenshot
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(self.output_dir, f"screenshot_{timestamp}.png")
        screenshot.save(screenshot_path)
        
        # Add the screenshot to the list of images
        self.image_paths.append(screenshot_path)
        self.original_images.append(screenshot)
        
        # Process and display the screenshot
        self.process_new_image(screenshot, screenshot_path)
        
        # Enable download button
        self.download_btn.config(state=tk.NORMAL)
        
    def process_new_image(self, image, path):
        # Create frame for the image pair
        image_pair_frame = tk.Frame(self.scrollable_frame)
        image_pair_frame.pack(pady=20)
        
        # Original image label
        original_label = tk.Label(image_pair_frame, text="Original")
        original_label.pack(side=tk.LEFT, padx=20)
        
        # Resized image label
        resized_label = tk.Label(image_pair_frame, text="Resized (1:1)")
        resized_label.pack(side=tk.LEFT, padx=20)
        
        # Display original image
        self.display_image(image, original_label)
        
        # Resize and display
        resized_image = self.resize_image(image)
        self.resized_images.append(resized_image)
        self.display_image(resized_image, resized_label)
        
        # Add to paths list
        self.image_paths.append(path)

    def take_partial_screenshot(self):
        if not self.current_full_screenshot:
            messagebox.showwarning("Warning", "Please paste a full screenshot first!")
            return

        # Create window and set mouse callback
        window_name = "Select Area (Click and drag to select, Release to crop, ESC when done)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Convert PIL image to OpenCV format with high quality
        cv_image = cv2.cvtColor(np.array(self.current_full_screenshot), cv2.COLOR_RGB2BGR)
        self.current_cv_image = cv_image.copy()
        self.display_image = cv_image.copy()
        
        # Initialize rectangle drawing variables
        self.drawing = False
        self.ix, self.iy = -1, -1
        
        def draw_rectangle(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.drawing = True
                self.ix, self.iy = x, y
            elif event == cv2.EVENT_MOUSEMOVE:
                if self.drawing:
                    self.display_image = self.current_cv_image.copy()
                    cv2.rectangle(self.display_image, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
                    cv2.imshow(window_name, self.display_image)
            elif event == cv2.EVENT_LBUTTONUP:
                self.drawing = False
                if abs(x - self.ix) > 10 and abs(y - self.iy) > 10:  # Ensure minimum selection size
                    # Get coordinates
                    x1, y1 = min(self.ix, x), min(self.iy, y)
                    x2, y2 = max(self.ix, x), max(self.iy, y)
                    
                    # Draw the final rectangle
                    cv2.rectangle(self.current_cv_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    self.display_image = self.current_cv_image.copy()
                    cv2.imshow(window_name, self.display_image)
                    
                    # Crop directly from the original PIL image for best quality
                    cropped_image = self.current_full_screenshot.crop((x1, y1, x2, y2))
                    
                    # Stretch to 1:1 ratio
                    max_dim = max(cropped_image.size)
                    stretched_image = cropped_image.resize((max_dim, max_dim), Image.Resampling.LANCZOS)
                    
                    # Save the stretched image
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    cropped_path = os.path.join(self.output_dir, f"cropped_{timestamp}.png")
                    stretched_image.save(cropped_path, quality=100, optimize=False)
                    
                    # Add to lists and display
                    self.original_images.append(cropped_image)
                    self.resized_images.append(stretched_image)
                    self.image_paths.append(cropped_path)
                    
                    # Display both original and stretched versions
                    self.display_cropped_images(cropped_image, stretched_image)

        cv2.setMouseCallback(window_name, draw_rectangle)
        cv2.imshow(window_name, self.current_cv_image)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key to finish
                break
        
        cv2.destroyAllWindows()
        messagebox.showinfo("Complete", "Finished cropping. Press Ctrl+Shift+A again for more crops.")

    def display_cropped_images(self, original, stretched):
        # Create frame for the image pair
        image_pair_frame = tk.Frame(self.scrollable_frame)
        image_pair_frame.pack(pady=20)
        
        # Original image label
        original_label = tk.Label(image_pair_frame, text="Original")
        original_label.pack(side=tk.LEFT, padx=20)
        
        # Resized image label
        resized_label = tk.Label(image_pair_frame, text="Resized (1:1)")
        resized_label.pack(side=tk.LEFT, padx=20)
        
        # Display original image
        self.display_image(original, original_label)
        
        # Display stretched image
        self.display_image(stretched, resized_label)
        
        # Enable download button
        self.download_btn.config(state=tk.NORMAL)

    def paste_from_clipboard(self):
        try:
            # Get image from clipboard
            clipboard_image = ImageGrab.grabclipboard()
            if clipboard_image:
                # Save the image temporarily with high quality
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                temp_path = os.path.join(self.output_dir, f"pasted_{timestamp}.png")
                clipboard_image.save(temp_path, quality=100, optimize=False)
                
                # Store the full screenshot
                self.current_full_screenshot = clipboard_image
                
                # Create frame for the pasted image
                image_frame = tk.Frame(self.scrollable_frame)
                image_frame.pack(pady=20)
                
                # Original image label
                original_label = tk.Label(image_frame, text="Pasted Screenshot")
                original_label.pack()
                
                # Display original image without resizing
                self.display_image(clipboard_image, original_label)
                
                self.download_btn.config(state=tk.NORMAL)
                # messagebox.showinfo("Success", "Image pasted successfully!\nClick and drag to select area, release to crop automatically")
            else:
                messagebox.showwarning("Warning", "No image found in clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste image: {str(e)}")

    def reset_application(self):
        # Clear all images and reset state
        self.original_images = []
        self.resized_images = []
        self.image_paths = []
        self.current_full_screenshot = None
        self.current_cv_image = None
        
        # Clear the display
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Reset button states
        self.download_btn.config(state=tk.DISABLED)
        
        # Show confirmation message
        messagebox.showinfo("Reset", "Application has been reset successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()


