import os
from datetime import date
from tkinter import Tk, filedialog, Label, Button
from PIL import Image, ImageDraw, ImageFont

# ===============================
# 1️⃣ CONFIGURATION - You can edit this
# ===============================
PROBLEM_NAME = "1123. Lowest Common Ancestor of Deepest Leaves"
DIFFICULTY = "Medium"
TAGS = "DFS, BFS"

# ===============================
# 2️⃣ FUNCTION: Resize any image to square (for Insta)
# ===============================
def resize_to_square(image_path, size=1080):
    img = Image.open(image_path)
    width, height = img.size
    background = Image.new("RGB", (size, size), (255, 255, 255))  # white bg

    # Maintain aspect ratio
    ratio = min(size / width, size / height)
    new_size = (int(width * ratio), int(height * ratio))
    resized = img.resize(new_size)
    background.paste(resized, ((size - new_size[0]) // 2, (size - new_size[1]) // 2))

    return background

# ===============================
# 3️⃣ FUNCTION: Create title image
# ===============================
def create_title_image(output_path, problem_name, level, tags):
    img = Image.new("RGB", (1080, 1080), (30, 30, 30))  # dark background
    draw = ImageDraw.Draw(img)

    # Use system font (Windows/macOS), fallback if not found
    try:
        font_big = ImageFont.truetype("arialbd.ttf", 70)
        font_small = ImageFont.truetype("arial.ttf", 40)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    today = date.today().strftime("%d/%m/%Y")

    draw.text((80, 100), "Leetcode Daily Challenge ⭐", font=font_big, fill="white")
    draw.text((80, 230), f"{today}", font=font_small, fill="white")
    draw.text((80, 300), f"{problem_name}", font=font_small, fill="white")
    draw.text((80, 370), f"Difficulty : {level}", font=font_small, fill="white")
    draw.text((80, 440), f"Tags : {tags}", font=font_small, fill="white")

    img.save(output_path)

# ===============================
# 4️⃣ FUNCTION: Auto-generate caption/description
# ===============================
def generate_description(problem_name, level, tags):
    today = date.today().strftime("%Y-%m-%d")
    return (
        f"✨ Leetcode Daily Challenge - {today}\n"
        f"🔹 Problem: {problem_name}\n"
        f"🧠 Difficulty: {level}\n"
        f"🏷️ Tags: {tags}\n"
        "\n📌 Approach:\n"
        "1. Traverse tree to find the deepest level\n"
        "2. Backtrack to find common ancestor of deepest leaves\n"
        "3. Used DFS to calculate depth\n"
        "\n#leetcode #dsa #interviewprep #python #ai #coding"
    )

# ===============================
# 5️⃣ FUNCTION: Main processor - puts everything together
# ===============================
def process_images(image_paths):
    print("\n🔁 Processing images...")

    # Resize input images
    problem_image = resize_to_square(image_paths[0])
    solution_image = resize_to_square(image_paths[1])

    # Create output folder
    folder_name = f"Leetcode_{date.today()}_{PROBLEM_NAME.split('.')[0]}"
    os.makedirs(folder_name, exist_ok=True)

    # Save images
    problem_image.save(os.path.join(folder_name, "final_problem.jpg"))
    solution_image.save(os.path.join(folder_name, "final_solution.jpg"))

    # Create and save title image
    create_title_image(
        output_path=os.path.join(folder_name, "final_title.jpg"),
        problem_name=PROBLEM_NAME,
        level=DIFFICULTY,
        tags=TAGS
    )

    # Create and save description text
    description = generate_description(PROBLEM_NAME, DIFFICULTY, TAGS)
    with open(os.path.join(folder_name, "description.txt"), "w") as f:
        f.write(description)

    print(f"✅ Done! Assets saved in → {folder_name}")
    print("📁 Files: title, problem, solution, description")

# ===============================
# 6️⃣ FUNCTION: GUI - Upload Image Files
# ===============================
def select_images():
    files = filedialog.askopenfilenames(
        title="Select Problem & Solution Screenshots",
        filetypes=[("Image Files", "*.jpg *.png *.jpeg")]
    )
    if len(files) == 2:
        process_images(files)
    else:
        print("⚠️ Please select exactly 2 images (problem + solution)")

# ===============================
# 7️⃣ FUNCTION: Run the GUI App
# ===============================
def main_gui():
    root = Tk()
    root.title("LeetCode Insta Post Generator")
    root.geometry("400x200")

    Label(root, text="Upload 2 images (Problem + Solution)").pack(pady=20)
    Button(root, text="Upload Images", command=select_images).pack(pady=10)

    root.mainloop()

# ===============================
# 8️⃣ RUN THE PROGRAM
# ===============================
if __name__ == "__main__":
    main_gui()
