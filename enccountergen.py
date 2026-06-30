import os
import shutil
from datetime import datetime
from PIL import Image

def generate_custom_counter():
    image_path = input("Enter the path to your GIF or image file: ").strip().strip("'\"")

    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found. Please check the path and try again.")
        return

    output_root = "output"
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    animation_folder_name = f"{base_name}_{timestamp}"
    
    animation_root_dir = os.path.join(output_root, animation_folder_name)
    data_dir = os.path.join(animation_root_dir, "data")
    anim_dir = os.path.join(data_dir, "anim")
    os.makedirs(anim_dir, exist_ok=True)

    # Open image and extract frames
    with Image.open(image_path) as img:
        frames_data = []
        frame_idx = 0
        
        # Check if resizing is needed globally
        orig_w, orig_h = img.size
        needs_resize = (orig_w != 300 or orig_h != 250)
        
        choice = '1'
        crop_pct = 50.0  # Default to 50% (center)
        
        if needs_resize:
            print(f"\nYour image is {orig_w}x{orig_h}. It needs to be normalized to 300x250.")
            print("How would you like to handle the aspect ratio difference?")
            print("1. Cut (Scale and customize crop position)")
            print("2. Stretch (Force resize directly to 300x250)")
            while True:
                choice = input("Enter choice (1 or 2): ").strip()
                if choice in ['1', '2']:
                    break
                print("Invalid choice. Please enter 1 or 2.")
            
            if choice == '1':
                # Calculate aspect ratios to see which side has excess pixels
                orig_aspect = orig_w / orig_h
                target_aspect = 300 / 250
                
                if orig_aspect > target_aspect:
                    # Too wide
                    print("\nAfter scaling to match height, the image is too WIDE.")
                    prompt_msg = "What % from the LEFT side would you like to cut off? (0% = stick to left edge, 50% = center, 100% = stick to right edge): "
                else:
                    # Too tall
                    print("\nAfter scaling to match width, the image is too TALL.")
                    prompt_msg = "What % from the TOP would you like to cut off? (0% = stick to top edge, 50% = center, 100% = stick to bottom edge): "
                
                while True:
                    try:
                        pct_input = input(prompt_msg).strip()
                        crop_pct = float(pct_input)
                        if 0.0 <= crop_pct <= 100.0:
                            break
                        print("Please enter a percentage between 0 and 100.")
                    except ValueError:
                        print("Invalid number. Please enter an arbitrary value between 0 and 100 (e.g., 15, 62.5, 80).")

        while True:
            # Determine duration
            duration = img.info.get("duration", 100)
            if duration == 0:
                duration = 100
            
            # Extract current frame
            current_frame = img.copy()
            
            # Apply chosen resize mechanics
            if needs_resize:
                if choice == '2':
                    current_frame = current_frame.resize((300, 250), Image.Resampling.LANCZOS)
                else:
                    orig_aspect = orig_w / orig_h
                    if orig_aspect > (300 / 250):
                        # Too wide: match target height and calculate wide scaled width
                        new_h = 250
                        new_w = int(orig_w * (250 / orig_h))
                        current_frame = current_frame.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        
                        # Calculate available excess space to shift crop window based on custom %
                        excess_width = new_w - 300
                        left = int(excess_width * (crop_pct / 100.0))
                        top = 0
                    else:
                        # Too tall: match target width and calculate tall scaled height
                        new_w = 300
                        new_h = int(orig_h * (300 / orig_w))
                        current_frame = current_frame.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        
                        # Calculate available excess space to shift crop window based on custom %
                        excess_height = new_h - 250
                        left = 0
                        top = int(excess_height * (crop_pct / 100.0))
                    
                    current_frame = current_frame.crop((left, top, left + 300, top + 250))

            # Save the very first processed frame as icon.png
            if frame_idx == 0:
                icon_path = os.path.join(animation_root_dir, "icon.png")
                icon_img = current_frame.convert("RGB")
                icon_img.save(icon_path, "PNG")
            
            # Format and save frame asset
            delay_sec = duration / 1000.0
            frame_filename = f"frame_{frame_idx:02d}_delay-{delay_sec:.1f}s.jpg"
            frame_filepath = os.path.join(anim_dir, frame_filename)
            
            rgb_img = current_frame.convert("RGB")
            rgb_img.save(frame_filepath, "JPEG")
            
            area_name = f"bg-f{frame_idx+1:05d}"
            frames_data.append({
                "file": f"anim/{frame_filename}",
                "area_name": area_name,
                "duration": duration
            })
            
            frame_idx += 1
            try:
                img.seek(frame_idx)
            except EOFError:
                break

    # --- Generate custom-counter.xml Content ---
    custom_counter_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '',
        '<themes>'
    ]
    
    for f in frames_data:
        custom_counter_lines.append(f'<images file="{f["file"]}" filter="nearest">')
        custom_counter_lines.append(f'    <area name="{f["area_name"]}" xywh="*"/>')
        custom_counter_lines.append('</images>')
        custom_counter_lines.append('')
        
    custom_counter_lines.append('    <images>')
    custom_counter_lines.append('        <animation name="encounter_counter_anim" timeSource="enabled">')
    for f in frames_data:
        custom_counter_lines.append(f'  <frame ref="{f["area_name"]}" duration="{f["duration"]}"/>')
    custom_counter_lines.append('        </animation>')
    custom_counter_lines.append('    </images>')
    custom_counter_lines.append('    ')
    
    custom_counter_lines.append("""  <theme name="encounter-counter" ref="resizableframe">
    <param name="titleAreaTop"><int>8</int></param>
    <param name="titleAreaLeft"><int>11</int></param>
    <param name="titleAreaRight"><int>-1</int></param>
    <param name="titleAreaBottom"><int>20</int></param>
    <param name="border"><border>20,0,0,0</border></param>
    <param name="background"><image>encounter_counter_anim</image></param>
    <param name="minWidth"><int>200</int></param>
    <theme name="content" ref="-defaults">
      <theme name="label" ref="label">
        <param name="minWidth"><int>50</int></param>
        <param name="font"><font>alphabeta-border</font></param>
        <param name="border"><border>7,7</border></param>
        <param name="textAlignment"><enum type="alignment">CENTER</enum></param>
      </theme>
      <theme name="label-left" ref="label">
        <param name="textAlignment"><enum type="alignment">LEFT</enum></param>
      </theme>
      <theme name="icon" ref="label">
        <param name="border"><border>7,7</border></param>
      </theme>
      <theme name="cell" ref="label">
        <param name="background"><image>ui-inputbox.background</image></param>
        <param name="textAlignment"><enum type="alignment">LEFT</enum></param>
        <param name="border"><border>5</border></param>
      </theme>
    </theme>
  </theme>

   <theme name="encounter-counter-expanded" ref="encounter-counter">
      <param name="background"><image>encounter_counter_anim</image></param>
 </theme>

</themes>""")

    # Write out data/custom-counter.xml
    custom_counter_path = os.path.join(data_dir, "custom-counter.xml")
    with open(custom_counter_path, "w", encoding="utf-8") as xml_file:
        xml_file.write("\n".join(custom_counter_lines))

    # --- Generate info.xml Content ---
    info_xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<resource name="{base_name}" version="1.0" description="Custom encounter counter - created with enccountergen" author="enccountergen" weblink="https://github.com/cassnadra?tab=repositories">
  <theme_extensions theme_extension_revision="1">
    <theme_extension name="{base_name}" path="data/custom-counter.xml" is_mobile="false"/>
  </theme_extensions>
</resource>"""

    info_xml_path = os.path.join(animation_root_dir, "info.xml")
    with open(info_xml_path, "w", encoding="utf-8") as xml_file:
        xml_file.write(info_xml_content)

    # --- Package into .zip for PokeMMO ---
    print("\nPackaging files into PokeMMO theme zip format...")
    zip_output_base = os.path.join(output_root, animation_folder_name)
    shutil.make_archive(zip_output_base, 'zip', animation_root_dir)

    print("\n--- Processing Complete ---")
    print(f"Processed {frame_idx} frames successfully.")
    print(f"Directory Created: {animation_root_dir}/")
    print(f"PokeMMO Ready Zip: {zip_output_base}.zip")

if __name__ == "__main__":
    generate_custom_counter()