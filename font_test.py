import pygame
import sys
import os

pygame.init()

print("=" * 50)
print("Pygame Font Diagnostic Report")
print("=" * 50)

print("\n1. Pygame version:", pygame.version.ver)

print("\n2. Font module initialized:", pygame.font.get_init())

print("\n3. Default font:", pygame.font.get_default_font())

try:
    default_font_path = pygame.font.match_font(pygame.font.get_default_font())
    print("   Default font path:", default_font_path)
except Exception as e:
    print("   Error getting default font path:", e)

print("\n4. Testing font rendering:")

test_texts = ["Hello", "中文", "English", "测试"]

print("\n   Using pygame.font.Font(None, 24):")
try:
    font = pygame.font.Font(None, 24)
    for text in test_texts:
        try:
            surface = font.render(text, True, (255, 255, 255))
            print(f"      '{text}' -> size: {surface.get_size()}")
        except Exception as e:
            print(f"      '{text}' -> Error: {e}")
except Exception as e:
    print(f"      Error creating font: {e}")

print("\n5. Checking available fonts (if SysFont works):")

chinese_font_names = [
    'simhei',
    'SimHei',
    'msyh',
    'Microsoft YaHei',
    'simsun',
    'SimSun',
    'mingliu',
    'MingLiU',
]

print("\n   Trying to match Chinese fonts:")
for font_name in chinese_font_names:
    try:
        font_path = pygame.font.match_font(font_name)
        if font_path:
            print(f"      {font_name}: {font_path}")
        else:
            print(f"      {font_name}: Not found")
    except Exception as e:
        print(f"      {font_name}: Error - {e}")

print("\n6. Trying to load fonts with SysFont:")
for font_name in chinese_font_names[:3]:
    try:
        font = pygame.font.SysFont(font_name, 24)
        print(f"      {font_name}: Success")
        for text in ["Hello", "中文"]:
            try:
                surface = font.render(text, True, (255, 255, 255))
                print(f"         '{text}' -> size: {surface.get_size()}")
            except Exception as e:
                print(f"         '{text}' -> Error: {e}")
    except Exception as e:
        print(f"      {font_name}: Error - {e}")

print("\n7. Checking pygame.freetype:")
try:
    import pygame.freetype
    print("   pygame.freetype available")
    pygame.freetype.init()
    print("   pygame.freetype initialized")
    
    try:
        font = pygame.freetype.Font(None, 24)
        print("   Default freetype font loaded")
        for text in ["Hello", "中文"]:
            try:
                surface, rect = font.render(text, (255, 255, 255))
                print(f"      '{text}' -> size: {surface.get_size()}")
            except Exception as e:
                print(f"      '{text}' -> Error: {e}")
    except Exception as e:
        print(f"   Error loading freetype font: {e}")
except ImportError:
    print("   pygame.freetype not available")
except Exception as e:
    print(f"   pygame.freetype error: {e}")

print("\n" + "=" * 50)
print("Diagnostic Complete")
print("=" * 50)

pygame.quit()
