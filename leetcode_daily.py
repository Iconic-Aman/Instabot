import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageDraw, ImageFont
import time
from datetime import datetime
import os
import json

class LeetCodeDaily:
    def __init__(self):
        # Update output directory to use saved_img folder in current workspace
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_img")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")
            
        # Initialize Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def get_daily_challenge(self):
        try:
            print("Getting daily challenge from LeetCode API...")
            # Use LeetCode's GraphQL API to get the daily challenge
            url = "https://leetcode.com/graphql"
            query = """
            query questionOfToday {
                activeDailyCodingChallengeQuestion {
                    date
                    userStatus
                    question {
                        questionId
                        questionFrontendId
                        title
                        titleSlug
                        difficulty
                        topicTags {
                            name
                        }
                    }
                }
            }
            """
            
            headers = {
                "Content-Type": "application/json",
            }
            
            response = requests.post(url, json={"query": query}, headers=headers)
            data = response.json()
            
            if "data" in data and "activeDailyCodingChallengeQuestion" in data["data"]:
                question = data["data"]["activeDailyCodingChallengeQuestion"]["question"]
                tags = [tag["name"] for tag in question["topicTags"]]
                
                problem_info = {
                    "number": question["questionFrontendId"],
                    "title": question["title"],
                    "difficulty": question["difficulty"],
                    "tags": tags
                }
                
                print(f"Found problem: {problem_info['number']}. {problem_info['title']} (Difficulty: {problem_info['difficulty']})")
                print(f"Tags: {tags}")
                
                return problem_info
            else:
                print("Could not find daily challenge in API response")
                return None
                
        except Exception as e:
            print(f"Error getting daily challenge: {str(e)}")
            return None
        
    def create_title_image(self, problem_info):
        print("\nCreating title image...")
        # Load background image
        bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg_img", "wimg.jpg")
        try:
            background = Image.open(bg_path)
            # Resize background to 1:1 ratio (square)
            size = 1080  # Instagram's recommended size
            background = background.resize((size, size), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Error loading background image: {str(e)}")
            # Fallback to dark background if image loading fails
            background = Image.new('RGB', (size, size), (30, 30, 30))
        
        # Create a semi-transparent overlay
        overlay = Image.new('RGBA', (size, size), (0, 0, 0, 180))
        background = Image.alpha_composite(background.convert('RGBA'), overlay)
        
        draw = ImageDraw.Draw(background)
        
        try:
            print("Loading fonts...")
            # Load fonts with fallbacks
            fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
            
            # Title font
            try:
                title_font = ImageFont.truetype(os.path.join(fonts_dir, "MontserratAlternates-Bold.ttf"), 60)
            except:
                try:
                    title_font = ImageFont.truetype(os.path.join(fonts_dir, "BebasNeue-Regular.ttf"), 60)
                except:
                    print("Could not load preferred fonts, using system font")
                    title_font = ImageFont.truetype("arial.ttf", 60)
            
            # Regular text font
            try:
                text_font = ImageFont.truetype(os.path.join(fonts_dir, "Poppins-Regular.ttf"), 45)
            except:
                try:
                    text_font = ImageFont.truetype(os.path.join(fonts_dir, "Lato-Regular.ttf"), 45)
                except:
                    print("Could not load preferred fonts, using system font")
                    text_font = ImageFont.truetype("arial.ttf", 45)
            
            # Load emoji font (Segoe UI Emoji on Windows)
            try:
                emoji_font = ImageFont.truetype("C:\\Windows\\Fonts\\seguiemj.ttf", 60)
            except:
                print("Could not load emoji font, using system font")
                emoji_font = title_font
            
            print("Drawing title...")
            # Draw title and star separately - moved down
            title = "Leetcode Daily Challenge"
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_y = 180  # Moved down from 100
            draw.text(((size - title_width) // 2 - 30, title_y), title, font=title_font, fill=(255, 255, 255))
            
            # Draw star emoji with emoji font
            star = "⭐"
            star_bbox = draw.textbbox((0, 0), star, font=emoji_font)
            star_width = star_bbox[2] - star_bbox[0]
            star_height = star_bbox[3] - star_bbox[1]
            
            # Calculate vertical offset to align with title
            title_height = title_bbox[3] - title_bbox[1]
            vertical_offset = (title_height - star_height) // 2
            
            # Position star after the title with proper alignment
            star_x = (size - title_width) // 2 + title_width - 15  # Adjusted for the title shift
            star_y = title_y + vertical_offset + 13
            
            # Draw star in yellow color
            draw.text((star_x, star_y), star, font=emoji_font, fill=(255, 215, 0))  # Gold color
            
            print("Drawing date...")
            # Draw date in DD/MM/YYYY format - increased spacing
            date = datetime.now().strftime("%d/%m/%Y")
            date_bbox = draw.textbbox((0, 0), date, font=title_font)  # Changed to title_font
            date_width = date_bbox[2] - date_bbox[0]
            draw.text(((size - date_width) // 2 - 30, title_y + 120), date, font=title_font, fill=(255, 255, 255))  # Changed to title_font and shifted left
            
            print("Drawing problem info...")
            # Draw problem number and name - increased spacing
            problem_text = f"{problem_info['number']}. {problem_info['title']}"
            
            # Split long titles into two lines
            max_width = size - 100  # Leave some margin on both sides
            words = problem_text.split()
            line1 = []
            line2 = []
            current_line = line1
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_bbox = draw.textbbox((0, 0), test_line, font=text_font)
                test_width = test_bbox[2] - test_bbox[0]
                
                if test_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line is line1:
                        current_line = line2
                        current_line.append(word)
                    else:
                        break
            
            # Draw the two lines
            line1_text = ' '.join(line1)
            line2_text = ' '.join(line2)
            
            # Draw first line
            line1_bbox = draw.textbbox((0, 0), line1_text, font=text_font)
            line1_width = line1_bbox[2] - line1_bbox[0]
            draw.text(((size - line1_width) // 2, title_y + 280), line1_text, font=text_font, fill=(255, 255, 255))
            
            # Draw second line if it exists
            if line2_text:
                line2_bbox = draw.textbbox((0, 0), line2_text, font=text_font)
                line2_width = line2_bbox[2] - line2_bbox[0]
                draw.text(((size - line2_width) // 2, title_y + 340), line2_text, font=text_font, fill=(255, 255, 255))
            
            # Draw difficulty - increased spacing
            difficulty_text = f"\nDifficulty : {problem_info['difficulty']}"
            diff_bbox = draw.textbbox((0, 0), difficulty_text, font=text_font)
            diff_width = diff_bbox[2] - diff_bbox[0]
            draw.text(((size - diff_width) // 2, title_y + 400), difficulty_text, font=text_font, fill=(255, 255, 255))
            
            # Draw tags - increased spacing
            tags_text = f"\nTags : {', '.join(problem_info['tags'])}"
            tags_bbox = draw.textbbox((0, 0), tags_text, font=text_font)
            tags_width = tags_bbox[2] - tags_bbox[0]
            draw.text(((size - tags_width) // 2, title_y + 520), tags_text, font=text_font, fill=(255, 255, 255))
            
            print("Saving image...")
            # Save the image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(self.output_dir, f"leetcode_daily_{timestamp}.png")
            background.save(image_path)
            print(f"Title image saved to: {image_path}")
            return image_path
            
        except Exception as e:
            print(f"Error creating title image: {str(e)}")
            return None
        
    def cleanup(self):
        self.driver.quit()

def main():
    leetcode = LeetCodeDaily()
    try:
        # Get daily challenge info
        problem_info = leetcode.get_daily_challenge()
        if problem_info:
            # Create and save title image
            image_path = leetcode.create_title_image(problem_info)
            if image_path:
                print("Successfully created title image!")
    finally:
        leetcode.cleanup()

if __name__ == "__main__":
    main() 